#!/usr/bin/env bash
#
# Integration test: build Docker images, deploy to minikube, verify pods are healthy.
# Called automatically by the pre-commit hook after unit tests pass.
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
NAMESPACE="web-crawler"
RELEASE="web-crawler"
CHART="$REPO_ROOT/web-crawler"

FEEDER_IMAGE="ghcr.io/bluedotiya/web_crawler/feeder"
MANAGER_IMAGE="ghcr.io/bluedotiya/web_crawler/manager"
TAG="latest"

echo "==> Building Docker image $FEEDER_IMAGE:$TAG..."
docker build -q -t "$FEEDER_IMAGE:$TAG" -f "$REPO_ROOT/feeder/Dockerfile" "$REPO_ROOT"

echo "==> Building Docker image $MANAGER_IMAGE:$TAG..."
docker build -q -t "$MANAGER_IMAGE:$TAG" -f "$REPO_ROOT/manager/Dockerfile" "$REPO_ROOT"

echo "==> Loading images into minikube..."
minikube image load "$FEEDER_IMAGE:$TAG"
minikube image load "$MANAGER_IMAGE:$TAG"

echo "==> Building Helm dependencies..."
helm dependency build "$CHART" 2>/dev/null

echo "==> Upgrading Helm release..."
helm upgrade "$RELEASE" "$CHART" \
    -n "$NAMESPACE" \
    -f "$CHART/values.yaml" \
    -f "$CHART/local-values.yaml"

echo "==> Waiting for rollout..."
kubectl rollout status deployment/feeder -n "$NAMESPACE" --timeout=120s
kubectl rollout status deployment/manager -n "$NAMESPACE" --timeout=120s

echo "==> Verifying pods are running..."
NOT_RUNNING=$(kubectl get pods -n "$NAMESPACE" \
    -l 'app.kubernetes.io/name in (feeder,manager)' \
    --no-headers | grep -v "Terminating" | grep -cv "Running" || true)

if [ "$NOT_RUNNING" -ne 0 ]; then
    echo ""
    echo "INTEGRATION TEST FAILED: some pods are not Running."
    kubectl get pods -n "$NAMESPACE" -l 'app.kubernetes.io/name in (feeder,manager)'
    exit 1
fi

echo "==> Integration test passed. All pods are Running."
kubectl get pods -n "$NAMESPACE" -l 'app.kubernetes.io/name in (feeder,manager)'
