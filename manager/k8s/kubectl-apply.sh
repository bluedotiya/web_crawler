#!/bin/bash
echo "Create Namespace"
kubectl apply -f create-ns.yaml
echo "Delete manager Application"
kubectl delete deployment manager
echo "Create manager Application"
kubectl apply -f deployment-file.yaml
echo "Create manager service"
kubectl apply -f expose-service.yaml

