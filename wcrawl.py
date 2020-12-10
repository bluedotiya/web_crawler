import requests

# Config
ROOT_DOMAINS = ["www.google.com", "www.youtube.com"]
CRAWL_DEPTH = []


def main():
    for domain in ROOT_DOMAINS:
        respond = requests.get("https://" + domain).content.split()
        for item in respond:
            if bytes("http://", "utf-8") or bytes("https://", "utf-8") in item:
                print(item)


if __name__ == "__main__":
    main()
