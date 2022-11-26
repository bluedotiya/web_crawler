#!/bin/bash
echo "Create Namespace"
kubectl apply -f create-ns.yaml
echo "Delete manager Application"
kubectl delete deployment -n manager manager
echo "Create manager Application"
kubectl apply -n manager -f deployment-file.yaml
echo "Create manager service"
kubectl apply -n manager -f expose-service.yaml

