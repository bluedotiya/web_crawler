import requests
import re
from py2neo import Graph, NodeMatcher, Relationship, Node
import random
import time
import os
import debugpy # TODO REMOVE ALL DEBUG ONCE READY

# 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
# debugpy.listen(("0.0.0.0", 5678))
# print("Waiting for debugger attach")
# debugpy.wait_for_client()

# Global DNS Record
# Should be 'neo4j.neo4j.svc.cluster.local:7687'
NEO4J_DNS_NAME = "neo4j.neo4j.svc.cluster.local:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"

# Global Neo4j connection obj
graph = Graph(f"bolt://{NEO4J_DNS_NAME}", auth=(NEO4J_USERNAME, NEO4J_PASSWORD))


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

def get_domain_name(url):
    normalized_url, http_type = normalize_url(url)
    splited_url = normalized_url.split('.')
    counter = 2
    while True:
        shift_list = splited_url[-1:-counter:-1][-1::-1]
        shift_url = '.'.join(shift_list)
        response = os.system("nslookup " + shift_url + " > /dev/null 2>&1")
        if response == 0:
            return shift_list[0]
        if counter >= 6:
            return shift_list[0]
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

def feeding(job, neo4j_connection_object):
    url = job.get('name')
    http_type = job.get('http_type')
    response = get_page_data(http_type + url)
    if response == ('', ''):
        print(f"Request failed: {http_type + url}")
        return False
    url_data, request_time = response
    extracted_url_list = extract_page_data(url_data)
    deduped_url_list = []
    lead = Relationship.type("Lead")
    relationship_tree = None

    # Declare Job as in-progress
    job['job_status'] = 'IN-PROGRESS'
    neo4j_connection_object.push(job)
    
    # This loop, normalize the extracted url and also discards urls that are found in database
    for url in extracted_url_list:
        normalized_url = normalize_url(url)
        database_nodes_list = NodeMatcher(neo4j_connection_object).match().all()
        for node in database_nodes_list:
            if normalized_url == node.get('name'):
                break
        deduped_url_list.append(normalized_url)

    urls_set = set(deduped_url_list)
    # This loop create node object for each url and connects it to the main url
    for url in urls_set:
        domain = get_domain_name(url[0])
        url_node = Node("URL", domain, job_status="PENDING", http_type=url[1], name=url[0], requested_depth=job.get('requested_depth'), current_depth=(job.get('current_depth') + 1), request_time=request_time)
        if relationship_tree is None:
            relationship_tree = lead(job, url_node)
        else:
            relationship_tree = relationship_tree | lead(job, url_node) 
    neo4j_connection_object.create(relationship_tree)

    # Change task status to completed
    job['job_status'] = 'COMPLETED'
    neo4j_connection_object.push(job)
    return True



def main():
    while(True):
        random_sleep()
        job_found, work_node = fetch_neo4j_for_jobs(graph)
        if job_found == False:
            print("Job not found, Give me something to do")
            continue
        feed_result = feeding(work_node, graph)
        if feed_result == False:
            print("Something went wrong during feeding :(")
            continue
        print(f"Feed Cycle Completed for: {work_node.get('name')}")
 


if __name__ == "__main__":
    main()
