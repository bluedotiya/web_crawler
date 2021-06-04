import os
import math
import itertools
for num in range(1, 4):
    for depth in os.walk(f"Depth{num}").__next__()[1]:
        for parent in os.walk(f"./Depth{num}/.").__next__()[1]:
            if os.walk(f"./Depth{num}/{parent}").__next__()[2].__len__() == 2:
                parent_url = os.walk(f"./Depth{num}/{parent}").__next__()[2][1]
            else:
                parent_url = os.walk(f"./Depth{num}/{parent}").__next__()[2][0]
            with open(f"./Depth{num}/{parent}/{parent_url}", 'r') as parent_file:
                sub_domain = ''
                sub_domain_sum = 0
                theta_angle = 0
                domain_name = ''
                top_level_domain = ''
                node_pose = []
                parent_file_data = parent_file.readlines()
                if type(parent_file_data) == list and parent_file_data.__len__() == 2:
                    url_string, time_delay = parent_file_data[0], parent_file_data[1]
                    vector_length = time_delay
                else:
                    continue
                url = ((url_string.replace('\n', '').replace('https://', '')).replace('http://', '')).replace('/', '')
                splited = url.split('.')
                if splited.__len__() == 3:
                    sub_domain, domain_name, top_level_domain = splited
                    for char in sub_domain:
                        sub_domain_sum += ord(char)
                    theta_angle = sub_domain_sum % 360
                    x_pos = math.sin(math.radians(90 - theta_angle)) * float(vector_length)
                    y_pos = math.sin(math.radians(theta_angle)) * float(vector_length)
                    if 0 <= theta_angle <= 90:
                        node_pose = f"{x_pos}:{y_pos}"
                    elif 90 < theta_angle <= 180:
                        node_pose = f"{-1.0 * x_pos}:{y_pos}"
                    elif 180 < theta_angle <= 270:
                        node_pose = f"{-1.0 * x_pos}:{-1.0 * y_pos}"
                    elif 270 < theta_angle < 360:
                        node_pose = f"{x_pos}:{-1.0 * y_pos}"
                    with open("Nodes_Data_duplicated.txt", "a") as nodes_file:
                        nodes_file.write(
                            f"{sub_domain}.{domain_name}.{top_level_domain},{node_pose}\n")
                else:
                    continue
count = 0
with open('Nodes_Data_duplicated.txt', 'rb') as input:
    with open('Nodes_Data.csv', 'wb') as output:
        for key,  group in itertools.groupby(sorted(input)):
            output.write(bytes(str(count) + ',' + str(key, 'ASCII'), 'ASCII'))
            count += 1
os.remove("Nodes_Data_duplicated.txt")

