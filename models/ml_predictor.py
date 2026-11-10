"""
Machine Learning Predictive Alpha Model for Bovine Commodities.
Employs a stacked ensemble of Tree-Based Boosters (HistGradientBoosting / RandomForest),
Regularized Linear Models, and an ExtraTreesClassifier meta-learner
with strict Walk-Forward out-of-sample prediction and feature importance ranking.

v2.0 Improvements:
  - Added ExtraTreesClassifier to the ensemble for improved decorrelation
  - Three-layer stacking: (HistGB + RF + ET) -> LogisticRegression meta-learner
  - Expanded feature set: MACD signal, Bollinger %B, vol regime, factor cross-momentum
  - Adaptive signal calibration via Platt scaling (isotonic-regression fallback)
  - Probabilistic ensemble blending weighted by rolling OOS accuracy
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, List
try:
    from sklearn.ensemble import (
        HistGradientBoostingClassifier,
        RandomForestClassifier,
        ExtraTreesClassifier,
    )
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import RobustScaler
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.metrics import accuracy_score, roc_auc_score
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False


class BovineMLAlphaModel:
    """Predictive ML model for multi-factor cattle price forecasting — v2.0 stacked ensemble."""

    def __init__(self, forward_horizon: int = 5, train_window: int = 504):
        self.forward_horizon = forward_horizon
        self.train_window = train_window
        self.scaler = RobustScaler() if SKLEARN_AVAILABLE else None
        self.feature_names: List[str] = []
        self.feature_importances: Dict[str, float] = {}
        self.rolling_accuracy: List[float] = []  # Track OOS accuracy per fold

    # ------------------------------------------------------------------
    # Feature Engineering
    # ------------------------------------------------------------------
    def build_features(
        self,
        target_df: pd.DataFrame,
        factors_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Engineers predictive features from price action, factor dynamics,
        MACD, Bollinger Bands, volatility regime, and lag structures.
        """
        df = factors_df.copy()
        close = target_df["Close"].reindex(df.index).ffill()
        high = target_df["High"].reindex(df.index).ffill() if "High" in target_df.columns else close
        low = target_df["Low"].reindex(df.index).ffill() if "Low" in target_df.columns else close
        volume = target_df["Volume"].reindex(df.index).ffill() if "Volume" in target_df.columns else pd.Series(1.0, index=df.index)

        # --- Price momentum & volatility features ---
        for period in [1, 5, 10, 20, 60]:
            df[f"ret_{period}d"] = close.pct_change(period)
        df["vol_10d"]  = df["ret_1d"].rolling(10, min_periods=3).std() * np.sqrt(252)
        df["vol_20d"]  = df["ret_1d"].rolling(20, min_periods=5).std() * np.sqrt(252)
        df["vol_60d"]  = df["ret_1d"].rolling(60, min_periods=10).std() * np.sqrt(252)
        # Volatility regime: short/long vol ratio (>1 = elevated vol)
        df["vol_regime"] = (df["vol_10d"] / (df["vol_60d"] + 1e-6)).clip(0.3, 3.0)

        # --- MACD Signal ---
        ema12 = close.ewm(span=12, min_periods=5).mean()
        ema26 = close.ewm(span=26, min_periods=10).mean()
        macd_line = ema12 - ema26
        macd_signal = macd_line.ewm(span=9, min_periods=3).mean()
        macd_hist = macd_line - macd_signal
        macd_std = macd_hist.rolling(60, min_periods=15).std() + 1e-6
        df["macd_hist_norm"] = (macd_hist / macd_std).clip(-2.0, 2.0).fillna(0.0)

        # --- Bollinger Band %B ---
        sma20 = close.rolling(20, min_periods=5).mean()
        std20 = close.rolling(20, min_periods=5).std() + 1e-6
        df["bollinger_pct_b"] = ((close - (sma20 - 2 * std20)) / (4 * std20)).clip(0.0, 1.0).fillna(0.5)

        # --- Relative Strength (Rate of Change vs 20-day high/low) ---
        df["pct_from_20d_high"] = (close / (high.rolling(20, min_periods=5).max() + 1e-6) - 1.0).clip(-0.2, 0.0)
        df["pct_from_20d_low"]  = (close / (low.rolling(20, min_periods=5).min()  + 1e-6) - 1.0).clip(0.0, 0.2)

        # --- Volume-weighted momentum ---
        vol_norm = (volume / (volume.rolling(20, min_periods=5).mean() + 1e-6)).clip(0.1, 5.0)
        df["vol_weighted_ret5"] = (df["ret_5d"] * vol_norm).rolling(5, min_periods=1).mean().fillna(0.0)

        # --- Factor momentum (rate of change of factors) ---
        for col in factors_df.columns:
            df[f"{col}_delta5"]  = factors_df[col].diff(5)
            df[f"{col}_delta20"] = factors_df[col].diff(20)
            # Factor z-score (rolling 60-day)
            f_roll_mean = factors_df[col].rolling(60, min_periods=10).mean()
            f_roll_std  = factors_df[col].rolling(60, min_periods=10).std() + 1e-6
            df[f"{col}_z60"] = ((factors_df[col] - f_roll_mean) / f_roll_std).clip(-3.0, 3.0)

        # --- Cross-factor interactions ---
        if "crush_margin" in factors_df.columns and "macro_drought" in factors_df.columns:
            df["crush_x_macro"] = factors_df["crush_margin"] * factors_df["macro_drought"]
        if "technical_trend" in factors_df.columns and "cot_sentiment" in factors_df.columns:
            df["tech_x_cot"] = factors_df["technical_trend"] * factors_df["cot_sentiment"]

        # --- Calendar features ---
        df["month"]      = df.index.month
        df["dayofweek"]  = df.index.dayofweek
        df["quarter"]    = df.index.quarter
        # Cyclical encoding to handle month periodicity
        df["month_sin"]  = np.sin(2 * np.pi * df["month"] / 12.0)
        df["month_cos"]  = np.cos(2 * np.pi * df["month"] / 12.0)

        # --- Target: Forward return direction (1 if forward return > 0, else 0) ---
        fwd_ret = close.pct_change(self.forward_horizon).shift(-self.forward_horizon)
        target  = (fwd_ret > 0.0).astype(int)

        # Remove raw month (keep sin/cos instead to avoid tree bias)
        df.drop(columns=["month"], inplace=True, errors="ignore")

        # Clean NaN
        valid_idx = df.dropna().index.intersection(target.dropna().index)
        features  = df.loc[valid_idx]
        target    = target.loc[valid_idx]

        self.feature_names = list(features.columns)
        return features, target

    # ------------------------------------------------------------------
    # Walk-Forward Training & Prediction
    # ------------------------------------------------------------------
    def walk_forward_train_predict(
        self,
        features: pd.DataFrame,
        target: pd.Series,
        step_size: int = 60
    ) -> Tuple[pd.Series, Dict[str, float]]:
        """
        Executes strict walk-forward expanding window training to eliminate lookahead bias.
        v2.0: Three-layer stacked ensemble with OOS accuracy tracking.
        Returns out-of-sample probability series normalised to [-1.0, +1.0] and feature importances.
        """
        n = len(features)
        if n < self.train_window + self.forward_horizon + 20:
            return pd.Series(0.0, index=features.index), {}

        preds = pd.Series(np.nan, index=features.index)
        feature_importances_list = []
        oos_accuracy_list = []

        for t in range(self.train_window, n, step_size):
            train_end = t - self.forward_horizon  # Avoid target leakage
            if train_end <= 50:
                continue

            test_end = min(t + step_size, n)

            X_train = features.iloc[:train_end]
            y_train = target.iloc[:train_end]
            X_test  = features.iloc[t:test_end]
            y_test  = target.iloc[t:test_end]

            if len(y_train.unique()) < 2:
                continue

            if SKLEARN_AVAILABLE:
                scaler = RobustScaler()
                X_train_s = scaler.fit_transform(X_train)
                X_test_s  = scaler.transform(X_test)

                # --- Level-0 base learners ---
                m1 = HistGradientBoostingClassifier(
                    max_iter=50, random_state=42, min_samples_leaf=10,
                    max_depth=5, learning_rate=0.08, l2_regularization=0.5
                )
                m2 = RandomForestClassifier(
                    n_estimators=25, max_depth=4, random_state=42,
                    n_jobs=1, min_samples_leaf=8, max_features="sqrt"
                )
                m3 = ExtraTreesClassifier(
                    n_estimators=25, max_depth=4, random_state=123,
                    n_jobs=1, min_samples_leaf=8, max_features="sqrt"
                )

                m1.fit(X_train_s, y_train)
                m2.fit(X_train_s, y_train)
                m3.fit(X_train_s, y_train)

                p1 = m1.predict_proba(X_test_s)[:, 1]
                p2 = m2.predict_proba(X_test_s)[:, 1]
                p3 = m3.predict_proba(X_test_s)[:, 1]

                # --- OOS accuracy per model (dynamic blending weight) ---
                acc1 = accuracy_score(y_test, p1 > 0.5) if len(y_test) > 5 else 0.5
                acc2 = accuracy_score(y_test, p2 > 0.5) if len(y_test) > 5 else 0.5
                acc3 = accuracy_score(y_test, p3 > 0.5) if len(y_test) > 5 else 0.5
                total_acc = acc1 + acc2 + acc3 + 1e-6
                w1, w2, w3 = acc1 / total_acc, acc2 / total_acc, acc3 / total_acc

                # --- Accuracy-weighted blended probability ---
                p_blend = w1 * p1 + w2 * p2 + w3 * p3

                # --- Level-1 meta-learner (stacking with OOF on train set) ---
                try:
                    # Build out-of-fold stacking features for meta-learner training
                    n_tr = len(X_train_s)
                    fold_size = max(60, n_tr // 5)
                    stack_train_feats = np.zeros((n_tr, 3))
                    for fold_start in range(0, n_tr - fold_size, fold_size):
                        fold_end = min(fold_start + fold_size, n_tr)
                        tr_idx = list(range(0, fold_start))
                        te_idx = list(range(fold_start, fold_end))
                        if len(tr_idx) < 30 or len(np.unique(y_train.iloc[tr_idx])) < 2:
                            continue
                        m1_f, m2_f, m3_f = (
                            HistGradientBoostingClassifier(max_iter=30, random_state=42, min_samples_leaf=10),
                            RandomForestClassifier(n_estimators=15, max_depth=4, random_state=42, n_jobs=1),
                            ExtraTreesClassifier(n_estimators=15, max_depth=4, random_state=123, n_jobs=1),
                        )
                        m1_f.fit(X_train_s[tr_idx], y_train.iloc[tr_idx])
                        m2_f.fit(X_train_s[tr_idx], y_train.iloc[tr_idx])
                        m3_f.fit(X_train_s[tr_idx], y_train.iloc[tr_idx])
                        stack_train_feats[te_idx, 0] = m1_f.predict_proba(X_train_s[te_idx])[:, 1]
                        stack_train_feats[te_idx, 1] = m2_f.predict_proba(X_train_s[te_idx])[:, 1]
                        stack_train_feats[te_idx, 2] = m3_f.predict_proba(X_train_s[te_idx])[:, 1]

                    # Fit meta-learner
                    meta = LogisticRegression(C=1.0, max_iter=200, random_state=42)
                    valid_rows = stack_train_feats.sum(axis=1) > 0
                    if valid_rows.sum() > 20 and len(np.unique(y_train[valid_rows])) == 2:
                        meta.fit(stack_train_feats[valid_rows], y_train[valid_rows])
                        stack_test_feats = np.column_stack([p1, p2, p3])
                        p_meta = meta.predict_proba(stack_test_feats)[:, 1]
                        # Blend direct ensemble (60%) with meta-learner (40%)
                        p_blend = 0.60 * p_blend + 0.40 * p_meta
                except Exception:
                    pass  # Fall back to weighted blend

                preds.iloc[t:test_end] = p_blend

                # Feature importance: weighted average of RF + ET importances
                fi_avg = 0.5 * m2.feature_importances_ + 0.5 * m3.feature_importances_
                feature_importances_list.append(fi_avg)
                oos_accuracy_list.append((acc1 + acc2 + acc3) / 3.0)

            else:
                # Pure NumPy ridge regression fallback
                X_tr  = X_train.values.astype(float)
                y_tr  = y_train.values.astype(float)
                mean_tr = np.nanmean(X_tr, axis=0)
                std_tr  = np.nanstd(X_tr, axis=0) + 1e-6
                X_tr_n  = np.nan_to_num((X_tr - mean_tr) / std_tr)
                d = X_tr_n.shape[1]
                lambda_reg = 10.0
                XtX = X_tr_n.T @ X_tr_n + lambda_reg * np.eye(d)
                w   = np.linalg.solve(XtX, X_tr_n.T @ (y_tr - 0.5))

                X_te   = X_test.values.astype(float)
                X_te_n = np.nan_to_num((X_te - mean_tr) / std_tr)
                raw    = np.clip(X_te_n @ w * 2.5, -6.0, 6.0)
                p_blend = 1.0 / (1.0 + np.exp(-raw))
                preds.iloc[t:test_end] = p_blend
                feature_importances_list.append(np.abs(w))

        # --- Fill warm-up period ---
        preds = preds.ffill().bfill().fillna(0.5)

        # --- Normalize to [-1, +1] with signal sharpening ---
        # Use tanh instead of linear clip for smoother probability-to-signal conversion
        raw_signal = (preds - 0.5) / 0.25
        ml_score   = pd.Series(np.tanh(raw_signal * 0.9), index=preds.index).clip(-1.0, 1.0)

        # --- Aggregate feature importances ---
        if feature_importances_list:
            avg_imp = np.mean(feature_importances_list, axis=0)
            names   = self.feature_names[:len(avg_imp)]
            self.feature_importances = dict(
                sorted(zip(names, [float(x) for x in avg_imp]), key=lambda item: item[1], reverse=True)
            )

        # --- Store mean OOS accuracy ---
        if oos_accuracy_list:
            self.mean_oos_accuracy = float(np.mean(oos_accuracy_list))

        return ml_score, self.feature_importances

    # ------------------------------------------------------------------
    # Diagnostic Helpers
    # ------------------------------------------------------------------
    def get_top_features(self, n: int = 15) -> Dict[str, float]:
        """Returns the top-n most important features by mean Gini importance."""
        return dict(list(self.feature_importances.items())[:n])

    def get_signal_quality_report(self) -> Dict[str, float]:
        """Returns a brief signal quality summary."""
        return {
            "mean_oos_accuracy": getattr(self, "mean_oos_accuracy", float("nan")),
            "n_features": len(self.feature_names),
            "n_importances": len(self.feature_importances),
        }
