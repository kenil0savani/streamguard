"""
Consumes IoT telemetry from Kafka, scores each event for anomalies, and
persists both the raw reading and the anomaly score to PostgreSQL
(bronze + silver tables) for downstream dbt modeling and BI.
"""

import json
import os
import time

import psycopg2
from kafka import KafkaConsumer

from anomaly_model import AnomalyModel
from feature_engineering import RollingFeatureStore

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST_MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "isolation_forest.joblib")

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:19092")
TOPIC = os.getenv("KAFKA_TOPIC", "iot.telemetry")
PG_DSN = os.getenv(
    "PG_DSN",
    "dbname=streamguard user=streamguard password=streamguard host=localhost port=5432",
)


def get_conn(retries: int = 15):
    for attempt in range(retries):
        try:
            return psycopg2.connect(PG_DSN)
        except Exception as exc:  # noqa: BLE001
            print(
                f"Postgres not ready yet ({exc}); retrying in 3s... [{attempt + 1}/{retries}]"
            )
            time.sleep(3)
    raise RuntimeError(f"Could not connect to Postgres using DSN: {PG_DSN}")


def main() -> None:
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id="streamguard-consumer",
    )

    conn = get_conn()
    conn.autocommit = True
    cur = conn.cursor()

    feature_store = RollingFeatureStore(window_size=30)
    model = AnomalyModel(model_path=os.getenv("MODEL_PATH", HOST_MODEL_PATH))

    print(f"Consumer started on topic '{TOPIC}', waiting for messages...")
    message_count = 0
    for message in consumer:
        message_count += 1
        if message_count % 20 == 0:
            if model.reload_if_updated():
                print("Loaded a freshly retrained model from disk.")

        event = message.value
        features = feature_store.update_and_extract(
            event["sensor_id"], event["temperature"], event["vibration"]
        )
        result = model.score(features)

        cur.execute(
            """
            INSERT INTO raw_events (sensor_id, event_time, temperature, vibration, is_synthetic_anomaly)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                event["sensor_id"],
                event["timestamp"],
                event["temperature"],
                event["vibration"],
                event["is_synthetic_anomaly"],
            ),
        )
        cur.execute(
            """
            INSERT INTO scored_events (sensor_id, event_time, anomaly_score, is_anomaly)
            VALUES (%s, %s, %s, %s)
            """,
            (
                event["sensor_id"],
                event["timestamp"],
                result["anomaly_score"],
                result["is_anomaly"],
            ),
        )

        flag = "ANOMALY" if result["is_anomaly"] else "ok"
        print(f"[{event['sensor_id']}] score={result['anomaly_score']:.3f} -> {flag}")


if __name__ == "__main__":
    main()
