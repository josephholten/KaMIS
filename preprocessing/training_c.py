from datetime import date, datetime
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

time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
print(time)
graph_paths = glob("/home/jholten/graphs/*")
feature_paths = [ "/home/jholten/graph_files/" + os.path.basename(path) + ".feat" for path in graph_paths]
label_paths = ["/home/jholten/mis/kamis_results/" + os.path.basename(path) + ".mis" for path in graph_paths]

with Pool(cpu_count()) as pool:
    feature_data = np.vstack(pool.map(np.loadtxt, feature_paths))  # tqdm concurrent process_map => progress bar
    label_data = np.hstack(pool.map(np.loadtxt, label_paths))

dtrain = xgb.DMatrix(feature_data, label=label_data)

num_round = 30 
evallist = [(dtrain, 'train')]
param = {'eta': 1, 'max_depth': 3, 'objective': 'binary:logistic', 'eval_metric': 'logloss', 'nthread': 32}

print("starting training...")
bst = xgb.train(param, dtrain, num_round, evallist)
time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
bst.save_model(f"/home/jholten/KaMIS/{time}.model")
