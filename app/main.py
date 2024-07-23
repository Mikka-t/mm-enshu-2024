from flask import Flask, request,render_template
from index import display_knowledge_graph,convert_json
from generate_graph import generate_graph
from graph2recipe import get_subgraph_str, subgraph2recipe_str
import json
import time
import markdown2
import re
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
        # recipe = subgraph2recipe_str(graph)
        # print("LLM Output: ", recipe)
    # recipe = recipe.replace("\n","<br>")
    # recipe = markdown2.markdown(recipe)
        recipe=f"""
<h2>麻婆茄子のレシピ</h2>
<ul>
  <li>ナス: 3本</li>
  <li>長ねぎ: 1本</li>
  <li>豚ひき肉: 150g</li>
  <li>豆板醤: 大さじ1/2</li>
  <li>すりおろし生姜: 小さじ1</li>
  <li>すりおろしニンニク: 小さじ1</li>
  <li>鷹の爪輪切り: 小さじ1/2</li>
  <li>水: 150ml</li>
  <li>めんつゆ（2倍濃縮）: 大さじ3</li>
  <li>水溶き片栗粉: 大さじ2</li>
  <li>ラー油: 大さじ1/2</li>
  <li>ごま油: 大さじ1</li>
  <li>小ねぎ（小口切り）: 適量</li>
</ul>
<ol>
  <li>フライパンにごま油を熱し、豚ひき肉を炒める。</li>
  <li>長ねぎを加えてさらに炒め、豚ひき肉に火が通るまで炒める。</li>
  <li>豆板醤、すりおろし生姜、すりおろしニンニク、鷹の爪輪切りを加えて炒める。</li>
  <li>ナスを加えて炒め、ナスがやわらかくなるまで炒める。</li>
  <li>水とめんつゆを加え、煮る。</li>
  <li>水溶き片栗粉でとろみをつける。</li>
  <li>ラー油をかけて完成。</li>
  <li>小ねぎを散らして器に盛り付ける。</li>
</ol>"""
    send_data = convert_json(graph)
    # print(send_data)

    title =re.search(r'<h2>(.*?)</h2>', recipe).group(0) #group(0)で<p></p>とかを保持したまま、group(1)ではtextだけ取得する
    ingredients_ul = re.search(r'<ul>(.*?)</ul>', recipe, re.DOTALL).group(0)
    HowToCook_ol = re.search(r'<ol>(.*?)</ol>', recipe, re.DOTALL).group(0)
    print(title)
    print(ingredients_ul)
    print(HowToCook_ol)
    
    
    return render_template("search/result.html",json_data=send_data,full_categories_list =[],recipe_title=title,ingredients=ingredients_ul,HowToCook=HowToCook_ol)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001,debug=True)
