"""
Bovine Synthetic Data Generator.
Produces high-fidelity, statistically accurate historical and live simulation data
for cattle futures (LE=F, GF=F), feed (ZC=F, ZM=F), macro (DXY, CL=F), CFTC COT, and Drought.
Ensures zero-dependency instant testing, backtesting, and offline reliability.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta

from config import COMMODITY_SPECS, CATTLE_CRUSH_CONFIG


class BovineSyntheticDataGenerator:
    """Generates realistic market price series with bovine economic microstructure."""

    def __init__(self, seed: int = 42):
        np.random.seed(seed)

    def generate_full_market_history(
        self,
        start_date: str = "2018-01-01",
        end_date: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Generates full market history for all assets with realistic cross-correlations,
        cattle cycles, seasonality, COT positioning, and drought indices.
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        dates = pd.date_range(start=start_date, end=end_date, freq="B")
        n = len(dates)

        # Baseline Parameters & Geometric Brownian Motion with Mean-Reverting Spread
        # 1. Macro Factors (DXY, Crude Oil, Drought)
        dxy = self._generate_mean_reverting_series(n, start_val=95.0, mean_val=98.0, vol=0.06, speed=0.01)
        crude = self._generate_mean_reverting_series(n, start_val=60.0, mean_val=75.0, vol=0.28, speed=0.02)
        
        # Drought Severity Index (0 to 100, where >40 is moderate drought, >70 is severe)
        # Seasonal peak in late summer, episodic multi-year drought in 2021-2023, Super El Niño relief in 2026
        year_frac = (dates.year - dates.year.min()) + dates.dayofyear / 365.25
        drought_cycle = 35 + 20 * np.sin(2 * np.pi * dates.dayofyear / 365.25 - 1.5)
        # Add 2021-2023 drought super-shock and 2026 Super El Niño moisture relief
        drought_shock = np.where((dates.year >= 2021) & (dates.year <= 2023), 28.0, 0.0)
        drought_relief = np.where(dates.year >= 2026, -18.0, 0.0) # Subtropical jet stream breaks Southern Plains drought
        drought_noise = np.cumsum(np.random.normal(0, 0.8, n))
        drought_noise = drought_noise - np.linspace(drought_noise[0], drought_noise[-1], n)
        drought_index = np.clip(drought_cycle + drought_shock + drought_relief + drought_noise, 5, 95)

        # ENSO Oceanic Niño Index (ONI) SST Anomaly (°C)
        oni_vals = np.zeros(n)
        for i, d in enumerate(dates):
            y = d.year + d.dayofyear / 365.25
            if y < 2019.0:
                oni = -0.3 + 0.4 * np.sin(2 * np.pi * y)
            elif y < 2020.0:
                oni = 0.5 + 0.2 * np.cos(2 * np.pi * y)
            elif y < 2023.0: # La Niña
                oni = -1.1 + 0.3 * np.sin(2 * np.pi * (y - 2020.5))
            elif y < 2024.5: # 2023-2024 El Niño
                oni = 1.6 + 0.3 * np.sin(2 * np.pi * (y - 2023.2))
            elif y < 2025.5: # Neutral
                oni = -0.2
            else: # 2026 SUPER EL NIÑO (+2.3°C peak)
                progress = np.clip((y - 2025.5) / 1.1, 0.0, 1.0)
                oni = 0.5 + 1.8 * np.sin(np.pi * progress * 0.5)
            oni_vals[i] = round(float(oni), 2)

        phases = [
            "SUPER_EL_NINO" if v >= 2.0 else "EL_NINO" if v >= 0.5 else "SUPER_LA_NINA" if v <= -1.5 else "LA_NINA" if v <= -0.5 else "NEUTRAL"
            for v in oni_vals
        ]
        df_enso = pd.DataFrame({"ONI": oni_vals, "Phase": phases}, index=dates)

        # 2. Feed: Corn (ZC=F) in cents/bushel (e.g. 350 to 750 cents)
        # Super El Niño brings Midwest bumper crop -> downward pressure on feed prices
        corn_drift = 0.05 * (drought_index - 40) / 40.0
        corn_elnino_relief = np.where(dates.year >= 2026, -0.06, 0.0)
        corn = self._generate_commodity_ohlcv(
            dates, start_price=380.0, mean_price=480.0, vol=0.22,
            season_amplitude=0.08, season_phase=200, drift_boost=corn_drift + corn_elnino_relief
        )

        # 3. Feeder Cattle (GF=F) in cents/lb ($/cwt, e.g. 140 to 260)
        # Higher corn -> negative pressure on feeder price; Super El Niño cheap corn + lush forage -> strong feeder demand
        heifer_retention_boost = np.where(dates.year >= 2026, 0.08, 0.0)
        feeder_drift = -0.04 * (corn["Close"].values - 450) / 450 + 0.06 * (drought_index - 35) / 50 + heifer_retention_boost
        feeder = self._generate_commodity_ohlcv(
            dates, start_price=145.0, mean_price=185.0, vol=0.18,
            season_amplitude=0.06, season_phase=280, drift_boost=feeder_drift
        )

        # 4. Live Cattle (LE=F) in cents/lb ($/cwt, e.g. 110 to 195)
        # Strong seasonal spring grilling demand; Super El Niño prompt slaughter deficit drift
        lagged_drought = pd.Series(drought_index).rolling(250, min_periods=1).mean().values
        slaughter_tightness = np.where(dates.year >= 2026, 0.07, 0.0)
        live_drift = 0.08 * (lagged_drought - 35) / 40.0 + slaughter_tightness
        live = self._generate_commodity_ohlcv(
            dates, start_price=120.0, mean_price=150.0, vol=0.16,
            season_amplitude=0.07, season_phase=120, drift_boost=live_drift
        )

        # 5. Lean Hogs (HE=F) - Substitute Meat
        hogs = self._generate_commodity_ohlcv(
            dates, start_price=68.0, mean_price=82.0, vol=0.26,
            season_amplitude=0.12, season_phase=160
        )

        # 5b. Soybean Meal (ZM=F) - Feed Protein Component ($/ton, e.g. 300 to 450)
        soymeal = self._generate_commodity_ohlcv(
            dates, start_price=330.0, mean_price=380.0, vol=0.21,
            season_amplitude=0.07, season_phase=210, drift_boost=corn_drift * 0.8
        )

        # 6. Class III Milk (DC=F)
        milk = self._generate_commodity_ohlcv(
            dates, start_price=16.5, mean_price=18.5, vol=0.20,
            season_amplitude=0.05, season_phase=260
        )

        # 7. CFTC COT Positioning Data (Weekly aligned to Daily)
        # Commercials (Hedgers) vs Non-Commercials (Managed Money)
        cot_live = self._generate_cot_data(dates, live["Close"].values)
        cot_feeder = self._generate_cot_data(dates, feeder["Close"].values)

        # Macro series DataFrames
        df_dxy = pd.DataFrame({"Close": dxy, "Open": dxy, "High": dxy * 1.002, "Low": dxy * 0.998, "Volume": 50000}, index=dates)
        df_crude = pd.DataFrame({"Close": crude, "Open": crude, "High": crude * 1.01, "Low": crude * 0.99, "Volume": 250000}, index=dates)
        df_drought = pd.DataFrame({"DroughtIndex": drought_index, "SevereDroughtPct": np.clip(drought_index * 0.6, 0, 100)}, index=dates)

        return {
            "LE=F": live,
            "GF=F": feeder,
            "ZC=F": corn,
            "ZM=F": soymeal,
            "HE=F": hogs,
            "DC=F": milk,
            "CL=F": df_crude,
            "DX-Y.NYB": df_dxy,
            "COT_LE": cot_live,
            "COT_GF": cot_feeder,
            "DROUGHT": df_drought,
            "ENSO": df_enso
        }

    def _generate_mean_reverting_series(
        self, n: int, start_val: float, mean_val: float, vol: float, speed: float
    ) -> np.ndarray:
        """Ornstein-Uhlenbeck mean-reverting stochastic process."""
        dt = 1.0 / 252.0
        x = np.zeros(n)
        x[0] = start_val
        for t in range(1, n):
            dx = speed * (mean_val - x[t-1]) * dt + vol * np.sqrt(dt) * x[t-1] * np.random.normal()
            x[t] = max(x[t-1] + dx, 1.0)
        return x

    def _generate_commodity_ohlcv(
        self,
        dates: pd.DatetimeIndex,
        start_price: float,
        mean_price: float,
        vol: float,
        season_amplitude: float = 0.05,
        season_phase: int = 100,
        drift_boost: Optional[np.ndarray] = None
    ) -> pd.DataFrame:
        """Generates realistic OHLCV dataframe with intra-day spread, volume, and open interest."""
        n = len(dates)
        dt = 1.0 / 252.0
        close = np.zeros(n)
        close[0] = start_price

        day_of_year = dates.dayofyear.values
        season_cycle = season_amplitude * np.sin(2 * np.pi * (day_of_year - season_phase) / 365.25)

        for t in range(1, n):
            drift = 0.03 * (mean_price - close[t-1]) / mean_price
            if drift_boost is not None:
                drift += drift_boost[t]
            ret = (drift + season_cycle[t] * 0.1) * dt + vol * np.sqrt(dt) * np.random.normal()
            close[t] = max(close[t-1] * np.exp(ret), start_price * 0.3)

        # Generate Open, High, Low
        intraday_vol = vol * np.sqrt(dt) * 0.8
        open_p = close * np.exp(np.random.normal(0, intraday_vol * 0.4, n))
        high_p = np.maximum(open_p, close) * (1.0 + np.abs(np.random.normal(0, intraday_vol, n)))
        low_p = np.minimum(open_p, close) * (1.0 - np.abs(np.random.normal(0, intraday_vol, n)))

        # Realistic volume & Open Interest
        vol_base = np.random.lognormal(mean=9.5, sigma=0.4, size=n)
        volume = (vol_base * (1.0 + np.abs(close - np.roll(close, 1)) / (close + 1e-6) * 5.0)).astype(int)
        open_interest = np.random.normal(loc=300_000, scale=30_000, size=n).astype(int)

        df = pd.DataFrame(
            {
                "Open": np.round(open_p, 3),
                "High": np.round(high_p, 3),
                "Low": np.round(low_p, 3),
                "Close": np.round(close, 3),
                "Volume": volume,
                "OpenInterest": open_interest
            },
            index=dates
        )
        return df

    def _generate_cot_data(self, dates: pd.DatetimeIndex, price_close: np.ndarray) -> pd.DataFrame:
        """Generates realistic Commercial Hedger & Managed Money CFTC positioning."""
        n = len(dates)
        # Commercials are typically net short (hedging physical cattle inventory),
        # but become less short / net long at market bottoms
        price_norm = (price_close - pd.Series(price_close).rolling(252, min_periods=30).mean().values) / \
                     (pd.Series(price_close).rolling(252, min_periods=30).std().values + 1e-6)
        price_norm = np.nan_to_num(price_norm, nan=0.0)

        # Commercials fade the price trend (smart money accumulation)
        comm_net = -50_000 - price_norm * 30_000 + np.random.normal(0, 3000, n)
        comm_long = np.clip(60_000 - price_norm * 15_000, 10_000, 150_000)
        comm_short = comm_long - comm_net

        # Managed Money (CTAs/trend followers) follow the price trend
        money_net = 40_000 + price_norm * 35_000 + np.random.normal(0, 4000, n)
        money_long = np.clip(70_000 + price_norm * 20_000, 15_000, 180_000)
        money_short = np.clip(money_long - money_net, 5_000, 120_000)

        # 3-Year COT Index (Percentile of Commercial Net Positioning over 156 weeks ~ 756 days)
        comm_net_s = pd.Series(comm_net)
        roll_min = comm_net_s.rolling(756, min_periods=50).min()
        roll_max = comm_net_s.rolling(756, min_periods=50).max()
        cot_index = (comm_net_s - roll_min) / (roll_max - roll_min + 1e-6) * 100.0
        cot_index = cot_index.fillna(50.0).clip(0, 100).values

        df = pd.DataFrame(
            {
                "Commercial_Long": comm_long.astype(int),
                "Commercial_Short": comm_short.astype(int),
                "Commercial_Net": comm_net.astype(int),
                "ManagedMoney_Long": money_long.astype(int),
                "ManagedMoney_Short": money_short.astype(int),
                "ManagedMoney_Net": money_net.astype(int),
                "COT_Commercial_Index": np.round(cot_index, 2),
            },
            index=dates
        )
        return df
