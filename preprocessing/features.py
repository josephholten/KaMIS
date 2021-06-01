import numpy as np
import networkx as nx


def features(g: nx.Graph) -> np.array:
    """ calculates feature matrix, where each row is a feature vector for a specific node"""

    def average(x):
        if len(x) == 0:
            return 0
        return sum(x) / len(x)

    def chi2(obs, exp):
        if exp == 0:
            return 0
        return ((obs - exp) ** 2) / exp

    deg = dict(g.degree)
    avg_deg = average(deg.values())
    lcc = nx.clustering(g)
    avg_lcc = average(lcc.values())
    eigencentrality = nx.algorithms.centrality.eigenvector_centrality_numpy(g)
    greedy_coloring = nx.greedy_color(g)
    greedy_chr_nmbr = len(set(greedy_coloring.values()))

    def f(v):
        """ calculates the feature vector """

        # assert type(v) == type(next(g.__iter__())), "possibly there was passed a wrong type of node"
        return np.array([
            # graph-theoretical features
            g.number_of_nodes(),  # F1: n, number of nodes
            g.number_of_edges(),  # F2: m, number of edges
            deg[v],  # F3: vertex degree
            lcc[v],  # F4: lcc, local clustering coefficient of node v
            eigencentrality[v],  # F5: eigencentrality
            # stat. features
            chi2(deg[v], avg_deg),  # F6: chi2 of vertex deg
            average([chi2(deg[u], avg_deg) for u in g.neighbors(v)]),  # F7: average chi2 of deg of neighbours
            chi2(lcc[v], avg_lcc),  # F8: chi2 of lcc of vertex
            average([chi2(lcc[u], avg_lcc) for u in g.neighbors(v)]),  # F9: average chi2 of lcc of neighbours
            len({greedy_coloring[u] for u in g.neighbors(v)}) / greedy_chr_nmbr
            # F10: estimate for local chromatic density
        ])

    return (np.vectorize(f)(np.array(g.nodes))).T
