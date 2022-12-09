import json
import jsonschema
from flask import Flask, request, Response
import gqlalchemy as gq
from gqlalchemy.query_builders.memgraph_query_builder import Operator
import requests
import re
import py2neo
import debugpy # TODO REMOVE ALL DEBUG ONCE READY

# 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
debugpy.listen(5678)
print("Waiting for debugger attach")
debugpy.wait_for_client()

# Global DNS Record
# Should be memgraph-0.memgraph-svc.default.svc.cluster.local
MEMGRAPH_DNS_NAME = "memgraph-0.memgraph-svc.default.svc.cluster.local"

# Global Memgraph connection obj
# Port should be 7687
db = gq.Memgraph(host=MEMGRAPH_DNS_NAME, port=7687)


# Global Flask server obj
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
    This function job is takes raw HTML Data and extracts URLs from it by using regex.
    Extracts from the Raw HTML a list of URLs, and extracts it to a dict, output will always be a dict.
    Returns:
        A dict containing the URLs extracted from the Raw HTML Data
    """
    found_list = re.findall("(https?://[\w\-.]+)", html_content)
    response_dict = {'urls': found_list}
    return response_dict


def normalize_url(url):
    url_list = (url.replace('https://', '')).replace('http://', '').split('.')
    if url_list.__len__() == 2:
        return '.'.join(url_list)
    if url_list.__len__() == 3:
        return ('.'.join(url_list[-1:-3:-1][-1:-3:-1])).upper()
    else:
        return ('.'.join(url_list[-1:-4:-1][-1:-4:-1])).upper()


@app.route('/', methods=['POST'])
def index():
    # Check client request header is json
    if not request.is_json:
        return Response("{'Error':'Only json data is allowed'}", status=400, mimetype='application/json')
    # Validate client request json scheme
    try:
        schema = {"type": "object", "properties": {"url": {"type": "string"}, "depth": {"type": "integer"}}}
        jsonschema.validate(request.get_json(), schema)
    except jsonschema.exceptions.ValidationError:
        return Response("{'Error':'Bad Json scheme'}", status=400, mimetype='application/json')
    # Check if client request json key is valid
    client_req = request.get_json()
    if list(client_req.keys())[0] != "url":
        return Response("{'Error':'url key was not found in json'}", status=400, mimetype='application/json')

    # Remove http/s Scheme from URL, take only Domain name
    requested_url = client_req['url']
    root_url = normalize_url(requested_url)

    # Declare Root Node labels & Node match filter
    root_labels_dict = {'url'            : root_url,
                        'depth'          : 'ROOT',
                        'requested_depth': 'req_depth_3'}

    root_node_labels = [root_labels_dict['depth'],
                        root_labels_dict['requested_depth']]

    match_filters = root_node_labels

    # Prepare Match query for root node
    find_root_node_query = gq.Match(connection=db)\
                             .node(labels=match_filters, variable='node')\
                             .where(item='node.name', operator=Operator.EQUAL, literal=root_url)\
                             .return_()

    # Check if the desired request was successful
    request_obj = get_page_data(client_req['url'])
    if request_obj == ('', ''):
        return Response("{'Error':'Requested URL was not found'}", status=404, mimetype='application/json')

    # Check if URL Root is found on memgraph
    try:
       next(find_root_node_query.execute())
       return Response("{'Info':'requested url was already searched'}", status=200, mimetype='application/json')
    except StopIteration:
        print("requested url is not on database, starting search! :)")

    # Create ROOT URL Node on memgraph
    gq.Create(db)\
      .node(labels=root_node_labels, name=root_labels_dict['url'])\
      .execute()


    # Assign html content, request time to vars & Extracting urls from html content
    request_html, request_time = request_obj
    extracted_urls = extract_page_data(request_html)
    for url in extracted_urls['urls']:
        # Normalize url iterator
        norm_url = normalize_url(url)
        # Create node for each URL found and link it to Root Node
        gq.Match(db) \
            .node(labels=match_filters, variable='node') \
            .where(item='node.name', operator=Operator.EQUAL, literal=root_url) \
            .create(db) \
            .to(relationship_type="Links") \
            .node(labels=['curr_depth_1', 'req_depth_3', 'processed_0'], name=norm_url) \
            .execute()

    client_answer = json.dumps({'Success': 'Job started'}), "200"
    return client_answer