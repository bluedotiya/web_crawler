import requests
import re
import os


class Requester:
    def __init__(self, url):
        self.url = url

    def __str__(self):
        return "This Class Gets a URL (String) and Returns its HTML Content"

    def request(self):
        try:
            request = requests.get(self.url, timeout=3)
            html_content = request.content
            elapsed = request.elapsed
            if html_content is None or elapsed is None:
                raise TypeError
            else:
                return str(html_content), elapsed
        except:
            pass


class Parser:
    def __init__(self, html_content):
        self.html_content = html_content

    def __str__(self):
        return "This Class Gets a HTML Content(String) and Extracts URLS from it"

    def extract(self):
        try:
            return re.findall("(https?://[\w\-\.]+)", self.html_content)
        except:
            pass


class Buffer:
    def __init__(self, parent_url , url_list, depth_num, time_elapsed, url_counter):
        self.parent_url = parent_url
        self.url_list = url_list
        self.depth_num = depth_num
        self.time_elapsed = time_elapsed
        self.url_counter = url_counter

    def __str__(self):
        return "This Class Gets a URL (List) and Saves it on Storage"

    def save(self):
        try:
            os.mkdir(f"Depth{self.depth_num}/Parent{self.url_counter}")
            with open(f"Depth{self.depth_num}/Parent{self.url_counter}/Parent_Url_{self.url_counter}.txt", "a") as parent_file:
                parent_file.write(f"{self.parent_url}\n")
                parent_file.write(str(self.time_elapsed.microseconds / 1000 / 2))
            with open(f"Depth{self.depth_num}/Parent{self.url_counter}/Child_Urls_{self.url_counter}.txt", "a") as buffer_file:
                for url in set(self.url_list):
                    buffer_file.writelines(f"{url}\n")
        except:
            pass
