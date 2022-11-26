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

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0

def determine_environment():
    REDIS_DNS_NAME = "redis.redis.svc.cluster.local"
    return ping(REDIS_DNS_NAME)

REDIS_ENV = determine_environment()

if REDIS_ENV:
    # Global DNS Record
    REDIS_DNS_NAME = "redis.redis.svc.cluster.local"

    # Global Redis connection obj
    redis_obj = redis.Redis(host=REDIS_DNS_NAME, port=6379, db=0, password='a-very-complex-password-here')

    @app.route('/', methods=['POST'])
    def index():

        # Check client request header is json
        if request.is_json == False:
            return Response("{'Error':'Only json data is allowed'}", status=400, mimetype='application/json')

        # Validate client request json scheme
        try:
            schema = {"type" : "object","properties" : {"url" : {"type" : "string"}, "depth" : {"type" : "integer"}}}
            jsonschema.validate(request.get_json(), schema)
        except jsonschema.exceptions.ValidationError:
            return Response("{'Error':'Bad Json scheme'}", status=400, mimetype='application/json')

        # Check if client request json key is vaild
        client_req = request.get_json()
        if list(client_req.keys())[0] != "url":
            return Response("{'Error':'url key was not found in json'}", status=400, mimetype='application/json')
        
        # Remove http/s Scheme from URL, take only Domain name
        requested_url = client_req['url']
        normalized_url = ('.'.join((requested_url.replace('https://', '')).replace('http://', '').split('.')[-1:-3:-1][-1:-3:-1])).upper()
        root_url = f"{normalized_url}_ROOT"
        
        # Check if URL Root is found on redis, if not creates a root url.
        if redis_obj.exists(root_url) == 1:
            return Response("{'Info':'requested url was already searched'}", status=200, mimetype='application/json')

        # Check if the desired request was successful
        request_obj = get_page_data(client_req['url'])
        if request_obj == ('', ''):
            return Response("{'Error':'Requested URL was not found'}", status=404, mimetype='application/json')
        
        # Assign html content, request time to vars & Extracting urls from html content
        request_html, request_time = request_obj
        extracted_urls = extract_page_data(request_html)
        for url in extracted_urls['urls']:
            redis_obj.sadd(root_url, str(url))

        # Send Successful Job status to Client
        client_answer = json.dumps({'Success':'Job started'}), "200"
        return client_answer

else:
    @app.route('/', methods=['POST'])
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


        