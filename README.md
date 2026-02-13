[![Release & Publish](https://github.com/bluedotiya/web_crawler/actions/workflows/docker-publish-master.yml/badge.svg?branch=master)](https://github.com/bluedotiya/web_crawler/actions/workflows/docker-publish-master.yml)
[![PR Title Check](https://github.com/bluedotiya/web_crawler/actions/workflows/pr-title.yml/badge.svg)](https://github.com/bluedotiya/web_crawler/actions/workflows/pr-title.yml)

# Web Crawler

Recursive web crawler built in Rust. Feed it one URL and the crawler will map all related websites at a chosen depth, storing the graph in Neo4j.

## Architecture

```
                    ┌──────────┐
  POST /  ────────► │ Manager  │ ──── Creates ROOT + child URL nodes
                    └──────────┘
                         │
                      Neo4j DB
                         │
                    ┌──────────┐
                    │ Feeder   │ ──── Picks up PENDING URLs, crawls, creates children
                    │ (x8)     │
                    └──────────┘
```

**Rust workspace** with three crates:
- `shared/` — common library (crawler, DNS, Neo4j client, URL normalization)
- `manager/` — HTTP API (Axum) that accepts crawl requests
- `feeder/` — worker loop that processes pending URLs

## Quick Start

### Prerequisites
- kubectl, Helm 3.x
- Kubernetes cluster (minikube, EKS, GKE, etc.)

### Install

```bash
git clone https://github.com/bluedotiya/web_crawler.git
cd web_crawler

helm repo add neo4j https://helm.neo4j.com/neo4j
helm repo update

cd web-crawler
helm dependency update
helm install web-crawler . -f values.yaml -n web-crawler --create-namespace
```

### Wait for readiness

```bash
kubectl rollout status statefulset/crawler-neo4j -n web-crawler
kubectl get pods -n web-crawler -l app.kubernetes.io/instance=web-crawler
```

### Access services

```
Neo4j Browser:  http://<NODE_IP>:30074
Neo4j Bolt:     bolt://<NODE_IP>:30087
Manager API:    http://<NODE_IP>:30080
```

### Start a crawl

```bash
curl -X POST http://<NODE_IP>:30080 \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://www.example.com","depth":2}'
```

## Development

### Local dev loop

```bash
# Run unit tests and clippy
cargo test --workspace
cargo clippy --workspace -- -D warnings

# Full integration test (builds Docker images, deploys to minikube, verifies pods)
./dev.sh
```

### Pre-commit hooks

Configured via `.pre-commit-config.yaml`:
- `cargo check --workspace`
- `cargo clippy --workspace -- -D warnings`
- `cargo test --workspace`
- Integration test (`dev.sh`) — runs on changes to `shared/`, `feeder/`, or `manager/`

## CI/CD & Versioning

### Automatic semantic versioning

Every merge to `master` automatically:
1. Calculates the next version for each service based on conventional commits
2. Creates git tags (`feeder/v1.2.0`, `manager/v1.1.0`, `chart/v1.0.3`)
3. Builds and pushes Docker images to GHCR with both semver and `latest` tags
4. Packages and publishes the Helm chart to GHCR OCI registry

Services are versioned independently — only services with relevant file changes get a new release. Changes to `shared/` trigger releases for both `feeder` and `manager`.

### Conventional commits

PR titles **must** follow [conventional commit](https://www.conventionalcommits.org/) format (enforced by CI):

| Prefix | Version bump | Example |
|--------|-------------|---------|
| `feat:` | Minor (1.0.0 → 1.1.0) | `feat: add health endpoint` |
| `fix:` | Patch (1.0.0 → 1.0.1) | `fix: handle DNS timeout` |
| `feat!:` | Major (1.0.0 → 2.0.0) | `feat!: redesign API` |
| `chore:`, `docs:`, `refactor:`, etc. | Patch | `chore: update dependencies` |

### Docker images

```
ghcr.io/bluedotiya/web_crawler/feeder:latest
ghcr.io/bluedotiya/web_crawler/feeder:1.0.0
ghcr.io/bluedotiya/web_crawler/manager:latest
ghcr.io/bluedotiya/web_crawler/manager:1.0.0
```

### Helm chart

```bash
# Install from GHCR OCI registry
helm install web-crawler oci://ghcr.io/bluedotiya/web_crawler/charts/web-crawler --version 1.0.0
```

## Configuration

Customize via `web-crawler/values.yaml` or `--set` flags:

```bash
helm install web-crawler ./web-crawler -n web-crawler --create-namespace \
  --set feeder.replicaCount=16 \
  --set neo4j.neo4j.password=SecurePassword123
```

## Visualization

Use Neo4j Desktop with GraphXR for the best graph viewing experience:

![GraphXR Visualization](https://user-images.githubusercontent.com/75704012/214429032-f19d2bb0-e09b-470e-94b2-faa925c3be59.png)
