import networkx as nx
import matplotlib.pyplot as plt
import json

G = nx.Graph()

with open("Nodes_Position_Data.txt", "r") as json_file:
    node_counter = 0
    for line in json_file:
        line_dict = json.loads(line)
        x_pos, y_pos = line_dict['son_url']['pos'][0], line_dict['son_url']['pos'][1]
        domain_name = line_dict['son_url']['url'].split('.')[-2] + "." + line_dict['son_url']['url'].split('.')[-1]
        url_link = line_dict['son_url']['url'].split('/')[2]
        parent_url = line_dict['parent_url']
        son_url = line_dict['son_url']['url']
        G.add_node(node_counter, pos=(float(x_pos), float(y_pos)), size=100, dname=domain_name, url=url_link,
                   parent=parent_url, son=son_url)
        node_counter += 1

pos = nx.get_node_attributes(G, 'pos')
size_dict = nx.get_node_attributes(G, 'size')
size_list = [size for size in size_dict.values()]
size_outline_list = [size + 20 for size in size_dict.values()]
url = nx.get_node_attributes(G, 'url')
parent_dict = nx.get_node_attributes(G, 'parent')
for node_checker in G.nodes.items():
    for node_runner in G.nodes.items():
        if node_runner[1]['parent'] == node_checker[1]['son']:
            start_edge = node_runner[0]
            end_edge = node_checker[0]
            G.add_edge(start_edge, end_edge)

nx.draw_networkx(G, pos, labels=url, node_size=size_outline_list, with_labels=True, font_size=6, node_color='r')
nx.draw_networkx(G, pos, node_size=size_list, with_labels=False, node_color='g')
nx.draw_networkx_edges(G, pos, width=0.2, alpha=0.5)

plt.show()
# plt.savefig('figure1.png', bbox_inches='tight')
