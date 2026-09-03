# CloudNativePG test cluster

This directory adds a CloudNativePG cluster alongside the existing
`k8s/postgres` Deployment. It does not replace the existing PostgreSQL,
PgBouncer, PVC, Services, or application configuration.

The cluster contains two instances: one primary and one streaming replica.
CloudNativePG creates the following Services automatically:

- `booking-postgres-cluster-rw` routes to the primary;
- `booking-postgres-cluster-ro` routes to replicas;
- `booking-postgres-cluster-r` routes to any instance.

The `poolers.yaml` manifest adds two independent PgBouncer endpoints:

- `booking-pooler-rw` routes to the primary;
- `booking-pooler-ro` routes to replicas.

## 1. Install the operator

Install CloudNativePG once per Kubernetes cluster:

```bash
kubectl apply --server-side \
  -f https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.27/releases/cnpg-1.27.0.yaml

kubectl rollout status deployment/cnpg-controller-manager \
  --namespace cnpg-system \
  --timeout=300s
```

## 2. Create the application database secret

The secret deliberately is not committed to the repository. CloudNativePG
requires a `kubernetes.io/basic-auth` Secret with `username` and `password`
keys. If `booking-secrets` already exists, create the CNPG secret from its
encoded values without printing the password:

```bash
kubectl get secret booking-secrets --namespace booking -o json \
  | jq '{
      apiVersion: "v1",
      kind: "Secret",
      metadata: {
        name: "booking-cnpg-app",
        namespace: "booking"
      },
      type: "kubernetes.io/basic-auth",
      data: {
        username: .data.PG_USER,
        password: .data.PG_PASS
      }
    }' \
  | kubectl apply -f -
```

For a standalone cluster, create it explicitly instead. Use the same
credentials as the backend if the application will later be switched to this
cluster:

```bash
kubectl create secret generic booking-cnpg-app \
  --namespace booking \
  --type=kubernetes.io/basic-auth \
  --from-literal=username=booking_user \
  --from-literal=password='replace-me'
```

## 3. Start the cluster and both Poolers

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres-cluster/

kubectl get clusters.postgresql.cnpg.io --namespace booking
kubectl get pods --namespace booking \
  -l cnpg.io/cluster=booking-postgres-cluster \
  -L cnpg.io/instanceRole
kubectl get services --namespace booking \
  -l cnpg.io/cluster=booking-postgres-cluster
kubectl get poolers --namespace booking
```

Wait until the cluster reports `Cluster in healthy state` and both instances
are ready:

```bash
kubectl wait cluster/booking-postgres-cluster \
  --namespace booking \
  --for=condition=Ready \
  --timeout=300s
```

## 4. Verify primary and replica

Find the pod names and run the following query on each instance:

```bash
kubectl get pods --namespace booking \
  -l cnpg.io/cluster=booking-postgres-cluster \
  -L cnpg.io/instanceRole

kubectl exec --namespace booking <pod-name> -- \
  psql -U postgres -d booking_db -c \
  "select pg_is_in_recovery(), current_setting('transaction_read_only');"
```

Expected results:

- primary: `pg_is_in_recovery = false`, `transaction_read_only = off`;
- replica: `pg_is_in_recovery = true`, `transaction_read_only = on`.

Check streaming replication on the primary:

```bash
kubectl exec --namespace booking <primary-pod-name> -- \
  psql -U postgres -d booking_db -c \
  "select client_addr, state, sync_state from pg_stat_replication;"
```

## 5. Wait for both PgBouncer Poolers

The Pooler resources are applied together with the Cluster. CloudNativePG
reconciles them as the database instances become available. After the Cluster
is ready, wait for the generated PgBouncer Deployments:

```bash
kubectl rollout status deployment/booking-pooler-rw \
  --namespace booking \
  --timeout=300s
kubectl rollout status deployment/booking-pooler-ro \
  --namespace booking \
  --timeout=300s

kubectl get poolers,pods,services --namespace booking
```

## 6. Apply migrations through the new RW Pooler

The migration Job lives in `after-ready`, so the directory-wide apply above
does not start it before PostgreSQL and PgBouncer are ready:

```bash
kubectl apply -f k8s/postgres-cluster/after-ready/migration-job.yaml
kubectl wait job/backend-migrations-cnpg \
  --namespace booking \
  --for=condition=Complete \
  --timeout=600s
kubectl logs job/backend-migrations-cnpg --namespace booking
```

The Job overrides only its own database hosts and does not change
`booking-config` or restart the running backend. It sets both the current
`PG_RW_HOST` and the legacy `PG_HOST`, so a previously built backend image can
still run migrations through the new RW Pooler.

## 7. Switch the application when ready

No application configuration is changed automatically. To bypass PgBouncer
and test direct database connections, use:

```yaml
PG_RW_HOST: booking-postgres-cluster-rw
PG_RO_HOST: booking-postgres-cluster-ro
```

For the intended configuration through the managed PgBouncer instances, use:

```yaml
PG_RW_HOST: booking-pooler-rw
PG_RO_HOST: booking-pooler-ro
```

Apply migrations only through the RW endpoint. Do not point Alembic at the RO
Service or Pooler.

After changing `k8s/configmap.yaml`, apply it and restart only the consumers of
those environment variables:

```bash
kubectl apply -f k8s/configmap.yaml
kubectl rollout restart deployment/backend deployment/worker \
  --namespace booking
kubectl rollout status deployment/backend deployment/worker \
  --namespace booking \
  --timeout=300s
```

Keep the old PostgreSQL and PgBouncer running until command and query paths
have both been verified against the new endpoints.

## Existing installation

The existing manifests remain active and unchanged:

- `k8s/postgres/`;
- `k8s/pgbouncer/`;
- `k8s/configmap.yaml` still points both application pools at `pgbouncer`.

The new cluster starts with an empty `booking_db`. Existing data is not copied
automatically; use a dump/restore migration if it must be preserved.
