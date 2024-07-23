import json
import os

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def merge_graphs(existing_graph, new_graph):
    nodes_set = {node['id'] for node in existing_graph['nodes']}
    edges_set = {(edge['source'], edge['target']) for edge in existing_graph['edges']}
    
    for node in new_graph['nodes']:
        if node['id'] not in nodes_set:
            nodes_set.add(node['id'])
            existing_graph['nodes'].append(node)
    
    for edge in new_graph['edges']:
        edge_tuple = (edge['source'], edge['target'])
        if edge_tuple not in edges_set:
            edges_set.add(edge_tuple)
            existing_graph['edges'].append(edge)
    
    return existing_graph

def initialize_empty_graph():
    return {'nodes': [], 'edges': []}

def save_merged_graph(graph, file_path):
    save_json(graph, file_path)
    print(f'Merged graph saved to {file_path}')

