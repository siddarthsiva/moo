"""
Bovine Multi-Factor Aggregation Engine.
Assembles, normalizes, and synthesizes individual factors into a single composite alpha signal,
generates factor correlation matrices, and constructs features for Machine Learning models.
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
    """Multi-factor quant alpha generator for Cattle and Bovine Commodities."""

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

        self.crush_calc = CattleCrushFactor()
        self.cot_calc = COTSentimentFactor()
        self.season_calc = BovineSeasonalityFactor()
        self.macro_calc = MacroWeatherFactor()
        self.tech_calc = BovineTechnicalFactors()

    def compute_all_factors(
        self,
        market_data: Dict[str, pd.DataFrame],
        target_asset: str = "LE=F",
        enso_regime: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Computes all individual factor series and aligns them with target asset index.
        Returns a DataFrame where each column is a normalized factor in [-1.0, +1.0].
        Compensates for active ENSO / Super El Niño regime in crush margins, seasonality, and macro factors.
        """
        if target_asset not in market_data or market_data[target_asset].empty:
            raise ValueError(f"Target asset {target_asset} not found in market data.")

        regime = enso_regime if enso_regime is not None else self.enso_regime
        target_df = market_data[target_asset]
        index = target_df.index

        # 1. Cattle Crush Factor (with Super El Niño feedlot mud drag compensation)
        live_p = market_data["LE=F"]["Close"].reindex(index).ffill() if "LE=F" in market_data else target_df["Close"]
        feeder_p = market_data["GF=F"]["Close"].reindex(index).ffill() if "GF=F" in market_data else target_df["Close"] * 1.3
        corn_p = market_data["ZC=F"]["Close"].reindex(index).ffill() if "ZC=F" in market_data else pd.Series(450.0, index=index)
        
        f_crush = self.crush_calc.compute_factor_score(
            live_p, feeder_p, corn_p, target_asset=target_asset, enso_regime=regime
        )

        # 2. COT Sentiment Factor
        cot_key = f"COT_{target_asset.replace('=F', '')}"
        cot_df = market_data.get(cot_key, market_data.get("COT_LE", None))
        f_cot = self.cot_calc.compute_factor_score(cot_df, target_asset=target_asset)

        # 3. Seasonality & Biological Cycle Factor (with Super El Niño suppressed autumn calf run & mud storm lag)
        f_seasonal = self.season_calc.compute_factor_score(
            target_df["Close"], target_asset=target_asset, enso_regime=regime
        )

        # 4. Macro, ENSO & Weather/Drought Factor (with Super El Niño heifer retention & prompt supply deficit)
        drought_df = market_data.get("DROUGHT", None)
        dxy_df = market_data.get("DX-Y.NYB", None)
        enso_df = market_data.get("ENSO", None)
        hogs_p = market_data["HE=F"]["Close"] if "HE=F" in market_data else None
        f_macro = self.macro_calc.compute_factor_score(
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

        factors_df = pd.DataFrame({
            "crush_margin": f_crush.reindex(index).ffill().fillna(0.0),
            "cot_sentiment": f_cot.reindex(index).ffill().fillna(0.0),
            "seasonality": f_seasonal.reindex(index).ffill().fillna(0.0),
            "macro_drought": f_macro.reindex(index).ffill().fillna(0.0),
            "technical_trend": f_tech.reindex(index).ffill().fillna(0.0),
        }, index=index)

        return factors_df

    def compute_composite_alpha(
        self,
        factors_df: pd.DataFrame,
        ml_score: Optional[pd.Series] = None,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> pd.Series:
        """
        Calculates weighted composite alpha score:
        S_t = sum(w_i * Factor_i) / sum(w_i)
        """
        weights = custom_weights if custom_weights is not None else self.weights
        total_weight = 0.0
        composite = pd.Series(0.0, index=factors_df.index)

        for factor_name, weight in weights.items():
            if factor_name == "ml_ensemble":
                if ml_score is not None:
                    aligned_ml = ml_score.reindex(factors_df.index).fillna(0.0)
                    composite += weight * aligned_ml
                    total_weight += weight
            elif factor_name in factors_df.columns:
                composite += weight * factors_df[factor_name]
                total_weight += weight

        if total_weight > 0:
            composite = composite / total_weight

        return composite.clip(-1.0, 1.0)

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
                ic_dict[col] = float(np.nan_to_num(spearman_corr, nan=0.0))
            else:
                ic_dict[col] = 0.0

        return ic_dict
