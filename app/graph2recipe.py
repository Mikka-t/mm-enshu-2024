from graph2recipe_utils import *
import replicate
import openai
import os
import json
import time

SELECT_LLM = "ChatGPT"
# SELECT_LLM = "LLama"

# 中間発表用．ノードIDやエッジIDがなく，ノード名はstrで管理されています
def get_subgraph_str(target_node: str,):
    """
    Input: ノード名
    Output: graph (json形式)
    """

    # 料理名パース 今はそのまま料理名返すだけ
    target_node = parse_dish_name(target_node)

    # get_edges: サーバーと通信する関数，edgesを取得
    # edges: [{"source":str, "target":str, "action":str}, ...]
    nodes, edges = get_graph_str()

    ### 前処理
    reverse_edges = {}
    # エッジを逆向きにして計算量削減
    # [{target : [source, action]}, ...]
    create_reverse_edges_str(edges, reverse_edges)

    # ノードを辞書形式にして計算量削減
    node_dict = {}
    create_node_dict_str(nodes, node_dict)

    ### 処理
    # 結果を格納
    subgraph_nodes_set = set()
    subgraph_nodes = []
    subgraph_node_info = {}
    subgraph_edges = []
    subgraph_edge_info = {}

    # 深さ優先探索で逆向きに探索，サブグラフを取得
    get_subgraph_dfs_str(target_node, reverse_edges, subgraph_nodes_set, subgraph_edges)

    # ノード説明文を取得
    for node in subgraph_nodes_set:
        # node_info = get_node_info_str(node) # ノードIDがそのままノードの説明なので，中間発表時はいらない
        if node in node_dict:
            subgraph_nodes.append(node_dict[node])
        else:
            error_node = {"id": node, "type": "misc"}
            subgraph_nodes.append(error_node)
            print("Error node:",error_node)

    # エッジ説明文を取得
    for edge in subgraph_edges:
        # エッジIDという概念が無く，エッジにそのままactionが紐づいているので，中間発表時はいらない
        # edge_info = get_edge_info_str(edge)
        pass

    subgraph = {"nodes": subgraph_nodes, "edges": subgraph_edges}
    return subgraph

# 中間発表用．ノードIDやエッジIDがなく，ノード名はstrで管理されています
def subgraph2recipe_str(graph, dish_name_plus_url):
    cache_file_path = "./data/subgraph2recipe_cache.json"
    ### プロンプト作成
    nodes, edges = graph["nodes"], graph["edges"]

    # ノードとエッジの情報をテキスト形式で整形
    nodes_text = ', '.join([f'{{"id": "{node["id"]}", "type": "{node["type"]}", "quantity":"{node["quantity"] if "quantity" in node else "未定義"}"}}' for node in nodes])
    edges_text = ', '.join([f'{{"source": "{edge["source"]}", "target": "{edge["target"]}", "action": "{edge["action"]}"}}' for edge in edges])
    
    graph_text = f'{{"nodes": [{nodes_text}], "edges": [{edges_text}]}}'

    cached_data = {}
    if os.path.exists(cache_file_path):
        with open(cache_file_path, 'r', encoding='utf-8') as file:
            cached_data = json.load(file)
        
        if dish_name_plus_url in cached_data:
            print("Fetched Cache")
            time.sleep(8 if dish_name_plus_url[:4]=='http' else 5)
            return cached_data[dish_name_plus_url]
    else:
        # ファイルが存在しない場合は新しく作成
        with open(cache_file_path, 'w', encoding='utf-8') as file:
            json.dump({}, file)

    if SELECT_LLM == "LLama":
        with open('./.token/llama', 'r') as f:
            api_token = f.read().strip()
        print('api_token:', api_token)
        client = replicate.Client(api_token=api_token)

        prompt = "jsonファイルの内容: " + graph_text + "\n" + \
        "このようなjsonファイルがあります。このjsonファイルから得られる知識だけを用いて、レシピの文章を書いてください。返答はレシピのみにしてください。" + \
        "レシピ名から始めて、材料と作り方を書いてください。\n"

        # LLMにプロンプトを送信し、レシピの文章を生成
        output = client.run(
            "meta/meta-llama-3-70b-instruct",
            input={"prompt": prompt}
        )

        # 出力を結合してレシピの文章を生成
        output_list = list(output)
        output_str = "".join(output_list)

    elif SELECT_LLM == "ChatGPT":
        # GPT特有の```によるコードブロックを削除
        def remove_first_and_last_line(text):
            lines = text.split('\n')
            if len(lines) > 2:
                return '\n'.join(lines[1:-1])
            else:
                return ''
            
        try:
            with open('./.token/openai_api_key', 'r') as f:
                api_key = f.read().strip()
            openai.api_key = api_key
        except:
            print("No API key.")
            return "NO_API"

        messages = [
            {"role": "system", "content": "あなたは料理のレシピの知識グラフから、料理のレシピを復元することができます。レシピを記述したHTMLコードのみを出力することができます。"}
        ]
        messages.append({"role": "system", "content": "与えられたデータ以外の知識を用いてはいけません。レシピ以外のことを書いてはいけません。"})
        messages.append({"role": "assistant", "content": f"与えられたjsonファイル形式の知識グラフの内容: {graph_text}"})
        messages.append({"role": "user", "content": "このjsonファイルから得られる知識だけを用いて、レシピの文章を書いてください。返答はレシピのみにしてください。"})
        messages.append({"role": "user", "content": "レシピ名から初めて、材料と作り方を書いてください。ただし、HTMLの形で出力し、改行は改行タグ<br>を使用してください。"})
        messages.append({"role": "user", "content": "材料は<ul>内で羅列してください。レシピの段階は<ol>内で羅列してください。最初は<h2>で始め，type='final'の'id'を<h2>内で書いてください。"})

        response = openai.chat.completions.create(
            # model="gpt-3.5-turbo",
            model="gpt-4o",
            messages=messages,
        )
        
        output = response 
        output_str = response.choices[0].message.content
        
        output_str = remove_first_and_last_line(output_str)

    if os.path.exists(cache_file_path):
        cached_data[dish_name_plus_url] = output_str
        # JSONファイルに保存
        with open(cache_file_path, 'w', encoding='utf-8') as file:
            json.dump(cached_data, file, ensure_ascii=False, indent=4)
    else:
        print("Cache file Not Found.")

    return output_str

# ノードID等がintで管理されていることを前提にした関数．
# 中間発表時点ではtoy_graphのノードIDがstrで管理されているので、使いません
def get_subgraph(target_node: int):
    """
    future work: cache recent subgraph

    get recipe subgraph from dataset

    Input: target_node(int)...完成料理ノードID
    Returns: 
        subgraph_nodes(dict) {nodeID(int) : node_info(dict)}, 
        node_info(dict) = {nodeID(int) : node_info(dict)}
        subgraph_edges(dict) {edgeID(int) : [nodeID1(int), nodeID2(int)]}
            意味: nodeID1 -> nodeID2
    """
    # edges: dict {edgeID:int : [nodeID1:int, nodeID2:int]}, 意味: nodeID1 -> nodeID2
    # get_edges: サーバーと通信する関数，edgesを取得
    edges = get_edges()

    reverse_edges = {}
    # エッジを逆向きにして計算量削減
    # {nodeID2(int) : [[nodeID1a(int), edgeIDa(int)], ...} nodeID1 -> nodeID2
    create_reverse_edges(edges, reverse_edges)

    # 結果を格納
    subgraph_nodes = set()
    subgraph_node_info = {}
    subgraph_edges = {}
    subgraph_edge_info = {}

    # 深さ優先探索で逆向きに探索，サブグラフを取得
    get_subgraph_dfs(target_node, reverse_edges, subgraph_nodes, subgraph_edges)

    # ノード説明文を取得
    for nodeID in subgraph_nodes:
        # サーバにノードIDを渡して説明文を取得
        node_info = get_node_info(nodeID)
        subgraph_node_info[nodeID] = node_info

    # エッジ説明文を取得
    for edgeID, edge in subgraph_edges.items():
        # サーバにノードIDを渡して説明文を取得
        edge_info = get_edge_info(edgeID)
        subgraph_edge_info[edgeID] = edge_info

    return subgraph_nodes, subgraph_edges, subgraph_node_info, subgraph_edge_info

if __name__ == "__main__":
    # テスト用
    import json
    subgraph = get_subgraph_str("デコレーションケーキ")
    with open(f'data/toy_subgraph_cake.json', 'w', encoding='utf-8') as f:
        json.dump(subgraph, f, ensure_ascii=False, indent=4)
    subgraph = get_subgraph_str("いちごタルト")
    with open(f'data/toy_subgraph_tart.json', 'w', encoding='utf-8') as f:
        json.dump(subgraph, f, ensure_ascii=False, indent=4)
    subgraph = get_subgraph_str("カレーライス")
    with open(f'data/toy_subgraph_curry.json', 'w', encoding='utf-8') as f:
        json.dump(subgraph, f, ensure_ascii=False, indent=4)

    recipe = subgraph2recipe(get_subgraph_str("いちごタルト"))  
    print("Output: ", recipe)