import itertools
import os
import copy
from pprint import pprint
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

import numpy as np
import networkx as nx
import xgboost as xgb

from typing import List

from features import features


def pool_map_tqdm(func, argument_list):
    pool = Pool(processes=cpu_count())

    jobs = [
        pool.apply_async(func=func, args=(*argument,)) if isinstance(argument, tuple) else pool.apply_async(func=func,
                                                                                                            args=(
                                                                                                            argument,))
        for argument in argument_list]
    pool.close()
    result_list_tqdm = []
    for job in tqdm(jobs):
        result_list_tqdm.append(job.get())

    return result_list_tqdm


def metis_format_to_nx(graph_file, weights="uniform") -> nx.Graph:
    """ parses METIS graph format into networkx graph"""
    # TODO: use numpy loadtxt to load graph_file as matrix and then process each row of the matrix

    assert weights in {"uniform", "source"}, "param 'weights' needs to be either 'uniform' or 'source'"

    # read header
    header = graph_file.readline().split()
    assert len(header) in {2, 3}  # last param can be omitted

    # handle weights param
    weights = 0
    if len(header) == 3:
        weights = int("0b" + header[2], 2)
    header = list(map(int, header))

    graph = nx.Graph()

    # add the correct nodes (1-based indexing)
    graph.add_nodes_from(range(1, header[0] + 1))

    # iterate over lines (which represent a node)
    for v, line in enumerate(graph_file, 1):
        line = list(map(int, line.split()))
        # based on weights param add the neighbours (and their weights) correctly
        if weights & 2 == 2:  # graph has node weights
            w = line.pop(0)
            graph.nodes[v]['weight'] = w if weights == "source" else 1
        if weights & 1 == 1:  # graph has edge weights
            edges = zip(len(line) // 2 * [v], line[0::2],
                        [{'weight': w if weights == "source" else 1} for w in line[1::2]])
        else:  # no edge weights
            edges = list(zip(len(line) * [v], line[0:]))
        graph.add_edges_from(edges)

    # assert that the added number of nodes and edges are the same as specified in the file
    assert len(graph.nodes) == header[0], \
        f"{os.path.basename(graph_file.name)} # of nodes in graph: {len(graph.nodes)}, # of nodes in header: {int(header[0])}"  # header: n m f       with f being one of: (0), 1, 10, 11
    assert len(graph.edges) == header[1], \
        f"{os.path.basename(graph_file.name)} # of edges in graph: {len(graph.edges)}, # of edges in header: {int(header[1])}"

    return graph


def write_nx_in_metis_format(graph: nx.Graph, path):
    # type of weights
    weights = 0
    if 'weight' in next(iter(graph.nodes(data=True))):
        weights = weights | 1  # set least-significant bit
    if 'weight' in next(iter(graph.edges(data=True))):
        weights = weights | 2  # set second-to-least-significant bit

    mapping = dict([(node, idx) for idx, node in enumerate(sorted(list(graph.nodes)), start=1)])
    normalized_graph = nx.relabel_nodes(graph, mapping)

    with open(path, "w") as graph_file:
        # header
        graph_file.write(f"{normalized_graph.number_of_nodes()} {normalized_graph.number_of_edges()} {weights}\n")
        if not normalized_graph.number_of_nodes():  # 0 nodes
            return

            # FIXME: FATAL, COULD FAIL due to too large graph... :/
        lines = '\n'.join(
            " ".join(map(str, sorted(list(normalized_graph.neighbors(node))))) for node in normalized_graph.nodes)
        graph_file.write(lines)


def search_for_graphs(keyword_list, graph_folder="instances", recursive=True, exclude=False):
    """ find matching paths for keywords (or all if no keywords) """

    graph_folder = os.path.abspath(graph_folder)
    matched_graphs = []
    for path in os.listdir(graph_folder):
        # get the correct absolute path
        path = graph_folder + "/" + path

        # add graph file
        if os.path.isfile(path):
            if exclude:
                if path[-6:] == ".graph" and (not keyword_list or (not any([kw in path for kw in keyword_list]))):
                    matched_graphs.append(path)
            else:
                if path[-6:] == ".graph" and (not keyword_list or any([kw in path for kw in keyword_list])):
                    matched_graphs.append(path)

                    # if recursive option is true, then add all graphs from all dictionaries
        if os.path.isdir(path) and recursive:
            matched_graphs.extend(search_for_graphs(keyword_list, graph_folder=path, recursive=True))

    return matched_graphs


# # calculate MIS if neccesary
# graph_mis_path = graph_mis_dir + (os.path.basename(graph_path) if graph_mis_dir else graph_path)[:-6] + ".MIS"
# subprocess.run(["sh", "features/calc_mis.sh", graph_path, graph_mis_path])

def load_graph(idx, graph_path, mis_path, num_of_graphs, no_labels):
    print(f"{os.path.basename(graph_path)} ({idx}/{num_of_graphs}) ...")

    with open(graph_path) as graph_file:   # read graph and labels from resp. files
        graph = metis_format_to_nx(graph_file)

    with open(mis_path) as mis_file:
        if not no_labels:
            graph.graph['labels'] = np.loadtxt(mis_file)  # add labels as attribute to graph

    graph.graph['path'] = graph_path
    graph.graph['kw'] = os.path.basename(graph_path)

    print(f"{graph.graph['kw']} ({idx}/{num_of_graphs}) done.")
    return graph


def get_graphs_and_labels(graph_paths: List[str], mis_paths=None, no_labels=False) -> List[nx.Graph]:
    """ get list of nx.Graphs (each with their associated MIS labels) from a list of paths """

    # if no mis_paths specified, then assume they are in the same location as the graphs, but with the ".MIS" ending
    if not mis_paths:
        if not no_labels:
            mis_paths = [graph_path[:-6] + ".MIS" for graph_path in graph_paths]
        else:
            mis_paths = itertools.cycle([None])

    # need exactly one mis_path for each graph_path
    if not no_labels:
        assert len(graph_paths) == len(mis_paths), "unequal lenghts of graphs and MIS"

    print("loading graphs:")
    with Pool(cpu_count()) as pool:
        return pool.starmap(load_graph, zip(range(1, len(graph_paths) + 1), graph_paths, mis_paths, itertools.cycle([len(graph_paths)]), itertools.cycle([no_labels])))


def features_helper(idx, g, num_of_graphs) -> np.array:
    print(f"{g.graph['kw']} ({idx}/{num_of_graphs}) ...")
    f = features(g)
    print(f"{g.graph['kw']} ({idx}/{num_of_graphs}) done.")
    return f


def get_dmatrix_from_graphs(graphs, no_labels=False):
    # initialize np.array feature_data and labels through first graph
    graphs = [graph for graph in graphs if graph]
    if not graphs:
        print(f"get_dmatrix_from_graphs(graphs={graphs}): provided only empty (or no) graphs, returning empty np.array")
        return xgb.DMatrix(np.array([[]]))

    # asynchronously calculate features for each graph and then
    print("calculating features for graph:")

    with Pool(cpu_count()) as pool:
        feature_data = np.array(pool.starmap(features_helper, zip(range(1, len(graphs) + 1), graphs, itertools.cycle([len(graphs)])))).T
        # flatten the array along the last axis (i.e. list of matrices are appended to each other)
        feature_data.reshape(-1, feature_data.shape[-1])
        # do the same for label array (simpler since it only is a matrix)
        labels = np.array(map(lambda g: g.graph['labels'], graphs)).flatten()

    return xgb.DMatrix(np.array(feature_data), label=np.array(labels)) if not no_labels else xgb.DMatrix(
        np.array(feature_data))


# testing
if __name__ == "__main__":
    with open("../instances/karate.graph") as graph_file:
        G = metis_format_to_nx(graph_file)
        write_nx_in_metis_format(G, "../instances/karate_rewritten.graph")
