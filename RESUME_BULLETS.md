# Resume & LinkedIn Copy

Use these once the corresponding phase is actually built and pushed —
don't claim a step you haven't finished. Swap in real numbers from your own
run (anomaly rate detected vs. the ~3% injected rate, actual latency from
`/metrics`, etc.) instead of the placeholders.

## Resume — Projects section (Phase 1 complete)

**StreamGuard — Real-Time IoT Anomaly Detection Platform** | [github.com/kenil0savani/streamguard]
- Built an end-to-end streaming pipeline (Kafka, Python) that ingests IoT
  sensor telemetry and scores it for anomalies in real time using a
  self-supervised IsolationForest model.
- Orchestrated hourly data-quality checks and automated model retraining
  with Apache Airflow, keeping detection stable as sensor behaviour drifts.
- Modeled raw events into analytics-ready fact and aggregate tables with
  dbt, enforcing schema tests for data quality.
- Served real-time anomaly scores via a FastAPI REST endpoint with
  Prometheus metrics; containerized the full stack with Docker Compose and
  automated testing with GitHub Actions CI.

## Resume — Projects section (after Phase 2 / Azure + K8s + Terraform)

**StreamGuard — Real-Time IoT Anomaly Detection Platform** | [github.com/kenil0savani/streamguard]
- Designed and deployed a production-shaped streaming data platform (Kafka,
  Airflow, dbt) on Azure, using a bronze/silver/gold lakehouse pattern on
  ADLS Gen2 and Azure Database for PostgreSQL.
- Provisioned all cloud infrastructure as code with Terraform (AKS, ACR,
  managed Postgres, storage) and deployed the scoring API to Azure
  Kubernetes Service with autoscaling.
- Built Prometheus/Grafana observability for pipeline health, anomaly rate,
  and scoring latency; extended CI/CD to automate image builds and
  deployments on every merge.

## LinkedIn "Featured" project description

Extended my M.Sc. thesis research (self-supervised anomaly detection on
streaming IoT data at Fraunhofer ISST) into a production-shaped data
platform: Kafka → feature engineering → anomaly scoring → dbt → Airflow →
FastAPI, running on Azure with Kubernetes, Terraform, and Grafana
monitoring. Full write-up and code: [link]

## GitHub README tips

- Keep the architecture diagram at the top of the README (already included).
- Add a short GIF or screenshot of the Airflow UI showing a successful DAG
  run, and one of the Grafana dashboard once Phase 2 is live — recruiters
  and hiring managers skim, they rarely run the code themselves.
- Pin this repo on your GitHub profile.
- Link it from your LinkedIn "Featured" section, not just your profile
  "Projects" list — Featured items get shown to profile visitors by default.
