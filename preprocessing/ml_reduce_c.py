import sys
import os

import numpy as np
import xgboost as xgb
from cpp_preprocessing import cpp_features, write, weight_nodes, get_neighbors
from os.path import basename
from time import time

start = time()

# only run on first graph of them all
GRAPH_PATH = sys.argv[1]
q = float(sys.argv[2])

bst = xgb.Booster({'nthread': 16})
bst.load_model("2021-07-09_15-05-56.model")

with open(GRAPH_PATH) as graph_file:
    line = graph_file.readline()
    while line[0] == "%":  # skip comments at start
        line = graph_file.readline()
    header = list(map(int, line.split()))
    number_of_nodes = header[0]  # number of nodes is first number in first line
    if len(header) == 3:
        has_node_weights = bool(int(line.split()[2]) & 2)
    else:
        has_node_weights = False

# where the reduced graph is stored
reduction_path = ""
exists = np.ones(number_of_nodes)
total_added = np.array([])

num_stages = 5
for stage in range(1, num_stages + 1):
    #print(f"{stage=}")
    # calculate features and store them in the "/graph_files/" folder, reduce the graph and write the reduced graph
    # to reduction_path
    reduction_path = cpp_features(GRAPH_PATH, "/home/jholten/graph_files/", exists=exists)

    # load features into a dmatrix
    removed = np.where(exists == 0)
    feature_path = "/home/jholten/graph_files/" + os.path.basename(GRAPH_PATH) + (
        "." + reduction_path.split(".")[-1] if len(removed) != 0 else "") + ".feat"
    feature_matrix = xgb.DMatrix(data=np.loadtxt(feature_path))

    # predict based on the features
    label_pred = bst.predict(feature_matrix)

    # remove if prediction lower than threshold
    exists[np.where(label_pred <= 1 - q)[0]] = 0

    # add to MIS if prediction is higher than threshold
    likely = np.where(label_pred >= q)[0]
    # decending sort the likely candidates based on their predicted value
    for node in np.flip(likely[np.argsort(label_pred[likely])]):
        # if it still exists, keep it, and remove its neighbors
        if exists[node]:
            total_added = np.append(total_added, node)
            exists[get_neighbors(GRAPH_PATH, [node])] = 0

KERNEL_FOLDER = "/home/jholten/kernels/ml_reduce_kernels/"

end = time()

print("elapsed time:", end - start)

ml_reduction_path = KERNEL_FOLDER + basename(GRAPH_PATH) + ".ml_kernel" + str(int(q * 100))
print("writing kernel to", ml_reduction_path)
number_removed = write(GRAPH_PATH, ml_reduction_path, exists)
print(f"removed in total {number_removed} nodes ({number_removed/number_of_nodes:.2%})")

# save the added nodes to a file and print offset
offset_weight = weight_nodes(GRAPH_PATH, total_added)
print(f"with offset {offset_weight}")

np.savetxt(KERNEL_FOLDER + basename(GRAPH_PATH) + ".ml_offset" + str(int(q*100)), total_added, header=f"% {offset_weight}")
