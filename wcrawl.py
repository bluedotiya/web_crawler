import requests
import re
import tldextract
from multiprocessing import Pool
import subprocess
import os
import time


# Config
ROOT_DOMAIN = "https://www.google.com"
WELL_KNOWN = ["google", "amazon", "facebook", "youtube", "twitter", "linkedin", "wikipedia", "instagram", "cloudflare"]


def find(string):
    # findall() has been used
    # with valid conditions for urls in string
    urls = re.findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", string)
    return urls


def root_crawler():
    respond = (str(requests.get(ROOT_DOMAIN).content))
    urls = find(respond)
    return urls


def get_content(url):
    try:
        return str(requests.get(url).content)
    except Exception:
        return ""


def is_known(url_arg):
    for known_domain in WELL_KNOWN:
        if known_domain in url_arg:
            return True
    return False


def regular_crawler(url_list):
    url_output_list = []
    print("Crawl Website Count: {} ".format(url_list.__len__()))
    for url in url_list:
        respond = get_content(url)
        parsed_respond = find(respond)
        if type(parsed_respond) == list and len(parsed_respond) != 0:
            for item in parsed_respond:
                if "https://" in item:
                    url_prefix = "https://"
                else:
                    url_prefix = "http://"
                ext = tldextract.extract(item)
                if len(ext.subdomain) == 0:
                    ext_domain = url_prefix + ".".join((ext.domain, ext.suffix))
                else:
                    ext_domain = url_prefix + ".".join((ext.subdomain, ext.domain, ext.suffix))
                if (ext_domain not in url_output_list) and (not is_known(ext_domain)):
                    url_output_list.append(ext_domain)
    return url_output_list


def check_ping(url_str):
    if "http://" in url_str:
        hostname = url_str[7:]
    else:
        hostname = url_str[8:]
    if os.name == 'nt':
        count_char = '-n'
    else:
        count_char = '-c'
    status = subprocess.call(
        ['ping', count_char, '1', hostname], stdout=open(os.devnull, 'wb'))
    if status == 0:
        return url_str
    else:
        return None


def crawl_depth(int_depth):
    print("\nRoot Layer Started: ")
    depth0 = root_crawler()
    print("Root Layer Done")
    for level in list(range(int_depth)):
        if level == 0:
            print("\n1 Layer Started: ")
            output = regular_crawler(depth0)
            print("1 Layer Done")
        print("\n{} Layer Started: ".format(level + 2))
        output = regular_crawler(output)
        print("{} Layer Done".format(level + 2))
        time.sleep(2)
    return output


def main():
    final_url_list = crawl_depth(1)
    print("Validating URLS....")
    with Pool(10) as pool:
        valid_urls_unfiltered = pool.map(check_ping, final_url_list)
    valid_urls = list(filter(None, valid_urls_unfiltered))
    print("{} - Connected Sites Found\n".format(len(valid_urls)))
    print("Done, Writing to Disk")
    time.sleep(2)
    with open(r"./Crawled_Urls.txt", "w") as text_file:
        text_file.write("")
    with open(r"./Crawled_Urls.txt", "a") as text_file:
        text_file.write("{} - Connected Sites Found\n".format(len(valid_urls)))
        for line in valid_urls:
            text_file.write(line + "\n")


if __name__ == "__main__":
    main()
