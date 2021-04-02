import os
import sys
from loading_utils import search_for_graphs
import subprocess

""" Usage: python calc_kernels.py <graph_folder> <kernel_folder> [graph_keyword1 graph_keyword2 ...] """ 

assert len(sys.argv) >= 2, "Usage: python calc_kernels.py <graph_folder> <kernel_folder> [graph_keyword1 graph_keyword2 ...]"
graph_folder = os.path.abspath(sys.argv[1])
kernel_folder = os.path.abspath(sys.argv[2])
keyword_list = sys.argv[3:]

graph_paths = search_for_graphs(keyword_list, graph_folder=graph_folder)
for graph_path in graph_paths:
    print("calculating kernel of", graph_path)
    graph_name = graph_path[len(graph_folder):-6] 
    subprocess.run(["deploy/weighted_branch_reduce", graph_path, "--output_kernel=" + kernel_folder + graph_name + ".kernel"])
