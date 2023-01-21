#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

kubectl apply -f pvc.yaml
echo "Local storage created"

mkdir -p /storage/local-storage-3
chgrp -R 7474 /storage/local-storage-3
chmod -R g+rwx /storage/local-storage-3
chmod g+s /storage/local-storage-3
setfacl -d -m g:7474:rwx /storage/local-storage-3
echo "Configured Permission for local storage directory"

helm repo add neo4j https://helm.neo4j.com/neo4j
echo "Added neo4j helm repo"

helm repo update
echo "Helm repo updated"

kubectl create namespace neo4j
echo "Created neo4j Namespace"

# kubectl config set-context --current --namespace=neo4j
# echo "Switched to neo4j context"

helm install neo4j neo4j/neo4j -f values.yaml
echo "Deployed neo4j using helm"

helm install neo4j-expose . -f values.yaml
echo "Deployed neo4j Expose (Nodeport expose)"