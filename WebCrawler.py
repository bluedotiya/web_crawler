from RTB_Class import Requester, Parser, Buffer
from ValidatorClass import Validator
import os
import time


def runtime_cycle(depth, root_url, path="./output_urls.txt",):
    if os.path.isfile(path):
        os.remove(path)
    depth_cycle(depth, root_url)
    archiver(depth, path)
    validator(path, f"{path}.tmp")


def depth_cycle(depth, root_url):
    for depth in range(1, depth + 1):
        start_time_depth = time.time()
        if depth == 1:
            rtb_cycle(root_url , depth)
            cycle_stats(depth, start_time_depth)
        else:
            with open(f"./depth{depth - 1}.tmp", "r") as url_file:
                for url in url_file.readlines():
                    rtb_cycle(url[:-1], depth)
            cycle_stats(depth, start_time_depth)


def rtb_cycle(url, depth=1):
    html = Requester(f"{url}").request()
    url_list = Parser(html).extract()
    buffer = Buffer(url_list, f"./depth{depth}.tmp")  #TODO: Fix the buffer so it can split tmp files into bit chunks so python wont crash :)
    buffer.save()


def tmp_deduper(tmp_path):
    with open(tmp_path, "r") as tmp_file:
        deduped_list = set(tmp_file.readlines())
    os.remove(tmp_path)
    with open(tmp_path, "a") as tmp_file:
        tmp_file.writelines(deduped_list)
    return len(deduped_list)


def archiver(depth, file_path):
    for level in range(1, depth + 1):
        with open(f"{file_path}.tmp", "a") as output_file:
            with open(f"./depth{level}.tmp", "r") as tmp_file:
                tmp_list = tmp_file.readlines()
                output_file.writelines(tmp_list)
            os.remove(f"./depth{level}.tmp")


def validator(result_path, tmp_path):
    validator_obj = Validator(result_path, tmp_path)
    validator_obj.read_file()
    validator_obj.dedupe()
    validator_obj.validate()
    validator_obj.write_file()
    validator_obj.remove_tmp()


def cycle_stats(depth, start_time_point):
    time_unit = ["Seconds", "Minutes", "Hours"]
    tmp_url_count = tmp_deduper(f"./depth{depth}.tmp")
    time_passed = time.time() - start_time_point
    if time_passed > 3600:
        time_unit = time_unit[2]
        elapsed_time = time_passed / 3600
    elif time_passed > 60:
        time_unit = time_unit[1]
        elapsed_time = time_passed / 60
    else:
        time_unit = time_unit[0]
        elapsed_time = time_passed
    print(f"==========Depth-{depth}============ ")
    print(f"URL Found: {tmp_url_count}")
    print(f"Elapsed {time_unit}: {str(elapsed_time)[0:4]}")
    speed = str(tmp_url_count / time_passed)[0:4]
    print(f"Speed: {speed} URL/Sec")
    print(f"=============================\n")


def main():
    runtime_cycle(3, "https://www.youtube.com")


if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"--- {str((time.time() - start_time) / 60)[0:4]} Minutes ---")
