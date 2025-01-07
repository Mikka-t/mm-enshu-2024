import os
from merge_graphs import merge_graphs, initialize_empty_graph, save_merged_graph, load_json
from final_nodes import update_final_nodes, update_ing_nodes

# Set file paths
big_graph_path = os.path.join(os.path.dirname(__file__), 'data', 'toy_graph_big.json')
final_nodes_path = os.path.join(os.path.dirname(__file__), 'data', 'final_nodes.json')
final_nodes_ing_path = os.path.join(os.path.dirname(__file__), 'data', 'final_nodes_ing.json')

# Initialize or load big graph
if os.path.exists(big_graph_path):
    big_graph = load_json(big_graph_path)
else:
    big_graph = initialize_empty_graph()

def add_new_graph(new_graph_path):
    global big_graph
    new_graph = load_json(new_graph_path)
    big_graph = merge_graphs(big_graph, new_graph)
    save_merged_graph(big_graph, big_graph_path)
    update_final_nodes(new_graph, final_nodes_path)
    update_ing_nodes(new_graph, final_nodes_ing_path)

# For testing purposes
if __name__ == '__main__':
    new_graph_path = os.path.join(os.path.dirname(__file__), 'data', 'toy_graph.json')
    add_new_graph(new_graph_path)
