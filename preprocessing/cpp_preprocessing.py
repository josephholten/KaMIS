import subprocess
import numpy as np

GRAPH_TMP_FOLDER = "/home/jholten/graphs/"


class Logger:
    def __init__(self, log=True):
        self.log = log

    def log(self, *args, **kwargs):
        if self.log: print(*args, **kwargs)


def cpp_features(graph_path: str, temp_folder: str,removed: np.array = None) -> str:
    graph_name = graph_path[graph_path.rfind("/")+1:]
    if removed is not None and len(removed) != 0:
        reduced_path = temp_folder + graph_name + ".red" + str(len(removed))  # not super elegant...?
        write(graph_path, reduced_path, removed)
    else:
        reduced_path = graph_path
    subprocess.run(["deploy/features", reduced_path, temp_folder, "5"])

    return reduced_path


def write(in_graph_path: str, out_graph_path: str, removed: np.array = None):
    if removed is None:
        removed = np.array([])

    removed = removed.astype(int)

    with open(in_graph_path) as graph_file, open(out_graph_path, "w") as out_file:
        header = graph_file.readline()
        while header[0] == "%":
            header = graph_file.readline()

        # convert the NodeIDs (indices of the nodes to be removed to a bool array representing whether that index has
        # been removed
        header = list(map(int, header.split()))
        if len(header) == 2:
            header.append(0)
        exists = np.ones(header[0]) # header : n m w  => n = number of nodes
        if removed.size != 0:
            exists[removed] = 0
        # cumulative sum: new_ids[i] = sum_{0..i} (exists([k])  => makes a closed set
        new_id_vec = np.cumsum(exists).astype(int)

        out_file.write(str(new_id_vec[len(new_id_vec)-1]) + " ")   # number of new nodes
        number_of_edges = 0

        new_lines = [[] for _ in range(header[0])]

        # iterate over graph file removing lines (neighborhoods) of nodes that don't exist and mapping old NodeIDs to
        # the closed set of 0 ... (n-len(removed)
        for idx, line in enumerate(graph_file):
            if exists[idx]:
                line = list(map(int, line.split()))
                if header[2] & 2 == 2:
                    # node weight
                    new_lines[idx].append(line.pop(0))

                for i, num in enumerate(line):
                    if header[2] & 1 == 1 and i % 2 == 1:
                        # edge weight
                        new_lines[idx].append(num)
                        continue
                    num = int(num) - 1
                    if exists[num]:
                        new_lines[idx].append(new_id_vec[num])
                        number_of_edges += 1

        out_file.write(str(number_of_edges // 2) + " ")
        out_file.write(str(header[2]) + "\n")

        for node, line in enumerate(new_lines):
            if exists[node]:
                out_file.write(" ".join(map(str, line)) + "\n")


if __name__ == "__main__":
    # write("/home/jholten/KaMIS/examples/weight_nodes.graph", "/home/jholten/KaMIS/examples/weight_nodes.graph.red", np.array([]))
    # write("/home/jholten/KaMIS/examples/weight_nodes.graph", "/home/jholten/KaMIS/examples/weight_nodes.graph.red1", np.array([1]))
    # write("/home/jholten/KaMIS/examples/weight_nodes.graph", "/home/jholten/KaMIS/examples/weight_nodes.graph.red2", np.array([1, 3]))
    print(cpp_features("/home/jholten/test_graphs/bcsstk31-sorted.graph", "/home/jholten/graph_files/", np.array([])))
