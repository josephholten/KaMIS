import os
import numpy as np
import networkx as nx
import xgboost as xgb

from typing import List

from features import features

def metis_format_to_nx(graph_file) -> nx.Graph: 
    """ parses METIS graph format into networkx graph"""

    # read header
    header = graph_file.readline().split()
    assert len(header) in {2,3}  # last param can be omitted

    # handle weights param
    weights = 0
    if len(header) == 3:
        weights = int("0b" + header[2], 2)
    header = list(map(int, header))

    graph = nx.Graph()

    # add the correct nodes (1-based indexing)
    graph.add_nodes_from(range(1,header[0]+1))

    # iterate over lines (which represent a node)
    for v, line in enumerate(graph_file, 1):
        line = list(map(int, line.split()))
        edges = []

        # based on weights param add the neighbours (and their weights) correctly
        if weights & 2 == 2:  # graph has node weights
            graph.nodes[v]['weight'] = line.pop(0)
        if weights & 1 == 1:  # graph has edge weights
            edges = zip(len(line)//2 * [v], line[0::2], [{'weight': w} for w in line[1::2]])      
        else:                 # no edge weights
            edges = list(zip(len(line) * [v], line[0:]))
        graph.add_edges_from(edges)
    
    # assert that the added number of nodes and edges are the same as specified in the file
    assert len(graph.nodes) == header[0], f"{os.path.basename(graph_file.name)} # of nodes in graph: {len(graph.nodes)}, # of nodes in header: {int(header[0])}"   # header: n m f       with f being one of: (0), 1, 10, 11 
    assert len(graph.edges) == header[1], f"{os.path.basename(graph_file.name)} # of edges in graph: {len(graph.edges)}, # of edges in header: {int(header[1])}" 

    return graph

def search_for_graphs(keyword_list, graph_folder="instances", recursive=True, exclude=False):
    """ find matching paths for keywords (or all if no keywords) """ 

    graph_folder = os.path.abspath(graph_folder)
    matched_graphs = []
    for path in os.listdir(graph_folder):
        # get the correct absolute path
        path = graph_folder + "/" + path 

        # add graph file
        if os.path.isfile(path):
            if path[-6:] == ".graph" and (not keyword_list or (any([kw in path for kw in keyword_list]) != exclude)):
               matched_graphs.append(path) 

        # if recursive option is true, then add all graphs from all dictionaries
        if os.path.isdir(path) and recursive:
            matched_graphs.extend(search_for_graphs(keyword_list, graph_folder=path, recursive=True))

    return matched_graphs 


# # calculate MIS if neccesary
# graph_mis_path = graph_mis_dir + (os.path.basename(graph_path) if graph_mis_dir else graph_path)[:-6] + ".MIS"
# subprocess.run(["sh", "features/calc_mis.sh", graph_path, graph_mis_path])

def get_graphs_and_labels(graph_paths: List[str], mis_paths=None) -> List[nx.Graph]: 
    """ get list of nx.Graphs (each with their associated MIS labels) from a list of paths """

    graphs = [] 

    # if no mis_paths specified, then assume they are in the same location as the graphs, but with the ".MIS" ending
    if not mis_paths:
        mis_paths = [graph_path[:-6] + ".MIS" for graph_path in graph_paths]

    # need exactly one mis_path for each graph_path
    assert len(graph_paths) == len(mis_paths), "unequal lenghts of graphs and MIS"

    num_of_graphs = len(graph_paths)
    for idx, (graph_path, mis_path) in enumerate(zip(graph_paths, mis_paths), start=1):
        with open(graph_path) as graph_file:           # read graph ...
            G = metis_format_to_nx(graph_file)
        with open(mis_path) as mis_file:               # and labels from resp. files
            G.graph['labels'] = np.loadtxt(mis_file)   # add labels as attribute to graph
        G.graph['path'] = graph_path
        G.graph['kw'] = os.path.basename(graph_path)
        graphs.append(G)
        print(f"finished loading graph {os.path.basename(graph_path)} ({idx}/{num_of_graphs})")
    return graphs

def get_dmatrix_from_graphs(graphs):
    # initialize np.array feature_data and labels through first graph
    graphs = [graph for graph in graphs if graph]
    if not graphs:
        print(f"get_dmatrix_from_graphs(graphs={graphs}): provided only empty (or no) graphs, returning empty np.array")
        return np.array([])

    feature_data = features(graphs[0])
    labels = graphs[0].graph['labels']

    for g in graphs[1:]:
        # append data and labels to np.array
        np.append(feature_data, features(g), axis=0)        
        np.append(labels, g.graph['labels'])                         

    return xgb.DMatrix(np.array(feature_data), label=np.array(labels)) 


# testing
if __name__ == "__main__":
    # with open("instances/karate.graph") as graph_file:
    #     G = metis_format_to_nx(graph_file)
    # print(search_for_graphs(["adjnoun.graph", "astro"]))
    pass
