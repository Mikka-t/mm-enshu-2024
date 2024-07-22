import os
import os.path as osp
import replicate
from scrape import scrape
import re
import json
import openai

# 使用するLLMの選択，デフォルトはLLama
SELECT_LLM = "LLama" 
# SELECT_LLM = "ChatGPT" 


def parse_to_json(input_string):
    # TODO: 色々なパターンのテキストに対応する
    # ノードのセクションを解析
    node_pattern = re.compile(r"Node \d+: ([^\n]+)\nType: ([^\n]+)\nQuantity: ([^\n]+)")
    nodes = []
    for match in node_pattern.finditer(input_string):
        node_id, node_type, quantity = match.groups()
        nodes.append({"id": node_id, "type": node_type, "quantity": quantity})
    
    # エッジのセクションを解析
    # edge_pattern = re.compile(r"Edge \d+: ([^\s]+) - ([^\s]+) \(([^)]+)\)") # コメント：修正前のコード．
    edge_pattern = re.compile(r"Edge \d+: ([^\s]+) - ([^\s]+)（([^）]+)）") # コメント：修正後のコード．制限によりLLamaで動くかのチェックができていない・
    edges = []
    for match in edge_pattern.finditer(input_string):
        source, target, action = match.groups()
        edges.append({"source": source, "target": target, "action": action})

    # JSONオブジェクトを作成
    result = {
        "nodes": nodes,
        "edges": edges
    }

    return result


def generate_graph(url):
    # URLからテキストをスクレイプ
    text_content = scrape(url)
    if text_content is None:
        return None, None

    if SELECT_LLM == "LLama":
        # api_token = os.getenv("REPLICATE_API_TOKEN")
        with open('./.token/llama', 'r') as f:
            api_token = f.read().strip()
        print('api_token:', api_token)
        client = replicate.Client(api_token=api_token)

        # graph example
        # with open('data/toy_graph_eng.json', 'r', encoding='utf-8') as f:
        #     example_graph = json.load(f)
        #     example_graph = str(example_graph)
        with open('data/llama_format.txt', 'r', encoding='utf-8') as f:
            example_graph = f.read()

        prompt = "I will provide you with all the text from a web page." \
        + "Following the example format, generate a knowledge graph for the recipe." \
        + "However, you must not output any text other than the knowledge graph."

        prompt = prompt
        text_content = '\n\nweb page:{' + text_content + '}'
        example = '\n\nexample:{' + example_graph + '}'
        
        text_content = text_content[:4096 - len(prompt) - len(example)]
        prompt = prompt + text_content + example

        # テキストを入力として、Replicateで知譆グラフを生成
        output = client.run(
            "replicate/llama-2-70b-chat:2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1",
            input={"prompt": prompt}
        )
        output_list = list(output)
        output_str = "".join(output_list)
        
        
    elif SELECT_LLM == "ChatGPT":
        
        # OpenAIのAPIキーを読み込み
        with open('./.token/openai_api_key', 'r') as f:
            api_key = f.read().strip()
        openai.api_key = api_key
        
        
        with open('data/llama_format_ja.txt', 'r', encoding='utf-8') as f:
            format_text = f.read()
        
        # プロンプトの作成
        messages = [
            {"role": "system", "content": "あなたは以下の例のように料理のレシピを知識グラフに変換してください。"},
        ]
        
        # レシピと知識グラフの例を追加
        examples = []
        
        for recipe in ["syogayaki", "butter_chicken_curry"]:
            examples.append([])
            
            with open(f'data/recipe_text_{recipe}.txt', 'r', encoding='utf-8') as f:
                examples[-1].append(f.read())
            with open(f'data/toy_subgraph_{recipe}.json', 'r', encoding='utf-8') as f:
                examples[-1].append(json.load(f))
        
        for i, example in enumerate(examples):
            messages.append({"role": "system", "content": f"【例{i+1}】"})
            messages.append({"role": "system", "content": example[0]})
            messages.append({"role": "system", "content": json.dumps(example[1])})
        
        
        # メインのプロンプトを追加
        messages.append({"role": "user", "content": "スクレイピングしたWebページ全体のテキストが与えられます，その中からレシピを抜き出し，知識グラフを作成してください"})
        messages.append({"role": "assistant", "content": "【Webページ全体のテキスト】" + text_content})
        messages.append({"role": "system", "content": "次のフォーマットに従って知識グラフを作成してください．また，知識グラフのみを返答してください"})
        messages.append({"role": "system", "content": "【フォーマット】\n" + format_text})
        
        
        response = openai.chat.completions.create(
            # model="gpt-3.5-turbo",
            model="gpt-4o",
            messages=messages,
        )
        
        output = response 
        output_str = response.choices[0].message.content
        
        
    else:
        raise ValueError("SELECT_LLM must be 'LLama' or 'ChatGPT'")
        

    # JSON形式に変換
    try:
        output_json = parse_to_json(output_str)
    except:
        output_json = None

    return output, output_json