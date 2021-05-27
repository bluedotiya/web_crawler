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
            return str(requests.get(self.url).content)
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
    def __init__(self, html_content, file_path):
        self.html_content = html_content
        self.file_path = file_path

    def __str__(self):
        return "This Class Gets a URL (String) and Saves it on Storage"

    def save(self):
        try:
            with open(self.file_path, "a") as buffer_file:
                for url in set(self.html_content):
                    buffer_file.writelines(f"{url}\n")
        except:
            pass

    def read(self):
        with open(self.file_path, "r") as buffer_file:
            file_content = buffer_file.readlines()
            return file_content

    def del_buffer(self):
        os.remove(self.file_path)
