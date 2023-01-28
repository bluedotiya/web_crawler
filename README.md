[![Docker Build](https://github.com/bluedotiya/web_crawler/actions/workflows/docker-publish-master.yml/badge.svg?branch=master)](https://github.com/bluedotiya/web_crawler/actions/workflows/docker-publish-master.yml)
# Python web crawler
Recursive WebCrawler, Feed it one URL and the crawler will return all the websites that are related to that address at a chosen depth

## Kubernetes Crawler
K8s Flavor of web crawler is custom built to serve as a native k8s app, its provide scalability, stability and high performance.

### Installation prerequisites
1. Apt packages: setfacl, git
2. Kubectl cli
3. Helm cli
4. Single/multi node K8s cluster (tested on Kubeadm)
5. Root access (Duh :))

### How to install
1. Clone this repo using
```
git clone https://github.com/bluedotiya/web_crawler.git
```
2. Change to the new git directory
```
cd web_crawler
```
3. Run bash install & wait for installation to complete
```
bash installer.sh -o install
```
4. Installation complete you should be able to access your neo4j DB.
```
Example: Deployment Done you can connect Neo4j Browser on: http://<YOUR_K8S_NODE_IP_HERE>:30074
Example: Database Port is: 30087
```


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

