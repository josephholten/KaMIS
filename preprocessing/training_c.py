import datetime
from datetime import date
from glob import glob
from multiprocessing import Pool, cpu_count

import numpy as np
import xgboost as xgb

from cpp_preprocessing import cpp_features
import sys
import os
from tqdm import tqdm

# GRAPH_FOLDER = "/home/graph_collection/independentset_instances/walshaw/"
#TEMP_FOLDER = "/home/jholten/graph_files/"
# graph_paths = ["bcsstk30-sorted.graph", "cs4-sorted.graph", "crack-sorted.graph"]
# graph_paths = [GRAPH_FOLDER + path for path in graph_paths]
#graph_paths = glob("/home/jholten/kernels/kamis_kernels/*.kernel")
#non_working = "a5esindl.mtx-sorted.graph.kernel blockqp1.mtx-sorted.graph.kernel c-57.mtx-sorted.graph.kernel c-67.mtx-sorted.graph.kernel c-68.mtx-sorted.graph.kernel ca-HepPh.mtx-sorted.graph.kernel Dubcova1.mtx-sorted.graph.kernel enron-sorted.graph.kernel Oregon-1.mtx-sorted.graph.kernel rajat07.mtx-sorted.graph.kernel TSOPF_FS_b300_c2.mtx-sorted.graph.kernel".split()
#graph_paths = list(filter(lambda x: os.path.basename(x) not in non_working, graph_paths))
#graph_paths, test_paths = graph_paths[:-10], graph_paths[-10:]
#print(test_paths)

feature_paths = glob("/home/jholten/graph_files/*.graph.kernel.feat")
with open("test_graphs.txt") as test_file:
    test_paths = test_file.readlines()
feature_paths = list(filter(lambda x: x not in test_paths, feature_paths))  # remove the test paths
label_paths = ["/home/jholten/mis/kamis_results/" + os.path.basename(path)[:-len(".feat")] + ".mis" for path in feature_paths]

with Pool(cpu_count()) as pool:
    feature_data = np.vstack(pool.map(np.loadtxt, feature_paths))  # tqdm concurrent process_map => progress bar
    label_data = np.hstack(pool.map(np.loadtxt, label_paths))

dtrain = xgb.DMatrix(feature_data, label=label_data)

num_round = 30 
evallist = [(dtrain, 'train')]
param = {'eta': 1, 'max_depth': 3, 'objective': 'binary:logistic', 'eval_metric': 'logloss', 'nthread': 16}

print("starting training...")
bst = xgb.train(param, dtrain, num_round, evallist)
bst.save_model("/home/jholten/KaMIS/all_kernels.model")
