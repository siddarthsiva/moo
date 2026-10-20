"""
Project MOO - Command-Line Interface & Orchestrator.
Allows running live alpha scans, full strategy backtests, ML model training,
paper trade execution, or launching the Streamlit interactive dashboard.
"""

import os
import sys
import argparse
import subprocess
from tabulate import tabulate
from datetime import datetime

# Configure UTF-8 encoding on Windows to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import COMMODITY_SPECS, DEFAULT_FACTOR_WEIGHTS
from data.data_loader import UnifiedDataLoader
from models.strategy import BovineQuantitativeStrategy
from backtest.backtester import BovineBacktester
from execution.paper_trader import BovinePaperTrader


def print_banner():
    banner = r"""
  ========================================================================
     __  __  ___   ___     ___                  _   
    |  \/  |/ _ \ / _ \   / _ \ _  _ __ _ _ _ _| |_ 
    | |\/| | (_) | (_) | | (_) | || / _` | ' \  _|
    |_|  |_|\___/ \___/   \__\_\\_,_\__,_|_||_\__|
    Ultimate Multi-Factor Bovine Commodity Trading Engine
    100% Free & Open-Source Institutional Quantitative Platform
  ========================================================================
    """
    print(banner)


def run_live_scan(symbols=None, enso="super_elnino"):
    """Performs live multi-factor scan and prints formatted terminal report."""
    if symbols is None:
        symbols = ["LE=F", "GF=F"]

    print(f"\n[+] Running Multi-Factor Alpha Scan on {symbols} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    print(f"    ENSO Climatology Regime: {enso.upper()} (Compensating for active climate shock)\n")
    trader = BovinePaperTrader(enso_regime=enso)
    scan_results = trader.scan_live_signals(symbols, enso_regime=enso)

    summary_table = []
    for sym, res in scan_results.items():
        summary_table.append([
            res["symbol"],
            res["name"],
            f"${res['latest_price']:.2f}",
            f"{res['daily_change_pct']:+.2f}%",
            res["signal_regime"],
            f"{res['composite_alpha']:+.3f}",
            f"{res['target_weight']*100:.0f}%",
            f"{res['recommended_contracts']} contracts",
            f"${res['stop_loss_price']:.2f}",
            f"${res['take_profit_price']:.2f}",
            f"{res['annualized_vol_pct']}%"
        ])

    headers = ["Ticker", "Name", "Price", "1D Chg", "Regime", "Alpha", "Target %", "Size", "Stop Loss", "Take Profit", "Ann. Vol"]
    print(tabulate(summary_table, headers=headers, tablefmt="grid"))

    # Print ENSO Climatology Telemetry
    sample_sym = list(scan_results.keys())[0] if scan_results else None
    if sample_sym and "enso_telemetry" in scan_results[sample_sym]:
        t = scan_results[sample_sym]["enso_telemetry"]
        print("\n--- [CLIMATE] ENSO Climatology & Super El Nino Telemetry ---")
        enso_table = [
            ["Active ENSO Phase", t["phase"]],
            ["Oceanic Niño Index (ONI)", f"{t['oni_anomaly']:+.2f}°C Sea Surface Anomaly"],
            ["Cow-Calf Heifer Retention", t["heifer_retention"]],
            ["Feed Grain / Corn Outlook", t["corn_feed_trend"]],
            ["Feedlot Mud & ADG Risk", t["winter_mud_risk"]],
            ["Australian Beef Trade Balance", t["australian_beef_status"]],
            ["Structural Bovine Alpha Bias", t["bovine_alpha_bias"]]
        ]
        print(tabulate(enso_table, headers=["ENSO Metric / Channel", "Status & Quantitative Impact"], tablefmt="simple"))

    print("\n--- Factor Score Decomposition [-1.0 to +1.0] ---")
    for sym, res in scan_results.items():
        f = res["factor_breakdown"]
        f_table = [
            ["Cattle Crush / Feedlot Margin", f"{f['crush_margin']:+.3f}"],
            ["CFTC COT Smart Money Sentiment", f"{f['cot_sentiment']:+.3f}"],
            ["Biological Bovine Seasonality", f"{f['seasonality']:+.3f}"],
            ["US Drought & Macro DXY Elasticity", f"{f['macro_drought']:+.3f}"],
            ["Kalman Adaptive Trend & Momentum", f"{f['technical_trend']:+.3f}"],
            ["Walk-Forward ML Ensemble Alpha", f"{f['ml_score']:+.3f}"],
        ]
        print(f"\n[{sym}] {res['name']}:")
        print(tabulate(f_table, headers=["Factor Name", "Normalized Score"], tablefmt="simple"))


def run_full_backtest(symbol="LE=F", start_date="2018-01-01", mode="directional", capital=100_000.0, enable_ml=True, enso="super_elnino"):
    """Runs high-fidelity backtest simulation and outputs institutional tear sheet."""
    print(f"\n[+] Initiating Backtest Simulation:")
    print(f"    Symbol:         {symbol} ({COMMODITY_SPECS.get(symbol, COMMODITY_SPECS['LE=F']).name})")
    print(f"    Mode:           {mode}")
    print(f"    Start Date:     {start_date}")
    print(f"    Initial Capital: ${capital:,.2f}")
    print(f"    ML Ensemble:    {enable_ml}")
    print(f"    ENSO Regime:    {enso.upper()}\n")

    loader = UnifiedDataLoader()
    market_data = loader.load_dataset(start_date=start_date)

    strategy = BovineQuantitativeStrategy(mode=mode, enable_ml=enable_ml, enso_regime=enso)
    signals_df = strategy.generate_signals(market_data, target_asset=symbol)

    backtester = BovineBacktester(initial_capital=capital)
    results = backtester.run_backtest(market_data, signals_df, target_symbol=symbol)

    m = results["metrics"]
    metrics_table = [
        ["Initial Capital", f"${m['initial_capital']:,.2f}"],
        ["Final Equity", f"${m['final_equity']:,.2f}"],
        ["Total Return (%)", f"{m['total_return_pct']:+.2f}%"],
        ["CAGR (%)", f"{m['cagr_pct']:+.2f}%"],
        ["Annualized Volatility (%)", f"{m['annual_volatility_pct']:.2f}%"],
        ["Sharpe Ratio (Rf=3%)", f"{m['sharpe_ratio']:.2f}"],
        ["Sortino Ratio", f"{m['sortino_ratio']:.2f}"],
        ["Calmar Ratio", f"{m['calmar_ratio']:.2f}"],
        ["Max Drawdown (%)", f"{m['max_drawdown_pct']:.2f}%"],
        ["Max DD Duration (Days)", f"{m['max_drawdown_duration_days']} days"],
        ["Total Executed Trades", f"{m['total_trades']}"],
        ["Win Rate (%)", f"{m['win_rate_pct']:.1f}%"],
        ["Profit Factor", f"{m['profit_factor']:.2f}"],
        ["Average Trade PnL ($)", f"${m['avg_trade_pnl']:,.2f}"],
    ]

    print("=" * 60)
    print("       INSTITUTIONAL PERFORMANCE TEAR SHEET")
    print("=" * 60)
    print(tabulate(metrics_table, headers=["Performance Metric", "Strategy Value"], tablefmt="grid"))

    print("\n--- Monthly Returns Matrix (%) ---")
    monthly = results["monthly_table"]
    if not monthly.empty:
        print(tabulate(monthly, headers="keys", tablefmt="simple"))


def execute_rebalance(enso="super_elnino"):
    """Executes paper trade rebalancing based on live scan."""
    trader = BovinePaperTrader(enso_regime=enso)
    signals = trader.scan_live_signals(["LE=F", "GF=F"], enso_regime=enso)
    orders = trader.execute_rebalance(signals)
    print(f"\n[+] Paper Trade Rebalance Execution (ENSO: {enso.upper()}):")
    if orders:
        for o in orders:
            print(f"    * {o['symbol']}: Target {o['target_contracts']} contracts @ ${o['filled_price']} (Delta: {o['delta']})")
    else:
        print("    * No orders needed. Portfolio is in target equilibrium.")
    print(f"\n    Current Portfolio Equity: ${trader.portfolio['equity']:,.2f}")
    print(f"    Available Cash:           ${trader.portfolio['cash']:,.2f}\n")


def launch_dashboard():
    """Launches the Streamlit Web Application."""
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "app.py")
    print(f"\n[+] Launching Streamlit Bovine Trading Cockpit...")
    print(f"    URL: http://localhost:8501\n")
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], env=env)


def main():
    print_banner()
    parser = argparse.ArgumentParser(description="ALPHA-BOVINE: Ultimate Bovine Commodity Trading Engine")
    parser.add_argument(
        "--mode",
        choices=["scan", "backtest", "rebalance", "dashboard", "train-ml"],
        default="scan",
        help="Execution mode (default: scan)"
    )
    parser.add_argument("--symbol", default="LE=F", help="Target symbol (e.g. LE=F, GF=F)")
    parser.add_argument("--start-date", default="2018-01-01", help="Backtest start date (YYYY-MM-DD)")
    parser.add_argument("--strategy", choices=["directional", "spread_trading"], default="directional", help="Strategy mode")
    parser.add_argument("--capital", type=float, default=100000.0, help="Initial capital in USD")
    parser.add_argument("--no-ml", action="store_true", help="Disable ML ensemble in backtest")
    parser.add_argument(
        "--enso",
        choices=["super_elnino", "elnino", "neutral", "lanina"],
        default="super_elnino",
        help="ENSO climatology compensation regime (default: super_elnino)"
    )

    args = parser.parse_args()

    if args.mode == "scan":
        run_live_scan(["LE=F", "GF=F"], enso=args.enso)
    elif args.mode == "backtest":
        run_full_backtest(
            symbol=args.symbol,
            start_date=args.start_date,
            mode=args.strategy,
            capital=args.capital,
            enable_ml=not args.no_ml,
            enso=args.enso
        )
    elif args.mode == "rebalance":
        execute_rebalance(enso=args.enso)
    elif args.mode == "dashboard":
        launch_dashboard()
    elif args.mode == "train-ml":
        print("\n[+] Training Walk-Forward Machine Learning Alpha Model...")
        loader = UnifiedDataLoader()
        m_data = loader.load_dataset()
        strat = BovineQuantitativeStrategy(enable_ml=True, enso_regime=args.enso)
        signals = strat.generate_signals(m_data, target_asset=args.symbol)
        print("\n[+] ML Training Complete. Feature Importances:")
        for feat, imp in strat.ml_model.feature_importances.items():
            print(f"    * {feat:<20}: {imp*100:.2f}%")


if __name__ == "__main__":
    main()
