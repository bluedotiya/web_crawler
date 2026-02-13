#!/usr/bin/env bash
#
# Integration test: build Docker image, deploy to minikube, verify pods are healthy.
# Called automatically by the pre-commit hook after unit tests pass.
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
IMAGE="ghcr.io/bluedotiya/web_crawler/feeder"
TAG="rust"
NAMESPACE="web-crawler"
RELEASE="web-crawler"
CHART="$REPO_ROOT/web-crawler"

echo "==> Building Docker image $IMAGE:$TAG..."
docker build -q -t "$IMAGE:$TAG" "$REPO_ROOT/feeder"

echo "==> Loading image into minikube..."
minikube image load "$IMAGE:$TAG"

echo "==> Building Helm dependencies..."
helm dependency build "$CHART" 2>/dev/null

echo "==> Upgrading Helm release..."
helm upgrade "$RELEASE" "$CHART" \
    -n "$NAMESPACE" \
    -f "$CHART/values.yaml" \
    -f "$CHART/local-values.yaml"

echo "==> Waiting for rollout..."
kubectl rollout status deployment/feeder -n "$NAMESPACE" --timeout=120s

echo "==> Verifying pods are running..."
NOT_RUNNING=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=feeder \
    --no-headers | grep -cv "Running" || true)

if [ "$NOT_RUNNING" -ne 0 ]; then
    echo ""
    echo "INTEGRATION TEST FAILED: some feeder pods are not Running."
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=feeder
    exit 1
fi

echo "==> Integration test passed. All feeder pods are Running."
kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=feeder
