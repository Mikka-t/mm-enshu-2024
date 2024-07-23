import json
import os

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def replace_ids_with_numbers(graph):
    id_map = {}
    new_nodes = []
    new_edges = []

    for i, node in enumerate(graph['nodes']):
        new_id = str(i + 1)
        id_map[node['id']] = new_id
        new_node = node.copy()
        new_node['id'] = new_id
        new_nodes.append(new_node)
    
    for edge in graph['edges']:
        new_edge = edge.copy()
        new_edge['source'] = id_map[edge['source']]
        new_edge['target'] = id_map[edge['target']]
        new_edges.append(new_edge)
    
    graph['nodes'] = new_nodes
    graph['edges'] = new_edges
    return graph, id_map

if __name__ == '__main__':
    graph_file = os.path.join(os.path.dirname(__file__), 'data', 'toy_graph.json')
    graph = load_json(graph_file)
    new_graph, id_map = replace_ids_with_numbers(graph)
    output_file = os.path.join(os.path.dirname(__file__), 'data', 'new_toy_graph.json')
    save_json(new_graph, output_file)
    print(f'ID replaced graph saved to {output_file}')
    print(f'ID map: {id_map}')

