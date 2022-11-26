#!/bin/bash
echo "Create Namespace"
kubectl apply -f create-ns.yaml
echo "Delete Feeder Application"
kubectl delete -n feeder deployment feeder
echo "Create Feeder Application"
kubectl apply -n feeder -f deployment-file.yaml
echo "Create Feeder service"
kubectl apply -n feeder -f expose-service.yaml

