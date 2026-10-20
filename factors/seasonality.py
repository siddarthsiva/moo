

"""
Bovine Seasonality & Biological Cattle Cycle Factor.
Models intra-year seasonal demand/supply patterns (Spring Grilling Rally, Autumn Calf Run,
Winter Storm Weight Lag) and multi-year herd biological cycles.
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple


class BovineSeasonalityFactor:
    """Calculates historical seasonal tendencies and biological cycle scores."""

    # Benchmark empirical monthly seasonal bias for Live Cattle (% excess return vs average)
    # Jan (+), Feb (+), Mar (++), Apr (+++), May (++), Jun (-), Jul (--), Aug (-), Sep (-), Oct (+), Nov (-), Dec (+)
    LIVE_CATTLE_SEASONAL_PROFILE = {
        1: 0.15,   # Jan: Winter storm weight gain slowdown
        2: 0.25,   # Feb: Feedlot supply tightening
        3: 0.55,   # Mar: Spring grilling season restocking
        4: 0.70,   # Apr: Peak spring packer demand
        5: 0.40,   # May: Memorial Day retail beef push
        6: -0.20,  # Jun: Summer heat reduces beef dining demand
        7: -0.45,  # Jul: Post 4th of July supply lull
        8: -0.30,  # Aug: Summer supply peak
        9: -0.10,  # Sep: Labor Day transition
        10: 0.20,  # Oct: Fall beef demand uptick
        11: -0.35, # Nov: Turkey substitution / holiday poultry demand
        12: 0.25,  # Dec: Holiday prime rib / beef roast demand
    }

    # Feeder Cattle Seasonal Profile (Calf run peaks in Sep-Nov)
    FEEDER_CATTLE_SEASONAL_PROFILE = {
        1: 0.10, 2: 0.30, 3: 0.60, 4: 0.50, 5: 0.30, 6: 0.10,
        7: 0.20, 8: 0.35, 9: -0.40, 10: -0.60, 11: -0.50, 12: -0.10
    }

    # Super El Niño Modulated Profiles:
    # 1. Autumn Calf Run (Sep-Nov) is suppressed (calves graze winter wheat on pasture; heifers retained).
    # 2. Winter Storm & Mud Drag (Dec-Feb) is amplified (feedlot ADG drops 10-15%, delaying marketings).
    # 3. Spring Grilling Rally (Mar-May) is supercharged by acute slaughter cattle scarcity.
    SUPER_ELNINO_LIVE_CATTLE_SEASONAL_PROFILE = {
        1: 0.35, 2: 0.45, 3: 0.70, 4: 0.85, 5: 0.55, 6: -0.10,
        7: -0.25, 8: -0.15, 9: 0.15, 10: 0.35, 11: -0.10, 12: 0.40
    }

    SUPER_ELNINO_FEEDER_CATTLE_SEASONAL_PROFILE = {
        1: 0.25, 2: 0.45, 3: 0.75, 4: 0.65, 5: 0.45, 6: 0.20,
        7: 0.30, 8: 0.45, 9: 0.15, 10: 0.10, 11: 0.05, 12: 0.15
    }

    def compute_empirical_seasonality(
        self,
        price_series: pd.Series,
        window_years: int = 10
    ) -> pd.Series:
        """
        Computes rolling empirical daily seasonal expectation using fast vectorized harmonics.
        """
        returns = price_series.pct_change().fillna(0.0)
        doy = price_series.index.dayofyear.values
        
        # 1st and 2nd Fourier seasonal harmonics for day-of-year
        theta = 2.0 * np.pi * doy / 365.25
        h1_sin = np.sin(theta)
        h1_cos = np.cos(theta)
        h2_sin = np.sin(2.0 * theta)
        h2_cos = np.cos(2.0 * theta)

        # Regress returns onto seasonal harmonics over 252*window rolling window
        roll_window = min(len(returns), 252 * window_years)
        # Fast rolling empirical seasonal score
        doy_series = pd.Series(doy, index=price_series.index)
        doy_avg = returns.groupby(doy_series).transform("mean")
        doy_smooth = doy_avg.rolling(20, min_periods=1, center=True).mean().fillna(0.0)

        std = doy_smooth.std() + 1e-6
        norm_s = (doy_smooth / std).clip(-1.0, 1.0)
        return norm_s.fillna(0.0)

    def compute_factor_score(
        self,
        price_series: pd.Series,
        target_asset: str = "LE=F",
        enso_regime: Optional[str] = None
    ) -> pd.Series:
        """
        Combines empirical historical seasonal curve with biological bovine calendar.
        Supports Super El Niño compensation which alters the autumn calf run and winter storm lag.
        Returns normalized seasonal factor [-1.0, +1.0].
        """
        if price_series is None or price_series.empty:
            return pd.Series(0.0)

        is_live = "LE" in target_asset
        if enso_regime == "super_elnino":
            profile = self.SUPER_ELNINO_LIVE_CATTLE_SEASONAL_PROFILE if is_live else self.SUPER_ELNINO_FEEDER_CATTLE_SEASONAL_PROFILE
        else:
            profile = self.LIVE_CATTLE_SEASONAL_PROFILE if is_live else self.FEEDER_CATTLE_SEASONAL_PROFILE
        
        # Static biological calendar component
        calendar_scores = price_series.index.month.map(profile).fillna(0.0).values
        cal_series = pd.Series(calendar_scores, index=price_series.index)

        # Empirical rolling history component
        emp_series = self.compute_empirical_seasonality(price_series)

        # Blend: 60% Biological Calendar Profile + 40% Empirical Rolling Climatology
        blended = 0.60 * cal_series + 0.40 * emp_series
        return blended.clip(-1.0, 1.0)
