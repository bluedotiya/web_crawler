import requests
import re
import os
import datetime


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
    try:
        response = requests.get(url, timeout=1)
    except:
        return '', ''
    else:
        html_content = response.content
        elapsed = response.elapsed
        return str(html_content), elapsed


def extract(html_content):
    """
    This function job is takes raw HTML Data and extracts URL's from it by using regex.
    Extracts from the Raw HTML a list of URL's, output will always be a list.
    Returns:
        A List containing the URL's extracted from the Raw HTML Data
    """
    return re.findall("(https?://[\w\-.]+)", html_content)


def main():
    pass


if __name__ == "__main__":
    main()