import subprocess
import sys
import os

import numpy as np
import xgboost as xgb
from cpp_preprocessing import cpp_features, Logger, write
from os.path import basename

# mtxe first graph no convergence of eigenvectors ... strange

# only run on first graph of them all
GRAPH_PATH = sys.argv[1]
q = float(sys.argv[2])

KERNEL_FOLDER = "/home/jholten/kernels/ml_reduce_kernels/"

# list of nodes that have been removed
removed = np.array([])

bst = xgb.Booster({'nthread': 16})
bst.load_model("2021-07-01_09-47-28.model")

num_stages = 1
#q = 0.98   # confidence niveau

with open(GRAPH_PATH) as graph_file:
    line = graph_file.readline()
    while line[0]=="%":  # skip comments at start
        line = graph_file.readline()
    number_of_nodes = int(line.split()[0])   # number of nodes is first number in first line

reduction_path = ""
#logger.log("reducing graph:")
for stage in range(1, num_stages+1):
    #logger.log(f"stage {stage}")

    # calculate and write features to feature_path
    reduction_path = cpp_features(GRAPH_PATH, "/home/jholten/graph_files/", removed=removed)

    # load features and labels into a dmatrix

    feature_path = "/home/jholten/graph_files/" + os.path.basename(GRAPH_PATH) + ("." + reduction_path.split(".")[-1] if len(removed) != 0 else "") + ".feat" 
    feature_matrix = xgb.DMatrix(data=np.loadtxt(feature_path))

    # predict based on the features
    label_pred = bst.predict(feature_matrix)

    # remove if prediction lower than threshold
    removed = np.array(np.where(label_pred <= 1 - q))[0]
    print(len(removed))

#logger.log(f"in graph {basename(GRAPH_PATH)} removed a total of {len(removed)} nodes, {len(removed)/number_of_nodes * 100:.4f}%", "(", *removed, ")")
ml_reduction_path = KERNEL_FOLDER + basename(GRAPH_PATH) + ".ml_kernel" + str(int(q*100))
print("writing to", ml_reduction_path)
write(reduction_path, ml_reduction_path, removed)
