import requests
import re
from py2neo import Graph, NodeMatcher, Relationship, Node
import random
import time
import subprocess

# Global DNS Record
# Should be 'neo4j.default.svc.cluster.local:7687'
NEO4J_DNS_NAME = "neo4j.default.svc.cluster.local:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"

# Global Neo4j connection obj
graph = Graph(f"bolt://{NEO4J_DNS_NAME}", auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


def run_health_check(neo4j_connection_object):
    try:
        neo4j_connection_object.run("Match () Return 1 Limit 1")
        return True
    except Exception:
        print("Warning: Database connection degraded")
        return False

def restore_db_connection():
    graph = Graph(f"bolt://{NEO4J_DNS_NAME}", auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        graph.run("Match () Return 1 Limit 1")
        print("Info: Database connection restored")
    except Exception:
        random_sleep()

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


def random_sleep():
    time.sleep((random.randrange(1,10,1)))

def fetch_neo4j_for_jobs(neo4j_connection_object):
    try:
        work_node = NodeMatcher(neo4j_connection_object).match("URL").where("_.current_depth <> _.requested_depth and _.job_status = 'PENDING'").first()
        if work_node is None:
            return (False, '')
    except:
        return (False, '')
    return (True, work_node)

def validate_job( current_job, neo4j_connection_object):
    # Get Website HTML content from URL
    url = current_job.get('name')
    http_type = current_job.get('http_type')
    page_data_response = get_page_data(http_type + url)
    url_data, request_time = page_data_response
    if page_data_response != ('', ''):
        return True, url_data, request_time
    # Failure code block, Website HTML Fetch failed, adding attempts counter
    attempts_counter = current_job.get('attempts')
    if attempts_counter is None:
        attempts_counter = 0
    current_job['attempts'] = attempts_counter + 1
    print(f"Request failed: {http_type + url} -- Attempts: {attempts_counter}")
    # Failure code block, giving up on URL request after 3 failed attempts
    if attempts_counter > 2:
        current_job['job_status'] = 'FAILED'
        print(f"Failure limit reached! Giving up on f{http_type + url} after f{attempts_counter} attempts.")
    # Pushing any changes to DB
    neo4j_connection_object.push(current_job)
    return False

def feeding(job, neo4j_connection_object):
    # Validate Job is Ok
    return_code, url_data, request_time = validate_job(job, neo4j_connection_object)
    if return_code == False:
        return False

    # Declare Job as in-progress
    job['job_status'] = 'IN-PROGRESS'
    neo4j_connection_object.push(job)

    extracted_url_list = extract_page_data(url_data)
    lead = Relationship.type("Lead")
    relationship_tree = None

    # Get all DB Nodes
    database_nodes_list = NodeMatcher(neo4j_connection_object).match().all()
    # Normalize all URLs extracted from page
    upper_urls_set = {url.upper() for url in extracted_url_list}
    # Create a set of all DB nodes with only node names
    database_nodes_names_set = {node.get('http_type') + node.get('name') for node in database_nodes_list}
    
    # Removes all URLs that are found on database
    upper_urls_set -= database_nodes_names_set

    if upper_urls_set.__len__() == 0:
        print(f"Warning: No new URLs found in: {job.get('name')}")
        job['job_status'] = 'COMPLETED'
        neo4j_connection_object.push(job)
        return True

    # This loop create node object for each url and connects it to the main url
    for url in {normalize_url(url) for url in upper_urls_set}:
        domain, ip, return_code = get_network_stats(url[0])
        if return_code == False:
            print(f"Error: URL:{url} -- FAILED")
            continue
        url_node = Node("URL", ip=ip, domain=domain, job_status="PENDING", http_type=url[1], name=url[0], requested_depth=job.get('requested_depth'), current_depth=(job.get('current_depth') + 1), request_time=request_time)
        if relationship_tree is None:
            relationship_tree = lead(job, url_node)
        else:
            relationship_tree = relationship_tree | lead(job, url_node)
    if relationship_tree is None:
        job['job_status'] = 'FAILED'
        neo4j_connection_object.push(job)
        return False
    neo4j_connection_object.create(relationship_tree)

    # Change task status to completed
    job['job_status'] = 'COMPLETED'
    neo4j_connection_object.push(job)
    return True



def main():
    while(True):
        while(run_health_check(graph) == False):
            restore_db_connection()
        random_sleep()
        job_found, work_node = fetch_neo4j_for_jobs(graph)
        if job_found == False:
            print("Info: Job not found, Give me something to do")
            continue
        feed_result = feeding(work_node, graph)
        if feed_result == False:
            print("Error: Something went wrong during feeding :(")
            continue
        print(f"Info: Feed Cycle Completed for: {work_node.get('name')}")
 


if __name__ == "__main__":
    main()
