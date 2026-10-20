"""
Quantitative Technical & Trend Following Factors.
Implements Kalman Filter adaptive trend, ATR Donchian breakout, Multi-timeframe momentum,
RSI oscillator, and Garman-Klass volatility regime estimation.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple


class BovineTechnicalFactors:
    """Calculates robust statistical and technical momentum, trend, and volatility factors."""

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Computes Average True Range (ATR)."""
        high = df["High"]
        low = df["Low"]
        close = df["Close"]
        prev_close = close.shift(1)

        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = tr.ewm(span=period, min_periods=1).mean()
        return atr.bfill().fillna(2.0)

    @staticmethod
    def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Computes Relative Strength Index (RSI)."""
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -1.0 * delta.clip(upper=0)

        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=1).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=1).mean()

        rs = avg_gain / (avg_loss + 1e-8)
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return rsi.fillna(50.0)

    @staticmethod
    def calculate_kalman_trend(series: pd.Series, q: float = 1e-4, r: float = 1e-2) -> pd.Series:
        """
        1D Kalman Filter for adaptive, low-lag trend filtering of commodity prices.
        """
        n = len(series)
        xhat = np.zeros(n)      # A-posteriori estimate of x
        P = np.zeros(n)         # A-posteriori error estimate
        xhatminus = np.zeros(n) # A-priori estimate of x
        Pminus = np.zeros(n)    # A-priori error estimate
        K = np.zeros(n)         # Kalman gain

        vals = series.values
        xhat[0] = vals[0]
        P[0] = 1.0

        for k in range(1, n):
            # Time update
            xhatminus[k] = xhat[k-1]
            Pminus[k] = P[k-1] + q

            # Measurement update
            K[k] = Pminus[k] / (Pminus[k] + r)
            xhat[k] = xhatminus[k] + K[k] * (vals[k] - xhatminus[k])
            P[k] = (1.0 - K[k]) * Pminus[k]

        return pd.Series(xhat, index=series.index)

    @staticmethod
    def calculate_garman_klass_vol(df: pd.DataFrame, window: int = 20) -> pd.Series:
        """
        Garman-Klass Volatility Estimator (uses OHLC for ~8x efficiency over close-to-close).
        """
        log_hl = np.log(df["High"] / (df["Low"] + 1e-8))
        log_co = np.log(df["Close"] / (df["Open"] + 1e-8))

        rs = 0.5 * (log_hl ** 2) - (2 * np.log(2) - 1) * (log_co ** 2)
        gk_vol = np.sqrt(rs.rolling(window, min_periods=5).mean() * 252.0)
        return gk_vol.fillna(0.15)

    def compute_factor_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Computes composite technical alpha factor [-1.0, +1.0]:
        1. Kalman Adaptive Trend (Price vs Kalman Filter slope).
        2. Donchian Breakout (20-day high/low breakout channel).
        3. Multi-timeframe Momentum (20d, 60d, 120d price return blend).
        4. RSI Mean Reversion / Overbought-Oversold penalty.
        """
        if df is None or df.empty or len(df) < 30:
            return pd.Series(0.0)

        close = df["Close"]

        # 1. Kalman Trend Slope
        kalman = self.calculate_kalman_trend(close)
        kalman_slope = (kalman - kalman.shift(10)) / (kalman.shift(10) + 1e-6)
        slope_std = kalman_slope.rolling(252, min_periods=30).std() + 1e-6
        trend_score = (kalman_slope / slope_std / 2.0).clip(-1.0, 1.0)

        # 2. Donchian 20-day Channel Position (0 to 1 -> -1.0 to +1.0)
        high20 = df["High"].rolling(20, min_periods=5).max()
        low20 = df["Low"].rolling(20, min_periods=5).min()
        donchian_pos = (close - low20) / (high20 - low20 + 1e-6)
        donchian_score = (2.0 * donchian_pos - 1.0).clip(-1.0, 1.0)

        # 3. Multi-Timeframe Momentum Blend
        mom20 = close.pct_change(20)
        mom60 = close.pct_change(60)
        mom120 = close.pct_change(120)
        mom_blend = 0.5 * mom20 + 0.3 * mom60 + 0.2 * mom120
        mom_std = mom_blend.rolling(252, min_periods=30).std() + 1e-6
        mom_score = (mom_blend / mom_std / 2.0).clip(-1.0, 1.0)

        # 4. RSI Overbought/Oversold Dampener
        rsi = self.calculate_rsi(close, 14)
        # Invert extremes: RSI > 75 = -0.3 penalty, RSI < 25 = +0.3 boost
        rsi_penalty = np.where(rsi > 75, -0.3 * (rsi - 75) / 25, 0.0)
        rsi_boost = np.where(rsi < 25, 0.3 * (25 - rsi) / 25, 0.0)
        rsi_dampener = pd.Series(rsi_penalty + rsi_boost, index=df.index)

        # Composite Technical Score: 40% Kalman Trend + 30% Momentum + 20% Donchian + 10% RSI
        composite = 0.40 * trend_score + 0.30 * mom_score + 0.20 * donchian_score + 0.10 * rsi_dampener
        return composite.clip(-1.0, 1.0).fillna(0.0)
