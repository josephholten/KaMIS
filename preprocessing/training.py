import os
import sys
import copy 
import subprocess
import numpy as np
import networkx as nx
import xgboost as xgb

from features import features
from loading_utils import metis_format_to_nx, search_for_graphs, get_graphs_and_labels, get_dmatrix_from_graphs

training_graphs_paths = search_for_graphs([
        "jazz",
        "celegans_met",
        "email",
        "adjnoun",
        "celegansneural",
        "dolphins",
        "football",
        "karate",
        "lesmis",
        #"netscience",
        #"hep-th",
        #"polbooks",
        #"power"
])

training_graphs = get_graphs_and_labels(training_graphs_paths)

if len(training_graphs) < 1:
    print("no training graphs provided, terminating...")
    sys.exit()

dtrain = get_dmatrix_from_graphs(training_graphs)

num_round = 20
evallist = [(dtrain, 'train')]
param = {'eta': 0.4, 'max_depth': 5, 'objective':'binary:logistic', 'eval_metric':'logloss'}

bst = xgb.train(param, dtrain, num_round, evallist)
bst.save_model("simple.model")
