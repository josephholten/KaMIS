import os
import sys
import copy 
import subprocess
import numpy as np
import networkx as nx
import xgboost as xgb

from features import features
from loading_utils import metis_format_to_nx, search_for_graphs, get_graphs_and_labels, get_dmatrix_from_graphs

training_graphs_paths = search_for_graphs(["bay", "col", "fla"], exclude=True, graph_folder="/home/graph_collection/independentset_instances/")
training_graphs_paths = list(filter(lambda path: path[path.rfind("/")+1:] != "ny-sorted.graph", training_graphs_paths))

label_paths = ["/home/jholten/mis/kamis_results/" + path[path.rfind("/")+1:-len(".graph")] + ".uniform.mis" for path in training_graphs_paths]

# print(training_graphs_paths)
# print(label_paths)
training_graphs = get_graphs_and_labels(training_graphs_paths, label_paths)


if len(training_graphs) < 1:
    print("no training graphs provided, terminating...")
    sys.exit()

dtrain = get_dmatrix_from_graphs(training_graphs)

num_round = 20
evallist = [(dtrain, 'train')]
param = {'eta': 0.4, 'max_depth': 5, 'objective':'binary:logistic', 'eval_metric':'logloss'}

bst = xgb.train(param, dtrain, num_round, evallist)
bst.save_model("simple.model")
