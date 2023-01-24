# Python web crawler
Recursive WebCrawler, Feed it one URL and the crawler will return all the websites that are related to that address at a chosen depth

## Kubernetes Crawler
K8s Flavor of web crawler is custom built to serve as a native k8s app, its provide scalability, stability and high performance.

### Installation prerequisites
1. Apt package: setfacl
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


## Legacy crawler
### How to use
1. Pull the latest image with:
```
docker pull ghcr.io/bluedotiya/web_crawler/legacy_crawler:master
```
2. Run the container with:
```
docker run --env URL='<INSERT_URL_HERE>' --env DEPTH='<INSERT_WANTED_DEPTH>' -v $(pwd)/output:/app/output ghcr.io/bluedotiya/web_crawler/legacy_crawler:master 
```

Example Run:
```
docker run --env URL='https://facebook.com' --env DEPTH='2' -v $(pwd)/output:/app/output ghcr.io/bluedotiya/web_crawler/legacy_crawler:master
```

### Output folder structure

```
Output
|
|- Depth1
|  |- Parent1
|     |- Child_Urls_1.txt
|     |- Parent_Url_1.txt
|
|- Depth2
   |- Parent2
   |  |- Child_Urls_2.txt
   |  |- Parent_Url_2.txt
   |
   |- Parent3
      |- Child_Urls_3.txt
      |- Parent_Url_2.txt
```
TXT File Format:
```
Parent_URL.txt format: <parent url value>
                       <request time>

Child_URL.txt format: <URL1>
                      <URL2>
                      <URL3>
                      .....
```
Matplot Visualizer:

![image](https://user-images.githubusercontent.com/75704012/205511336-4a0af7d1-4b8a-4753-863a-4839a46966fe.png)

