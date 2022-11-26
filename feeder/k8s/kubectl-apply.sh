#!/bin/bash
echo "Create Namespace"
kubectl apply -f create-ns.yaml
sleep 3
echo "Delete Feeder Application"
kubectl delete -n feeder deployment feeder
sleep 3
echo "Create Feeder Application"
kubectl apply -n feeder -f deployment-file.yaml
sleep 3
echo "Create Feeder service"
kubectl apply -n feeder -f expose-service.yaml
sleep 3

