import networkx as nx
import matplotlib.pyplot as plt
import csv
G = nx.Graph()

with open("Nodes_Data.csv", "r") as csv_file:
    csv_iter = csv.reader(csv_file)
    for line in csv_iter:
        x_pos, y_pos = line[2].split(':')
        domain_name = line[1].split('.')[1] + "." + line[1].split('.')[2]
        url_link = line[1].split('.')[1]
        G.add_node(line[0], pos=(float(x_pos), float(y_pos)), size=100, dname=domain_name, url=url_link)


pos = nx.get_node_attributes(G, 'pos')
size_dict = nx.get_node_attributes(G, 'size')
size_list = [size for size in size_dict.values()]
size_outline_list = [size+20 for size in size_dict.values()]
url = nx.get_node_attributes(G, 'url')
dname_dict = nx.get_node_attributes(G, 'dname')
for node_num in dname_dict:
    node_value_count = 0
    for node_value in dname_dict.values():
        if dname_dict[node_num] == node_value:
            G.add_edge(node_num, str(node_value_count))
        node_value_count += 1
nx.draw_networkx(G, pos, labels=url, node_size=size_outline_list, with_labels=False, font_size=6, node_color='r')
nx.draw_networkx(G, pos, node_size=size_list, with_labels=False, node_color='g')
nx.draw_networkx_edges(G, pos, width=0.2, alpha=0.5)
plt.axis(True)
plt.show()
plt.savefig('figure1.png', bbox_inches='tight')

