import requests
import re
import tldextract
from tqdm import tqdm
from multiprocessing import Pool
import subprocess
import os


# Config
ROOT_DOMAIN = "https://www.wikipedia.org/"


def find(string):
    # findall() has been used
    # with valid conditions for urls in string
    url = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", string)
    return url


def root_parser():
    respond = (str(requests.get(ROOT_DOMAIN).content))
    urls = find(respond)
    return urls


def get_content(url):
    try:
        return str(requests.get(url).content)
    except Exception:

        return ""


def regular_parser(url_list):
    url_output_list = []
    for url in tqdm(url_list):
        respond = get_content(url)
        parsed_respond = find(respond)
        if type(parsed_respond) == list and len(parsed_respond) != 0:
            for item in parsed_respond:
                ext = tldextract.extract(item)
                if len(ext.subdomain) == 0:
                    ext_domain = "https://" + ".".join((ext.domain, ext.suffix))
                else:
                    ext_domain = "https://" + ".".join((ext.subdomain, ext.domain, ext.suffix))
                if ext_domain not in url_output_list:
                    url_output_list.append(ext_domain)
        elif type(parsed_respond) == str and len(parsed_respond) != 0:
            ext = tldextract.extract(respond)
            if len(ext.subdomain) == 0:
                ext_domain = "https://" + ".".join((ext.domain, ext.suffix))
            else:
                ext_domain = "https://" + ".".join((ext.subdomain, ext.domain, ext.suffix))
            if ext_domain not in url_output_list:
                url_output_list.append(ext_domain)
    return url_output_list


def check_ping(url_str):
    hostname = url_str[8:]
    status = subprocess.call(
        ['ping', '-n', '1', hostname], stdout=open(os.devnull, 'wb'))
    if status == 0:
        return url_str
    else:
        return None


def main():
    depth0 = root_parser()
    print("Root Layer Done")
    depth1 = regular_parser(depth0)
    print("First Layer Done")
    depth2 = regular_parser(depth1)
    print("Second Layer Done")
    print("Validating URLS....")
    with Pool(10) as pool:
        valid_urls_unfiltered = pool.map(check_ping, depth2)
    valid_urls = list(filter(None, valid_urls_unfiltered))
    print("Done, Writing to Disk")
    with open(r"C:/Users/ooora/Desktop/Crawled_Urls.txt", "w") as text_file:
        text_file.write("")
    with open(r"C:/Users/ooora/Desktop/Crawled_Urls.txt", "a") as text_file:
        text_file.write("{} - Connected Sites Found\n".format(len(valid_urls)))
        for line in valid_urls:
            text_file.write(line + "\n")


if __name__ == "__main__":
    main()
