#!/bin/bash

# Uninstall & Install feeder app
helm uninstall feeder feeder/k8s/
helm install feeder feeder/k8s/

# Uninstall & Install manager app
helm uninstall manager manager/k8s/
helm install manager manager/k8s/

# Uninstall & Install memgraphDB app
helm uninstall memgraph memgraph/k8s/
helm install memgraph memgraph/k8s/

# Uninstall & Install memgraph-lab (VNC)
helm uninstall memgraph-lab memgraph-lab/k8s/
helm install memgraph-lab memgraph-lab/k8s/

