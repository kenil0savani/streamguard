"""
Real-time anomaly scoring API. Wraps the same feature engineering + model
used by the stream consumer so a single reading can be scored on demand
(e.g. from an external system that can't consume Kafka directly).
"""
import os
import sys
import time

from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "stream_processor"))
from anomaly_model import AnomalyModel  # noqa: E402
from feature_engineering import RollingFeatureStore  # noqa: E402

app = FastAPI(title="StreamGuard Anomaly Scoring API", version="1.0.0")

feature_store = RollingFeatureStore(window_size=30)
model = AnomalyModel()

REQUEST_COUNT = Counter("streamguard_requests_total", "Total scoring requests")
ANOMALY_COUNT = Counter("streamguard_anomalies_total", "Total anomalies flagged")
LATENCY = Histogram("streamguard_scoring_latency_seconds", "Scoring latency in seconds")


class SensorReading(BaseModel):
    sensor_id: str
    temperature: float
    vibration: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/score")
def score(reading: SensorReading):
    start = time.time()
    features = feature_store.update_and_extract(
        reading.sensor_id, reading.temperature, reading.vibration
    )
    result = model.score(features)

    REQUEST_COUNT.inc()
    if result["is_anomaly"]:
        ANOMALY_COUNT.inc()
    LATENCY.observe(time.time() - start)

    return {"sensor_id": reading.sensor_id, **result}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
