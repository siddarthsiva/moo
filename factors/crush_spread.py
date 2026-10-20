"""
Cattle Crush & Feedlot Economics Factor.
Models the fundamental margin of transformation:
Feeder Calf (750 lbs) + Corn Feed (50 bu) -> Finished Live Slaughter Steer (1,300 lbs).
Generates directional alpha and mean-reverting spread signals.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple
from config import CATTLE_CRUSH_CONFIG


class CattleCrushFactor:
    """Calculates synthetic feedlot gross margins, input ratios, and spread z-scores."""

    def __init__(self, config: dict = CATTLE_CRUSH_CONFIG):
        self.live_wt = config.get("live_weight_cwt", 13.0)
        self.feeder_wt = config.get("feeder_weight_cwt", 7.5)
        self.corn_bu = config.get("corn_bushels_per_head", 50.0)
        self.overhead = config.get("yardage_overhead_usd", 85.0)

    def calculate_crush_metrics(
        self,
        live_price: pd.Series,
        feeder_price: pd.Series,
        corn_price: pd.Series,
        enso_regime: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Computes synthetic gross crush margin per head ($/head),
        margin per cwt, Feeder-to-Live ratio, and 252-day z-scores.
        Compensates for feedlot mud/yardage overhead drag under Super El Niño.
        """
        # Align series
        df = pd.DataFrame({
            "Live": live_price,
            "Feeder": feeder_price,
            "Corn": corn_price
        }).dropna()

        # Adjust overhead for wet winter feedlot mud drag under Super El Niño
        overhead = self.overhead + (12.0 if enso_regime == "super_elnino" else 0.0)

        # Revenue per finished steer ($/head)
        revenue = self.live_wt * df["Live"]

        # Feeder calf input cost ($/head)
        feeder_cost = self.feeder_wt * df["Feeder"]

        # Corn feed cost ($/head) - Corn is quoted in cents/bushel so divide by 100
        corn_cost = self.corn_bu * (df["Corn"] / 100.0)

        # Net Feeding Margin per head ($/head)
        margin_head = revenue - feeder_cost - corn_cost - overhead

        # Margin per finished hundredweight ($/cwt)
        margin_cwt = margin_head / self.live_wt

        # Feeder to Live Price Ratio (Parity)
        feeder_live_ratio = df["Feeder"] / (df["Live"] + 1e-6)

        # 1-Year (252-day) Rolling Mean & Std of Margin
        margin_mean = margin_head.rolling(252, min_periods=30).mean()
        margin_std = margin_head.rolling(252, min_periods=30).std()
        margin_zscore = (margin_head - margin_mean) / (margin_std + 1e-6)

        # Ratio Z-Score (60-day short term for pair trading)
        ratio_mean = feeder_live_ratio.rolling(60, min_periods=15).mean()
        ratio_std = feeder_live_ratio.rolling(60, min_periods=15).std()
        ratio_zscore = (feeder_live_ratio - ratio_mean) / (ratio_std + 1e-6)

        res = pd.DataFrame({
            "CrushMargin_Head": margin_head,
            "CrushMargin_Cwt": margin_cwt,
            "FeederLiveRatio": feeder_live_ratio,
            "Margin_ZScore": margin_zscore.fillna(0.0),
            "Ratio_ZScore": ratio_zscore.fillna(0.0),
        }, index=df.index)

        return res

    def compute_factor_score(
        self,
        live_price: pd.Series,
        feeder_price: pd.Series,
        corn_price: pd.Series,
        target_asset: str = "LE=F",
        enso_regime: Optional[str] = None
    ) -> pd.Series:
        """
        Transforms crush dynamics into normalized trading factor score [-1.0, +1.0]:
        - For Live Cattle (LE=F):
          Depressed margins (negative z-score) -> Placement cutbacks -> Future supply deficit -> Bullish (+1.0).
          Excessive margins (positive z-score) -> Over-placement -> Future glut -> Bearish (-1.0).
        - For Feeder Cattle (GF=F):
          Depressed margins -> Feedlots refuse to buy expensive feeders -> Bearish Feeder (-1.0).
          Elevated margins -> Feedlots aggressively bid for feeders -> Bullish Feeder (+1.0).
          Under Super El Niño, cheap corn expands margins, providing persistent feeder bidding support.
        """
        metrics = self.calculate_crush_metrics(live_price, feeder_price, corn_price, enso_regime=enso_regime)
        z = metrics["Margin_ZScore"]

        if "LE" in target_asset:
            # Mean-reverting forward supply relationship for Live Cattle
            # Deep negative margin -> Strong buy signal for forward live cattle
            score = -1.0 * (z / 2.0)
        else:
            # Direct demand relationship for Feeder calves
            score = 1.0 * (z / 2.0)
            if enso_regime == "super_elnino":
                # With cheap bumper corn, feedlots tolerate higher calf prices
                score = score + 0.15

        return score.clip(-1.0, 1.0)
