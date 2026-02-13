[![Docker Build](https://github.com/bluedotiya/web_crawler/actions/workflows/docker-publish-master.yml/badge.svg?branch=master)](https://github.com/bluedotiya/web_crawler/actions/workflows/docker-publish-master.yml)
# Python web crawler
Recursive WebCrawler, Feed it one URL and the crawler will return all the websites that are related to that address at a chosen depth

## Kubernetes Crawler
K8s Flavor of web crawler is custom built to serve as a native k8s app, providing scalability, stability and high performance.

### Installation prerequisites
1. Kubectl CLI
2. Helm 3.x CLI
3. Kubernetes cluster (tested on Kubeadm, works on any K8s cluster)
4. StorageClass available in cluster (or configure static storage)

### How to install

1. Clone this repository
```bash
git clone https://github.com/bluedotiya/web_crawler.git
cd web_crawler
```

2. Add Neo4j Helm repository
```bash
helm repo add neo4j https://helm.neo4j.com/neo4j
helm repo update
```

3. Install dependencies and deploy
```bash
cd web-crawler
helm dependency update
helm install web-crawler . -f values.yaml -n web-crawler --create-namespace
```

4. Wait for all components to be ready
```bash
kubectl rollout status statefulset/crawler-neo4j -n web-crawler
kubectl get pods -n web-crawler -l app.kubernetes.io/instance=web-crawler
```

5. Access your services
```
Neo4j Browser: http://<K8S_NODE_IP>:30074
Neo4j Database: bolt://<K8S_NODE_IP>:30087
Manager API: http://<K8S_NODE_IP>:30080
```

**Get your node IP:**
```bash
kubectl get nodes -o wide
```

### Configuration

You can customize the deployment by editing `web-crawler/values.yaml` or using `--set` flags:

```bash
# Change feeder replica count
helm install web-crawler ./web-crawler -n web-crawler --create-namespace \
  --set feeder.replicaCount=16

# Use specific StorageClass
helm install web-crawler ./web-crawler -n web-crawler --create-namespace \
  --set neo4j.volumes.data.dynamic.storageClassName=fast-ssd

# Change Neo4j password
helm install web-crawler ./web-crawler -n web-crawler --create-namespace \
  --set neo4j.neo4j.password=SecurePassword123
```

### Upgrade

```bash
helm upgrade web-crawler ./web-crawler -n web-crawler -f values.yaml
```

### Uninstall

```bash
helm uninstall web-crawler -n web-crawler
# Optionally delete the namespace
kubectl delete namespace web-crawler
```

### Legacy Installation (deprecated)

For the old bash script installation method, see [legacy installation guide](legacy_crawler/README.md).
Note: The legacy installer.sh requires root access and manual storage configuration.


### How to use
1. To init a search run the following query (you can replace url & depth values to your own)
```
curl -X POST http://<YOUR_K8S_NODE_IP_HERE>:30080 -H 'Content-Type: application/json' -d '{"url":"https://www.google.com","depth":2}'
```
2. You can now see your data from the native neo4j browser or your favorite Neo4j DB Viewer app

### Recommendation
Use Neo4j Desktop app along side GraphXR for the best graph viewing and search experience

GraphXR Visualization:
![image](https://user-images.githubusercontent.com/75704012/214429032-f19d2bb0-e09b-470e-94b2-faa925c3be59.png)

