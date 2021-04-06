import os
import sys
from loading_utils import search_for_graphs
import subprocess
import itertools

def intersperse(iterable, delimiter):
    it = iter(iterable)
    yield next(it)
    for x in it:
        yield delimiter
        yield x

usage_doc = f""" Usage: python {sys.argv[0]} <graph_folder> [--kernels=KERNEL_FOLDER] [--mis=MIS_FOLDER] [graph_keyword1 graph_keyword2 ...] """ 

graph_folder_DEFAULT = "/home/graph_collection/independentset_instances/" 
kernel_folder_DEFAULT = "/home/jholten/kernels/" 
mis_folder_DEFAULT = "/home/jholten/mis/"

# print help
if any([arg == "-h" or arg == "--help" for arg in sys.argv]):
    print(usage_doc)
    sys.exit()

# too few arguments
if len(sys.argv) < 2:
    response = input(f"too few arguments, use default values (graph_folder={graph_folder_DEFAULT}, kernel_folder={kernel_folder_DEFAULT}, mis_folder={mis_folder_DEFAULT})? Y/n: ")
    if response.lower() in {"", "y"}:
        graph_folder = graph_folder_DEFAULT
        kernel_folder = kernel_folder_DEFAULT 
        calc_kernel = True
        mis_folder = mis_folder_DEFAULT
        calc_mis = True
        keyword_list = []
    else:
        print(usage_doc)
        sys.exit()

kernel_folder = ""
mis_folder = ""

# regular program
graph_folder = os.path.abspath(sys.argv[1])
options = [[option[option.index('=')+1:] for option in sys.argv[2:] if option.find("=") != -1 and option[:option.index('=')] == specifier] for specifier in ["--kernels", "--mis"]]

assert all(map(lambda x: len(x)<=1, options)), "used options multiple times. exiting."

calc_kernel, calc_mis = map(lambda x: len(x) == 1, options)

assert any([calc_kernel, calc_mis]), "no jobs given. exiting."

if calc_kernel:
    if options[0][0] == "": # meaning kernel option was passed with no path
        kernel_folder = graph_folder
    else:
        kernel_folder = os.path.abspath(*options[0]) if calc_kernel and not kernel_folder else ""
else:
    kernel_folder = ""

if calc_mis: 
    if options[1][0] == "": # meaning mis option was passed with no path
        mis_folder = graph_folder
    else:
        mis_folder = os.path.abspath(*options[1]) if calc_mis and not mis_folder else ""
else:
    mis_folder = ""

keyword_list = [arg for arg in sys.argv[2:] if not any([arg[:len(specifier)] == specifier for specifier in ["--kernels", "--mis"]])] 
print("keyword_list:", keyword_list)

graph_paths = search_for_graphs(keyword_list, graph_folder=graph_folder)
if not graph_paths:
    print("no graphs found.")

with open("run_kamis_mis", "w") as mis_file, open("run_kamis_kernel", "w") as kernel_file:
    for idx, graph_path in enumerate(graph_paths, start=1):
        print(f"graph #{idx}/{len(graph_paths)}, path: {graph_path}")
        graph_name = graph_path[len(graph_folder):-6] 

        if calc_kernel:
            kernel_path = kernel_folder + graph_name + ".kernel"
            if os.path.isfile(kernel_path) and os.path.getsize(kernel_path) > 0:   # kernel file does exist and isn't empty
                print("already calculated kernel")
            else:
                print("calculating kernel")
                kernel_file.write(f"deploy/weighted_branch_reduce {graph_path} --kernel={kernel_path} --time_limit=3600 --weight_source=uniform\n")

        if calc_mis:
            mis_path = mis_folder + graph_name + ".MIS"
            if os.path.isfile(mis_path) and os.path.getsize(mis_path) > 0:
                print("already calculated MIS")
            else:
                print("calculating MIS")
                mis_file.write("deploy/weighted_branch_reduce graph_path --output={mis_path} --time_limit=3600 --weight_source=uniform\n")

