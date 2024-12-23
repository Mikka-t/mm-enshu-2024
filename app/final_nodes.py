import json
import os

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_final_nodes(file_path):
    if os.path.exists(file_path):
        return load_json(file_path)
    else:
        return []

def save_final_nodes(final_nodes, file_path):
    save_json(final_nodes, file_path)
    print(f'Final nodes saved to {file_path}')

def update_final_nodes(graph, final_nodes_file):
    final_nodes = load_final_nodes(final_nodes_file)
    final_node_ids = {node['id'] for node in final_nodes}
    
    for node in graph['nodes']:
        if node.get('type') == 'final' and node['id'] not in final_node_ids:
            final_nodes.append(node)
            final_node_ids.add(node['id'])
    
    save_final_nodes(final_nodes, final_nodes_file)

def update_ing_nodes(graph, ing_nodes_file):
    ing_nodes = load_final_nodes(ing_nodes_file)
    ing_node_ids = {node['id'] for node in ing_nodes}
    
    for node in graph['nodes']:
        if node.get('type') == 'ingredient' and node['id'] not in ing_node_ids:
            ing_nodes.append(node)
            ing_node_ids.add(node['id'])
    
    save_final_nodes(ing_nodes, ing_nodes_file)
