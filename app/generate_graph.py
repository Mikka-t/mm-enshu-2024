import os
import os.path as osp
import replicate
from scrape import scrape
import re
import json


def parse_to_json(input_string):
    # TODO: 色々なパターンのテキストに対応する
    # ノードのセクションを解析
    node_pattern = re.compile(r"Node \d+: ([^\n]+)\nType: ([^\n]+)")
    nodes = []
    for match in node_pattern.finditer(input_string):
        node_id, node_type = match.groups()
        nodes.append({"id": node_id, "type": node_type})

    # エッジのセクションを解析
    edge_pattern = re.compile(r"Edge \d+: ([^\s]+) - ([^\s]+) \(([^)]+)\)")
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

    # JSON形式に変換
    try:
        output_json = parse_to_json(output_str)
    except:
        output_json = None

    return output, output_json