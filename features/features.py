import os
import sys
import subprocess
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import xgboost

def parse_graph(graph_list: list[str]) -> nx.Graph: 
    """ parses METIS graph format into networkx graph"""
    header = graph_list[0].split()
    assert len(header) in {2,3}  # last param can be omitted
    weights = 0
    if len(header) == 3:
        weights = int("0b" + header[2], 2)

    graph = nx.Graph()
    graph.add_nodes_from(range(1,len(graph_list)))

    for v, line in zip(graph.nodes, graph_list[1:]):
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


def features(g: nx.Graph) -> np.array:
    """ calculates feature matrix, where each row is a feature vector for a specific node"""

    def average(x):
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
        return [
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
        ]

    return np.array([f(v) for v in g.nodes])


def search_for_graphs(keyword_list, graph_folder="instances"):
    # find matching paths for keywords
    matched_paths = [[path for path in os.listdir(graph_folder) if kw in path and path[-6:] == ".graph"] for kw in keyword_list]
    for paths in matched_paths:
        # check if kw's are unique
        assert len(paths) == 1

    return [graph_folder + ("/" if graph_folder[-1] != "/" else "") + paths[0] for paths in matched_paths]

training_graphs = search_for_graphs([
        "jazz",
        "celegans_met",
        "email",
        "adjnoun",
        "celegansneural",
        "dolphins",
        "football",
        "karate",
        "lesmis",
        "netscience"
])

test_graphs = search_for_graphs([
        "polblogs",
])

if len(training_graphs) < 1:
    print("no training graphs provided, terminating...")
    sys.exit()

# initialize np.array feature_data and labels through first graph
graph_path = training_graphs[0]
graph_mis_path = graph_path[:-6]+".MIS"
subprocess.run(["sh", "features/calc_mis.sh", graph_path, graph_mis_path])

with open(graph_path) as graph_file, open(graph_mis_path) as mis_file:
    g = parse_graph(graph_file.readlines())  
    g_labels = np.array(list(map(int, mis_file.readlines())))   

feature_data = features(g)
labels = g_labels 

for graph_path in training_graphs[1:]:
    # compute maximum independent set of graph
    graph_mis_path = graph_path[:-6]+".MIS"
    subprocess.run(["sh", "features/calc_mis.sh", graph_path, graph_mis_path])

    # read graph and labels from resp. files
    with open(graph_path) as graph_file, open(graph_mis_path) as mis_file:
        g = parse_graph(graph_file.readlines())                     
        g_labels = np.array(list(map(int, mis_file.readlines())))   

    # append data and labels to np.array
    np.append(feature_data, features(g), axis=0)        
    np.append(labels, g_labels)                         

dtrain = xgboost.DMatrix(np.array(feature_data), label=np.array(labels)) 