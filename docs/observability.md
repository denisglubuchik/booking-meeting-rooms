# Observability

## Current data path

The API and worker send traces, metrics, and logs over OTLP/gRPC to the
OpenTelemetry Collector:

```text
backend / worker -> otel-collector:4317
                         |-> Tempo       (traces)
                         |-> Prometheus  (metrics)
                         `-> Loki        (logs)
                                  |
                               Grafana

CloudNativePG instances and their managed PgBouncer Poolers expose native
Prometheus endpoints and are scraped directly:

```text
PostgreSQL primary / replica :9187 --\
                                      -> Prometheus -> Grafana
PgBouncer RW / RO           :9127 --/
```
```

Useful checks:

```bash
docker compose config --quiet
docker compose up -d otel-collector
docker compose logs -f otel-collector
```

Grafana is available at `http://127.0.0.1:3000`. The default local credentials
are `admin` / `admin`; set `GRAFANA_ADMIN_USER` and `GRAFANA_ADMIN_PASSWORD` in
the root `.env` before using the production Compose file outside a workstation.

The Collector health endpoint is available only inside the production Compose
network at `http://otel-collector:13133/`. The development Compose file also
publishes it to `http://127.0.0.1:13133/`. It also publishes OTLP/gRPC on port
4317 and OTLP/HTTP on port 4318 for local tools and other clients.

## Backend decision

For this project, the most practical open-source baseline is:

| Signal | Backend | Why |
| --- | --- | --- |
| Traces | Grafana Tempo | Native distributed trace storage and Grafana integration |
| Metrics | Prometheus | Straightforward alerting and a mature query ecosystem |
| Logs | Grafana Loki | Lower operational overhead than a full-text search stack for structured application logs |
| UI | Grafana | One place to correlate all three signals |

For local development and a demo, `grafana/otel-lgtm` can provide the whole
stack in one container. It is convenient for development, but separate services
or a managed observability platform are a better production boundary.

Before adding backends, decide:

1. Required retention for traces, metrics, and logs.
2. Expected traffic and acceptable disk usage.
3. Whether production telemetry may leave the infrastructure.
4. Which alerts and service-level indicators are actually needed.
5. Whether high-cardinality or sensitive attributes must be filtered in the
   Collector.

The Compose stack persists all backend data in named volumes. Current retention
is 7 days for Tempo and Loki and 15 days for Prometheus.

## Kubernetes

The Kubernetes resources live in `k8s/observability/` and are assembled with
Kustomize. They use the existing `booking` namespace and its default-deny
NetworkPolicy.

Backend configuration files live in `k8s/observability/configs/` and are the
single source used by both Kubernetes and Docker Compose. Kustomize generates
content-hashed ConfigMaps from those files, so a configuration change updates
the pod template reference and triggers a rollout.

Before applying them, add `GRAFANA_ADMIN_USER` and `GRAFANA_ADMIN_PASSWORD` to
the existing `booking-secrets` Secret. Then deploy the application ConfigMap,
updated backend policies, and the observability stack:

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/backend/network-policy.yaml
kubectl apply -k k8s/observability
kubectl rollout restart deployment/backend deployment/worker -n booking
```

Grafana automatically provisions two dashboards in the `Booking` folder:

- `Booking overview` contains request rate, error rate, p95 latency, breakdowns
  by operation, traces, and application logs;
- `PostgreSQL CQRS` compares primary and replica load, replication lag, WAL,
  database connections, transaction and row-read rates, buffer cache, and the
  RW/RO PgBouncer pools.

Their sources are `k8s/observability/dashboards/booking-overview.json` and
`k8s/observability/dashboards/postgres-cqrs.json`.

The standalone Prometheus uses Kubernetes pod discovery for CloudNativePG. Its
namespace-scoped ServiceAccount can only list and watch Pods in `booking`.

The stateful services are intentionally single-replica Deployments with
`ReadWriteOnce` volumes of 500 MiB each. This is appropriate for a small
installation, not a highly available production topology.
