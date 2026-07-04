# StreamGuard — Real-Time IoT Anomaly Detection & Analytics Platform

End-to-end data platform that ingests streaming IoT sensor data, scores it for
anomalies in real time, orchestrates periodic retraining and data-quality
checks, models the results into analytics-ready tables, and serves scores
over a REST API — with monitoring, tests, and CI baked in.

This is a production-shaped extension of self-supervised anomaly detection
research on streaming IoT data (originally explored in an M.Sc. thesis at
Fraunhofer ISST), rebuilt around a modern data engineering stack.

## Architecture (Phase 1 — this repo)

```
IoT sensors (simulated)
        │  JSON events
        ▼
   Kafka / Redpanda  ──topic: iot.telemetry──┐
        │                                     │
        ▼                                     │
  Stream Consumer                             │
  (feature engineering + IsolationForest)     │
        │                                     │
        ▼                                     │
   PostgreSQL  ◄── raw_events / scored_events │
        │                                     │
        ▼                                     │
   dbt (staging → marts)                      │
   fct_anomaly_events, agg_hourly_anomaly_rate│
        │                                     │
        ▼                                     │
   Apache Airflow                             │
   hourly: data-quality checks + retrain      │
                                               │
   FastAPI  ◄── on-demand /score endpoint ────┘
   /metrics (Prometheus format)
```

See `ROADMAP.md` for Phase 2 (Azure, Kubernetes, Terraform, Grafana).

## Stack

| Layer | Tool |
|---|---|
| Ingestion | Kafka-API compatible broker (Redpanda) |
| Stream processing | Python (kafka-python, scikit-learn IsolationForest) |
| Storage | PostgreSQL |
| Transformation | dbt-core |
| Orchestration | Apache Airflow |
| Serving | FastAPI |
| Testing | pytest, dbt tests |
| CI | GitHub Actions |

## Prerequisites

- Docker Desktop
- Python 3.11+ (for running the producer/tests locally, outside containers)
- VS Code (recommended: Docker + Python extensions)

## Quickstart

```bash
git clone <your-repo-url> streamguard
cd streamguard
cp .env.example .env

# 1. Start the core stack: broker, database, orchestrator, API
docker compose up -d redpanda postgres airflow api

# 2. Install local Python deps (for producer/consumer/tests on host)
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Start the IoT data simulator (Terminal 1)
python data_simulator/producer.py

# 4. Start the stream consumer (Terminal 2)
cd stream_processor && python consumer.py

# 5. Run dbt transformations on demand
docker compose run --rm dbt run
docker compose run --rm dbt test

# 6. Trigger the Airflow DAG manually (or wait for the hourly schedule)
# Airflow UI: http://localhost:8080  (user: admin / pass: admin)
```

## Try the live scoring API

```bash
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{"sensor_id": "sensor_01", "temperature": 95.4, "vibration": 3.2}'

# Prometheus metrics
curl http://localhost:8000/metrics
```

## Expected results

- The producer injects synthetic anomalies (temperature spikes / vibration
  surges) roughly 3% of the time. Ground truth is stored in
  `raw_events.is_synthetic_anomaly` for offline evaluation only — the model
  never sees this label.
- After a few minutes of streaming, query `analytics.agg_hourly_anomaly_rate`
  (built by dbt) to see anomaly rate per sensor per hour and compare it
  against the injected 3% rate — this is your model-quality sanity check,
  mirroring how a real anomaly-detection system is monitored in production.
- The Airflow DAG retrains the IsolationForest hourly on the last 5,000
  events and fails the run (visible in the Airflow UI) if data freshness or
  null checks fail — this is the "kept it stable as the data changed"
  behaviour from the original thesis work, now automated instead of manual.

## Repository layout

```
data_simulator/     synthetic IoT sensor event generator → Kafka
stream_processor/   feature engineering + anomaly model + Kafka consumer
airflow/dags/       hourly data-quality + retraining DAG
dbt_project/        staging + marts models, schema tests
api/                FastAPI real-time scoring service
sql/                Postgres schema (bronze/silver tables)
tests/              pytest unit tests
.github/workflows/  CI: lint, test, build
ROADMAP.md          Phase 2 plan: Azure, Kubernetes, Terraform, Grafana
RESUME_BULLETS.md   suggested CV / LinkedIn copy once this is deployed
```
