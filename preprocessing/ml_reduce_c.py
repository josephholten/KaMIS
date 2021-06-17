import subprocess
import sys

import numpy as np
import xgboost as xgb
from cpp_preprocessing import cpp_features, Logger
from os.path import basename

# mtxe first graph no convergence of eigenvectors ... strange

# only run on first graph of them all
GRAPH_PATH = sys.argv[1]

logger = Logger()  # commandline argument

KERNEL_FOLDER = "/home/jholten/kernels/ml_reduce_kernels/"

# list of nodes that have been removed
removed = np.array([])

bst = xgb.Booster({'nthread': 16})
bst.load_model("first-10_2021-04-11.model")

num_stages = 5
q = 0.98   # confidence niveau

with open(GRAPH_PATH) as graph_file:
    number_of_nodes = int(graph_file.readline().split()[0])   # number of nodes is first number in first line

last_reduction_path = ""
logger.log("reducing graph:")
for stage in range(1, num_stages+1):
    logger.log(f"stage {stage}")

    # calculate and write features to feature_path
    feature_path, reduction_path = cpp_features(GRAPH_PATH, removed=removed)
    # load features and labels into a dmatrix
    feature_matrix = xgb.DMatrix(data=np.loadtxt(feature_path))

    # predict based on the features
    label_pred = bst.predict(feature_matrix)

    # remove if prediction lower than threshold
    removed = np.append(removed, np.where(label_pred <= 1 - q))

logger.log(f"in graph {basename(GRAPH_PATH)} removed a total of {len(removed)} nodes, {len(removed)/number_of_nodes * 100:.4f}%", "(", *removed, ")")
ml_reduction_path = KERNEL_FOLDER + basename(GRAPH_PATH) + ".ml_kernel"
subprocess.run(["cp", last_reduction_path, ml_reduction_path])
