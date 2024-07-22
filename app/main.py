from flask import Flask, request,render_template
from index import display_knowledge_graph,convert_json
from generate_graph import generate_graph
import json
import time

app = Flask(__name__)
@app.context_processor
def inject_now():
    return {'now': lambda: int(time.time())} #ブラウザがキャッシュをしないようにcssなどのurlを変更するための対策用。こう書くことによってjinja2がみることができるようになる
import os

CD = "/"
CD = os.getcwd() + "/app/"
@app.route('/')
def index():
    # # JSON形式の知識グラフ
    with open(CD+'data/toy_graph.json', 'r', encoding='utf-8') as f:
        graph = json.load(f)
    
    send_data = convert_json(graph)
    # print(send_data)
    random_work = {"title":"a","img_url":"A","url":"a"}
    category_list = ["カレー","ケーキ"]
    # return render_template("result.html",json_data = send_data)
    return render_template('search/index.html',full_categories_list=category_list,start_year=1900, end_year=2024,random_work=random_work)

@app.route('/submit_url', methods=['POST'])
def submit_url():
    url = request.form.get('url')
    # ここでURLを使った処理を行う
    with open(CD+f'data/url2graph.json', 'r', encoding='utf-8') as f:
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

    return render_template("result.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001,debug=True)
