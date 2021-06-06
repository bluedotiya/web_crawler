from RTB_Class import Requester, Parser, Buffer
import os


def depth_cycle(depth, root_url):
    for depth in range(1, depth + 1):
        os.mkdir(f"Depth{depth}")
        if depth == 1:
            rtb_cycle(depth, root_url)
        else:
            if len(os.walk(f"Depth{depth - 1}").__next__()[1]) == 1:
                parent_url_counter = 1
                with open(f"./Depth{depth - 1}/Parent{parent_url_counter}/Child_Urls_{parent_url_counter}.txt", "r") as url_file:
                    for url in url_file.readlines():
                        rtb_cycle(depth, url[:-1], parent_url_counter)
                        parent_url_counter += 1
            else:
                for parent_folder in set([int(name.replace('Parent', '')) for name in os.walk(f"Depth2").__next__()[1]]):
                    parent_url_counter = 1
                    with open(f"./Depth{depth - 1}/Parent{parent_folder}/Child_Urls_{parent_folder}.txt",
                          "r") as url_file:
                        url_file_content = url_file.readlines()
                        if type(url_file_content) == list :
                            for url in url_file_content:
                                rtb_cycle(depth, url[:-1], parent_url_counter)
                                parent_url_counter += 1


def rtb_cycle(depth=1, url="https://www.google.com/", url_list_counter=1):
    response_tuple = Requester(f"{url}").request()
    html_content, time_elapsed = response_tuple
    url_list = Parser(html_content).extract()
    buffer = Buffer(url, url_list, depth, time_elapsed, url_list_counter)
    buffer.save()


def main():
    depth_cycle(3, "https://www.google.com/search?q=random&sxsrf=ALeKk02dTZ6AmqHNAEcYzyhdVVpyoUi1Mg%3A1622768275768&source=hp&ei=k3q5YP2vLKaN9u8P4suciAo&iflsig=AINFCbYAAAAAYLmIo9YtRtSo9ycAJGcQK1gA2c74XNjc&oq=random&gs_lcp=Cgdnd3Mtd2l6EAMyBQgAEMsBMgQIABBDMgUIABDLATIFCAAQywEyBQgAEMsBMgUIABDLATIFCAAQywEyBQgAEMsBMgUIABDLATIFCAAQywE6BAgjECc6CAguELEDEIMBOgUIABCxAzoICAAQsQMQgwE6CQgAELEDEAoQAToCCAA6BggjECcQEzoFCC4QsQM6CwgAELEDEMcBEKMCOgIILlD7FFjjG2ChHWgAcAB4AIABvwGIAZYIkgEDMC42mAEAoAEBqgEHZ3dzLXdpeg&sclient=gws-wiz&ved=0ahUKEwi9xYL14vzwAhWmhv0HHeIlB6EQ4dUDCAY&uact=5")


if __name__ == "__main__":
    main()
