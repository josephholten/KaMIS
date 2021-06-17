from datetime import date
from multiprocessing import Pool

import numpy as np
import xgboost as xgb

from cpp_preprocessing import cpp_features

graph_paths = [...]

label_paths = ["/home/jholten/mis/kamis_results/" + path[path.rfind("/") + 1:-len(".graph")] + ".uniform.mis" for path
               in graph_paths]

print("calculating features:")
with Pool() as pool:
    feature_data = np.vstack(pool.map(cpp_features, graph_paths))  # tqdm concurrent process_map => progress bar
    label_data = np.vstack(pool.map(np.loadtxt, label_paths))
dtrain = xgb.DMatrix(feature_data, label=label_data)

num_round = 20
evallist = [(dtrain, 'train')]
param = {'eta': 0.4, 'max_depth': 5, 'objective': 'binary:logistic', 'eval_metric': 'logloss', 'nthread': 16}

print("starting training...")
bst = xgb.train(param, dtrain, num_round, evallist)
bst.save_model("" + str(date.today()) + ".model")
