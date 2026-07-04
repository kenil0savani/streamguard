"""
Maintains a per-sensor rolling window of recent readings and derives features
(rolling mean/std, z-scores) used by the anomaly model. This mirrors the
feature engineering approach used for concept-drift-aware anomaly detection
on non-stationary streaming data.
"""
from collections import defaultdict, deque

import numpy as np


class RollingFeatureStore:
    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.history: dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))

    def update_and_extract(self, sensor_id: str, temperature: float, vibration: float) -> dict:
        self.history[sensor_id].append((temperature, vibration))
        temps = np.array([t for t, _ in self.history[sensor_id]])
        vibs = np.array([v for _, v in self.history[sensor_id]])

        temp_mean, temp_std = float(np.mean(temps)), float(np.std(temps)) if len(temps) > 1 else 0.0
        vib_mean, vib_std = float(np.mean(vibs)), float(np.std(vibs)) if len(vibs) > 1 else 0.0

        return {
            "temperature": temperature,
            "vibration": vibration,
            "temp_rolling_mean": temp_mean,
            "temp_rolling_std": temp_std,
            "vib_rolling_mean": vib_mean,
            "vib_rolling_std": vib_std,
            "temp_zscore": float((temperature - temp_mean) / (temp_std + 1e-6)),
            "vib_zscore": float((vibration - vib_mean) / (vib_std + 1e-6)),
        }
