from flask import Flask, request,render_template
from index import display_knowledge_graph,convert_json
from generate_graph import generate_graph
from graph2recipe import get_subgraph_str, subgraph2recipe_str
import json
import time
import markdown2
# LLM にレシピを生成させる時は True にする。無駄なプロンプト実行を防ぐためテスト時は False
USE_LLM_FLAG = True

app = Flask(__name__)
@app.context_processor
def inject_now():
    return {'now': lambda: int(time.time())} #ブラウザがキャッシュをしないようにcssなどのurlを変更するための対策用。こう書くことによってjinja2がみることができるようになる




@app.route('/')
def index():

    # with open('data/toy_graph.json', 'r', encoding='utf-8') as f:
    #     graph = json.load(f)
        
    # send_data = convert_json(graph)
    # print(send_data)
    category_list = ["デコレーションケーキ","いちごタルト","カレーライス"]
    # return render_template("result.html",json_data = send_data)
    return render_template('search/index.html',full_categories_list=category_list)

@app.route('/search', methods=['POST'])
def submit_url():
    url = request.form.get('inputText') if request.form.get('inputText')!="" else None
    # ここでURLを使った処理を行う
      # クエリパラメータを取得
    input_url = "" if request.form.get('input')== None else request.args.get('input')
    categories =  request.form.get('liData').split(",")
    categories =None if categories== [''] else categories
    dish_name = None if not categories else  categories[0] #とりあえず初めだけ表示する
    print(f"{dish_name=}")
    print(f"{url=}")
    
    if dish_name:
        graph = get_subgraph_str(dish_name)
        
    elif url:
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

    print(graph)
    if USE_LLM_FLAG:
        # TODO: フロントエンドに表示
        recipe = subgraph2recipe_str(graph)
        print("LLM Output: ", recipe)
        if recipe == "NO_API":
            recipe = ""
        else:            
            # recipe = recipe.replace("\n","<br>")
            recipe = markdown2.markdown(recipe)
    
    send_data = convert_json(graph)
    # print(send_data)
            
    return render_template("search/result.html",json_data=send_data,full_categories_list =[],recipe = recipe)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001,debug=True)
