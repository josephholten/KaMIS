import numpy as np
import xgboost as xgb

from features import features
from loading_utils import metis_format_to_nx, write_nx_in_metis_format, search_for_graphs, get_graphs_and_labels, get_dmatrix_from_graphs

from datetime import date
import os
import subprocess


# mtxe first graph no convergence of eigenvectors ... strange

graph_paths = search_for_graphs([], graph_folder="/home/graph_collection/independentset_instances/mtxe")[:1]
label_paths = ["/home/jholten/mis/kamis_results/" + os.path.basename(path)[:-6] + ".uniform.mis" for path in graph_paths]

OUTPUT_FOLDER = "/home/jholten/kernels/ml_reduce_kernels/"

graphs = get_graphs_and_labels(graph_paths, label_paths)

data = get_dmatrix_from_graphs(graphs)

bst = xgb.Booster({'nthread': 16})
bst.load_model("first-10_2021-04-11.model")

num_stages = 5
q = 0.98   # confidence niveau

for graph in graphs:
    graph.graph['removals'] = []
    graph.graph['old_number_of_nodes'] = graph.number_of_nodes()

print("reducing graphs")
for stage in range(1, num_stages+1):
    print(f"stage {stage}")
    label_pred = bst.predict(data)
    # np.savetxt(f"{date.today()}prediction_stage{stage}.pred", label_pred)

    for graph in graphs:
        print(f"{graph.graph['kw']} ...")
        removal = np.array(graph.nodes)[label_pred <= 1 - q]
        graph.remove_nodes_from(removal)
        graph.graph['labels'] = graph.graph['labels'][np.where(label_pred > q)[0]]  # remove labels of removed nodes in test graph
        graph.graph['removals'].append(len(removal))
        print("done.")

    print("recalculating features...")
    data = get_dmatrix_from_graphs(graphs)
    print("done.")

for graph in graphs:
    print(f"in graph {graph.graph['kw']} removed a total of {sum(graph.graph['removals'])} nodes, \
            {sum(graph.graph['removals'])/graph.graph['old_number_of_nodes'] * 100 :.4f}%", "(", *graph.graph['removals'], ")")
    ml_reduction_path = OUTPUT_FOLDER + graph.graph['kw'][:-6] + ".ml_kernel"
    print(f"writing {graph.graph['kw']} to {ml_reduction_path} ...")
    write_nx_in_metis_format(graph, ml_reduction_path)
    print("done.")
