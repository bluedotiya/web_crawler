import requests
import re
from py2neo import Graph, NodeMatcher, Relationship, Node
import random
import time
import subprocess

# Debug
import debugpy
debugpy.listen(("0.0.0.0", 5678))

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

def get_page_data(url, timeout=1):
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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'}
    try:
        response = requests.get(url, timeout=timeout, headers=headers)
        html_content = response.content
        elapsed = response.elapsed
        return str(html_content), elapsed
    except:
        return '', ''      

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
        if response.returncode == 0 and "**" not in response.stdout.decode('utf-8'):
            ipv4 = ipv4_pattern.findall(response.stdout.decode('utf-8'))[-1]
            return shift_list[0], ipv4, True
        if counter >= 6:
            return _, _, False
        counter = counter + 1

def random_sleep():
    time.sleep((random.randrange(1,5,1)))

def fetch_neo4j_for_jobs(neo4j_connection_object):
    try:
        work_node = NodeMatcher(neo4j_connection_object).match("URL").where("_.current_depth <> _.requested_depth and _.job_status = 'PENDING'").first()
        if work_node is None:
            work_node = NodeMatcher(neo4j_connection_object).match("ROOT").where("_.current_depth <> _.requested_depth and _.job_status = 'PENDING'").first()
            if work_node is None:
                return (False, '')
    except:
        return (False, '')
    return (True, work_node)

def validate_job( current_job, neo4j_connection_object):
    # Get Website HTML content from URL
    url = current_job.get('name')

    # Add Failure count to job
    attempts_counter = current_job.get('attempts')
    if attempts_counter is None:
        attempts_counter = 0

    http_type = current_job.get('http_type')
    page_data_response = get_page_data(http_type + url, timeout=(attempts_counter + 1))
    url_data, request_time = page_data_response
    if page_data_response != ('', ''):
        return True, url_data, request_time

    # Failure code block, Website HTML Fetch failed, adding attempts counter
    current_job['attempts'] = attempts_counter + 1
    print(f"Warning: Request failed: {http_type + url} -- Attempts: {attempts_counter}")

    # Failure code block, giving up on URL request after 3 failed attempts
    if attempts_counter > 2:
        current_job['job_status'] = 'FAILED'
        print(f"Error: Failure limit reached! Giving up on {http_type + url} after{attempts_counter} attempts.")

    # Pushing any changes to DB
    neo4j_connection_object.push(current_job)
    return False, None, None

def feeding(job, neo4j_connection_object):

    # Declare Job as in-progress - Prevents other workers from taking the same job
    job['job_status'] = 'IN-PROGRESS'
    neo4j_connection_object.push(job)

    # Validate Job is Ok
    return_code, url_data, request_time = validate_job(job, neo4j_connection_object)
    if return_code == False:
        return False

    extracted_url_list = extract_page_data(url_data)
    lead = Relationship.type("Lead")
    relationship_tree = None

    # Get all DB Nodes
    database_nodes_list = NodeMatcher(neo4j_connection_object).match().all()

    # Upperize all URLs extracted from page
    urls_set = set()
    url_http_scheme = dict()
    for full_url in extracted_url_list:
        url, http_scheme = normalize_url(full_url)
        url_http_scheme[url] = http_scheme
        urls_set.add(url)


    # Create a set of all DB nodes with http type & url address
    database_nodes_names_set = {node.get('name') for node in database_nodes_list}
    
    # Does a Left join exclusive operation on upper_urls_set:
    # This operation makes sure that no duplicates nodes are added to DB
    urls_set -= database_nodes_names_set
    
    deduped_set = set()
    for scheme_key in url_http_scheme:
        if scheme_key in urls_set:
            deduped_set.add(f"{url_http_scheme[scheme_key]}{scheme_key}")



    if deduped_set.__len__() == 0:
        print(f"Warning: No new URLs found in: {job.get('name')}")
        job['job_status'] = 'NO LEAD'
        neo4j_connection_object.push(job)
        return True

    # This loop create node object for each url and connects it to the main url
    for url in {normalize_url(url) for url in deduped_set}:
        # Declare Default values

        requested_depth = job.get('requested_depth')
        current_depth = (job.get('current_depth') + 1)
        job_status = "PENDING"

        # Check if reached max depth
        if current_depth == requested_depth:
            job_status = "RESTRICTED"

        # Get URL network stats and validate its DNS record
        domain, ip, return_code = get_network_stats(url[0])
        if return_code == False:
            print(f"Error: URL: {url[0]} -- FAILED")
            continue

        # Define search mode
        search_mode = job.get('search_mode')
        if domain !=  job.get('domain') and search_mode == 'domain':
            continue

        url_node = Node("URL", ip=ip, domain=domain, job_status=job_status, http_type=url[1], name=url[0], requested_depth=requested_depth, current_depth=current_depth, request_time=f"{request_time.microseconds / 1000}MS", search_mode=search_mode)
        if relationship_tree is None:
            relationship_tree = lead(job, url_node)
        else:
            relationship_tree = relationship_tree | lead(job, url_node)

    if relationship_tree is None:
        job['job_status'] = 'NO LEAD'
        neo4j_connection_object.push(job)
        return False
    neo4j_connection_object.create(relationship_tree)

    # Change task status to completed
    job['job_status'] = 'COMPLETED'
    neo4j_connection_object.push(job)
    return True



def main():
    while(run_health_check(graph) == False):
        restore_db_connection()
    random_sleep()
    job_found, work_node = fetch_neo4j_for_jobs(graph)
    if job_found == False:
        print("Info: Job not found, Give me something to do")
        exit(2)
    feed_result = feeding(work_node, graph)
    if feed_result == False:
        print("Error: Something went wrong during feeding :(")
        exit(1)
    print(f"Info: Feed Cycle Completed for: {work_node.get('name')}")


if __name__ == "__main__":
    main()
