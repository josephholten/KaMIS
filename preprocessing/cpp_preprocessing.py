import subprocess
import numpy as np

GRAPH_TMP_FOLDER = "/home/jholten/graphs/"


class Logger:
    def __init__(self, log=True):
        self.log = log

    def log(self, *args, **kwargs):
        if self.log: print(*args, **kwargs)


def cpp_features(graph_path: str, removed: np.array = None) -> (str, str):
    reduced_path = graph_path  # nothing to reduce then the reduction is the same as the original graph
    if removed is not None:
        reduced_path = graph_path + ".red" + str(len(removed))  # not super elegant...?
        write(graph_path, reduced_path, removed)

    feature_path = reduced_path + ".feat"
    subprocess.run(["deploy/features", reduced_path, feature_path])

    return feature_path, reduced_path


def write(in_graph_path: str, out_graph_path: str, removed: np.array = None):
    if removed is None:
        removed = np.array([])

    with open(in_graph_path) as graph_file, open(out_graph_path, "w") as out_file:
        header = graph_file.readline()

        # convert the NodeIDs (indices of the nodes to be removed to a bool array representing whether that index has
        # been removed
        exists = np.ones(header.split()[0])  # header : n m w  => n = number of nodes
        exists[removed] = 0
        new_id_vec = np.cumsum(exists)
        # cumulative sum: new_ids[i] = sum_{0..i} (exists([k])  => makes a closed set
        new_id = lambda x: str(new_id_vec[int(x)])

        # iterate over graph file removing lines (neighborhoods) of nodes that don't exist and mapping old NodeIDs to
        # the closed set of 0 ... (n-len(removed)
        for idx, line in enumerate(graph_file):
            if exists[idx]:
                # split line into nodes, map them to new node ids and join with spaces again
                out_file.write(" ".join(map(new_id, line.split())))