import os
import sys
import copy 
import subprocess
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import xgboost as xgb



def features(g: nx.Graph) -> np.array:
    """ calculates feature matrix, where each row is a feature vector for a specific node"""

    def average(x):
        if len(x) == 0:
            return 0
        return sum(x)/len(x) 

    def chi2(obs,exp): 
        return ((obs-exp)**2) / exp

    deg = dict(g.degree)
    avg_deg = average(deg.values())
    lcc = nx.clustering(g)
    avg_lcc = average(lcc.values())
    eigencentrality = nx.algorithms.centrality.eigenvector_centrality_numpy(g)
    greedy_coloring = nx.greedy_color(g)
    greedy_chr_nmbr = len(set(greedy_coloring.values()))

    def f(v):
        """ calculates the feature vector """
        return np.array([
            # graph-theoretical features
            g.number_of_nodes(),                                          # F1: n, number of nodes
            g.number_of_edges(),                                          # F2: m, number of edges
            deg[v],                                                     # F3: vertex degree
            lcc[v],                                                     # F4: lcc, local clustering coefficient of node v
            eigencentrality[v],                                         # F5: eigencentrality
            # stat. features
            chi2(deg[v], avg_deg),                                      # F6: chi2 of vertex deg
            average([chi2(deg[u], avg_deg) for u in g.neighbors(v)]),    # F7: average chi2 of deg of neighbours
            chi2(lcc[v], avg_lcc),                                      # F8: chi2 of lcc of vertex
            average([chi2(lcc[u], avg_lcc) for u in g.neighbors(v)]),    # F9: average chi2 of lcc of neighbours
            len({greedy_coloring[u] for u in g.neighbors(v)}) / greedy_chr_nmbr  # F10: estimate for local chromatic density
        ])
    return np.array([f(v) for v in g.nodes])   # why does f(np.array) not behave like map(f, np.array) ???? 


def search_for_graphs(keyword_list, graph_folder="instances"):
    # find matching paths for keywords
    matched_paths = [[path for path in os.listdir(graph_folder) if kw in path and path[-6:] == ".graph"] for kw in keyword_list]
    for paths in matched_paths:
        # check if kw's are unique
        assert len(paths) == 1

    return [graph_folder + ("/" if graph_folder[-1] != "/" else "") + paths[0] for paths in matched_paths]


def parse_graph(graph_lines: list[str]) -> nx.Graph: 
    """ parses METIS graph format into networkx graph"""
    header = graph_lines[0].split()
    assert len(header) in {2,3}  # last param can be omitted
    weights = 0
    if len(header) == 3:
        weights = int("0b" + header[2], 2)

    graph = nx.Graph()
    graph.add_nodes_from(range(1,len(graph_lines)))

    for v, line in zip(graph.nodes, graph_lines[1:]):
        line = list(map(int, line.split()))
        edges = []
        if weights & 2 == 2:  # graph has node weights
            graph.nodes[v]['weight'] = line.pop(0)
        if weights & 1 == 1:  # graph has edge weights
            edges = zip(len(line)//2 * [v], line[0::2], [{'weight': w} for w in line[1::2]])      
        else:                 # no edge weights
            edges = list(zip(len(line) * [v], line[0:]))
        graph.add_edges_from(edges)
    
    assert len(graph.nodes) == int(header[0])   # header: n m f       with f one of: (0), 1, 10, 11 
    assert len(graph.edges) == int(header[1]) 

    return graph

def get_graphs_and_labels(graph_paths):
    graphs = []    
    for graph_path in graph_paths:
        # calculate MIS if neccesary
        graph_mis_path = graph_path[:-6]+".MIS"
        subprocess.run(["sh", "features/calc_mis.sh", graph_path, graph_mis_path])
        # read graph and labels from resp. files
        with open(graph_path) as graph_file, open(graph_mis_path) as mis_file:
            graphs.append({
                'graph': parse_graph(graph_file.readlines()),
                'labels': np.array(list(map(int, mis_file.readlines())))   
            })
    return graphs

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

test_graphs_paths = search_for_graphs([
        "netscience"
        #"astro-ph"
])

training_graphs = get_graphs_and_labels(training_graphs_paths)

test_graphs = get_graphs_and_labels(test_graphs_paths)
original_test_graphs = copy.deepcopy(test_graphs)

if len(training_graphs) < 1:
    print("no training graphs provided, terminating...")
    sys.exit()

def get_dmatrix_from_graphs(graphs):
    # initialize np.array feature_data and labels through first graph

    feature_data = features(graphs[0]['graph'])
    labels = graphs[0]['labels']

    for g in graphs[1:]:
        # append data and labels to np.array
        np.append(feature_data, features(g['graph']), axis=0)        
        np.append(labels, g['labels'])                         

    return xgb.DMatrix(np.array(feature_data), label=np.array(labels)) 

dtrain = get_dmatrix_from_graphs(training_graphs)
dtest = get_dmatrix_from_graphs(test_graphs)

param = {"max_depth": 5, "eta": 1, "objective": "binary:logistic"}
evallist = [(dtest, 'eval'), (dtrain, 'train')]
num_round = 10

# bst = xgb.train(param, dtrain, num_round, evallist)
# bst.save_model(f"simple.model")

bst = xgb.Booster(param)
bst.load_model("simple.model")

num_stages = 5
q = 0.4   # confidence niveau

for stage in range(1, num_stages+1):
    label_pred = bst.predict(dtest)
    np.savetxt(f"prediction_stage{stage}.pred", label_pred)

    for graph in test_graphs:
        removal = np.array(graph['graph'].nodes)[label_pred <= q]
        print(len(removal))
        print(removal)
        graph['graph'].remove_nodes_from(removal)
        graph['labels'] = graph['labels'][np.where(label_pred > q)[0]]  # remove labels of removed nodes in test graph

    dtest = get_dmatrix_from_graphs(test_graphs)
    
# print(test_graphs[0].number_of_nodes())