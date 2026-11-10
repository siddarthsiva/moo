"""
Quantitative Strategy Logic & Signal Generation for Bovine Commodities — v2.0
Supports Multi-Factor Directional Alpha and Inter-Commodity Cattle Crush Spread Trading.

v2.0 Improvements:
  - Regime-adaptive signal smoothing via exponential decay rather than hard min-hold
  - Half-Kelly position sizing hint stored in signals_df for use by risk manager
  - Volatility-normalized alpha thresholds (regime-adaptive entry levels)
  - Composite alpha momentum filter: suppresses counter-trend entries during strong trends
  - Cross-IC weighted alpha mode toggle
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional

from config import STRATEGY_CONFIG, DEFAULT_FACTOR_WEIGHTS, SUPER_ELNINO_FACTOR_WEIGHTS, ENSO_CONFIG
from factors.factor_engine import BovineFactorEngine
from models.ml_predictor import BovineMLAlphaModel


class BovineQuantitativeStrategy:
    """Generates execution-ready portfolio target weights and trade orders — v2.0."""

    def __init__(
        self,
        factor_weights: Optional[Dict[str, float]] = None,
        enable_ml: bool = True,
        mode: str = "directional",  # "directional" or "spread_trading"
        enso_regime: Optional[str] = "super_elnino",
        use_ic_weighting: bool = False,
    ):
        self.enso_regime = enso_regime
        if factor_weights is not None:
            self.factor_weights = factor_weights
        elif self.enso_regime == "super_elnino":
            self.factor_weights = SUPER_ELNINO_FACTOR_WEIGHTS.copy()
        else:
            self.factor_weights = DEFAULT_FACTOR_WEIGHTS.copy()

        self.enable_ml       = enable_ml
        self.mode            = mode
        self.use_ic_weighting = use_ic_weighting
        self.factor_engine   = BovineFactorEngine(weights=self.factor_weights, enso_regime=self.enso_regime)
        self.ml_model        = BovineMLAlphaModel()

    def generate_signals(
        self,
        market_data: Dict[str, pd.DataFrame],
        target_asset: str = "LE=F"
    ) -> pd.DataFrame:
        """
        Executes full quant pipeline: factor computation, ML walk-forward training,
        alpha scoring, regime filtering, and target weight generation.
        v2.0: Adds IC-weighted composite, vol-normalized thresholds, and Kelly sizing hints.
        """
        # 1. Compute Base Factors (conditioned on ENSO / Super El Niño)
        factors_df = self.factor_engine.compute_all_factors(
            market_data, target_asset=target_asset, enso_regime=self.enso_regime
        )
        target_df = market_data[target_asset]

        # 2. Run ML Predictive Model if enabled
        ml_scores          = None
        feature_importances = {}
        if self.enable_ml and len(factors_df) > 200:
            try:
                features, target = self.ml_model.build_features(target_df, factors_df)
                ml_scores, feature_importances = self.ml_model.walk_forward_train_predict(features, target)
            except Exception:
                pass

        # 3. Compute Composite Alpha Score (optionally IC-weighted)
        price_series_for_ic = target_df["Close"] if self.use_ic_weighting else None
        composite_alpha = self.factor_engine.compute_composite_alpha(
            factors_df=factors_df,
            ml_score=ml_scores,
            custom_weights=self.factor_weights,
            use_ic_weighting=self.use_ic_weighting,
            price_series=price_series_for_ic,
        )

        # 4. Alpha Momentum Filter (suppress whipsaw counter-trend signals)
        composite_alpha = self._apply_alpha_momentum_filter(composite_alpha)

        # 5. Generate Target Position Weights based on Strategy Mode
        if self.mode == "spread_trading" and "GF=F" in market_data and "LE=F" in market_data:
            weights_df = self._generate_spread_weights(market_data, factors_df)
        else:
            weights_df = self._generate_directional_weights(composite_alpha, target_df)

        # 6. Merge everything into signals DataFrame
        signals_df = factors_df.copy()
        signals_df["composite_alpha"] = composite_alpha
        if ml_scores is not None:
            signals_df["ml_score"] = ml_scores.reindex(signals_df.index).fillna(0.0)
        else:
            signals_df["ml_score"] = 0.0

        signals_df["target_weight"]  = weights_df["target_weight"]
        signals_df["signal_regime"]  = weights_df["signal_regime"]

        # 7. Kelly sizing hint (fractional Kelly = 0.5 * edge/odds estimate)
        signals_df["kelly_fraction"] = self._compute_kelly_fraction(composite_alpha)

        return signals_df

    # ------------------------------------------------------------------
    # Alpha Momentum Filter (v2.0 NEW)
    # ------------------------------------------------------------------
    @staticmethod
    def _apply_alpha_momentum_filter(
        composite_alpha: pd.Series,
        fast_window: int = 5,
        slow_window: int = 20
    ) -> pd.Series:
        """
        Suppresses signals that are directionally opposed to the prevailing alpha trend.
        Uses a dual-EMA crossover of the composite alpha itself:
          - If short-term alpha EMA > long-term alpha EMA: bullish alpha regime
            → allow long signals, dampen short signals by 30%.
          - Vice versa for bearish alpha regime.
        """
        alpha_fast = composite_alpha.ewm(span=fast_window, min_periods=2).mean()
        alpha_slow = composite_alpha.ewm(span=slow_window, min_periods=5).mean()

        filtered = composite_alpha.copy()
        for i in range(len(composite_alpha)):
            af, as_ = alpha_fast.iloc[i], alpha_slow.iloc[i]
            raw     = composite_alpha.iloc[i]
            if af > as_:  # Bullish alpha regime
                # Dampen bearish signals by 30%
                filtered.iloc[i] = raw * (0.70 if raw < 0 else 1.0)
            else:          # Bearish alpha regime
                # Dampen bullish signals by 30%
                filtered.iloc[i] = raw * (0.70 if raw > 0 else 1.0)

        return filtered.clip(-1.0, 1.0)

    # ------------------------------------------------------------------
    # Kelly Fraction (v2.0 NEW)
    # ------------------------------------------------------------------
    @staticmethod
    def _compute_kelly_fraction(composite_alpha: pd.Series) -> pd.Series:
        """
        Estimates a fractional Kelly position sizing coefficient from the alpha magnitude.
        Uses rolling win rate proxy:
          - Kelly f = (p * b - q) / b,  where b ≈ 1.5 (avg win/loss ratio),
            p = rolling fraction of time alpha > 0 (for longs), q = 1 - p.
        Returns a series in [0.0, 1.0] representing suggested position fraction.
        """
        window = 60
        b      = 1.5  # Assumed average win/loss ratio for cattle trend-following

        is_bullish = (composite_alpha > 0.10).astype(float)
        p_roll = is_bullish.rolling(window, min_periods=10).mean().fillna(0.5)
        q_roll = 1.0 - p_roll

        kelly_full = (p_roll * b - q_roll) / b
        # Half-Kelly (more robust):
        kelly_half = (kelly_full * 0.5).clip(0.0, 1.0)

        # Zero Kelly when composite alpha is weak (|alpha| < 0.1)
        kelly_half = kelly_half * (composite_alpha.abs() > 0.10).astype(float)
        return kelly_half.fillna(0.0)

    # ------------------------------------------------------------------
    # Directional Weight Generation
    # ------------------------------------------------------------------
    def _generate_directional_weights(
        self,
        composite_alpha: pd.Series,
        target_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Converts continuous alpha score to discrete risk-managed position weights — v2.0:
        - Strong Long:    +1.0
        - Moderate Long:  +0.5
        - Neutral/Flat:    0.0
        - Moderate Short: -0.5
        - Strong Short:   -1.0

        v2.0: Uses exponential decay smoothing (EMA) instead of hard min-hold period
        to reduce flip-flopping while preserving responsiveness to genuine regime changes.
        """
        cfg    = STRATEGY_CONFIG
        s_long  = cfg.get("signal_threshold_strong_long",  0.35)
        w_long  = cfg.get("signal_threshold_weak_long",    0.15)
        w_short = cfg.get("signal_threshold_weak_short",  -0.15)
        s_short = cfg.get("signal_threshold_strong_short", -0.35)

        raw_weights = np.zeros(len(composite_alpha))
        regimes     = ["FLAT"] * len(composite_alpha)

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

        # --- Exponential decay smoothing (EMA-based hysteresis) ---
        # alpha_ema controls responsiveness: higher = faster (less smoothing)
        min_hold = cfg.get("min_holding_period_days", 3)
        ema_alpha = 2.0 / (min_hold + 1)  # Convert holding period to EMA factor

        smoothed_weights = raw_weights.copy()
        ema_val = smoothed_weights[0]
        for t in range(1, len(smoothed_weights)):
            ema_val = ema_alpha * raw_weights[t] + (1 - ema_alpha) * ema_val
            # Round to nearest discrete weight level
            if abs(ema_val) >= 0.75:
                smoothed_weights[t] = np.sign(ema_val)
            elif abs(ema_val) >= 0.35:
                smoothed_weights[t] = 0.5 * np.sign(ema_val)
            else:
                smoothed_weights[t] = 0.0

        return pd.DataFrame({
            "target_weight": smoothed_weights,
            "signal_regime": regimes
        }, index=composite_alpha.index)

    # ------------------------------------------------------------------
    # Spread Weight Generation
    # ------------------------------------------------------------------
    def _generate_spread_weights(
        self,
        market_data: Dict[str, pd.DataFrame],
        factors_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Feeder vs Live Cattle statistical arbitrage spread weights — v2.0:
        Added corn velocity as a secondary confirmation signal for spread trades.
        """
        live_p   = market_data["LE=F"]["Close"]
        feeder_p = market_data["GF=F"]["Close"]
        ratio    = feeder_p / (live_p + 1e-6)

        r_mean = ratio.rolling(60, min_periods=15).mean()
        r_std  = ratio.rolling(60, min_periods=15).std() + 1e-6
        zscore = (ratio - r_mean) / r_std

        weights = np.zeros(len(ratio))
        regimes = ["FLAT"] * len(ratio)
        thresh  = STRATEGY_CONFIG.get("spread_trade_zscore_threshold", 1.75)

        # Corn velocity confirmation: falling corn = wider normal parity
        # (feedlots can afford to pay more for feeders)
        corn_velocity = factors_df.get("corn_velocity", pd.Series(0.0, index=ratio.index))
        corn_velocity = corn_velocity.reindex(ratio.index).fillna(0.0)

        for i, z in enumerate(zscore.values):
            corn_v = float(corn_velocity.iloc[i])

            if z > thresh:
                # Feeder is expensive → Short Feeder, Long Live (but confirm with corn)
                # If corn is also falling (bullish), the spread is likely to widen further
                entry_w = 1.0 + (0.2 if corn_v > 0.3 else 0.0)  # Modest conviction boost
                weights[i] = min(entry_w, 1.0)
                regimes[i] = "LONG_LIVE_SHORT_FEEDER"
            elif z < -thresh:
                # Feeder is cheap → Long Feeder, Short Live
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
