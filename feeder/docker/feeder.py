import requests
import re
import redis
import random
import time

# Global DNS Record
REDIS_DNS_NAME = "redis.redis.svc.cluster.local"

# Global Redis connection obj
redis_obj = redis.Redis(host=REDIS_DNS_NAME, port=6379, db=0, password='a-very-complex-password-here')

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

def random_sleep():
    time.sleep((random.randrange(20,100,1)) / 100)

def check_redis_for_jobs(redis_connection_object):
    available_keys = redis_connection_object.keys('*')
    random.shuffle(available_keys)
    for key in available_keys:
        key_comp_list = key.decode('utf-8').split('_')
        if key_comp_list[-1] == 0 and (key_comp_list[-3] != key_comp_list[-2]):
            return True, key.decode('utf-8')
    return False, None
    

def feeding(key, redis_connection_object):
    url_list = redis_connection_object.smembers(key)
    for master_url in url_list.decode('utf-8'):
        request_obj = get_page_data(master_url)[0]

        # Continue if request fails
        if request_obj == '':
            continue
        request_html = request_obj
        extracted_urls = extract_page_data(request_html)

        # Continue if no URLs were extracted
        if extracted_urls.__len__() == 0:
            continue
        
        # Determine depths
        key_comp_list = key.decode('utf-8').split('_')
        curr_depth_indicator, req_depth = key_comp_list[1], key_comp_list[2]

        # Determine Curr depth
        if curr_depth_indicator == "ROOT":
            curr_depth = 1
        else:
            curr_depth = curr_depth_indicator + 1

        # Normalized master URL
        normalized_master_url = ('.'.join((master_url.replace('https://', '')).replace('http://', '').split('.')[-1:-3:-1][-1:-3:-1])).upper()

        # Check if processed set exist
        if redis_connection_object.exists(f"{normalized_master_url}_{curr_depth}_{req_depth}_*") != 0:
            continue

        # Create new set, insert urls
        for child_url in extracted_urls:
            normalized_child_url = ('.'.join((child_url.replace('https://', '')).replace('http://', '').split('.')[-1:-3:-1][-1:-3:-1])).upper()
            redis_connection_object.sadd(f"{normalized_child_url}_{curr_depth}_{req_depth}_1")



def main():
    while(True):
        job_starter, job_name = check_redis_for_jobs(redis_obj)
        if job_starter is False:
            random_sleep()
            continue
        feeding(job_name, redis_obj)


if __name__ == "__main__":
    main()
