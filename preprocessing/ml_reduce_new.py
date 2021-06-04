import numpy as np
import xgboost as xgb
import networkx as nx

from features import features
from loading_utils import metis_format_to_nx, write_nx_in_metis_format, search_for_graphs, get_graphs_and_labels, \
    get_dmatrix_from_graphs

from datetime import date
import os
import subprocess


# mtxe first graph no convergence of eigenvectors ... strange

# only run on first graph of them all
graph_paths = search_for_graphs([], graph_folder="/home/graph_collection/independentset_instances/")[:10]
graph_paths = list(
    filter(lambda path: path[path.rfind("/") + 1:] != "auto-sorted.graph", graph_paths))

OUTPUT_FOLDER = "/home/jholten/kernels/ml_reduce_kernels/"

graphs = get_graphs_and_labels(graph_paths, no_labels=True)

data = get_dmatrix_from_graphs(graphs, no_labels=True)

bst = xgb.Booster({'nthread': 16})
bst.load_model("first-10_2021-04-11.model")

num_stages = 5
q = 0.98   # confidence niveau

for graph in graphs:
    graph.graph['removals'] = []
    graph.graph['old_number_of_nodes'] = graph.number_of_nodes()

print("reducing graphs:")
for stage in range(1, num_stages+1):
    print(f"stage {stage}")
    label_pred = bst.predict(data)

    for graph in graphs:
        print(f"{graph.graph['kw']} ...")
        removal = np.array(graph.nodes)[label_pred <= 1 - q]
        graph.remove_nodes_from(removal)
        graph.graph['removals'].append(len(removal))
        print("done.")

    print("recalculating features...")
    data = get_dmatrix_from_graphs(graphs, no_labels=True)
    print("done.")

# removing self loops
print("removing self loops")
for graph in graphs:
    print(f"{graph.graph['kw']} ...")
    self_loops = nx.selfloop_edges(graph)
    print(f"self loops {list(self_loops)}")
    graph.remove_edges_from(self_loops)
    print("done.")

for graph in graphs:
    print(f"in graph {graph.graph['kw']} removed a total of {sum(graph.graph['removals'])} nodes, {sum(graph.graph['removals'])/graph.graph['old_number_of_nodes'] * 100 :.4f}%", "(", *graph.graph['removals'], ")")
    ml_reduction_path = OUTPUT_FOLDER + graph.graph['kw'][:-6] + ".ml_kernel"
    print(f"writing {graph.graph['kw']} to {ml_reduction_path} ...")
    write_nx_in_metis_format(graph, ml_reduction_path)
    print("done.")
