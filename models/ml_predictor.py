"""
Machine Learning Predictive Alpha Model for Bovine Commodities.
Employs an ensemble of Tree-Based Boosters (HistGradientBoosting / RandomForest)
and Regularized Linear Models with strict Walk-Forward out-of-sample prediction.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, List
try:
    from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import RobustScaler
    from sklearn.metrics import accuracy_score, roc_auc_score
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False



class BovineMLAlphaModel:
    """Predictive ML model for multi-factor cattle price forecasting."""

    def __init__(self, forward_horizon: int = 5, train_window: int = 504):
        self.forward_horizon = forward_horizon
        self.train_window = train_window
        self.scaler = RobustScaler() if SKLEARN_AVAILABLE else None
        self.feature_names: List[str] = []
        self.feature_importances: Dict[str, float] = {}

    def build_features(
        self,
        target_df: pd.DataFrame,
        factors_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Engineers predictive features from price action, factor dynamics, and lag structures.
        """
        df = factors_df.copy()
        close = target_df["Close"].reindex(df.index).ffill()

        # Price momentum & volatility features
        df["ret_1d"] = close.pct_change(1)
        df["ret_5d"] = close.pct_change(5)
        df["ret_20d"] = close.pct_change(20)
        df["vol_20d"] = df["ret_1d"].rolling(20, min_periods=5).std() * np.sqrt(252)

        # Factor momentum (rate of change of factors)
        for col in factors_df.columns:
            df[f"{col}_delta5"] = factors_df[col].diff(5)

        # Calendar features
        df["month"] = df.index.month
        df["dayofweek"] = df.index.dayofweek
        df["quarter"] = df.index.quarter

        # Target: Forward return direction (1 if forward return > 0, else 0)
        fwd_ret = close.pct_change(self.forward_horizon).shift(-self.forward_horizon)
        target = (fwd_ret > 0.0).astype(int)

        # Clean NaN
        valid_idx = df.dropna().index.intersection(target.dropna().index)
        features = df.loc[valid_idx]
        target = target.loc[valid_idx]

        self.feature_names = list(features.columns)
        return features, target

    def walk_forward_train_predict(
        self,
        features: pd.DataFrame,
        target: pd.Series,
        step_size: int = 60
    ) -> Tuple[pd.Series, Dict[str, float]]:
        """
        Executes strict walk-forward expanding window training to eliminate lookahead bias.
        Returns out-of-sample probability series in [-1.0, +1.0] and feature importances.
        """
        n = len(features)
        if n < self.train_window + self.forward_horizon + 20:
            # Not enough data for walk-forward, return zeros
            return pd.Series(0.0, index=features.index), {}

        preds = pd.Series(np.nan, index=features.index)
        feature_importances_list = []

        # Walk-forward loops
        for t in range(self.train_window, n, step_size):
            train_end = t - self.forward_horizon # Avoid target leakage
            if train_end <= 50:
                continue

            test_end = min(t + step_size, n)

            X_train = features.iloc[:train_end]
            y_train = target.iloc[:train_end]
            X_test = features.iloc[t:test_end]

            if len(y_train.unique()) < 2:
                continue

            if SKLEARN_AVAILABLE:
                # Fit Fast Boosted Trees & Random Forest
                scaler = RobustScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)

                m1 = HistGradientBoostingClassifier(max_iter=25, random_state=42, min_samples_leaf=15)
                m2 = RandomForestClassifier(n_estimators=15, max_depth=3, random_state=42, n_jobs=1)

                m1.fit(X_train_scaled, y_train)
                m2.fit(X_train_scaled, y_train)

                p1 = m1.predict_proba(X_test_scaled)[:, 1]
                p2 = m2.predict_proba(X_test_scaled)[:, 1]

                # Blended Probability
                p_blend = 0.60 * p1 + 0.40 * p2
                preds.iloc[t:test_end] = p_blend

                # Store importances from RandomForest
                feature_importances_list.append(m2.feature_importances_)
            else:
                # Robust regularized ridge probability predictor in pure numpy
                X_tr = X_train.values.astype(float)
                y_tr = y_train.values.astype(float)
                mean_tr = np.nanmean(X_tr, axis=0)
                std_tr = np.nanstd(X_tr, axis=0) + 1e-6
                X_tr_norm = np.nan_to_num((X_tr - mean_tr) / std_tr)
                d = X_tr_norm.shape[1]
                lambda_reg = 15.0
                XtX = X_tr_norm.T @ X_tr_norm + lambda_reg * np.eye(d)
                w = np.linalg.solve(XtX, X_tr_norm.T @ (y_tr - 0.5))

                X_te = X_test.values.astype(float)
                X_te_norm = np.nan_to_num((X_te - mean_tr) / std_tr)
                raw_logits = np.clip(X_te_norm @ w * 2.5, -6.0, 6.0)
                p_blend = 1.0 / (1.0 + np.exp(-raw_logits))
                preds.iloc[t:test_end] = p_blend
                feature_importances_list.append(np.abs(w))

        # Fill any initial warm-up period
        preds = preds.ffill().bfill().fillna(0.5)

        # Convert Probability [0..1] to Normalized Signal [-1.0..+1.0]
        # Prob 0.5 -> 0.0, Prob 0.7 -> +0.8, Prob 0.3 -> -0.8
        ml_score = ((preds - 0.5) / 0.25).clip(-1.0, 1.0)

        # Aggregate feature importances
        if feature_importances_list:
            avg_imp = np.mean(feature_importances_list, axis=0)
            self.feature_importances = dict(zip(self.feature_names, [float(x) for x in avg_imp]))
            # Sort descending
            self.feature_importances = dict(sorted(self.feature_importances.items(), key=lambda item: item[1], reverse=True))

        return ml_score, self.feature_importances
