import requests
import re
import os


def request(url):
    """
    Takes a URL and return its website html content

    This function send a GET request to a given url, receives the response, return the raw HTML Data and the
    time the request has taken.
    The function checks whether the request succeeded or failed

    Args:
        url (str): The received website address

    Returns:
        A Tuple containing the raw HTML data and the time the request took.
        first member of the tuple will be string and the second a datetime.timedelta object.
        if the request fails returns a tuple with two members containing empty string.

        Successful request:
        (str, timedelta)

        Failed request:
        ('', '')

    """
    request = requests.get(url, timeout=3)
    html_content = request.content
    elapsed = request.elapsed
    if request.status_code == 200:
        return str(html_content), elapsed
    else:
        return '', ''


def extract(html_content):
    """
    This function job is takes raw HTML Data and extracts URL's from it by using regex.
    Extracts from the Raw HTML a list of URL's, output will always be a list.

    Returns:
        A List containing the URL's extracted from the Raw HTML Data
    """
    return re.findall("(https?://[\w\-.]+)", html_content)


def save(parent_url, url_list, depth_num, time_elapsed, url_counter):
    """
       This function handles the writing, saving and organizing of the Web Crawler Operation.

       The function acts as a DataBase to the web crawling operation, its ordered by Depth, Parent Folder,
       Parent URL and Child URL list, the save function is the lower-end of the DB Operation, this means it need
       higher external function in order to work, such function is the depth_cycle

       Depth: represent how deep the crawler will search after the original website provided. Parent Folder: Each
       parent folder represent a URL that was found from the previous depth. Parent URL: Represent the URL that
       was crawled I.E: http://www.example.com/ and the request time that URL took (MS). Child URL's: Represent
       all the extracted URL's from the Parent URL Request

       Data Order:
       Depth -> Parent Folder -> Parent_URL.txt, Child_URL's.txt
       Parent_URL.txt format: <parent url value>newline<request time>
       Child_URL.txt format: <URL1>newline<URL2>newline<URL3>....

       Args:
           parent_url (str): The Current URL that was searched by the Crawler
           url_list (list[str]): A list that represent the Output from the Parser.extract
           depth_num (int): A Int that represent the current crawler depth
           time_elapsed (datetime.timedelta): represent the request time delta from request to response
           url_counter (int): represent the current folder number and file numbering


       """

    try:
        os.mkdir(f"Depth{depth_num}/Parent{url_counter}")
        with open(f"Depth{depth_num}/Parent{url_counter}"
                  f"/Parent_Url_{url_counter}.txt", "a") as parent_file:
            parent_file.write(f"{parent_url}\n")
            parent_file.write(str(time_elapsed.microseconds / 1000 / 2))
        with open(f"Depth{depth_num}/Parent{url_counter}"
                  f"/Child_Urls_{url_counter}.txt", "a") as buffer_file:
            for url in set(url_list):
                buffer_file.writelines(f"{url}\n")
    except:
        pass
