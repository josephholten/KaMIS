import numpy as np
import xgboost as xgb

from features import features
from loading_utils import metis_format_to_nx, search_for_graphs, get_graphs_and_labels, get_dmatrix_from_graphs

graphs_paths = search_for_graphs([
        "netscience"
        #"astro-ph"
])
graphs = get_graphs_and_labels(graphs_paths)

data = get_dmatrix_from_graphs(graphs)

bst = xgb.Booster()
bst.load_model("simple.model")

num_stages = 5
q = 0.7   # confidence niveau

print("reducing graphs", *(graph.graph['kw'] for graph in graphs))
track_removals = {graph.graph['kw']: [] for graph in graphs} 

for stage in range(1, num_stages+1):
    label_pred = bst.predict(data)
    np.savetxt(f"prediction_stage{stage}.pred", label_pred)

    for graph in graphs:
        removal = np.array(graph.nodes)[label_pred <= q]
        graph.remove_nodes_from(removal)
        graph.graph['labels'] = graph.graph['labels'][np.where(label_pred > q)[0]]  # remove labels of removed nodes in test graph
        track_removals[graph.graph['kw']].append(len(removal))

    dtest = get_dmatrix_from_graphs(graphs)

for graph in graphs:
    print("in graph", graph.graph['kw'], "removed a total of", sum(track_removals[graph.graph['kw']]), "nodes", "(", *track_removals[graph.graph['kw']], ")")

# solution quality: (of course first reduce graphs with KaMIS) use ML to reduce graphs further, then calculate MIS and compare to MIS on original kernal