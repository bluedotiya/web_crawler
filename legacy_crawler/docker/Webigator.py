import WebCrawler
import Node_Generator
import networksX
import os
from shutil import rmtree

def crawl(crawl_depth, root_url):
	WebCrawler.depth_cycle(crawl_depth, root_url)


def calculate(calculate_depth, is_positive_graph, vector_file_name, nodes_pos_file):
	Node_Generator.generator(calculate_depth, vector_file_name)
	Node_Generator.nodes_calculator(is_positive_graph, vector_file_name, nodes_pos_file)


def draw(nodes_size, nodes_pos_file, font_size, node_color, save, label):
	networksX.drawer(nodes_size, nodes_pos_file, font_size, node_color, save, label)


def webigator(crawl_depth=2, root_url="https://www.google.com/", calculate_only=False, is_positive_graph=False, vector_file="output/vector_file.txt",
	nodes_file="output/nodes_file.txt", node_size=100, node_label_size=7, show_label=True, nodes_color="r", save_graph=True):
	crawl(crawl_depth, root_url)
	calculate(crawl_depth, is_positive_graph, vector_file, nodes_file)
	draw(node_size, nodes_file, node_label_size, nodes_color, show_label, save_graph)


def main():
	try:
		os.mkdir("output")
	except FileExistsError:
		dir = 'output'
		for files in os.listdir(dir):
			path = os.path.join(dir, files)
			try:
				rmtree(path)
			except OSError:
				os.remove(path)
	if (os.environ.get('URL') is not None) and (os.environ.get('DEPTH') is not None):
		url_str = str(os.environ.get('URL'))
		crawl_depth_int = int(os.environ.get('DEPTH'))
		print(f"Starting \n - URL: {url_str} \n - Depth: {crawl_depth_int}")
		webigator(crawl_depth=crawl_depth_int, root_url=url_str)
		print("Done")
	else:
		print("Args not provided\n - Starting with Default Parameters\n - URL: https://www.google.com \n - Depth: 2")
		webigator()
		print("Done")
		

if __name__ == "__main__":
	main()

