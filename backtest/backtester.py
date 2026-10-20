"""
Bovine Quantitative Backtesting Engine.
Executes event-driven futures simulation with contract multipliers, point values,
slippage, commission, volatility targeting, dynamic ATR stops, and trailing exits.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple

from config import COMMODITY_SPECS, CommoditySpec, RISK_CONFIG
from execution.risk_manager import BovineRiskManager, PositionRiskState
from factors.technical import BovineTechnicalFactors
from backtest.metrics import PerformanceMetrics


class BovineBacktester:
    """High-fidelity backtesting engine for cattle futures and spreads."""

    def __init__(
        self,
        initial_capital: float = 100_000.0,
        risk_config: Optional[Dict] = None
    ):
        self.initial_capital = initial_capital
        self.risk_cfg = risk_config if risk_config is not None else RISK_CONFIG.copy()
        self.risk_manager = BovineRiskManager(self.risk_cfg)

    def run_backtest(
        self,
        market_data: Dict[str, pd.DataFrame],
        signals_df: pd.DataFrame,
        target_symbol: str = "LE=F"
    ) -> Dict[str, Any]:
        """
        Runs the backtest simulation over aligned market data and trading signals.
        """
        if target_symbol not in market_data:
            raise ValueError(f"Symbol {target_symbol} missing from market data.")

        df = market_data[target_symbol]
        spec: CommoditySpec = COMMODITY_SPECS.get(target_symbol, COMMODITY_SPECS["LE=F"])
        multiplier = spec.point_value

        # Calculate ATR and Volatility series
        atr_series = BovineTechnicalFactors.calculate_atr(df, period=14).fillna(2.0)
        vol_series = BovineTechnicalFactors.calculate_garman_klass_vol(df, window=20).fillna(0.16)

        # Simulation State
        cash = self.initial_capital
        current_contracts = 0
        entry_price = 0.0
        current_pos_state: Optional[PositionRiskState] = None

        dates = df.index.intersection(signals_df.index)
        equity_records = []
        trades_log = []

        slippage_pct = self.risk_cfg.get("slippage_bps", 2.5) / 10000.0
        commission_per_contract = self.risk_cfg.get("commission_per_contract", 2.50)

        for i, dt in enumerate(dates):
            bar_open = float(df.loc[dt, "Open"])
            bar_high = float(df.loc[dt, "High"])
            bar_low = float(df.loc[dt, "Low"])
            bar_close = float(df.loc[dt, "Close"])
            current_atr = float(atr_series.loc[dt])
            current_vol = float(vol_series.loc[dt])

            target_weight = float(signals_df.loc[dt, "target_weight"])

            # 1. Update Portfolio Equity
            if current_contracts != 0 and current_pos_state is not None:
                unrealized_pnl = current_contracts * (bar_close - entry_price) * multiplier
            else:
                unrealized_pnl = 0.0

            total_equity = cash + unrealized_pnl

            # Calculate current running drawdown
            prev_peak = max([r["equity"] for r in equity_records]) if equity_records else self.initial_capital
            running_peak = max(prev_peak, total_equity)
            curr_drawdown = max(0.0, (running_peak - total_equity) / (running_peak + 1e-6))

            # 2. Check Stop Loss / Take Profit / Trailing Exits on open position
            exit_triggered = False
            exit_reason = ""
            exit_price = bar_close

            if current_contracts != 0 and current_pos_state is not None:
                # Test high/low against stops
                test_price = bar_low if current_contracts > 0 else bar_high
                should_exit, reason, stop_p = self.risk_manager.update_trailing_stops(
                    current_pos_state, test_price, current_atr
                )

                if should_exit:
                    exit_triggered = True
                    exit_reason = reason
                    # Apply slippage on exit
                    exit_slip = stop_p * (1.0 - slippage_pct) if current_contracts > 0 else stop_p * (1.0 + slippage_pct)
                    exit_price = exit_slip

                    # Realize Trade PnL
                    trade_pnl = current_contracts * (exit_price - entry_price) * multiplier
                    comm = abs(current_contracts) * commission_per_contract
                    net_trade_pnl = trade_pnl - comm

                    cash += net_trade_pnl
                    total_equity = cash

                    trades_log.append({
                        "entry_date": current_pos_state.symbol, # stored entry date in symbol temporarily or metadata
                        "exit_date": dt.strftime("%Y-%m-%d"),
                        "symbol": target_symbol,
                        "side": "LONG" if current_contracts > 0 else "SHORT",
                        "contracts": abs(current_contracts),
                        "entry_price": round(entry_price, 3),
                        "exit_price": round(exit_price, 3),
                        "pnl": round(net_trade_pnl, 2),
                        "commission": round(comm, 2),
                        "exit_reason": exit_reason
                    })

                    current_contracts = 0
                    current_pos_state = None
                    unrealized_pnl = 0.0

            # 3. Position Sizing & Rebalancing
            if not exit_triggered:
                ideal_contracts = self.risk_manager.calculate_position_size(
                    symbol=target_symbol,
                    price=bar_close,
                    asset_volatility=current_vol,
                    portfolio_equity=total_equity,
                    current_drawdown=curr_drawdown,
                    target_weight=target_weight
                )

                # If position needs to change
                if ideal_contracts != current_contracts:
                    # Close existing position if reversing or going flat
                    if current_contracts != 0:
                        close_slip = bar_close * (1.0 - slippage_pct) if current_contracts > 0 else bar_close * (1.0 + slippage_pct)
                        trade_pnl = current_contracts * (close_slip - entry_price) * multiplier
                        comm = abs(current_contracts) * commission_per_contract
                        net_trade_pnl = trade_pnl - comm
                        cash += net_trade_pnl

                        trades_log.append({
                            "entry_date": str(current_pos_state.symbol) if current_pos_state else "",
                            "exit_date": dt.strftime("%Y-%m-%d"),
                            "symbol": target_symbol,
                            "side": "LONG" if current_contracts > 0 else "SHORT",
                            "contracts": abs(current_contracts),
                            "entry_price": round(entry_price, 3),
                            "exit_price": round(close_slip, 3),
                            "pnl": round(net_trade_pnl, 2),
                            "commission": round(comm, 2),
                            "exit_reason": "SIGNAL_REBALANCE"
                        })

                        current_contracts = 0
                        current_pos_state = None

                    # Open new position
                    if ideal_contracts != 0:
                        entry_slip = bar_close * (1.0 + slippage_pct) if ideal_contracts > 0 else bar_close * (1.0 - slippage_pct)
                        entry_price = entry_slip
                        current_contracts = ideal_contracts
                        comm = abs(current_contracts) * commission_per_contract
                        cash -= comm

                        # Set Stop Loss & Take Profit
                        if current_contracts > 0:
                            sl = entry_price - (self.risk_manager.atr_stop_mult * current_atr)
                            tp = entry_price + (self.risk_manager.atr_tp_mult * current_atr)
                        else:
                            sl = entry_price + (self.risk_manager.atr_stop_mult * current_atr)
                            tp = entry_price - (self.risk_manager.atr_tp_mult * current_atr)

                        current_pos_state = PositionRiskState(
                            symbol=dt.strftime("%Y-%m-%d"),
                            entry_price=entry_price,
                            current_price=bar_close,
                            position_units=current_contracts,
                            stop_loss_price=sl,
                            take_profit_price=tp,
                            trailing_high_water=entry_price,
                            atr_at_entry=current_atr,
                            unrealized_pnl=0.0
                        )

            # Recompute total equity at close of bar
            if current_contracts != 0:
                unrealized_pnl = current_contracts * (bar_close - entry_price) * multiplier
            else:
                unrealized_pnl = 0.0

            total_equity = cash + unrealized_pnl

            equity_records.append({
                "date": dt,
                "equity": total_equity,
                "cash": cash,
                "unrealized_pnl": unrealized_pnl,
                "contracts": current_contracts,
                "close_price": bar_close,
                "target_weight": target_weight
            })

        # Assemble Output DataFrames
        equity_df = pd.DataFrame(equity_records).set_index("date")
        trades_df = pd.DataFrame(trades_log)

        # Benchmark Buy & Hold Equity (1 Contract equivalent or 100% buy and hold)
        bnh_returns = df.loc[dates, "Close"].pct_change().fillna(0.0)
        bnh_equity = self.initial_capital * (1.0 + bnh_returns).cumprod()
        equity_df["benchmark_bnh"] = bnh_equity

        # Compute Institutional Performance Metrics
        metrics = PerformanceMetrics.calculate_tear_sheet(
            equity_series=equity_df["equity"],
            trades_df=trades_df,
            risk_free_rate=0.03
        )

        monthly_table = PerformanceMetrics.generate_monthly_table(equity_df["equity"])

        return {
            "equity_curve": equity_df,
            "trades_df": trades_df,
            "metrics": metrics,
            "monthly_table": monthly_table,
            "target_symbol": target_symbol
        }
