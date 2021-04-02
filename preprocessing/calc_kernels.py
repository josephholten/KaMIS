import os
import sys
from loading_utils import search_for_graphs
import subprocess

usage_doc = """ Usage: python calc_kernels.py <graph_folder> <kernel_folder> [graph_keyword1 graph_keyword2 ...] """ 

graph_folder_DEFAULT = "/home/graph_collections/independentset_instances" 
kernel_folder_DEFAULT = "/home/jholten/kernels" 


if any([arg == "-h" or arg == "--help" for arg in sys.argv]):
    print(usage_doc)
    sys.exit()

if len(sys.argv) < 2:
    response = input(f"too few arguments, use default values (graph_folder={graph_folder_DEFAULT}, kernel_folder={kernel_folder_DEFAULT})? Y/n")
    if response.lower() in {"", "y"}:
        graph_folder = graph_folder_DEFAULT
        kernel_folder = kernel_folder_DEFAULT 
    else:
        print(usage_doc)
        sys.exit()
else:
    graph_folder = os.path.abspath(sys.argv[1])
    kernel_folder = os.path.abspath(sys.argv[2])
    keyword_list = sys.argv[3:]

graph_paths = search_for_graphs(keyword_list, graph_folder=graph_folder)
for graph_path in graph_paths:
    graph_name = graph_path[len(graph_folder):-6] 
    kernel_path = kernel_folder + graph_name + ".kernel"
    if os.path.isfile(kernel_path) and os.path.getsize(kernel_path) > 0:
        print("calculating kernel of", graph_path)
        subprocess.run(["deploy/weighted_branch_reduce", graph_path, "--output_kernel=" + kernel_path])
    else:
        print("already calculated kernel of", graph_path)
