"""
CFTC Commitments of Traders (COT) Sentiment Factor.
Quantifies Smart Money (Commercial Cattlemen/Packers) vs Speculator (Managed Money/CTA)
positioning, percentile extremes, and accumulation velocity.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple


class COTSentimentFactor:
    """Computes institutional sentiment signals from CFTC COT positioning."""

    def compute_factor_score(
        self,
        cot_df: pd.DataFrame,
        target_asset: str = "LE=F"
    ) -> pd.Series:
        """
        Calculates composite COT sentiment score [-1.0, +1.0]:
        1. Commercial Hedger Index (Percentile of net commercial contracts over 3 years / 756 days).
           - COT Index > 80: High commercial smart-money buying (Bullish: +1.0)
           - COT Index < 20: High commercial selling / Speculator extreme bubble (Bearish: -1.0)
        2. Speculator Crowding: When Managed Money is in top 5th percentile long, high risk of cascade liquidation.
        3. Commercial Accumulation Velocity: 4-week change in commercial net positioning.
        """
        if cot_df is None or cot_df.empty:
            return pd.Series(0.0)

        # 1. COT Commercial Index (0 to 100)
        if "COT_Commercial_Index" in cot_df.columns:
            cot_idx = cot_df["COT_Commercial_Index"].astype(float)
        elif "Commercial_Net" in cot_df.columns:
            cnet = cot_df["Commercial_Net"].astype(float)
            roll_min = cnet.rolling(756, min_periods=50).min()
            roll_max = cnet.rolling(756, min_periods=50).max()
            cot_idx = ((cnet - roll_min) / (roll_max - roll_min + 1e-6) * 100.0).clip(0, 100)
        else:
            return pd.Series(0.0, index=cot_df.index)

        # Normalized index score (-1.0 to +1.0)
        idx_score = (cot_idx - 50.0) / 35.0

        # 2. Speculator Crowding Penalty
        if "ManagedMoney_Net" in cot_df.columns:
            mnet = cot_df["ManagedMoney_Net"].astype(float)
            m_min = mnet.rolling(756, min_periods=50).min()
            m_max = mnet.rolling(756, min_periods=50).max()
            m_percentile = ((mnet - m_min) / (m_max - m_min + 1e-6)).clip(0, 1)
            # When managed money is ultra-crowded (>90%), add short/pullback pressure
            crowd_penalty = np.where(m_percentile > 0.85, -0.3 * (m_percentile - 0.85) / 0.15, 0.0)
            crowd_boost = np.where(m_percentile < 0.15, 0.3 * (0.15 - m_percentile) / 0.15, 0.0)
            spec_signal = pd.Series(crowd_penalty + crowd_boost, index=cot_df.index)
        else:
            spec_signal = pd.Series(0.0, index=cot_df.index)

        # 3. Commercial Accumulation Velocity (20-day delta in Commercial Net)
        if "Commercial_Net" in cot_df.columns:
            cnet = cot_df["Commercial_Net"].astype(float)
            cnet_delta = cnet.diff(20).fillna(0.0)
            cnet_delta_std = cnet_delta.rolling(252, min_periods=30).std() + 1e-6
            vel_score = (cnet_delta / cnet_delta_std) / 2.0
            vel_score = vel_score.clip(-1.0, 1.0)
        else:
            vel_score = pd.Series(0.0, index=cot_df.index)

        # Composite COT Factor: 50% Index, 25% Speculator Crowding, 25% Velocity
        composite = 0.50 * idx_score + 0.25 * spec_signal + 0.25 * vel_score
        return composite.clip(-1.0, 1.0).fillna(0.0)
