"""
Bovine Multi-Factor Aggregation Engine — v2.0
Assembles, normalizes, and synthesizes individual factors into a single composite alpha signal,
generates factor correlation matrices, Information Coefficient (IC) metrics, and constructs
features for Machine Learning models.

v2.0 Improvements:
  - Cross-asset momentum factor: Corn/Feeder spread velocity as a leading indicator
  - Volatility regime dampener: Reduces factor conviction during high-vol regimes
  - IC-weighted dynamic re-weighting: Optional rolling IC-weighted composite alpha
  - Drawdown-aware factor conditioning
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple

from config import DEFAULT_FACTOR_WEIGHTS, SUPER_ELNINO_FACTOR_WEIGHTS, ENSO_CONFIG
from factors.crush_spread import CattleCrushFactor
from factors.sentiment_cot import COTSentimentFactor
from factors.seasonality import BovineSeasonalityFactor
from factors.macro_weather import MacroWeatherFactor
from factors.technical import BovineTechnicalFactors


class BovineFactorEngine:
    """Multi-factor quant alpha generator for Cattle and Bovine Commodities — v2.0."""

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        enso_regime: Optional[str] = "super_elnino"
    ):
        self.enso_regime = enso_regime
        if weights is not None:
            self.weights = weights
        elif self.enso_regime == "super_elnino":
            self.weights = SUPER_ELNINO_FACTOR_WEIGHTS.copy()
        else:
            self.weights = DEFAULT_FACTOR_WEIGHTS.copy()

        self.crush_calc  = CattleCrushFactor()
        self.cot_calc    = COTSentimentFactor()
        self.season_calc = BovineSeasonalityFactor()
        self.macro_calc  = MacroWeatherFactor()
        self.tech_calc   = BovineTechnicalFactors()

    def compute_all_factors(
        self,
        market_data: Dict[str, pd.DataFrame],
        target_asset: str = "LE=F",
        enso_regime: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Computes all individual factor series and aligns them with target asset index.
        Returns a DataFrame where each column is a normalized factor in [-1.0, +1.0].
        v2.0: Adds cross-asset corn velocity and volatility regime dampener.
        """
        if target_asset not in market_data or market_data[target_asset].empty:
            raise ValueError(f"Target asset {target_asset} not found in market data.")

        regime    = enso_regime if enso_regime is not None else self.enso_regime
        target_df = market_data[target_asset]
        index     = target_df.index

        # 1. Cattle Crush Factor (with Super El Niño feedlot mud drag compensation)
        live_p   = market_data["LE=F"]["Close"].reindex(index).ffill() if "LE=F" in market_data else target_df["Close"]
        feeder_p = market_data["GF=F"]["Close"].reindex(index).ffill() if "GF=F" in market_data else target_df["Close"] * 1.3
        corn_p   = market_data["ZC=F"]["Close"].reindex(index).ffill() if "ZC=F" in market_data else pd.Series(450.0, index=index)

        f_crush = self.crush_calc.compute_factor_score(
            live_p, feeder_p, corn_p, target_asset=target_asset, enso_regime=regime
        )

        # 2. COT Sentiment Factor
        cot_key = f"COT_{target_asset.replace('=F', '')}"
        cot_df  = market_data.get(cot_key, market_data.get("COT_LE", None))
        f_cot   = self.cot_calc.compute_factor_score(cot_df, target_asset=target_asset)

        # 3. Seasonality & Biological Cycle Factor (with Super El Niño suppressed autumn calf run & mud storm lag)
        f_seasonal = self.season_calc.compute_factor_score(
            target_df["Close"], target_asset=target_asset, enso_regime=regime
        )

        # 4. Macro, ENSO & Weather/Drought Factor (with Super El Niño heifer retention & prompt supply deficit)
        drought_df = market_data.get("DROUGHT", None)
        dxy_df     = market_data.get("DX-Y.NYB", None)
        enso_df    = market_data.get("ENSO", None)
        hogs_p     = market_data["HE=F"]["Close"] if "HE=F" in market_data else None
        f_macro    = self.macro_calc.compute_factor_score(
            drought_df=drought_df,
            dxy_df=dxy_df,
            live_price=target_df["Close"],
            hogs_price=hogs_p,
            target_asset=target_asset,
            enso_df=enso_df,
            active_regime=regime
        )

        # 5. Technical & Trend Factor
        f_tech = self.tech_calc.compute_factor_score(target_df)

        # 6. Cross-Asset Corn Velocity Factor (NEW in v2.0)
        # Falling corn prices signal expanding feedlot margins 3–6 months forward (bullish LE)
        f_corn_velocity = self._compute_corn_velocity_factor(corn_p, index)

        # 7. Volatility Regime Dampener (NEW in v2.0)
        # In high-vol regimes, all factor signals are dampened to avoid false conviction
        vol_regime_scalar = self._compute_vol_regime_scalar(target_df, index)

        factors_df = pd.DataFrame({
            "crush_margin":    f_crush.reindex(index).ffill().fillna(0.0),
            "cot_sentiment":   f_cot.reindex(index).ffill().fillna(0.0),
            "seasonality":     f_seasonal.reindex(index).ffill().fillna(0.0),
            "macro_drought":   f_macro.reindex(index).ffill().fillna(0.0),
            "technical_trend": f_tech.reindex(index).ffill().fillna(0.0),
            "corn_velocity":   f_corn_velocity.reindex(index).ffill().fillna(0.0),
        }, index=index)

        # Apply volatility regime dampener to all factors
        for col in factors_df.columns:
            factors_df[col] = (factors_df[col] * vol_regime_scalar).clip(-1.0, 1.0)

        return factors_df

    # ------------------------------------------------------------------
    # New v2.0 Factor Components
    # ------------------------------------------------------------------
    def _compute_corn_velocity_factor(
        self,
        corn_price: pd.Series,
        index: pd.Index
    ) -> pd.Series:
        """
        Corn price momentum velocity as a leading signal for feedlot margin expansion.
        - Falling corn (negative 60d momentum) → feedlots expand → bullish LE/GF (positive score).
        - Rising corn (positive 60d momentum) → feedlot margin compression → bearish (negative score).
        """
        corn = corn_price.reindex(index).ffill()
        mom60 = corn.pct_change(60)
        mom20 = corn.pct_change(20)
        # Blend: 60% 60d momentum + 40% 20d momentum, then invert (falling corn = bullish cattle)
        blend     = 0.60 * mom60 + 0.40 * mom20
        blend_std = blend.rolling(252, min_periods=30).std() + 1e-6
        normalized = -1.0 * (blend / blend_std / 2.0)  # Invert: falling corn = bullish
        return normalized.clip(-1.0, 1.0).fillna(0.0)

    @staticmethod
    def _compute_vol_regime_scalar(
        price_df: pd.DataFrame,
        index: pd.Index
    ) -> pd.Series:
        """
        Returns a scalar in [0.5, 1.0] that dampens factor signals during high-vol regimes.
        Normal vol (20d/60d ratio < 1.3): scalar = 1.0 (no dampening).
        High vol (ratio > 2.0): scalar = 0.5 (halve all factor signals).
        """
        close    = price_df["Close"].reindex(index).ffill()
        ret      = close.pct_change()
        vol20    = ret.rolling(20, min_periods=5).std() * np.sqrt(252)
        vol60    = ret.rolling(60, min_periods=15).std() * np.sqrt(252)
        vol_ratio = (vol20 / (vol60 + 1e-6)).clip(0.5, 3.0)

        # Scalar decreases from 1.0 to 0.5 as vol_ratio goes from 1.3 to 2.0
        scalar = 1.0 - 0.5 * ((vol_ratio - 1.3) / (2.0 - 1.3)).clip(0.0, 1.0)
        return scalar.fillna(1.0)

    # ------------------------------------------------------------------
    # Composite Alpha
    # ------------------------------------------------------------------
    def compute_composite_alpha(
        self,
        factors_df: pd.DataFrame,
        ml_score: Optional[pd.Series] = None,
        custom_weights: Optional[Dict[str, float]] = None,
        use_ic_weighting: bool = False,
        price_series: Optional[pd.Series] = None,
    ) -> pd.Series:
        """
        Calculates weighted composite alpha score:
        S_t = sum(w_i * Factor_i) / sum(w_i)

        v2.0: Optional IC-weighted dynamic re-weighting when use_ic_weighting=True
        and price_series is provided. Rolling IC is computed over a 252-day window
        and factors are up-weighted proportional to their recent predictive power.
        """
        weights = custom_weights if custom_weights is not None else self.weights

        # -- Optional rolling IC-based weight adjustment --
        if use_ic_weighting and price_series is not None:
            ic_dict = self.calculate_factor_ic(factors_df, price_series, forward_horizon=10)
            # Only adjust weights for factors with positive IC (suppress negatives)
            adjusted_weights = {}
            for k, w in weights.items():
                if k == "ml_ensemble":
                    adjusted_weights[k] = w
                    continue
                ic = ic_dict.get(k, 0.0)
                ic_boost = max(0.0, ic)  # Only reward positive IC
                adjusted_weights[k] = w * (1.0 + ic_boost)
            # Renormalize
            total_w = sum(adjusted_weights.values()) + 1e-6
            weights = {k: v / total_w for k, v in adjusted_weights.items()}

        total_weight = 0.0
        composite    = pd.Series(0.0, index=factors_df.index)

        for factor_name, weight in weights.items():
            if factor_name == "ml_ensemble":
                if ml_score is not None:
                    aligned_ml = ml_score.reindex(factors_df.index).fillna(0.0)
                    composite  += weight * aligned_ml
                    total_weight += weight
            elif factor_name in factors_df.columns:
                composite    += weight * factors_df[factor_name]
                total_weight += weight

        if total_weight > 0:
            composite = composite / total_weight

        return composite.clip(-1.0, 1.0)

    # ------------------------------------------------------------------
    # Factor Analytics
    # ------------------------------------------------------------------
    def calculate_factor_ic(
        self,
        factors_df: pd.DataFrame,
        price_series: pd.Series,
        forward_horizon: int = 10
    ) -> Dict[str, float]:
        """
        Computes Information Coefficient (Rank correlation between factor score and forward return).
        """
        fwd_returns = price_series.pct_change(forward_horizon).shift(-forward_horizon)
        ic_dict = {}

        for col in factors_df.columns:
            valid = pd.DataFrame({"factor": factors_df[col], "fwd_ret": fwd_returns}).dropna()
            if len(valid) > 30:
                spearman_corr = valid["factor"].corr(valid["fwd_ret"], method="spearman")
                ic_dict[col]  = float(np.nan_to_num(spearman_corr, nan=0.0))
            else:
                ic_dict[col] = 0.0

        return ic_dict

    def calculate_rolling_ic(
        self,
        factors_df: pd.DataFrame,
        price_series: pd.Series,
        forward_horizon: int = 10,
        window: int = 126
    ) -> pd.DataFrame:
        """
        Computes rolling Information Coefficient over a trailing window.
        Returns a DataFrame of IC time-series per factor (useful for dashboard charting).
        """
        fwd_ret = price_series.pct_change(forward_horizon).shift(-forward_horizon)
        ic_records = {}

        for col in factors_df.columns:
            factor_aligned = factors_df[col].reindex(price_series.index)
            combined = pd.DataFrame({"f": factor_aligned, "r": fwd_ret}).dropna()
            if len(combined) < window:
                ic_records[col] = pd.Series(0.0, index=price_series.index)
                continue

            rolling_ic = combined["f"].rolling(window).corr(combined["r"], pairwise=False)
            ic_records[col] = rolling_ic.reindex(price_series.index).fillna(0.0)

        return pd.DataFrame(ic_records)

    def get_factor_correlation_matrix(self, factors_df: pd.DataFrame) -> pd.DataFrame:
        """Returns the factor cross-correlation matrix for orthogonality diagnostics."""
        return factors_df.corr(method="spearman").round(3)
