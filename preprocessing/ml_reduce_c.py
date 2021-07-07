import sys
import os

import numpy as np
import xgboost as xgb
from cpp_preprocessing import cpp_features, write, weight_nodes
from os.path import basename

# only run on first graph of them all
GRAPH_PATH = sys.argv[1]
q = float(sys.argv[2])

bst = xgb.Booster({'nthread': 16})
bst.load_model("2021-07-01_09-47-28.model")

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
total_removed = np.array([])

num_stages = 5
for stage in range(1, num_stages + 1):
    # calculate features and store them in the "/graph_files/" folder, reduce the graph and write the reduced graph
    # to reduction_path
    reduction_path = cpp_features(GRAPH_PATH, "/home/jholten/graph_files/", removed=total_removed)

    # load features into a dmatrix
    feature_path = "/home/jholten/graph_files/" + os.path.basename(GRAPH_PATH) + (
        "." + reduction_path.split(".")[-1] if len(total_removed) != 0 else "") + ".feat"
    feature_matrix = xgb.DMatrix(data=np.loadtxt(feature_path))

    # predict based on the features
    label_pred = bst.predict(feature_matrix)

    # remove if prediction lower than threshold
    total_removed = np.append(total_removed, np.array(np.where(label_pred <= 1 - q))[0])

print(f"removed in total {len(total_removed)} nodes ({len(total_removed)/number_of_nodes*100:.2%})")

#if has_node_weights:
    #print(f"with offset {weight_nodes(GRAPH_PATH, total_removed)}")

KERNEL_FOLDER = "/home/jholten/kernels/ml_reduce_kernels/"

ml_reduction_path = KERNEL_FOLDER + basename(GRAPH_PATH) + ".ml_kernel" + str(int(q * 100))
print("writing kernel to", ml_reduction_path)
write(reduction_path, ml_reduction_path, total_removed)
