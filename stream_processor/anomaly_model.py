"""
Self-supervised anomaly scoring via IsolationForest. The model bootstraps on
startup so the pipeline is usable immediately, then gets periodically
retrained by the Airflow DAG on freshly accumulated data. This version can
also reload the retrained model file while it is running, so a long-running
consumer or API process picks up improvements without needing a restart.
"""

import os

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

FEATURE_ORDER = [
    "temperature",
    "vibration",
    "temp_rolling_mean",
    "temp_rolling_std",
    "vib_rolling_mean",
    "vib_rolling_std",
    "temp_zscore",
    "vib_zscore",
]

DEFAULT_MODEL_PATH = os.getenv("MODEL_PATH", "/models/isolation_forest.joblib")


class AnomalyModel:
    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        self.model_path = model_path
        self.model = self._load_or_bootstrap()
        self._last_mtime = self._get_mtime()

    def _get_mtime(self):
        try:
            return os.path.getmtime(self.model_path)
        except OSError:
            return None

    def _load_or_bootstrap(self):
        if os.path.exists(self.model_path):
            return joblib.load(self.model_path)
        rng = np.random.default_rng(42)
        bootstrap_X = rng.normal(0, 1, size=(200, len(FEATURE_ORDER)))
        model = IsolationForest(n_estimators=150, contamination=0.03, random_state=42)
        model.fit(bootstrap_X)
        return model

    def reload_if_updated(self) -> bool:
        """
        Checks whether the model file on disk has changed since we last
        loaded it (for example, because Airflow just retrained it), and
        reloads it into memory if so. Returns True if a reload happened.
        """
        mtime = self._get_mtime()
        if mtime is not None and mtime != self._last_mtime:
            try:
                self.model = joblib.load(self.model_path)
                self._last_mtime = mtime
                return True
            except Exception:  # noqa: BLE001
                return False
        return False

    def score(self, features: dict) -> dict:
        x = np.array([[features[f] for f in FEATURE_ORDER]])
        raw_score = self.model.score_samples(x)[0]  # higher = more "normal"
        prediction = self.model.predict(x)[0]  # -1 = anomaly, 1 = normal
        return {
            "anomaly_score": float(-raw_score),  # flip so higher = more anomalous
            "is_anomaly": bool(prediction == -1),
        }

    def retrain(self, X: np.ndarray) -> None:
        model = IsolationForest(n_estimators=150, contamination=0.03, random_state=42)
        model.fit(X)
        self.model = model
        os.makedirs(os.path.dirname(self.model_path) or ".", exist_ok=True)
        joblib.dump(self.model, self.model_path)
        self._last_mtime = self._get_mtime()
