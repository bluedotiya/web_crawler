#!/usr/bin/env bash
#
# Local development: build frontend + run manager natively.
# Neo4j stays in minikube; manager connects via port-forward.
#
# Usage:  ./dev.sh
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
NAMESPACE="web-crawler"
NEO4J_SVC="svc/crawler-neo4j-lb-neo4j"
NEO4J_PORT=7687
PIDS=()

cleanup() {
    echo ""
    echo "==> Shutting down..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null
    echo "==> Done."
}
trap cleanup EXIT INT TERM

# --- Fetch Neo4j credentials from k8s secret ---
neo4j_username=$(kubectl get secret neo4j-credentials -n "$NAMESPACE" \
    -o jsonpath='{.data.NEO4J_USERNAME}' | base64 -d)
neo4j_password=$(kubectl get secret neo4j-credentials -n "$NAMESPACE" \
    -o jsonpath='{.data.NEO4J_PASSWORD}' | base64 -d)
echo "==> Neo4j credentials loaded from cluster secret"

# --- Kill stale port-forwards ---
lsof -ti:8080 2>/dev/null | xargs kill 2>/dev/null || true
lsof -ti:$NEO4J_PORT 2>/dev/null | xargs kill 2>/dev/null || true
sleep 0.5

kubectl port-forward -n "$NAMESPACE" "$NEO4J_SVC" "$NEO4J_PORT:$NEO4J_PORT" &
PIDS+=($!)

for i in $(seq 1 10); do
    if nc -z localhost $NEO4J_PORT 2>/dev/null; then
        echo "==> Neo4j reachable at localhost:$NEO4J_PORT"
        break
    fi
    sleep 1
done

# --- Build frontend ---
echo "==> Building frontend..."
cd "$REPO_ROOT/frontend"
npm run build
echo "==> Frontend built ($(du -sh "$REPO_ROOT/frontend/dist" | cut -f1))"

# --- Build manager ---
echo "==> Building manager..."
cd "$REPO_ROOT"
cargo build --package manager

# --- Run manager ---
echo "==> Starting manager..."
NEO4J_DNS_NAME="localhost:$NEO4J_PORT" \
NEO4J_USERNAME="$neo4j_username" \
NEO4J_PASSWORD="$neo4j_password" \
STATIC_DIR="$REPO_ROOT/frontend/dist" \
RUST_LOG="manager=debug,shared=debug" \
    ./target/debug/manager &
PIDS+=($!)

echo ""
echo "==> Local dev environment ready."
echo "    App: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop."
wait
