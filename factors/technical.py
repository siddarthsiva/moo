"""
Quantitative Technical & Trend Following Factors — v2.0
Implements Kalman Filter adaptive trend, ATR Donchian breakout, Multi-timeframe momentum,
RSI oscillator, Garman-Klass volatility regime estimation, MACD signal,
Bollinger Band squeeze detector, and Chande Momentum Oscillator.
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

    @staticmethod
    def calculate_macd_signal(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
        """
        MACD signal normalized by rolling standard deviation.
        Returns normalized MACD histogram in [-1, +1].
        """
        ema_fast   = series.ewm(span=fast,   min_periods=5).mean()
        ema_slow   = series.ewm(span=slow,   min_periods=10).mean()
        macd_line  = ema_fast - ema_slow
        macd_signal_line = macd_line.ewm(span=signal, min_periods=3).mean()
        macd_hist  = macd_line - macd_signal_line

        macd_std   = macd_hist.rolling(60, min_periods=15).std() + 1e-6
        return (macd_hist / macd_std).clip(-2.0, 2.0).fillna(0.0) / 2.0  # Scaled to [-1, +1]

    @staticmethod
    def calculate_bollinger_squeeze(df: pd.DataFrame, window: int = 20, keltner_mult: float = 1.5) -> pd.Series:
        """
        Bollinger Band Squeeze detector.
        Returns a score: +1.0 when bands are tightly squeezed (breakout incoming),
        -0.5 when bands are very wide (trend exhaustion), 0.0 at neutral.
        Squeeze momentum (direction of breakout) is estimated from recent price action.
        """
        close = df["Close"]
        high  = df["High"]
        low   = df["Low"]

        # Bollinger Bands
        sma    = close.rolling(window, min_periods=5).mean()
        std    = close.rolling(window, min_periods=5).std() + 1e-6
        bb_upper = sma + 2.0 * std
        bb_lower = sma - 2.0 * std
        bb_width = (bb_upper - bb_lower) / (sma + 1e-6)

        # Keltner Channel (ATR-based)
        atr = BovineTechnicalFactors.calculate_atr(df, period=window)
        kc_upper = sma + keltner_mult * atr
        kc_lower = sma - keltner_mult * atr

        # Squeeze: BB is inside KC
        in_squeeze = (bb_upper < kc_upper) & (bb_lower > kc_lower)

        # Squeeze score based on relative BB width (lower = tighter)
        bb_width_roll_max = bb_width.rolling(60, min_periods=15).max() + 1e-6
        squeeze_intensity = (1.0 - bb_width / bb_width_roll_max).clip(0.0, 1.0)

        # Direction of potential breakout (momentum of close vs midband)
        delta = (close - sma) / (std + 1e-6)
        delta_smooth = delta.rolling(5, min_periods=1).mean()

        # Positive squeeze: price above midband in squeeze = bullish breakout potential
        # Negative squeeze: price below midband in squeeze = bearish breakout potential
        squeeze_signal = squeeze_intensity * np.sign(delta_smooth)
        return squeeze_signal.clip(-1.0, 1.0).fillna(0.0)

    @staticmethod
    def calculate_chande_momentum(series: pd.Series, period: int = 14) -> pd.Series:
        """
        Chande Momentum Oscillator (CMO): measures raw momentum as sum of up/down periods.
        Returns normalized CMO in [-1, +1].
        """
        delta = series.diff()
        up   = delta.clip(lower=0)
        down = (-delta).clip(lower=0)

        sum_up   = up.rolling(period, min_periods=3).sum()
        sum_down = down.rolling(period, min_periods=3).sum()
        cmo = (sum_up - sum_down) / (sum_up + sum_down + 1e-6)
        return cmo.clip(-1.0, 1.0).fillna(0.0)

    def compute_factor_score(self, df: pd.DataFrame) -> pd.Series:
        """
        Computes composite technical alpha factor [-1.0, +1.0] — v2.0:
        1.  Kalman Adaptive Trend (Price vs Kalman Filter slope).
        2.  Donchian Breakout (20-day high/low breakout channel).
        3.  Multi-timeframe Momentum (20d, 60d, 120d price return blend).
        4.  RSI Mean Reversion / Overbought-Oversold dampener.
        5.  MACD Histogram normalized signal (NEW).
        6.  Bollinger Band Squeeze directional signal (NEW).
        7.  Chande Momentum Oscillator (NEW).
        """
        if df is None or df.empty or len(df) < 30:
            return pd.Series(0.0)

        close = df["Close"]

        # 1. Kalman Trend Slope
        kalman = self.calculate_kalman_trend(close)
        kalman_slope = (kalman - kalman.shift(10)) / (kalman.shift(10) + 1e-6)
        slope_std    = kalman_slope.rolling(252, min_periods=30).std() + 1e-6
        trend_score  = (kalman_slope / slope_std / 2.0).clip(-1.0, 1.0)

        # 2. Donchian 20-day Channel Position (0 to 1 -> -1.0 to +1.0)
        high20 = df["High"].rolling(20, min_periods=5).max()
        low20  = df["Low"].rolling(20, min_periods=5).min()
        donchian_pos   = (close - low20) / (high20 - low20 + 1e-6)
        donchian_score = (2.0 * donchian_pos - 1.0).clip(-1.0, 1.0)

        # 3. Multi-Timeframe Momentum Blend
        mom20   = close.pct_change(20)
        mom60   = close.pct_change(60)
        mom120  = close.pct_change(120)
        mom_blend = 0.50 * mom20 + 0.30 * mom60 + 0.20 * mom120
        mom_std   = mom_blend.rolling(252, min_periods=30).std() + 1e-6
        mom_score = (mom_blend / mom_std / 2.0).clip(-1.0, 1.0)

        # 4. RSI Overbought/Oversold Dampener
        rsi = self.calculate_rsi(close, 14)
        rsi_penalty = np.where(rsi > 75, -0.3 * (rsi - 75) / 25, 0.0)
        rsi_boost   = np.where(rsi < 25,  0.3 * (25 - rsi) / 25, 0.0)
        rsi_dampener = pd.Series(rsi_penalty + rsi_boost, index=df.index)

        # 5. MACD Signal (NEW)
        macd_score = self.calculate_macd_signal(close)

        # 6. Bollinger Squeeze (NEW)
        squeeze_score = self.calculate_bollinger_squeeze(df)

        # 7. Chande Momentum Oscillator (NEW)
        cmo_score = self.calculate_chande_momentum(close)

        # Composite Technical Score (weights sum to 1.0)
        # 30% Kalman + 20% Momentum + 15% Donchian + 15% MACD + 10% Bollinger Squeeze + 5% CMO + 5% RSI
        composite = (
            0.30 * trend_score
            + 0.20 * mom_score
            + 0.15 * donchian_score
            + 0.15 * macd_score
            + 0.10 * squeeze_score
            + 0.05 * cmo_score
            + 0.05 * rsi_dampener
        )
        return composite.clip(-1.0, 1.0).fillna(0.0)
