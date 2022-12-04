import RTB
import os
from shutil import rmtree

def depth_cycle(depth, root_url):
    """
    The Depth Cycle is the highest-level function of the crawler its job is to orchestrate the crawler operation
    and complete the DB file saving operation on the high-level, by providing arguments to the RTB_Cycle function.

    Args:
        depth (int): this represent the depth the crawler will search after the original URL
        root_url (str): root URL Represent the first URL provided by the user.
    """
    parent_url_counter = 1
    for depth in range(1, depth + 1):
        try:
            os.mkdir(f"output/Depth{depth}")
        except FileExistsError:
            pass
        if depth == 1:
            rtb_cycle(depth, root_url)
            parent_url_counter += 1
        else:
            for parent_folder in set([int(name.replace('Parent', '')) for name in os.walk(f"output/Depth{depth - 1}").__next__()[1]]):
                """List Comprehension explanation: Get a list of Parent folders on the previous depth, remove the 
                word Parent, turn into a int and order into a set this will give us an int following number set from 
                first parent folder to the last, this section have two jobs:
                1. give the for loop the correct number of iteration
                2. give the for loop a counter that is correlated with the number of iteration
                
                Examples:
                example depth folder:
                Depth1
                    -Parent1
                    -Parent2
                    -Parent3
                    
                ['Parent1', 'Parent2', 'Parent3'] --> [1, 2, 3]
                
                example of for loop:
                for parent_folder in set([1, 2, 3])
                
                """
                with open(f"output/Depth{depth - 1}/Parent{parent_folder}/Child_Urls_{parent_folder}.txt", "r") as url_file:
                    with open(f"output/Depth{depth - 1}/Parent{parent_folder}/Parent_Url_{parent_folder}.txt") as parent_file:
                        parent_url = parent_file.readlines()[0].replace('\n', '')
                        url_file_content = url_file.readlines()
                        for url in url_file_content:
                            rtb_cycle(depth, url.replace('\n', ''), parent_url_counter, parent_url)
                            parent_url_counter += 1


def rtb_cycle(current_depth=1, url="https://www.google.com/", url_list_counter=1, parent_file_pointer="Root"):
    """
    The RTB Cycle function uses the RTB.py methods to create a basic web crawler.
    The function sends a request, extracts the results and saves it.

    Args:
        current_depth (int):  a counter that represent the current Crawler Depth
        url (str): Input URL to Crawl into
        url_list_counter (int): represent the current folder number and file numbering

    """
    response_tuple = RTB.request(url)
    html_content, time_elapsed = response_tuple
    url_list = RTB.extract(html_content)
    RTB.save(url, url_list, current_depth, time_elapsed, url_list_counter, parent_file_pointer)


def main():
    depth_cycle(3, "https://www.google.com")


if __name__ == "__main__":
    main()
