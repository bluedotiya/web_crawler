#!/bin/bash

set -e

values_file_name=''

if [[ "$1" == "prod" ]]; then
    values_file_name='values.yaml'
else
    values_file_name='dev_values.yaml'
    for app in "feeder" "manager"; do
    echo "------------------------------ Building $app ------------------------------"
    docker build . -t $app:dev -f $app/docker/Dockerfile
    echo "------------------------------ Build Done ------------------------------"
done
fi

echo $values_file_name

# Uninstall & Install feeder app
helm uninstall feeder feeder/k8s/ | $true
helm install feeder feeder/k8s/ -f feeder/k8s/$values_file_name
echo "---"

# Uninstall & Install manager app
helm uninstall manager manager/k8s/ | $true
helm install manager manager/k8s/ -f manager/k8s/$values_file_name
echo "---"
