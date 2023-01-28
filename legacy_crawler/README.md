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
