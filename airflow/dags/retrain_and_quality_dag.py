"""
Hourly DAG that (1) checks pipeline data quality/freshness and (2) retrains
the anomaly model on the most recent data. This is the automated version of
the manual concept-drift monitoring used during the original thesis work.
"""
import sys
from datetime import datetime, timedelta

import numpy as np
import psycopg2
from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.append("/opt/airflow/stream_processor")
from anomaly_model import FEATURE_ORDER, AnomalyModel  # noqa: E402
from feature_engineering import RollingFeatureStore  # noqa: E402

PG_DSN = "dbname=streamguard user=streamguard password=streamguard host=postgres port=5432"

default_args = {
    "owner": "kenil",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


def check_data_quality(**_context) -> None:
    conn = psycopg2.connect(PG_DSN)
    cur = conn.cursor()

    cur.execute("SELECT count(*) FROM raw_events WHERE event_time > now() - interval '1 hour';")
    recent_count = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM raw_events WHERE temperature IS NULL OR vibration IS NULL;")
    null_count = cur.fetchone()[0]

    print(f"Freshness check: {recent_count} rows ingested in the last hour")
    print(f"Null check: {null_count} rows with missing sensor readings")

    if recent_count == 0:
        raise ValueError("No fresh data in the last hour — pipeline may be stalled.")
    if null_count > 0:
        raise ValueError(f"{null_count} rows have null sensor readings.")


def retrain_model(**_context) -> None:
    conn = psycopg2.connect(PG_DSN)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT sensor_id, temperature, vibration
        FROM raw_events
        ORDER BY event_time DESC
        LIMIT 5000;
        """
    )
    rows = cur.fetchall()
    if len(rows) < 100:
        print("Not enough accumulated data to retrain yet — skipping this run.")
        return

    store = RollingFeatureStore(window_size=30)
    feature_rows = []
    for sensor_id, temperature, vibration in reversed(rows):  # chronological order
        features = store.update_and_extract(sensor_id, temperature, vibration)
        feature_rows.append([features[f] for f in FEATURE_ORDER])

    X = np.array(feature_rows)
    model = AnomalyModel()
    model.retrain(X)
    print(f"Retrained IsolationForest on {len(X)} feature vectors -> saved to {model.model_path}")


with DAG(
    dag_id="streamguard_retrain_and_quality",
    default_args=default_args,
    description="Data quality checks + periodic anomaly model retraining for StreamGuard",
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["streamguard", "mlops"],
) as dag:

    quality_check = PythonOperator(
        task_id="check_data_quality",
        python_callable=check_data_quality,
    )

    retrain = PythonOperator(
        task_id="retrain_anomaly_model",
        python_callable=retrain_model,
    )

    quality_check >> retrain
