import networkx as nx
import matplotlib.pyplot as plt
import json
import os


def create_graph_object():
    return nx.Graph()


def data_to_node(graph_object, node_size, nodes_position_file):
    with open(nodes_position_file, "r") as json_file:
        node_counter = 0
        for line in json_file:
            line_dict = json.loads(line)
            x_pos, y_pos = line_dict['son_url']['pos'][0], line_dict['son_url']['pos'][1]
            domain_name = line_dict['son_url']['url'].split('.')[-2]
            parent_url = line_dict['parent_url']
            son_url = line_dict['son_url']['url']
            graph_object.add_node(node_counter, pos=(float(x_pos), float(y_pos)), size=node_size, dname=domain_name,
                                  url=domain_name , parent=parent_url, son=son_url)
            node_counter += 1
    pos = nx.get_node_attributes(graph_object, 'pos')
    size_dict = nx.get_node_attributes(graph_object, 'size')
    size_list = [size for size in size_dict.values()]
    label_dict = nx.get_node_attributes(graph_object, 'url')
    return pos, size_list, label_dict


def nodes_to_edges(graph_object):
    for node_checker in graph_object.nodes.items():
        for node_runner in graph_object.nodes.items():
            if node_runner[1]['parent'] == node_checker[1]['son']:
                start_edge = node_runner[0]
                end_edge = node_checker[0]
                graph_object.add_edge(start_edge, end_edge)


def drawer(node_size, nodes_pos_file, font_size, node_color, show_label, save):
    graph = create_graph_object()
    pos_dict, size_list, label_dict = data_to_node(graph, node_size, nodes_pos_file)
    nodes_to_edges(graph)
    nx.draw(graph, pos_dict, labels=label_dict, node_size=size_list, with_labels=show_label, font_size=font_size, node_color=node_color)
    if not save:
        plt.show()
    else:
        file_name_count = 1
        while True:
            file_name_ext = ".png"
            if f"{file_name_count}{file_name_ext}" in os.listdir("."):
                file_name_count += 1
            else:
                save_file_name = f"{file_name_count}{file_name_ext}"
                break
        plt.savefig(save_file_name, bbox_inches='tight', dpi=400)
