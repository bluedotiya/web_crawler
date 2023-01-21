#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

if [ $# -eq 0 ]; then
    >&2 printf "No Arguments provided! \nWebcrawler Neo4j Installer: \nusage: \nscript.sh -o <install/remove>\n"; exit 1
fi

operation='123'

while getopts ":ho:" option; do
   case $option in
      o) operation=$OPTARG;;
      h) printf "Webcrawler Neo4j Installer: \nusage: \nscript.sh -o <install/remove>\n"; exit 1;;
     \?) echo "Error: Invalid option"; exit 1;;
   esac
done

echo $operation

if [[ $operation == "install" ]];then
  kubectl apply -f neo4j/k8s/pvc.yaml
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
  helm install neo4j neo4j/neo4j -f neo4j/k8s/values.yaml
  echo "Deployed neo4j using helm"
  helm install neo4j-expose neo4j/k8s -f neo4j/k8s/values.yaml
  echo "Deployed neo4j Expose (Nodeport expose)"
  echo "Viewing Rollout status"
  kubectl rollout status --watch --timeout=600s statefulset/neo4j
  helm install feeder feeder/k8s/ -f feeder/k8s/values.yaml
  echo "Deployed Feeder via helm"
  helm install manager manager/k8s/ -f manager/k8s/values.yaml
  echo "Deployed Manager via helm"

  printf "Deployment Done you can connect Neo4j Browser on: http://$(hostname):$(kubectl describe svc crawler-neo4j-expose | grep http | grep NodePort | cut -d ' ' -f 20 | cut -d '/' -f 1)\n"
  printf "Database Port is: $(kubectl describe svc crawler-neo4j-expose | grep db-port | grep NodePort | cut -d ' ' -f 20 | cut -d '/' -f 1)\n"
elif [[ $operation == "uninstall" ]];then
  helm uninstall feeder 
  echo "Uninstalled Feeder"
  helm uninstall manager 
  echo "Uninstalled Manager"
  helm uninstall neo4j
  echo "Uninstalled Neo4j"
  helm uninstall neo4j-expose
  echo "Uninstalled Neo4j-expose service"
  kubectl delete pvc data-neo4j-0
  echo "Removed Neo4j PVC"
  kubectl delete pv local-storage-3
  echo "Removed K8S Local PV"
  rm -rf /storage/local-storage-3
  echo "Removed K8S PV Storage on filesystem"
fi