"""
Paper Trading & Live Bovine Signal Monitor.
Scans live multi-factor indicators, generates execution recommendations,
and maintains persistent simulated portfolio state.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd

from config import DATA_DIR, COMMODITY_SPECS, RISK_CONFIG, ENSO_CONFIG
from data.data_loader import UnifiedDataLoader
from models.strategy import BovineQuantitativeStrategy
from execution.risk_manager import BovineRiskManager
from factors.technical import BovineTechnicalFactors
from factors.macro_weather import MacroWeatherFactor


class BovinePaperTrader:
    """Live / paper execution engine and signal monitor."""

    def __init__(
        self,
        portfolio_file: str = os.path.join(DATA_DIR, "paper_portfolio.json"),
        initial_capital: float = 100_000.0,
        enso_regime: Optional[str] = "super_elnino"
    ):
        self.portfolio_file = portfolio_file
        self.initial_capital = initial_capital
        self.enso_regime = enso_regime
        self.data_loader = UnifiedDataLoader()
        self.strategy = BovineQuantitativeStrategy(enso_regime=self.enso_regime)
        self.risk_manager = BovineRiskManager(enso_regime=self.enso_regime)
        self.portfolio = self._load_portfolio()

    def _load_portfolio(self) -> Dict[str, Any]:
        """Loads paper trading portfolio state from disk or initializes defaults."""
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass

        default_state = {
            "created_at": datetime.now().isoformat(),
            "cash": self.initial_capital,
            "equity": self.initial_capital,
            "positions": {},
            "trade_history": [],
            "last_updated": datetime.now().isoformat()
        }
        self._save_portfolio(default_state)
        return default_state

    def _save_portfolio(self, state: Dict[str, Any]):
        """Saves paper trading portfolio state to disk."""
        with open(self.portfolio_file, "w") as f:
            json.dump(state, f, indent=2)

    def scan_live_signals(
        self,
        symbols: Optional[List[str]] = None,
        enso_regime: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Pulls current market state across all bovine commodities,
        evaluates all factors + ML, and computes live actionable signals.
        Compensates for ENSO / Super El Niño regime.
        """
        if symbols is None:
            symbols = ["LE=F", "GF=F"]

        regime = enso_regime if enso_regime is not None else self.enso_regime
        self.strategy.enso_regime = regime
        self.risk_manager.enso_regime = regime

        market_data = self.data_loader.load_dataset()
        scan_results = {}
        enso_telemetry = MacroWeatherFactor.get_enso_telemetry(
            market_data.get("ENSO", None), active_regime=regime
        )

        for sym in symbols:
            if sym not in market_data or market_data[sym].empty:
                continue

            df = market_data[sym]
            signals_df = self.strategy.generate_signals(market_data, target_asset=sym)
            last_row = signals_df.iloc[-1]
            last_price = float(df["Close"].iloc[-1])
            prev_price = float(df["Close"].iloc[-2]) if len(df) > 1 else last_price
            price_chg = round((last_price - prev_price) / prev_price * 100.0, 2)

            atr = float(BovineTechnicalFactors.calculate_atr(df).iloc[-1])
            vol = float(BovineTechnicalFactors.calculate_garman_klass_vol(df).iloc[-1])

            target_weight = float(last_row["target_weight"])
            composite_alpha = float(last_row["composite_alpha"])

            # Compute Recommended Position Size
            ideal_contracts = self.risk_manager.calculate_position_size(
                symbol=sym,
                price=last_price,
                asset_volatility=vol,
                portfolio_equity=self.portfolio["equity"],
                current_drawdown=0.0,
                target_weight=target_weight
            )

            # Compute Stop Levels
            spec = COMMODITY_SPECS.get(sym, COMMODITY_SPECS["LE=F"])
            if ideal_contracts > 0:
                stop_loss = round(last_price - (self.risk_manager.atr_stop_mult * atr), 3)
                take_profit = round(last_price + (self.risk_manager.atr_tp_mult * atr), 3)
            elif ideal_contracts < 0:
                stop_loss = round(last_price + (self.risk_manager.atr_stop_mult * atr), 3)
                take_profit = round(last_price - (self.risk_manager.atr_tp_mult * atr), 3)
            else:
                stop_loss = 0.0
                take_profit = 0.0

            scan_results[sym] = {
                "symbol": sym,
                "name": spec.name,
                "latest_price": round(last_price, 3),
                "daily_change_pct": price_chg,
                "signal_regime": last_row["signal_regime"],
                "target_weight": round(target_weight, 2),
                "composite_alpha": round(composite_alpha, 3),
                "recommended_contracts": ideal_contracts,
                "stop_loss_price": stop_loss,
                "take_profit_price": take_profit,
                "atr_14": round(atr, 3),
                "annualized_vol_pct": round(vol * 100.0, 1),
                "factor_breakdown": {
                    "crush_margin": round(float(last_row["crush_margin"]), 3),
                    "cot_sentiment": round(float(last_row["cot_sentiment"]), 3),
                    "seasonality": round(float(last_row["seasonality"]), 3),
                    "macro_drought": round(float(last_row["macro_drought"]), 3),
                    "technical_trend": round(float(last_row["technical_trend"]), 3),
                    "ml_score": round(float(last_row.get("ml_score", 0.0)), 3),
                },
                "enso_telemetry": enso_telemetry
            }

        return scan_results

    def execute_rebalance(self, live_signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executes simulated orders based on latest live scan signals.
        """
        orders_executed = []
        commission_fee = RISK_CONFIG.get("commission_per_contract", 2.50)

        for sym, sig in live_signals.items():
            target_contracts = sig["recommended_contracts"]
            current_pos = self.portfolio["positions"].get(sym, {"contracts": 0, "entry_price": 0.0})
            curr_contracts = current_pos["contracts"]

            if target_contracts != curr_contracts:
                delta = target_contracts - curr_contracts
                price = sig["latest_price"]
                spec = COMMODITY_SPECS.get(sym, COMMODITY_SPECS["LE=F"])

                # Realize PnL on existing closed portion
                if curr_contracts != 0 and (target_contracts == 0 or (target_contracts * curr_contracts < 0)):
                    pnl = curr_contracts * (price - current_pos["entry_price"]) * spec.point_value
                    comm = abs(curr_contracts) * commission_fee
                    net_pnl = pnl - comm
                    self.portfolio["cash"] += net_pnl
                    
                    self.portfolio["trade_history"].append({
                        "timestamp": datetime.now().isoformat(),
                        "symbol": sym,
                        "action": "CLOSE",
                        "contracts": curr_contracts,
                        "exit_price": price,
                        "pnl": round(net_pnl, 2)
                    })

                # Open new position
                if target_contracts != 0:
                    comm = abs(target_contracts) * commission_fee
                    self.portfolio["cash"] -= comm
                    self.portfolio["positions"][sym] = {
                        "contracts": target_contracts,
                        "entry_price": price,
                        "entry_time": datetime.now().isoformat(),
                        "stop_loss": sig["stop_loss_price"],
                        "take_profit": sig["take_profit_price"]
                    }
                else:
                    self.portfolio["positions"].pop(sym, None)

                orders_executed.append({
                    "symbol": sym,
                    "target_contracts": target_contracts,
                    "filled_price": price,
                    "delta": delta,
                    "timestamp": datetime.now().isoformat()
                })

        # Update Portfolio Equity
        unrealized = 0.0
        for sym, pos in self.portfolio["positions"].items():
            spec = COMMODITY_SPECS.get(sym, COMMODITY_SPECS["LE=F"])
            cur_price = live_signals.get(sym, {}).get("latest_price", pos["entry_price"])
            unrealized += pos["contracts"] * (cur_price - pos["entry_price"]) * spec.point_value

        self.portfolio["equity"] = round(self.portfolio["cash"] + unrealized, 2)
        self.portfolio["last_updated"] = datetime.now().isoformat()
        self._save_portfolio(self.portfolio)

        return orders_executed
