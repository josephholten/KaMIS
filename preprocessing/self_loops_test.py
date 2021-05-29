import networkx as nx

from loading_utils import metis_format_to_nx


def test_self_loop(graph: nx.Graph, verbose=False):
    selfloops = False
    for node in graph.nodes:
        if graph.has_edge(node, node):
            selfloops = True
            if verbose:
                print(node)


def remove_self_loop(graph: nx.Graph, verbose = True):
    for node in graph.nodes:
        if graph.has_edge(node, node):
            graph.remove_edge(node, node)
            if verbose:
                print(node)


with open("/home/jholten/kernels/olafu.mtx.ml_kernel") as graph_file:
    graph = metis_format_to_nx(graph_file)
    test_self_loop(graph, True)
    remove_self_loop(graph, True)