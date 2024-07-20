from flask import Flask, request
from index import display_knowledge_graph
from generate_graph import generate_graph
from graph2recipe import get_subgraph_str, subgraph2recipe_str
import json

# LLM にレシピを生成させる時は True にする。無駄なプロンプト実行を防ぐためテスト時は False
USE_LLM_FLAG = False

app = Flask(__name__)

@app.route('/')
def index():
    # JSON形式の知識グラフ
    # クエリパラメータを取得
    dish_name = request.args.get('dish', 'toy_graph')  # デフォルトは'toy_graph'
    if dish_name != "toy_graph":
        graph = get_subgraph_str(dish_name)
        if USE_LLM_FLAG:
            # TODO: フロントエンドに表示
            recipe = subgraph2recipe_str(graph)
            print("LLM Output: ", recipe)
    else:
        try:
            with open('data/toy_graph.json', 'r', encoding='utf-8') as f:
                graph = json.load(f)
        except FileNotFoundError:
            return "File not found", 404

    return display_knowledge_graph(graph)

@app.route('/submit_url', methods=['POST'])
def submit_url():
    url = request.form.get('url')
    # ここでURLを使った処理を行う
    with open(f'data/url2graph.json', 'r', encoding='utf-8') as f:
        url2graph = json.load(f)
    
    if url in url2graph:
        graph = url2graph[url]
    else:
        llm_output, graph = generate_graph(url)
        if llm_output is None:
            return "error"
        url2graph[url] = graph
        with open(f'data/url2graph.json', 'w', encoding='utf-8') as f:
            json.dump(url2graph, f, ensure_ascii=False, indent=4)

    return display_knowledge_graph(graph)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
