"""
Macroeconomic & Weather/Drought Impact Factor.
Models US Drought severity (Plains pasture stress), US Dollar export elasticity,
and Protein Substitution (Beef vs Pork/Lean Hogs) dynamics.
"""

import numpy as np
import pandas as pd
from typing import Dict, Optional


class MacroWeatherFactor:
    """Calculates macro, export, weather, and cross-protein substitute factors."""

    def compute_factor_score(
        self,
        drought_df: Optional[pd.DataFrame] = None,
        dxy_df: Optional[pd.DataFrame] = None,
        live_price: Optional[pd.Series] = None,
        hogs_price: Optional[pd.Series] = None,
        target_asset: str = "LE=F",
        enso_df: Optional[pd.DataFrame] = None,
        active_regime: Optional[str] = None
    ) -> pd.Series:
        """
        Computes composite macro-weather factor [-1.0, +1.0]:
        1. ENSO / Super El Niño Factor: Subtropical moisture revives Southern Plains pastures,
           triggering aggressive cow-calf heifer retention, starving feedlots of feeder calves,
           and creating an acute prompt slaughter deficit (massive bullish driver).
        2. Drought Factor: Severe drought in Plains causes herd liquidation (temporary supply boost)
           followed by a structural multi-year calf deficit (bullish super-cycle).
        3. DXY Dollar Factor: Weak USD is bullish for beef exports to Asia/Americas.
        4. Protein Substitution: Beef/Pork ratio mean reversion.
        """
        if live_price is None or live_price.empty:
            return pd.Series(0.0)

        index = live_price.index

        # 1. ENSO / Super El Niño Component
        enso_factor = None
        if enso_df is not None and not enso_df.empty:
            oni_col = "ONI" if "ONI" in enso_df.columns else enso_df.columns[0]
            oni_series = enso_df[oni_col].reindex(index).ffill().fillna(0.0)
            if active_regime == "super_elnino":
                oni_series = oni_series.clip(lower=2.0)
            elif active_regime == "lanina":
                oni_series = oni_series.clip(upper=-1.0)
            
            asset_mult = 1.15 if "GF" in target_asset else 1.0
            oni_norm = oni_series / 2.0 # 2.0°C = Super El Niño
            # S-curve response: sharp acceleration as ONI crosses +1.5°C into Super El Niño
            enso_factor = (np.tanh(oni_norm * 1.5) * asset_mult).clip(-1.0, 1.0)
        elif active_regime == "super_elnino":
            # Active Super El Niño override (e.g. 2026 Super El Niño +2.3°C)
            asset_mult = 1.15 if "GF" in target_asset else 1.0
            oni_norm = 2.3 / 2.0
            score_val = float(np.clip(np.tanh(oni_norm * 1.5) * asset_mult, -1.0, 1.0))
            enso_factor = pd.Series(score_val, index=index)

        # 2. Drought Component
        if drought_df is not None and not drought_df.empty:
            col = "DroughtIndex" if "DroughtIndex" in drought_df.columns else drought_df.columns[0]
            d_series = drought_df[col].reindex(index).ffill().fillna(35.0)
            # Long-term rolling drought memory (180 days)
            d_smooth = d_series.rolling(180, min_periods=1).mean()
            drought_factor = ((d_smooth - 35.0) / 30.0).clip(-1.0, 1.0).fillna(0.0)
        else:
            drought_factor = pd.Series(0.0, index=index)

        # 3. DXY Dollar Component
        if dxy_df is not None and not dxy_df.empty:
            col = "Close" if "Close" in dxy_df.columns else dxy_df.columns[0]
            dxy_series = dxy_df[col].reindex(index).ffill()
            dxy_sma = dxy_series.rolling(60, min_periods=1).mean()
            dxy_std = dxy_series.rolling(60, min_periods=1).std().fillna(1.0) + 1e-6
            z_dxy = (dxy_series - dxy_sma) / dxy_std
            # Inverted: Weak dollar = Bullish beef exports
            dollar_factor = (-1.0 * z_dxy / 2.0).clip(-1.0, 1.0).fillna(0.0)
        else:
            dollar_factor = pd.Series(0.0, index=index)

        # 4. Protein Substitution (Beef to Pork Price Ratio)
        if hogs_price is not None and not hogs_price.empty:
            aligned_hogs = hogs_price.reindex(index).ffill()
            beef_pork_ratio = live_price / (aligned_hogs + 1e-6)
            ratio_mean = beef_pork_ratio.rolling(252, min_periods=1).mean()
            ratio_std = beef_pork_ratio.rolling(252, min_periods=1).std().fillna(1.0) + 1e-6
            z_sub = (beef_pork_ratio - ratio_mean) / ratio_std
            # Mean reversion: When beef is too expensive relative to pork (Z > 2.0), consumers substitute -> Bearish
            sub_factor = (-1.0 * z_sub / 2.0).clip(-1.0, 1.0).fillna(0.0)
        else:
            sub_factor = pd.Series(0.0, index=index)

        # Composite Blend
        if enso_factor is not None:
            # 35% ENSO heifer retention / climate shock, 30% Pasture drought memory, 20% Dollar exports, 15% Meat substitution
            composite = 0.35 * enso_factor + 0.30 * drought_factor + 0.20 * dollar_factor + 0.15 * sub_factor
        else:
            # Standard Baseline: 45% Drought supply cycle, 30% Dollar exports, 25% Meat substitution
            composite = 0.45 * drought_factor + 0.30 * dollar_factor + 0.25 * sub_factor

        return composite.clip(-1.0, 1.0).fillna(0.0)

    @staticmethod
    def get_enso_telemetry(
        enso_df: Optional[pd.DataFrame] = None,
        active_regime: Optional[str] = "super_elnino"
    ) -> Dict[str, Any]:
        """Returns structured diagnostic telemetry of ENSO climatology state."""
        if enso_df is not None and not enso_df.empty and "ONI" in enso_df.columns:
            latest_oni = float(enso_df["ONI"].iloc[-1])
            phase = str(enso_df["Phase"].iloc[-1]) if "Phase" in enso_df.columns else "UNKNOWN"
        elif active_regime == "super_elnino":
            latest_oni = 2.3
            phase = "SUPER_EL_NINO"
        elif active_regime == "lanina":
            latest_oni = -1.2
            phase = "LA_NINA"
        else:
            latest_oni = 0.0
            phase = "NEUTRAL"

        if latest_oni >= 2.0:
            heifer_status = "EXTREME_RETENTION (Heifers withheld for breeding; acute slaughter deficit)"
            corn_trend = "BUMPER_CROP (Midwest moisture depresses feed prices; feedlot margins widen)"
            mud_risk = "SEVERE_FEEDLOT_MUD (Subtropical storm tracks cut ADG by 10-15%)"
            australia_status = "DROUGHT_LIQUIDATION (Initial cull -> Subsequent global structural beef shortage)"
            alpha_bias = "ULTRA_BULLISH (Supply squeeze in finished cattle & feeder calves)"
        elif latest_oni >= 0.5:
            heifer_status = "MODERATE_RETENTION (Pasture improving; lower auction placement)"
            corn_trend = "FAVORABLE_FEED (Lower corn costs support cattle margins)"
            mud_risk = "MODERATE_WINTER_LAG (Slight reduction in daily gain)"
            australia_status = "MODERATE_EXPORT_COMPETITION"
            alpha_bias = "MODERATE_BULLISH"
        elif latest_oni <= -0.5:
            heifer_status = "HERD_LIQUIDATION (Plains drought forces cow/heifer culling to slaughter)"
            corn_trend = "DROUGHT_RISK (Corn prices elevated; feedlot margin squeeze)"
            mud_risk = "LOW_MUD_RISK"
            australia_status = "HERD_REBUILDING (Australian cattle withheld from export)"
            alpha_bias = "BEARISH_SHORT_TERM_BULLISH_LONG_TERM"
        else:
            heifer_status = "NEUTRAL_EQUILIBRIUM"
            corn_trend = "BALANCED_SUPPLY"
            mud_risk = "NORMAL_SEASONAL"
            australia_status = "NORMAL_TRADE_FLOWS"
            alpha_bias = "NEUTRAL"

        return {
            "oni_anomaly": latest_oni,
            "phase": phase,
            "heifer_retention": heifer_status,
            "corn_feed_trend": corn_trend,
            "winter_mud_risk": mud_risk,
            "australian_beef_status": australia_status,
            "bovine_alpha_bias": alpha_bias
        }

