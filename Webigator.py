import WebCrawler
import Node_Generator
import networksX
import os
import shutil
import time


def crawl(crawl_depth, root_url):
	WebCrawler.depth_cycle(crawl_depth, root_url)


def calculate(calculate_depth, is_positive_graph, vector_file_name, nodes_pos_file):
	Node_Generator.generator(calculate_depth, vector_file_name)
	Node_Generator.nodes_calculator(is_positive_graph, vector_file_name, nodes_pos_file)


def draw(nodes_size, nodes_pos_file, font_size, node_color, save, label):
	networksX.drawer(nodes_size, nodes_pos_file, font_size, node_color, save, label)


def webigator(crawl_depth, root_url, calculate_only=False, is_positive_graph=True, vector_file="vector_file.txt",
	nodes_file="nodes_file.txt", node_size=100, node_label_size=7, show_label=True, nodes_color="b", save_graph=False):
	if not calculate_only:
		time.sleep(2)
		for i in range(1, 10):
			shutil.rmtree(f"Depth{i}", True)
		try:
			os.remove(vector_file)
			os.remove(nodes_file)
		except:
			pass
		time.sleep(2)
		crawl(crawl_depth, root_url)
	calculate(crawl_depth, is_positive_graph, vector_file, nodes_file)
	draw(node_size, nodes_file, node_label_size, nodes_color, show_label, save_graph)


def main():
	webigator(4, "https://www.google.com/", calculate_only=True, save_graph=False)


if __name__ == "__main__":
	main()

