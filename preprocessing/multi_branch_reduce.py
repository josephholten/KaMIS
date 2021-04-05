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
        kernel_folder = os.path.abspath(*options[0]) if calc_kernel else ""
else:
    kernel_folder = ""

if calc_mis: 
    if options[1][0] == "": # meaning mis option was passed with no path
        mis_folder = graph_folder
    else:
        mis_folder = os.path.abspath(*options[1]) if calc_mis else ""
else:
    mis_folder = ""

keyword_list = [arg for arg in sys.argv[2:] if arg not in set(itertools.chain.from_iterable(options))]

graph_paths = search_for_graphs(keyword_list, graph_folder=graph_folder)
for idx, graph_path in enumerate(graph_paths, start=1):
    print(f"graph #{idx}, path: {graph_path}")
    graph_name = graph_path[len(graph_folder):-6] 
    kernel_path = kernel_folder + graph_name + ".kernel"
    mis_path = mis_folder + graph_name + ".MIS"

    job_str = ""
    job_options = []

    if calc_kernel:
        if os.path.isfile(kernel_path) and os.path.getsize(kernel_path) > 0:   # kernel file does exist and isn't empty
            print("already calculated kernel")
        else:
            job_str += "kernel"
            job_options += ["--kernel=" + kernel_path]

    if job_str:
        job_str += " and "

    if calc_mis:
        if os.path.isfile(mis_path) and os.path.getsize(mis_path) > 0:
            print("already calculated MIS")
        else:
            job_str += "mis"
            job_options += ["--output=" + mis_path]

    if job_options:
        print("calculating", job_str)
        subprocess.run(["deploy/weighted_branch_reduce", graph_path, *job_options])
    else:
        print("skipping")
