import os
import json
import math
import itertools


def generator(depth):
    for level in range(1, depth + 1):
        for parent_folder in set([int(name.replace('Parent', '')) for name in os.walk(f"Depth{level}").__next__()[1]]):
            with open(f"Depth{level}/Parent{parent_folder}/Parent_Url_{parent_folder}.txt", "r") as url_file:
                file_content = url_file.readlines()
                file_content_no_newline = [url.replace('\n', '') for url in file_content]
                if file_content_no_newline[2] != "FAIL":
                    fcnn = file_content_no_newline
                    node_dict = vector_calculator(fcnn[0], fcnn[1], fcnn[2])
                    if node_dict is not None:
                        with open('Nodes_Data.txt', 'a') as node_file:
                            json_object = json.dumps(node_dict)
                            node_file.write(f"{json_object}\n")


def vector_calculator(son_url, parent_url, time):
    domain_sum = 0
    vector_length = time
    url_string = son_url
    url = url_string.split('/')[2]
    splited = url.split('.')
    if splited.__len__() == 3:
        sub_domain, domain_name, top_level_domain = splited
        for char in f"{domain_name}.{top_level_domain}":
            domain_sum += ord(char)
        theta_angle = domain_sum % 360
        return {"son_url" : {"url" : son_url, "theta" : int(theta_angle), "vector_len" : float(vector_length)},
                "parent_url" : parent_url}


def node_calculator(is_pos_graph):
    list_of_dicts = []
    with open('Nodes_Data.txt', 'r') as node_data_file:
        for data in node_data_file.readlines():
            json_str = data.replace('\n', '')
            dict_data = json.loads(json_str)
            list_of_dicts.append(dict_data)
        for node_dict in list_of_dicts:
            son_url = node_dict['son_url']['url']
            parent_url = node_dict['parent_url']
            theta_angle = node_dict['son_url']['theta']
            vector_length = node_dict['son_url']['vector_len']
            x_pos = math.sin(math.radians(90 - theta_angle)) * float(vector_length)
            y_pos = math.sin(math.radians(theta_angle)) * float(vector_length)
            if not is_pos_graph or 0 <= theta_angle <= 90:
                node_pose = [x_pos, y_pos]
            elif 90 < theta_angle <= 180:
                node_pose = [-1.0 * x_pos, y_pos]
            elif 180 < theta_angle <= 270:
                node_pose = [-1.0 * x_pos, -1.0 * y_pos]
            elif 270 < theta_angle < 360:
                node_pose = [x_pos, -1.0 * y_pos]
            if parent_url == "Root":
                with open('Nodes_Position_Data.txt', 'a') as nodes_pos_file:
                    node_output_data = {"son_url" : {"url" : son_url, "pos" : node_pose}, "parent_url" : parent_url}
                    nodes_pos_file.write(f"{json.dumps(node_output_data)}\n")
            else:
                with open('Nodes_Position_Data.txt', 'r') as nodes_data_file:
                    for line in nodes_data_file.readlines():
                        line_dict = json.loads(line)
                        if son_url == line_dict['son_url']['url']:
                            node_output_data = line_dict
                            break
                        elif parent_url == line_dict['son_url']['url']:
                            combined_poses = node_pose[0] + line_dict['son_url']['pos'][0],\
                                             node_pose[1] + line_dict['son_url']['pos'][0]
                            node_output_data = {"son_url": {"url": son_url, "pos": combined_poses},
                                                "parent_url": parent_url}
                            break
                with open('Nodes_Position_Data.txt', 'a') as nodes_pos_file:
                    nodes_pos_file.write(f"{json.dumps(node_output_data)}\n")


def main():
    generator(3)
    node_calculator(False)


if __name__ == "__main__":
    main()
