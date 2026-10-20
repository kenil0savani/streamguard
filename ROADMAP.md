# Roadmap

An honest account of what runs today, what is written but not currently deployed, and what would come next.

---

## Phase 1 — Complete and running locally

The whole pipeline runs from a single `docker compose up`.

- **Ingestion.** Simulated IoT fleet publishing telemetry to a Kafka-API broker (Redpanda), with synthetic faults injected at a configurable rate.
- **Stream processing.** Python consumer maintaining a 30-event rolling feature window per sensor, scoring each event with an IsolationForest and writing both raw and scored events to PostgreSQL.
- **Analytics modelling.** dbt project with two staging views and two marts tables, deriving per-sensor, per-hour precision and recall from a join between predictions and ground truth. 29 tests passing.
- **Orchestration.** Airflow DAG running hourly, checking data freshness and nulls before retraining the model on the most recent 5,000 events, and failing the run if the checks do not pass.
- **Serving.** FastAPI exposing `/health`, `/score` and `/metrics`.
- **Monitoring.** Prometheus scraping the API every 15 seconds, Grafana rendering request rate, anomaly rate, latency and flagged share. Datasource provisioned from code, dashboard definition version-controlled.
- **Quality gates.** pytest unit tests, ruff linting and a Docker image build running on every push via GitHub Actions.

---

## Phase 2 — Written, previously deployed, not currently running

**Terraform for Azure** lives in `infra/`. It provisions a resource group, an Azure Container Registry and a PostgreSQL Flexible Server. This was applied against a live Azure subscription during development and subsequently torn down with `terraform destroy`, so no cloud resources exist today.

Anyone re-applying it should first change `sku_name` on the PostgreSQL server from `GP_Standard_D2s_v3` to a Burstable tier such as `B_Standard_B1ms`. The General Purpose tier is considerably more expensive and offers nothing useful for a demonstration workload.

**Kubernetes manifests** live in `k8s/`, covering a deployment for the API and a monitoring configuration. These were authored against the intended cloud topology but have never been applied, because no cluster was provisioned. They should be treated as a design artefact rather than as tested code.

Completing this phase means provisioning AKS, pushing the API image to the container registry, applying the manifests and restoring the deployment job in CI. That job previously existed in the workflow and was removed, since a pipeline step that can only ever fail is worse than no step at all.

---

## Phase 3 — Model improvements

Ordered by expected benefit relative to effort.

**Feature scaling.** Fit a `StandardScaler` alongside the IsolationForest and persist both together. The eight features currently span very different ranges, so the larger ones dominate the splits. This also repairs the startup bootstrap, which currently fits on standard normal noise that bears no resemblance to real feature values.

**Seed the API feature window from PostgreSQL.** On startup, load the most recent readings per sensor so the rolling statistics are warm immediately. This removes the cold-start behaviour described in the README.

**Replace fixed contamination with a tuned threshold.** `anomaly_score` is already persisted for every event, so a threshold sweep against the stored ground truth would give a precision and recall curve and allow the operating point to be chosen deliberately rather than inherited from a default.

**Per-sensor thresholds.** Detection quality currently varies noticeably between sensors. Calibrating per sensor rather than globally would narrow that spread.

**Evaluate on a public real-world dataset.** Performance on injected synthetic faults sets an optimistic upper bound. A benchmark such as NAB or SKAB would give a more honest picture.

---

## Phase 4 — Operational maturity

- Alerting rules in Prometheus, firing when the flagged share drifts away from the expected rate for a sustained period.
- Model versioning and metric tracking across retraining runs, so performance regressions are visible rather than silent.
- Automatic rollback when a retrained model scores worse than the one it replaces.
- Report model-load status through `/health` so orchestration can detect a service that is running but not functional.
- Backfill support in the dbt models, so historical windows can be recomputed after a logic change.
