# Deployment choices and limits

## Verified local deployment

.NET 10 processes on loopback ports 5100–5102 and independent SQLite files. Only the local build and application verification have been executed. `scripts/run.sh` starts and stops the three hosts. Each database persists independently.

## Server deployment

Publish each service (`dotnet publish ... -c Release`) and run under a service manager behind a TLS reverse proxy, exposing only the web portal and an authenticated partner API route. Configure monitoring, secret rotation and backup/restore. Persist ASP.NET Core Data Protection keys with restricted permissions; shared keys are needed if portal replicas share authentication cookies. Replace the fixed demonstration password and tokens with an identity provider before external use. Add per-identity rate limiting and audit retention. `/health` is liveness only: add a database readiness probe for operational deployment.

## Docker Compose

`Dockerfile` builds one selected host and runs as the non-root `app` user. A writable data directory is prepared before switching user. `compose.yaml` creates separate data volumes and connects APIs privately; the portal binds to loopback. Set all required environment values (CUSTOMER_TOKEN, CUSTOMER2_TOKEN, PARTNER_TOKEN, OPERATOR_TOKEN at least 24 characters, plus DEMO_PASSWORD) and run `docker compose up --build`. For the local HTTP example the portal is explicitly Development. Before external deployment use Production behind verified TLS termination and configure forwarded headers for known proxies. Production cookie settings require HTTPS. Pin image digests and scan images in CI. This configuration has been reviewed but not executed here because Docker is unavailable.

## Kubernetes

Use separate Deployments/Services for the stateless API processes only after replacing per-container SQLite with an appropriate shared server database per business service. A Kubernetes replica must never keep an independent copy of the payment ledger. Keep database ownership separate even if both databases share a managed server. Use TLS ingress, secrets, restricted service identities, startup/readiness/liveness probes, resource limits and disruption budgets. Scale payment and usage workloads separately against measured latency and database contention, not an arbitrary replica count. No Kubernetes cluster has been deployed for this project.

## Recovery

Use SQLite's online backup API or stop the relevant writer before copying its data; copying a live db file without its WAL is unsafe. Verify restoration to an isolated environment. Add automated backups, a documented recovery objective and restore drills. Introduce schema migrations before changing deployed schemas. Roll back a service binary only when its database schema is backward compatible.
