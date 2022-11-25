import json
import jsonschema
from flask import Flask, request, Response
import requests
import re
app = Flask(__name__)


def get_page_data(url):
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


def extract_page_data(html_content):
    """
    This function job is takes raw HTML Data and extracts URL's from it by using regex.
    Extracts from the Raw HTML a list of URL's, and extracts it to a dict, output will always be a dict.
    Returns:
        A dict containing the URL's extracted from the Raw HTML Data
    """
    found_list = re.findall("(https?://[\w\-.]+)", html_content)
    response_dict = {'urls': found_list}
    return response_dict


@app.route('/api/data', methods=['POST'])
def index():

    # Check client request header is json
    if request.is_json == False:
        return Response("{'Error':'Only json data is allowed'}", status=400, mimetype='application/json')
    
    # Validate client request json scheme
    
    try:
        schema = {"type" : "object","properties" : {"url" : {"type" : "string"}}}
        jsonschema.validate(request.get_json(), schema)
    except jsonschema.exceptions.ValidationError:
        return Response("{'Error':'Bad Json scheme'}", status=400, mimetype='application/json')

    # Check if client request json key is vaild
    client_req = request.get_json()
    if list(client_req.keys())[0] != "url":
        return Response("{'Error':'url key was not found in json'}", status=400, mimetype='application/json')

    # Check if the desired request was successful
    request_obj = get_page_data(client_req['url'])
    if request_obj == ('', ''):
        return Response("{'Error':'Requested URL was not found'}", status=404, mimetype='application/json')

    request_html, request_time = request_obj
    extracted_urls = extract_page_data(request_html)
    extracted_urls['time'] = int(request_time.microseconds) / 1000
    client_answer = json.dumps(extracted_urls), "200"
    return client_answer
        