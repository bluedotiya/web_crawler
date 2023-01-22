import json
import jsonschema
from flask import Flask, request, Response
import requests
import re
import py2neo
import subprocess

# Global DNS Record
# Should be 'neo4j.default.svc.cluster.local:7687'
NEO4J_DNS_NAME = "neo4j.default.svc.cluster.local:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"

# Global Neo4j connection obj
graph = py2neo.Graph(f"bolt://{NEO4J_DNS_NAME}", auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

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
    This function job is takes raw HTML Data and extracts URL's from it by using regex.
    Extracts from the Raw HTML a list of URL's output will always be a list.
    Returns:
        A list containing the URL's extracted from the Raw HTML Data
    """
    found_list = re.findall("(https?://[\w\-.]+)", html_content)
    return found_list

def normalize_url(url):
    url_upper = url.upper()
    if 'HTTPS://' in url_upper:
        return ((url_upper.replace('HTTPS://', '')).replace('WWW.', ''), 'HTTPS://')
    else:
        return ((url_upper.replace('HTTP://', '')).replace('WWW.', ''), 'HTTP://')
    
    
def get_network_stats(url):
    ipv4_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    normalized_url, _ = normalize_url(url)
    splited_url = normalized_url.split('.')
    counter = 2
    while True:
        shift_list = splited_url[-1:-counter:-1][-1::-1]
        shift_url = '.'.join(shift_list)
        response = subprocess.run(['nslookup', shift_url], capture_output=True)
        if response.returncode == 0:
            ipv4 = ipv4_pattern.findall(response.stdout.decode('utf-8'))[-1]
            return shift_list[0], ipv4, True
        if counter >= 6:
            return _, _, False
        counter = counter + 1
        

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
    if list(client_req.keys())[0] != "url" or list(client_req.keys())[1] != "depth":
        return Response("{'Error':'url key or depth key was not found in json'}", status=400, mimetype='application/json')

    # Remove http/s Scheme from URL, take only Domain name
    requested_url = client_req['url']
    requested_depth = client_req['depth']
    root_url, http_type = normalize_url(requested_url)

    # Check if the desired request was successful & Assign html content, request time to vars 
    request_obj = get_page_data(client_req['url'])
    if request_obj == ('', ''):
        return Response("{'Error':'Requested URL was not found'}", status=404, mimetype='application/json')
    request_html, request_time = request_obj
    extracted_urls = extract_page_data(request_html)

    # Check if URL Root is found on neo4j
    if py2neo.NodeMatcher(graph).match("ROOT", name=root_url, requested_depth=requested_depth).first() is not None:
       return Response("{'Info':'requested url was already searched'}", status=200, mimetype='application/json')
    print("requested url is not on database, starting search! :)")
   
    # Get root node
    domain, ip, _ = get_network_stats(root_url)
    root_node = py2neo.Node(node_type="ROOT", ip=ip, domain=domain, http_type=http_type, name=root_url, requested_depth=requested_depth, current_depth=0, request_time=request_time)
    lead = py2neo.Relationship.type("Lead")
    relationship_tree = None
    for url in extracted_urls:
        domain, ip, return_code = get_network_stats(url)
        if return_code == False:
            continue
        norm_url, http_type = normalize_url(url)
        url_node = py2neo.Node(node_type="URL", ip=ip, domain=domain, job_status="PENDING", http_type=http_type, name=norm_url, requested_depth=requested_depth, current_depth=1, request_time=request_time)
        if relationship_tree is None:
            relationship_tree = lead(root_node, url_node)
        else:
            relationship_tree = relationship_tree | lead(root_node, url_node) 
    graph.create(relationship_tree)

    client_answer = json.dumps({'Success': 'Job started'}), "200"
    return client_answer