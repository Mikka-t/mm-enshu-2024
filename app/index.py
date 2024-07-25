import os.path as osp
from flask import Flask
from flask import render_template_string
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
import json
import matplotlib.font_manager as fm
import matplotlib as mpl
import matplotlib
matplotlib.get_cachedir()

font_family = 'TakaoPGothic'

def display_knowledge_graph(graph):
    # NetworkXグラフを作成
    G = nx.DiGraph()

    # ノードを追加
    for node in graph["nodes"]:
        quantity = node.get("quantity", "")
        label = f"{node['id']} ({quantity})" if quantity else node["id"]
        G.add_node(node["id"], label=label, type=node["type"], quantity=quantity)

    # エッジを追加
    for edge in graph["edges"]:
        G.add_edge(edge["source"], edge["target"], action=edge["action"])

    # # # グラフを描画
    pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 8))
    
    # ノードラベルを取得
    node_labels = {node: G.nodes[node].get('label', node) for node in G.nodes()}
    
    nx.draw(
        G, pos, labels=node_labels, with_labels=True, 
        node_color='lightblue', edge_color='gray', 
        node_size=3000, font_size=10, 
        font_weight='bold', arrowsize=20,
        font_family=font_family)
    
    # エッジラベルを取得
    edge_labels = {(u, v): d['action'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_family=font_family)

    # # 画像をバッファに保存
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # # HTMLテンプレート
    html_template = '''
    <html>
    <head><title>Knowledge Graph</title></head>
    <body>
    <img src="data:image/png;base64,{{ image_base64 }}">
    <form action="/submit_url" method="post">
    <label for="url">Enter URL:</label>
    <input type="text" id="url" name="url">
    <button type="submit">Submit</button>
    </form>
    </body>
    </html>
    '''

    return render_template_string(html_template, image_base64=image_base64)

    # return 'hello world!!'

def convert_json(data:json)->dict:
    nodes = data["nodes"]
    edges = data["edges"]
    convert_nodes = []
    convert_edges = []
    node_type = {"ingredient":1,"intermediate":2,"final":3}
    for node in nodes:
        try:
            quantity = node["quantity"]
            if quantity == None:
                quantity = ""
            else:
                quantity = "（"+quantity+"）"
        except:
            quantity =""
        
        # 料理タイトルが長い場合に対処するため，10文字ずつで改行する
        name = ""
        for i in range(0,len(node["id"]),10):
            name += node["id"][i:i+10] + "\\n"

        if node["type"] in node_type:
            node_group = node_type[node["type"]]
        else:
            node_group = "misc"
        convert_nodes.append({"id": node["id"], "label": name + "\\n" + quantity, "group": node_group})

    for edge in edges:
        convert_edges.append({"from": edge['source'], "to": edge['target'], "label": edge['action']})
    
    return {"nodes":convert_nodes,"edges":convert_edges}


if __name__ =="__main__":
    with open("./app/data/toy_graph_eng.json","r",encoding="utf-8") as f:
        data = json.load(f)
    data = convert_json(data)

    for key,value in data.items():
        print(value)
