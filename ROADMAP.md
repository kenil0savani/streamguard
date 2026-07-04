# Phase 2 Roadmap — Production Hardening on Azure

Phase 1 (this repo, as built) proves the pipeline logic end-to-end locally.
Phase 2 takes the same pipeline and makes it match what mid-size German
employers are actually running in production right now (confirmed against
live postings: Azure Databricks-based platforms, Kubernetes deployment,
Infrastructure-as-Code, and pipeline observability). Do this in order —
each step is independently demoable and resume-worthy on its own, so if you
run out of time partway through, you still have something to show.

Suggested pace at 10–15 hrs/week: ~1 week per numbered step below.

## 1. Move storage to Azure

- Provision an **Azure Database for PostgreSQL – Flexible Server** and point
  `PG_DSN` at it instead of the local container.
- Add an **Azure Blob Storage / ADLS Gen2** container as a raw "bronze" data
  lake: have the consumer (or a small scheduled script) periodically dump
  batches of `raw_events` to Parquet files in the lake, in addition to
  Postgres. This is the same medallion pattern (bronze → silver → gold) used
  at companies like Popken Fashion Group's Azure Databricks platform.
- **Resume line:** "Migrated the storage layer to Azure (ADLS Gen2 + Azure
  Database for PostgreSQL), implementing a bronze/silver/gold data lake
  pattern."

## 2. Azure Databricks batch job (optional but high-value)

- Use Databricks Community Edition (free) or an Azure Databricks trial
  workspace.
- Write a PySpark notebook that reads the Parquet files from ADLS Gen2,
  re-runs the same feature engineering logic at scale, and writes a Delta
  table — this demonstrates the exact stack (Databricks + Spark + Delta
  Lake) named explicitly in current German Data Engineer postings.
- **Resume line:** "Built a PySpark batch feature-engineering job on
  Databricks, writing to Delta Lake tables."

## 3. Containerize for Kubernetes

- You already have Dockerfiles for `api` and `airflow`. Push both images to
  **Azure Container Registry (ACR)**.
- Write Kubernetes manifests (`Deployment`, `Service`, and a
  `HorizontalPodAutoscaler` for the API) and deploy to **Azure Kubernetes
  Service (AKS)**. A single-node AKS cluster is enough to demo this.
- **Resume line:** "Containerized and deployed the scoring API to Azure
  Kubernetes Service (AKS) with autoscaling."

## 4. Infrastructure as Code with Terraform

- Write Terraform to provision: Resource Group, ACR, AKS cluster, Azure
  Database for PostgreSQL, and the Storage Account/ADLS Gen2 container.
- Goal: `terraform apply` recreates the entire cloud environment from
  scratch. This is one of the single highest-leverage additions to your CV —
  it directly answers "Infrastructure as Code" line items that show up
  across nearly every mid-to-senior Data Engineer posting.
- **Resume line:** "Provisioned all cloud infrastructure (AKS, ACR, managed
  Postgres, ADLS Gen2) as code using Terraform."

## 5. Monitoring with Prometheus + Grafana

- Add `prometheus` and `grafana` services to a `docker-compose.override.yml`
  (or a K8s equivalent if already on AKS).
- Point Prometheus at the API's existing `/metrics` endpoint.
- Build a Grafana dashboard: request rate, anomaly rate, scoring latency —
  directly extending the "monitoring and alerting" work from the original
  research into a real observability stack.
- **Resume line:** "Instrumented the service with Prometheus metrics and
  built Grafana dashboards for real-time pipeline observability."

## 6. Extend CI/CD

- Add a `deploy` job to `.github/workflows/ci.yml`: on merge to `main`, build
  and push images to ACR, then `kubectl apply` (or `helm upgrade`) against
  AKS.
- Add `terraform plan` as a required check on pull requests that touch the
  `infra/` directory.

## What to skip if time runs out

If 10–15 hrs/week doesn't stretch to all six steps, prioritize in this
order: **1 → 4 → 3 → 5 → 2 → 6**. Terraform (step 4) is disproportionately
valuable per hour invested — it's a small, self-contained addition that
unlocks a strong, distinct CV line ("Infrastructure as Code") independent of
whether steps 2, 3, 5, 6 are finished.
