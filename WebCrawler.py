from RTB_Class import Requester, Parser, Buffer
import os
import time


def runtime_cycle(depth, root_url, path="./output_urls.txt",):
    if os.path.isfile(path):
        os.remove(path)
    depth_cycle(depth, root_url)
    for level in range(depth):
        with open(f"{path}", "a") as output_file:
            with open(f"./depth{level}.tmp", "r") as tmp_file:
                tmp_list = tmp_file.readlines()
                print(f"Depth {level}: URL Count: {len(tmp_list)}")
                output_file.writelines(tmp_list)
            os.remove(f"./depth{level}.tmp")


def depth_cycle(depth, root_url):
    for depth in range(depth):
        if depth == 0:
            rtb_cycle(root_url , depth)
        else:
            validator(f"./depth{depth - 1}.tmp")
            with open(f"./depth{depth - 1}.tmp", "r") as url_file:
                for url in url_file.readlines():
                    rtb_cycle(url[:-1], depth)


def rtb_cycle(url, depth=0):
    html = Requester(f"{url}").request()
    url_list = Parser(html).extract()
    buffer = Buffer(url_list, f"./depth{depth}.tmp")
    buffer.save()


def validator(tmp_path):
    with open(tmp_path, "r") as tmp_file:
        deduped_list = set(tmp_file.readlines())
    os.remove(tmp_path)
    with open(tmp_path, "a") as tmp_file:
        tmp_file.writelines(deduped_list)


def main():

    runtime_cycle(3, "https://www.youtube.com")


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
