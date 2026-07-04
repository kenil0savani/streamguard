import os
import sys

import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "stream_processor"))

from anomaly_model import FEATURE_ORDER, AnomalyModel  # noqa: E402
from feature_engineering import RollingFeatureStore  # noqa: E402


def test_feature_engineering_produces_expected_keys():
    store = RollingFeatureStore(window_size=5)
    features = store.update_and_extract("sensor_test", 70.0, 1.0)
    for key in FEATURE_ORDER:
        assert key in features


def test_rolling_stats_update_across_calls():
    store = RollingFeatureStore(window_size=5)
    store.update_and_extract("sensor_test", 70.0, 1.0)
    features = store.update_and_extract("sensor_test", 72.0, 1.1)
    assert features["temp_rolling_mean"] == 71.0


def test_model_scores_have_expected_shape(tmp_path):
    model = AnomalyModel(model_path=str(tmp_path / "test_model.joblib"))
    features = {f: 0.0 for f in FEATURE_ORDER}
    result = model.score(features)
    assert "anomaly_score" in result
    assert "is_anomaly" in result
    assert isinstance(result["is_anomaly"], bool)


def test_model_retrain_and_reload(tmp_path):
    model_path = str(tmp_path / "model.joblib")
    model = AnomalyModel(model_path=model_path)
    X = np.random.default_rng(0).normal(0, 1, size=(150, len(FEATURE_ORDER)))
    model.retrain(X)
    assert os.path.exists(model_path)
