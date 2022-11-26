#!/bin/bash
echo "Create Namespace"
kubectl apply -f create-ns.yaml
sleep 3
echo "Create Storage class"
kubectl apply -f sc.yaml
sleep 3
echo "Create persistent Volume"
kubectl apply -f pv.yaml
sleep 3
echo "Create the ConfigMap"
kubectl apply -n redis -f redis-config.yaml
sleep 3
echo "Deploy Redis Using StatefulSet"
kubectl apply -n redis -f redis-statefulset.yaml
sleep 3
echo "Create Headless Service"
kubectl apply -n redis -f redis-service.yaml