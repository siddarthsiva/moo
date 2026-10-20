"""
Quantitative Strategy Logic & Signal Generation for Bovine Commodities.
Supports Multi-Factor Directional Alpha and Inter-Commodity Cattle Crush Spread Trading.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional

from config import STRATEGY_CONFIG, DEFAULT_FACTOR_WEIGHTS, SUPER_ELNINO_FACTOR_WEIGHTS, ENSO_CONFIG
from factors.factor_engine import BovineFactorEngine
from models.ml_predictor import BovineMLAlphaModel


class BovineQuantitativeStrategy:
    """Generates execution-ready portfolio target weights and trade orders."""

    def __init__(
        self,
        factor_weights: Optional[Dict[str, float]] = None,
        enable_ml: bool = True,
        mode: str = "directional", # "directional" or "spread_trading"
        enso_regime: Optional[str] = "super_elnino"
    ):
        self.enso_regime = enso_regime
        if factor_weights is not None:
            self.factor_weights = factor_weights
        elif self.enso_regime == "super_elnino":
            self.factor_weights = SUPER_ELNINO_FACTOR_WEIGHTS.copy()
        else:
            self.factor_weights = DEFAULT_FACTOR_WEIGHTS.copy()

        self.enable_ml = enable_ml
        self.mode = mode
        self.factor_engine = BovineFactorEngine(weights=self.factor_weights, enso_regime=self.enso_regime)
        self.ml_model = BovineMLAlphaModel()

    def generate_signals(
        self,
        market_data: Dict[str, pd.DataFrame],
        target_asset: str = "LE=F"
    ) -> pd.DataFrame:
        """
        Executes full quant pipeline: factor computation, ML walk-forward training,
        alpha scoring, regime filtering, and target weight generation.
        Compensates for active ENSO / Super El Niño regime.
        """
        # 1. Compute Base Factors (conditioned on ENSO / Super El Niño)
        factors_df = self.factor_engine.compute_all_factors(
            market_data, target_asset=target_asset, enso_regime=self.enso_regime
        )
        target_df = market_data[target_asset]

        # 2. Run ML Predictive Model if enabled
        ml_scores = None
        feature_importances = {}
        if self.enable_ml and len(factors_df) > 200:
            try:
                features, target = self.ml_model.build_features(target_df, factors_df)
                ml_scores, feature_importances = self.ml_model.walk_forward_train_predict(features, target)
            except Exception as e:
                # Fallback gracefully
                pass

        # 3. Compute Composite Alpha Score
        composite_alpha = self.factor_engine.compute_composite_alpha(
            factors_df=factors_df,
            ml_score=ml_scores,
            custom_weights=self.factor_weights
        )

        # 4. Generate Target Position Weights based on Strategy Mode
        if self.mode == "spread_trading" and "GF=F" in market_data and "LE=F" in market_data:
            weights_df = self._generate_spread_weights(market_data, factors_df)
        else:
            weights_df = self._generate_directional_weights(composite_alpha, target_df)

        # Merge everything into signals DataFrame
        signals_df = factors_df.copy()
        signals_df["composite_alpha"] = composite_alpha
        if ml_scores is not None:
            signals_df["ml_score"] = ml_scores.reindex(signals_df.index).fillna(0.0)
        else:
            signals_df["ml_score"] = 0.0

        signals_df["target_weight"] = weights_df["target_weight"]
        signals_df["signal_regime"] = weights_df["signal_regime"]

        return signals_df

    def _generate_directional_weights(
        self,
        composite_alpha: pd.Series,
        target_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Converts continuous alpha score to discrete risk-managed position weights:
        - Strong Long: +1.0
        - Moderate Long: +0.5
        - Neutral/Flat: 0.0
        - Moderate Short: -0.5
        - Strong Short: -1.0
        """
        cfg = STRATEGY_CONFIG
        s_long = cfg.get("signal_threshold_strong_long", 0.35)
        w_long = cfg.get("signal_threshold_weak_long", 0.15)
        w_short = cfg.get("signal_threshold_weak_short", -0.15)
        s_short = cfg.get("signal_threshold_strong_short", -0.35)

        raw_weights = np.zeros(len(composite_alpha))
        regimes = ["FLAT"] * len(composite_alpha)

        for i, val in enumerate(composite_alpha.values):
            if val >= s_long:
                raw_weights[i] = 1.0
                regimes[i] = "STRONG_LONG"
            elif val >= w_long:
                raw_weights[i] = 0.5
                regimes[i] = "MODERATE_LONG"
            elif val <= s_short:
                raw_weights[i] = -1.0
                regimes[i] = "STRONG_SHORT"
            elif val <= w_short:
                raw_weights[i] = -0.5
                regimes[i] = "MODERATE_SHORT"
            else:
                raw_weights[i] = 0.0
                regimes[i] = "FLAT"

        # Apply minimum holding period hysteresis (suppresses single-day noise)
        min_hold = cfg.get("min_holding_period_days", 3)
        smoothed_weights = raw_weights.copy()
        current_w = smoothed_weights[0]
        hold_count = 0

        for t in range(1, len(smoothed_weights)):
            if smoothed_weights[t] != current_w:
                if hold_count < min_hold:
                    # Maintain existing position until min holding days satisfied
                    smoothed_weights[t] = current_w
                    hold_count += 1
                else:
                    current_w = smoothed_weights[t]
                    hold_count = 1
            else:
                hold_count += 1

        return pd.DataFrame({
            "target_weight": smoothed_weights,
            "signal_regime": regimes
        }, index=composite_alpha.index)

    def _generate_spread_weights(
        self,
        market_data: Dict[str, pd.DataFrame],
        factors_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Feeder vs Live Cattle statistical arbitrage spread weights.
        """
        live_p = market_data["LE=F"]["Close"]
        feeder_p = market_data["GF=F"]["Close"]
        ratio = feeder_p / (live_p + 1e-6)
        r_mean = ratio.rolling(60, min_periods=15).mean()
        r_std = ratio.rolling(60, min_periods=15).std() + 1e-6
        zscore = (ratio - r_mean) / r_std

        weights = np.zeros(len(ratio))
        regimes = ["FLAT"] * len(ratio)
        thresh = STRATEGY_CONFIG.get("spread_trade_zscore_threshold", 1.75)

        for i, z in enumerate(zscore.values):
            if z > thresh:
                # Feeder is expensive, Live is cheap -> Short Feeder, Long Live
                weights[i] = 1.0 # Long Live Cattle spread leg
                regimes[i] = "LONG_LIVE_SHORT_FEEDER"
            elif z < -thresh:
                # Feeder is cheap, Live is expensive -> Long Feeder, Short Live
                weights[i] = -1.0
                regimes[i] = "SHORT_LIVE_LONG_FEEDER"
            elif abs(z) < 0.5:
                weights[i] = 0.0
                regimes[i] = "FLAT"
            else:
                weights[i] = weights[i-1] if i > 0 else 0.0

        return pd.DataFrame({
            "target_weight": weights,
            "signal_regime": regimes
        }, index=ratio.index)
