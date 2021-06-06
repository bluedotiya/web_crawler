import requests
import re
import os


class Requester:
    """
    This Class Handles the HTTP/S GET Requests for a given URL

    This class is responsible for the GET Request to the scanned websites
    and receiving the raw HTML Data from the website

    Attributes:
        url (str): The received website address
    """
    def __init__(self, url):
        """Inits the Requester Class with given URL."""

        self.url = url

    def __str__(self):
        """Override default class description with custom text"""
        return "This Class Gets a URL (String) and Returns its HTML Content"

    def request(self):
        """
        Takes a URL and return its website html content

        This function send a GET request to a given url, receives the response, return the raw HTML Data and the
        time the request has taken.
        The function checks whether the request succeeded or failed

        Returns:
            A Tuple containing the raw HTML data and the time the request took.
            first member of the tuple will be string and the second a datetime.timedelta object.
            if the request fails returns a tuple with two members containing empty string.

            Successful request:
            (str, timedelta)

            Failed request:
            ('', '')

        """
        request = requests.get(self.url, timeout=3)
        html_content = request.content
        elapsed = request.elapsed
        if request.status_code == 200:
            return str(html_content), elapsed
        else:
            return '', ''


class Parser:
    """
    This Class job is takes raw HTML Data and extracts URL's from it by using regex.

    Attributes:
        html_content (str): The raw HTML Data gathered from a website.
    """
    def __init__(self, html_content):
        """Inits the Parser Class with the provided HTML Content."""
        self.html_content = html_content

    def __str__(self):
        """Override default class description with custom text"""
        return "This Class Gets a HTML Content(String) and Extracts URLS from it"

    def extract(self):
        """
        Extracts from the Raw HTML a list of URL's.
        output will always be a list

        Returns:
            A List containing the URL's extracted from the Raw HTML Data
        """
        return re.findall("(https?://[\w\-.]+)", self.html_content)


class Buffer:
    """
    This Class handles the writing, saving and organizing of the Web Crawler Operation.

    The Class acts as a DataBase to the web crawling operation, its ordered by Depth, Parent Folder, Parent URL and
    Child URL list.

    Depth: represent how deep the crawler will search after the original website provided.
    Parent Folder: Each parent folder represent a URL that was found from the previous depth.
    Parent URL: Represent the URL that was crawled I.E: http://www.example.com/ and the request time that URL took (MS).
    Child URL's: Represent all the extracted URL's from the Parent URL Request

    Data Order:
    Depth -> Parent Folder -> Parent URL, Child URL's

    Args:
        parent_url (str): #TODO Complete DOCSTRING
    """
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
            with open(f"Depth{self.depth_num}/Parent{self.url_counter}"
                      f"/Parent_Url_{self.url_counter}.txt", "a") as parent_file:
                parent_file.write(f"{self.parent_url}\n")
                parent_file.write(str(self.time_elapsed.microseconds / 1000 / 2))
            with open(f"Depth{self.depth_num}/Parent{self.url_counter}"
                      f"/Child_Urls_{self.url_counter}.txt", "a") as buffer_file:
                for url in set(self.url_list):
                    buffer_file.writelines(f"{url}\n")
        except:
            pass
