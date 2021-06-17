import os
from loading_utils import search_for_graphs

import numpy as np

# solution quality: (of course first reduce graphs with KaMIS) use ML to reduce graphs further, then calculate MIS and compare to MIS on original kernal

optimal_sols = "/home/jholten/mis/kamis_resuls/"
optimal_sols_on_reduced = "/home/jholten/mis/ml_reduce_results/"
optimal_sols = os.path.abspath(optimal_sols)
optimal_sols = os.path.abspath(optimal_sols_on_reduced)

graphs = search_for_graphs([], graph_folder="/home/jholten/kernels/ml_reduce_kernels")

print("possible optimal MIS sizes after ml_reduce.py:")
for graph in graphs:
    with open(optimal_sols + graph.graph['kw'][:-6] + ".uniform.mis") as opt_sol_file:
        opt_ind_set_size = np.sum(np.fromfile(opt_sol_file))
        print(f"graph {graph.graph['kw']} {sum(graph.graph['removals']) / opt_ind_set_size * 100}%")
   