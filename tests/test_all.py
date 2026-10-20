"""
Comprehensive Test Suite for Project MOO (ALPHA-BOVINE).
Tests data loading, factors, ML predictors, risk managers, backtester, and paper trader.
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import COMMODITY_SPECS, CATTLE_CRUSH_CONFIG, RISK_CONFIG, ENSO_CONFIG, SUPER_ELNINO_FACTOR_WEIGHTS
from data.mock_generator import BovineSyntheticDataGenerator
from data.data_loader import UnifiedDataLoader
from data.macro_fetcher import MacroDataFetcher
from factors.crush_spread import CattleCrushFactor
from factors.sentiment_cot import COTSentimentFactor
from factors.seasonality import BovineSeasonalityFactor
from factors.macro_weather import MacroWeatherFactor
from factors.technical import BovineTechnicalFactors
from factors.factor_engine import BovineFactorEngine
from models.ml_predictor import BovineMLAlphaModel
from models.strategy import BovineQuantitativeStrategy
from execution.risk_manager import BovineRiskManager, PositionRiskState
from execution.paper_trader import BovinePaperTrader
from backtest.backtester import BovineBacktester
from backtest.metrics import PerformanceMetrics


class TestBovineTradingSystem(unittest.TestCase):
    """Unit and Integration tests for all components of the Bovine Trading System."""

    @classmethod
    def setUpClass(cls):
        cls.mock_gen = BovineSyntheticDataGenerator(seed=42)
        cls.market_data = cls.mock_gen.generate_full_market_history(start_date="2020-01-01", end_date="2024-01-01")

    def test_mock_data_generation(self):
        """Verify mock data generates all necessary assets with proper shapes and columns."""
        self.assertIn("LE=F", self.market_data)
        self.assertIn("GF=F", self.market_data)
        self.assertIn("ZC=F", self.market_data)
        self.assertIn("COT_LE", self.market_data)
        self.assertIn("DROUGHT", self.market_data)

        df_le = self.market_data["LE=F"]
        self.assertTrue(len(df_le) > 500)
        self.assertTrue(all(col in df_le.columns for col in ["Open", "High", "Low", "Close", "Volume"]))
        self.assertTrue((df_le["High"] >= df_le["Low"]).all())

    def test_cattle_crush_factor(self):
        """Verify Cattle Crush and Feedlot Margin calculations."""
        calc = CattleCrushFactor()
        live = self.market_data["LE=F"]["Close"]
        feeder = self.market_data["GF=F"]["Close"]
        corn = self.market_data["ZC=F"]["Close"]

        crush_df = calc.calculate_crush_metrics(live, feeder, corn)
        self.assertIn("CrushMargin_Head", crush_df.columns)
        self.assertIn("FeederLiveRatio", crush_df.columns)
        self.assertIn("Margin_ZScore", crush_df.columns)

        # Verify factor score is within [-1.0, +1.0]
        score = calc.compute_factor_score(live, feeder, corn, target_asset="LE=F")
        self.assertTrue((score >= -1.0).all() and (score <= 1.0).all())

    def test_cot_sentiment_factor(self):
        """Verify CFTC COT smart money factor score."""
        cot_calc = COTSentimentFactor()
        cot_df = self.market_data["COT_LE"]
        score = cot_calc.compute_factor_score(cot_df, target_asset="LE=F")
        self.assertTrue(len(score) == len(cot_df))
        self.assertTrue((score >= -1.0).all() and (score <= 1.0).all())

    def test_seasonality_factor(self):
        """Verify biological bovine seasonality score."""
        seas_calc = BovineSeasonalityFactor()
        score = seas_calc.compute_factor_score(self.market_data["LE=F"]["Close"], target_asset="LE=F")
        self.assertTrue(len(score) == len(self.market_data["LE=F"]))
        self.assertTrue((score >= -1.0).all() and (score <= 1.0).all())

    def test_macro_weather_factor(self):
        """Verify Drought and Macro DXY score."""
        macro_calc = MacroWeatherFactor()
        score = macro_calc.compute_factor_score(
            drought_df=self.market_data["DROUGHT"],
            dxy_df=self.market_data["DX-Y.NYB"],
            live_price=self.market_data["LE=F"]["Close"],
            hogs_price=self.market_data["HE=F"]["Close"],
            target_asset="LE=F"
        )
        self.assertTrue((score >= -1.0).all() and (score <= 1.0).all())

    def test_technical_factors(self):
        """Verify Kalman trend, ATR, RSI, and Garman-Klass volatility."""
        df = self.market_data["LE=F"]
        atr = BovineTechnicalFactors.calculate_atr(df)
        self.assertTrue((atr.dropna() > 0).all())

        rsi = BovineTechnicalFactors.calculate_rsi(df["Close"])
        self.assertTrue((rsi.dropna() >= 0).all() and (rsi.dropna() <= 100).all())

        kalman = BovineTechnicalFactors.calculate_kalman_trend(df["Close"])
        self.assertEqual(len(kalman), len(df))

        vol = BovineTechnicalFactors.calculate_garman_klass_vol(df)
        self.assertTrue((vol.dropna() > 0).all())

        tech_calc = BovineTechnicalFactors()
        score = tech_calc.compute_factor_score(df)
        self.assertTrue((score >= -1.0).all() and (score <= 1.0).all())

    def test_factor_engine(self):
        """Verify factor aggregation, composite alpha, and IC calculations."""
        engine = BovineFactorEngine()
        factors_df = engine.compute_all_factors(self.market_data, target_asset="LE=F")
        self.assertEqual(len(factors_df.columns), 5)

        composite = engine.compute_composite_alpha(factors_df)
        self.assertTrue((composite >= -1.0).all() and (composite <= 1.0).all())

        ic = engine.calculate_factor_ic(factors_df, self.market_data["LE=F"]["Close"])
        self.assertIn("crush_margin", ic)
        self.assertIn("cot_sentiment", ic)

    def test_ml_alpha_model(self):
        """Verify ML feature engineering and walk-forward prediction."""
        engine = BovineFactorEngine()
        factors_df = engine.compute_all_factors(self.market_data, target_asset="LE=F")
        target_df = self.market_data["LE=F"]

        ml_model = BovineMLAlphaModel(forward_horizon=5, train_window=300)
        features, target = ml_model.build_features(target_df, factors_df)
        self.assertTrue(len(features) > 0)
        self.assertTrue(len(target) > 0)

        ml_score, importances = ml_model.walk_forward_train_predict(features, target, step_size=50)
        self.assertTrue((ml_score >= -1.0).all() and (ml_score <= 1.0).all())
        self.assertTrue(len(importances) > 0)

    def test_risk_manager(self):
        """Verify position sizing and trailing stop logic."""
        rm = BovineRiskManager()
        contracts = rm.calculate_position_size(
            symbol="LE=F",
            price=150.0,
            asset_volatility=0.16,
            portfolio_equity=100_000.0,
            current_drawdown=0.0,
            target_weight=1.0
        )
        self.assertGreater(contracts, 0)

        # Test stop-loss trigger
        pos = PositionRiskState(
            symbol="2022-01-01",
            entry_price=150.0,
            current_price=145.0,
            position_units=2,
            stop_loss_price=146.0,
            take_profit_price=160.0,
            trailing_high_water=150.0,
            atr_at_entry=2.0,
            unrealized_pnl=-4000.0
        )
        should_exit, reason, _ = rm.update_trailing_stops(pos, current_price=144.0, current_atr=2.0)
        self.assertTrue(should_exit)
        self.assertEqual(reason, "STOP_LOSS")

    def test_backtest_simulation(self):
        """Verify full backtesting simulation and tear-sheet metrics."""
        strat = BovineQuantitativeStrategy(enable_ml=False) # Fast test without full ML loop
        signals_df = strat.generate_signals(self.market_data, target_asset="LE=F")

        backtester = BovineBacktester(initial_capital=100_000.0)
        bt_res = backtester.run_backtest(self.market_data, signals_df, target_symbol="LE=F")

        eq_df = bt_res["equity_curve"]
        metrics = bt_res["metrics"]
        monthly = bt_res["monthly_table"]

        self.assertTrue(len(eq_df) > 500)
        self.assertIn("sharpe_ratio", metrics)
        self.assertIn("max_drawdown_pct", metrics)
        self.assertIn("total_return_pct", metrics)
        self.assertFalse(monthly.empty)

    def test_paper_trader_scan_and_execute(self):
        """Verify live signal scan and simulated order execution."""
        trader = BovinePaperTrader()
        trader.data_loader.use_live_yf = False # Use benchmark data for instant unit test
        trader.strategy.enable_ml = False     # Disable ML walk-forward loop in unit test
        scan = trader.scan_live_signals(["LE=F", "GF=F"])
        self.assertIn("LE=F", scan)
        self.assertIn("GF=F", scan)

        self.assertIn("latest_price", scan["LE=F"])
        self.assertIn("composite_alpha", scan["LE=F"])
        self.assertIn("recommended_contracts", scan["LE=F"])

        orders = trader.execute_rebalance(scan)
        self.assertIsInstance(orders, list)
        self.assertGreater(trader.portfolio["equity"], 0)

    def test_super_elnino_compensation(self):
        """Verify end-to-end Super El Niño climatology compensation across factors and strategies."""
        # 1. Test ONI fetch and 2026 Super El Niño classification
        fetcher = MacroDataFetcher()
        enso_df = fetcher.fetch_enso_oni(start_date="2020-01-01", end_date="2026-12-31")
        self.assertIn("ONI", enso_df.columns)
        self.assertIn("Phase", enso_df.columns)
        
        # Verify 2026 exhibits Super El Niño (>= 2.0°C)
        oni_2026 = enso_df[enso_df.index.year == 2026]["ONI"]
        self.assertTrue((oni_2026 >= 2.0).any())
        self.assertIn("SUPER_EL_NINO", enso_df["Phase"].values)

        # 2. Test MacroWeatherFactor under Super El Niño
        macro = MacroWeatherFactor()
        live_p = self.market_data["LE=F"]["Close"]
        score_base = macro.compute_factor_score(
            drought_df=self.market_data["DROUGHT"],
            live_price=live_p,
            target_asset="LE=F",
            active_regime="neutral"
        )
        score_elnino = macro.compute_factor_score(
            drought_df=self.market_data["DROUGHT"],
            live_price=live_p,
            target_asset="LE=F",
            active_regime="super_elnino"
        )
        # Super El Niño heifer retention supply deficit should provide positive alpha relative to baseline
        self.assertGreater(score_elnino.mean(), score_base.mean())

        # Test Telemetry
        telemetry = MacroWeatherFactor.get_enso_telemetry(enso_df, active_regime="super_elnino")
        self.assertEqual(telemetry["phase"], "SUPER_EL_NINO")
        self.assertIn("RETENTION", telemetry["heifer_retention"])
        self.assertIn("BULLISH", telemetry["bovine_alpha_bias"])

        # 3. Test Seasonality Modulation under Super El Niño
        seas = BovineSeasonalityFactor()
        # In September (month 9), normal feeder seasonality is negative (-0.40),
        # but Super El Niño profile turns it positive (+0.15)
        dt_sep = pd.date_range("2026-09-01", "2026-09-10", freq="B")
        dummy_p = pd.Series(200.0, index=dt_sep)
        score_gf_base = seas.compute_factor_score(dummy_p, target_asset="GF=F", enso_regime="neutral")
        score_gf_elnino = seas.compute_factor_score(dummy_p, target_asset="GF=F", enso_regime="super_elnino")
        self.assertGreater(score_gf_elnino.iloc[0], score_gf_base.iloc[0])

        # 4. Test Crush Margin mud drag under Super El Niño
        crush = CattleCrushFactor()
        live = self.market_data["LE=F"]["Close"]
        feeder = self.market_data["GF=F"]["Close"]
        corn = self.market_data["ZC=F"]["Close"]
        metrics_base = crush.calculate_crush_metrics(live, feeder, corn, enso_regime="neutral")
        metrics_elnino = crush.calculate_crush_metrics(live, feeder, corn, enso_regime="super_elnino")
        # Overhead is $12/head higher under Super El Niño mud conditions -> margin is $12 lower
        margin_diff = metrics_base["CrushMargin_Head"].iloc[-1] - metrics_elnino["CrushMargin_Head"].iloc[-1]
        self.assertAlmostEqual(margin_diff, 12.0, places=2)

        # 5. Test Strategy and Risk Manager under Super El Niño
        strat_elnino = BovineQuantitativeStrategy(enso_regime="super_elnino", enable_ml=False)
        self.assertEqual(strat_elnino.factor_weights["macro_drought"], SUPER_ELNINO_FACTOR_WEIGHTS["macro_drought"])
        signals = strat_elnino.generate_signals(self.market_data, target_asset="LE=F")
        self.assertIn("composite_alpha", signals.columns)

        rm_elnino = BovineRiskManager(enso_regime="super_elnino")
        self.assertEqual(rm_elnino.atr_stop_mult, ENSO_CONFIG["atr_stop_loss_mult_elnino"])


if __name__ == "__main__":
    unittest.main()
