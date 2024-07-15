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

def display_knowledge_graph():
    # # JSON形式の知識グラフ
    with open('data/toy_graph.json', 'r', encoding='utf-8') as f:
        knowledge_graph = json.load(f)

    # NetworkXグラフを作成
    G = nx.DiGraph()

    for node in knowledge_graph["nodes"]:
        G.add_node(node["id"], type=node["type"])

    for edge in knowledge_graph["edges"]:
        G.add_edge(edge["source"], edge["target"], action=edge["action"])

    # # # グラフを描画
    pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 8))
    nx.draw(
        G, pos, with_labels=True, 
        node_color='lightblue', edge_color='gray', 
        node_size=3000, font_size=10, 
        font_weight='bold', arrowsize=20,
        font_family=font_family)
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
    <h1>ショートケーキのレシピ知識グラフ</h1>
    <img src="data:image/png;base64,{{ image_base64 }}">
    </body>
    </html>
    '''

    return render_template_string(html_template, image_base64=image_base64)
    # return 'hello world!!'