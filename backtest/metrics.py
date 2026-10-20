"""
Quantitative Performance Metrics & Institutional Tear-Sheet Analytics.
Computes Sharpe, Sortino, Calmar, Max Drawdown, Win Rate, Profit Factor,
and Monthly Returns Matrix.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional


class PerformanceMetrics:
    """Calculates comprehensive portfolio and backtest risk-return metrics."""

    @staticmethod
    def calculate_tear_sheet(
        equity_series: pd.Series,
        trades_df: Optional[pd.DataFrame] = None,
        risk_free_rate: float = 0.03
    ) -> Dict[str, Any]:
        """
        Computes standard institutional metrics from daily equity series.
        """
        if equity_series is None or len(equity_series) < 5:
            return {"Error": "Insufficient equity data for metrics calculation."}

        daily_returns = equity_series.pct_change().dropna()
        n_days = len(daily_returns)
        years = max(n_days / 252.0, 0.01)

        # 1. Total & Annualized Return
        total_return = (equity_series.iloc[-1] / equity_series.iloc[0]) - 1.0
        cagr = ((1.0 + total_return) ** (1.0 / years)) - 1.0 if total_return > -1.0 else -1.0

        # 2. Volatility
        daily_vol = daily_returns.std()
        annual_vol = daily_vol * np.sqrt(252.0)

        # 3. Sharpe Ratio
        rf_daily = (1.0 + risk_free_rate) ** (1.0 / 252.0) - 1.0
        excess_returns = daily_returns - rf_daily
        sharpe = (excess_returns.mean() / (daily_vol + 1e-8)) * np.sqrt(252.0)

        # 4. Sortino Ratio (Downside deviation)
        downside_returns = daily_returns[daily_returns < 0.0]
        downside_vol = downside_returns.std() * np.sqrt(252.0) if len(downside_returns) > 0 else 1e-6
        sortino = (excess_returns.mean() * 252.0) / (downside_vol + 1e-8)

        # 5. Drawdown Analytics
        running_max = equity_series.cummax()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown = float(drawdown.min())

        # Max Drawdown Duration
        is_in_dd = drawdown < 0.0
        dd_runs = is_in_dd.astype(int).groupby((~is_in_dd).cumsum()).cumsum()
        max_dd_duration = int(dd_runs.max()) if len(dd_runs) > 0 else 0

        # 6. Calmar Ratio
        calmar = cagr / abs(max_drawdown) if abs(max_drawdown) > 1e-6 else 0.0

        # 7. Trade Statistics (if trades_df provided)
        trade_stats = {}
        if trades_df is not None and not trades_df.empty and "pnl" in trades_df.columns:
            pnls = trades_df["pnl"]
            wins = pnls[pnls > 0]
            losses = pnls[pnls < 0]

            total_trades = len(pnls)
            win_rate = (len(wins) / total_trades) * 100.0 if total_trades > 0 else 0.0
            gross_profit = float(wins.sum()) if len(wins) > 0 else 0.0
            gross_loss = abs(float(losses.sum())) if len(losses) > 0 else 1e-6
            profit_factor = gross_profit / gross_loss

            avg_pnl = float(pnls.mean())
            avg_win = float(wins.mean()) if len(wins) > 0 else 0.0
            avg_loss = float(losses.mean()) if len(losses) > 0 else 0.0
            win_loss_ratio = abs(avg_win / avg_loss) if abs(avg_loss) > 1e-6 else 0.0

            trade_stats = {
                "total_trades": total_trades,
                "win_rate_pct": round(win_rate, 2),
                "profit_factor": round(profit_factor, 2),
                "avg_trade_pnl": round(avg_pnl, 2),
                "avg_win": round(avg_win, 2),
                "avg_loss": round(avg_loss, 2),
                "win_loss_ratio": round(win_loss_ratio, 2),
            }
        else:
            trade_stats = {
                "total_trades": 0,
                "win_rate_pct": 0.0,
                "profit_factor": 0.0,
                "avg_trade_pnl": 0.0,
            }

        metrics = {
            "initial_capital": float(equity_series.iloc[0]),
            "final_equity": float(equity_series.iloc[-1]),
            "total_return_pct": round(total_return * 100.0, 2),
            "cagr_pct": round(cagr * 100.0, 2),
            "annual_volatility_pct": round(annual_vol * 100.0, 2),
            "sharpe_ratio": round(float(sharpe), 2),
            "sortino_ratio": round(float(sortino), 2),
            "calmar_ratio": round(float(calmar), 2),
            "max_drawdown_pct": round(max_drawdown * 100.0, 2),
            "max_drawdown_duration_days": max_dd_duration,
            "daily_returns": daily_returns,
            "drawdown_series": drawdown,
            **trade_stats
        }

        return metrics

    @staticmethod
    def generate_monthly_table(equity_series: pd.Series) -> pd.DataFrame:
        """
        Creates a monthly returns matrix table (Year x Month).
        """
        daily_ret = equity_series.pct_change().dropna()
        if daily_ret.empty:
            return pd.DataFrame()

        # Monthly compounded return
        monthly_ret = daily_ret.resample("ME").apply(lambda r: (1.0 + r).prod() - 1.0)
        
        df = pd.DataFrame({
            "Year": monthly_ret.index.year,
            "Month": monthly_ret.index.month,
            "Return": monthly_ret.values * 100.0
        })

        month_names = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
        }
        df["Month"] = df["Month"].map(month_names)

        pivot = df.pivot(index="Year", columns="Month", values="Return")
        
        # Order columns chronologically
        cols = [m for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"] if m in pivot.columns]
        pivot = pivot[cols]

        # Calculate Full Year return
        pivot["Year_Total"] = pivot.apply(lambda row: ((1.0 + row.dropna() / 100.0).prod() - 1.0) * 100.0, axis=1)
        return pivot.round(2)
