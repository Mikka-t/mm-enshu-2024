from flask import Flask, request,render_template
from index import display_knowledge_graph,convert_json

# from generate_graph import generate_graph
from generate_graph_local import Graph_Generator
graph_generator = Graph_Generator(USE_LOCAL_LLM=True)

from graph2recipe import get_subgraph_str, subgraph2recipe_str
from ingredient2graph import ingredient2graph
from merge_new_graph import add_new_graph
from recommend_recipe import recommend_recipe
from image_detector import detect_and_crop, generate_recipes
import json
import time
import markdown2
import os
import re
# LLM にレシピを生成させる時は True にする。無駄なプロンプト実行を防ぐためテスト時は False
USE_LLM_FLAG = True

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
RESULTS_FOLDER = 'static/results/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

@app.context_processor
def inject_now():
    return {'now': lambda: int(time.time())} #ブラウザがキャッシュをしないようにcssなどのurlを変更するための対策用。こう書くことによってjinja2がみることができるようになる




@app.route('/')
def index():

    # with open('data/toy_graph.json', 'r', encoding='utf-8') as f:
    #     graph = json.load(f)
        
    # send_data = convert_json(graph)
    # print(send_data)
    category_list = []
    with open(f"data/final_nodes.json","r",encoding="utf-8") as f:
        data = json.load(f)
        # print(data)
        for d in data:
            category_list.append(d["id"])
    
    with open(f"data/final_nodes_ing.json","r",encoding="utf-8") as f:
        data = json.load(f)
        # print(data)
        category_listIng = []
        for d in data:
            category_listIng.append(d["id"])
    
    # return render_template("result.html",json_data = send_data)
    return render_template('search/index.html',full_categories_list=category_list, full_categories_listIng = category_listIng)

@app.route('/full')
def show_full_graph():
    with open(f'data/toy_graph_big.json', 'r', encoding='utf-8') as f:
        big_graph = json.load(f)
    send_data = convert_json(big_graph)
    print("send_data: ",send_data)
    return render_template("search/result_big_graph.html",json_data=send_data,full_categories_list =[],full_categories_listIng = [])


@app.route('/search', methods=['POST'])
def submit_url():
    url = request.form.get('inputText') if request.form.get('inputText')!="" else None
    # ここでURLを使った処理を行う
      # クエリパラメータを取得
    input_url = "" if request.form.get('input')== None else request.args.get('input')
    categories = request.form.get('liData', '').split(",")
    categories =None if categories== [''] else categories
    dish_name = None if not categories else  categories[0] #とりあえず初めだけ表示する
    categories_ing =  request.form.get('IngData').split(",")
    categories_ing = None if categories_ing== [''] else categories_ing
    category_name = None if not categories_ing else  categories_ing[0] #とりあえず初めだけ表示する2
    print(f"{dish_name=}")
    print(f"{category_name=}")
    print(f"{url=}")
    
    if dish_name:
        graph = get_subgraph_str(dish_name)
    
    elif category_name:
        graph = ingredient2graph(categories_ing)
        send_data = convert_json(graph)
        with open(f'data/toy_graph_tmp.json', 'w', encoding='utf-8') as f:
            json.dump(send_data, f, ensure_ascii=False, indent=4)
        return render_template("search/result_big_graph.html",json_data=send_data,full_categories_list = [],full_categories_listIng = [])
        
    elif url:
        with open(f'data/url2graph.json', 'r', encoding='utf-8') as f:
            url2graph = json.load(f)
        
        if url in url2graph:
            graph = url2graph[url]
        else:
            graph = graph_generator.generate_graph(url)
            if graph is None:
                return "error"
            url2graph[url] = graph
            with open(f'data/url2graph.json', 'w', encoding='utf-8') as f:
                json.dump(url2graph, f, ensure_ascii=False, indent=4)

        graph_path = os.path.join(os.path.dirname(__file__), 'data', 'toy_graph.json')
        with open(graph_path, 'w', encoding='utf-8') as f:
            json.dump(graph, f, ensure_ascii=False, indent=4)

        add_new_graph(graph_path)

    print(graph)
    if USE_LLM_FLAG:
        # TODO: フロントエンドに表示
        if dish_name:
            recipe = subgraph2recipe_str(graph, dish_name)
        else:
            recipe = subgraph2recipe_str(graph, url.replace('/', '').replace(':',''))
        print("LLM Output: ", recipe)
        if recipe == "NO_API":
            recipe = ""
        else:            
            # recipe = recipe.replace("\n","<br>")
            recipe = markdown2.markdown(recipe)
    send_data = convert_json(graph)
    # print(send_data)
    try:
        title =re.search(r'<h2>(.*?)</h2>', recipe).group(0) #group(0)で<p></p>とかを保持したまま、group(1)ではtextだけ取得する
    except:
        title = "<h2>変換失敗</h2>"
    try: 
        ingredients_ul = re.search(r'<ul>(.*?)</ul>', recipe, re.DOTALL).group(0)
    except:
        ingredients_ul = "<ul>変換失敗</ul>"
    try:
        HowToCook_ol = re.search(r'<ol>(.*?)</ol>', recipe, re.DOTALL).group(0)
    except:
        HowToCook_ol = "<ol>変換失敗</ol>"
    print(title)
    print(ingredients_ul)
    print(HowToCook_ol)
    
    
    return render_template("search/result.html",json_data=send_data,full_categories_list =[],recipe_title=title,ingredients=ingredients_ul,HowToCook=HowToCook_ol)

# 画像のアップロードと食材の検出を処理する
@app.context_processor
def inject_defaults():
    return dict(full_categories_list=[])

@app.route('/detect', methods=['GET', 'POST'])
def detect_route():
    uploaded_image = None
    detected_items = []
    recipes_1 = ""
    recipes_2 = ""
    
    if request.method == 'POST':
        if 'image' not in request.files:
            return "画像がアップロードされていません", 400

        file = request.files['image']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(file_path)

        # 検出と切り取り関数を呼び出す
        uploaded_image = file.filename
        detected_items = detect_and_crop(file_path, app.config['RESULTS_FOLDER'])
        print(detected_items)  # デバッグログ

        # 検出された食材を抽出する
        detected_ingredients = [item["label"] for item in detected_items]

        # レシピ提案を生成する
        if detected_ingredients:
            recipes_1, recipes_2 = generate_recipes(detected_ingredients)

    # デフォルト値を渡すことを確認
    return render_template(
        'search/detect.html',
        uploaded_image=uploaded_image or "",
        detected_items=detected_items or [],
        recipes_1=recipes_1,
        recipes_2=recipes_2
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001,debug=True)
