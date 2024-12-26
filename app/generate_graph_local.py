import os
import os.path as osp
import replicate
from scrape import scrape
import re
import json
import openai
from openai import OpenAI
import torch
import time

class Graph_Generator:
    def __init__(self,USE_LOCAL_LLM=False,model_name =None,tokenizer_name = None):
        # 使用するLLMの選択，デフォルトはChatGPT
        # SELECT_LLM = "LLama" 
        self.USE_LOCAL_LLM = USE_LOCAL_LLM
        self.GPT_MODEL = "gpt-4o"
        self.model_name = "elyza/Llama-3-ELYZA-JP-8B" #初期値
        self.tokenizer_name = self.model_name #初期値
        if model_name:
            self.model_name = model_name
            if not tokenizer_name:
                assert("tokenizer not set!")
            self.tokenizer_name = tokenizer_name
        # self.model_name ="microsoft/Phi-3.5-mini-instruct"
        # self.model_name = "Qwen/QwQ-32B-Preview"

        # OpenAIのAPIキーを読み込み
        with open('./.token/openai_api_key', 'r') as f:
            self.api_key = f.read().strip()
        openai.api_key = self.api_key

        if self.USE_LOCAL_LLM:
            #LLMをローカルで動かす
            #cudaデバイスがない場合はLLMは利用しない
            if not torch.cuda.is_available():
                print("CUDAデバイスが見つからないのでGPTを利用します")
                self.USE_LOCAL_LLM = False
            else:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                
                self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype="auto",
                    device_map="auto",
                )
                self.model.eval()

    def parse_to_json(self,input_string):
        # TODO: 色々なパターンのテキストに対応する
        # ノードのセクションを解析
        node_pattern = re.compile(r"Node (\d+): ([^\n]+)\nType: ([^\n]+)(?:\nQuantity: ([^\n]+))?")
        nodes = []
        for match in node_pattern.finditer(input_string):
            groups = match.groups() # example: ('1', '鶏もも肉', 'ingredient', '1枚(200g)')
            
            # quantityがある場合
            if len(groups) == 4:
                _, node_id, node_type, quantity = groups
                node = {"id": node_id, "type": node_type, "quantity": quantity}
            
            # quantityがない場合
            else:
                _, node_id, node_type = groups
                node = {"id": node_id, "type": node_type}
            
            nodes.append(node)
        
        # エッジのセクションを解析
        edge_pattern = re.compile(r"Edge \d+: ([^\s]+) - ([^\s]+) ?[\(（]([^)）]+)[\)）]")
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


    # def critic_graph(self,graph: str, recipe_txt: str):
    #     # ChatGPTによる生成結果のクリティック
    #     # 1. エッジが存在しない場合
    #     # 2. ノードが存在しない場合

    #     # エッジが存在しない場合
    #     if "Edge" not in graph:
    #         return True, "エッジが存在しません。修正してください"
        
    #     if "Node" not in graph:
    #         return True, "ノードが存在しません。修正してください"
        
    #     try:
    #         graph_dict = self.parse_to_json(graph)
    #     except:
    #         return True, "エッジまたはノードのフォーマットが正しくありません。修正してください"
        
    #     node_list = [ node["id"] for node in graph_dict["nodes"] ]
    #     connected_nodes = [ node["id"] for node in graph_dict["nodes"] if node['type'] == "final" ]
    #     prev_len = -1
    #     print("node_list:", node_list)
    #     while len(connected_nodes) != prev_len:
    #         prev_len = len(connected_nodes)
    #         for edge in graph_dict["edges"]:
    #             if edge["source"] not in node_list:
    #                 print("source:", edge["source"])
    #                 return True, f"Node {edge['source']}が存在しません。修正してください"
    #             if edge["target"] not in node_list:
    #                 print("target:", edge["target"])
    #                 return True, f"Node {edge['target']}が存在しません。修正してください"
    #             if edge["target"] in connected_nodes and edge["source"] not in connected_nodes:
    #                 connected_nodes.append(edge["source"])
        
    #     print("connected_nodes:", connected_nodes)
    #     unconnected_nodes = [ node for node in node_list if node not in connected_nodes ]
    #     if len(connected_nodes) != len(node_list):
    #         u_nodes = "、".join(unconnected_nodes)
    #         return True, f"Node {u_nodes}に接続したエッジがありません。修正してください"
        

    #     with open('data/llama_format_ja_input.txt', 'r', encoding='utf-8') as f:
    #         example_input = f.read()

    #     with open('data/llama_format_ja.txt', 'r', encoding='utf-8') as f:
    #         example_output = f.read()
        
    #     with open('data/wrong_example_input.txt', 'r', encoding='utf-8') as f:
    #         wrong_example_input = f.read()
        
    #     with open('data/wrong_example_output1.txt', 'r', encoding='utf-8') as f:
    #         wrong_example_output1 = f.read()
    #         reason1 = "Node 10とNode 11に接続したエッジがありません．料理に使用されていないノードです．修正してください"
        
    #     with open('data/wrong_example_output2.txt', 'r', encoding='utf-8') as f:
    #         wrong_example_output2 = f.read()
    #         reason2 = "Node 4とNode 5からNode 9へのエッジがありません．手順が一部欠けています．修正してください"

    #     messages = []
    #     messages.append({"role": "system", "content": "あなたはレシピの知識グラフの評論家です"})
    #     # メインのプロンプトを追加
    #     messages.append({"role": "user", "content": 
    #         f"以下の知識グラフは正しいですか？「Yes」か「No」で答えてください．Noであれば，その後に理由を教えてください．【元のレシピ】{example_input} 【知識グラフ】{example_output}"})
    #     messages.append({"role": "assistant", "content": "Yes"})
    #     messages.append({"role": "user", "content": 
    #         f"以下の知識グラフは正しいですか？「Yes」か「No」で答えてください．Noであれば，その後に理由を教えてください．【元のレシピ】{wrong_example_input} 【知識グラフ】{wrong_example_output1}"})
    #     messages.append({"role": "assistant", "content": f"No/{reason1}"})
    #     messages.append({"role": "user", "content": 
    #         f"以下の知識グラフは正しいですか？「Yes」か「No」で答えてください．Noであれば，その後に理由を教えてください．【元のレシピ】{wrong_example_input} 【知識グラフ】{wrong_example_output2}"})
    #     messages.append({"role": "assistant", "content": f"No/{reason2}"})
    #     messages.append({"role": "user", "content":
    #         f"以下の知識グラフは正しいですか？「Yes」か「No」で答えてください．Noであれば，その後に理由を教えてください．【元のレシピ】{recipe_txt} 【知識グラフ】{graph}"})

    #     remake = False
    #     message = None


    #     if self.USE_LOCAL_LLM:
    #         prompt = self.tokenizer.apply_chat_template(
    #             messages,
    #             tokenize=False,
    #             add_generation_prompt=True
    #         )
    #         token_ids = self.tokenizer.encode(
    #             prompt, add_special_tokens=False, return_tensors="pt"
    #         )

    #         with torch.no_grad():
    #             output_ids = self.model.generate(
    #                 token_ids.to(self.model.device),
    #                 max_new_tokens=1200,
    #                 do_sample=True,
    #                 temperature=0.6,
    #                 top_p=0.9,
    #             )
    #         output_str = self.tokenizer.decode(
    #             output_ids.tolist()[0][token_ids.size(1):], skip_special_tokens=True
    #         )

    #         if output_str.startswith("No"):
    #             remake = True
    #             message = output_str[3:]
    #     else :
    #         #GPTモデルをAPI経由で利用する
    #         # TODO: generate_graphと重複している変数をグローバルにする
    #         # OpenAIのAPIキーを読み込み
    #         with open('./.token/openai_api_key', 'r') as f:
    #             api_key = f.read().strip()
    #         openai.api_key = api_key

    #         try:
    #             response = openai.chat.completions.create(
    #                 model=self.GPT_MODEL,
    #                 messages=messages,
    #             )
    #             output_str = response.choices[0].message.content

    #             data = {"messages":messages, "output_str":output_str}
    #             with open(f"./data/GPT_messages_outputs/{time.time()}.json","w",encoding="utf-8") as f:
    #                 json.dump(data,f)

    #             print("=================================")
    #             print('critic output:\n', output_str)
    #             if output_str.startswith("No"):
    #                 remake = True
    #                 message = output_str[3:]
    #         except Exception as e:
    #             print(f"Error: {e}")

    #     return remake, message


    def generate_graph(self,url, max_n_loop=3,html = None,save_message=False):
        # URLからテキストをスクレイプ
        text_content = scrape(url,html=html)
        if text_content is None:
            return None, None

        # remake = True
        # make_cnt = 0
        # messages = None
        # output_str = ""
        # while remake:
        #     print("=================================")
        #     print("retry cnt:", make_cnt)
        #     tmp, messages = _generate_graph(text_content, messages)
        #     if tmp is not None:
        #         output_str = tmp
        #     if make_cnt >= max_n_loop:
        #         break
        #     remake, mistake_reason = critic_graph(output_str, text_content)
        #     messages.append({"role": "user", "content": mistake_reason})
        #     make_cnt += 1
        
        output_str, messages = self._generate_graph(text_content,save_message=save_message)

        # JSON形式に変換
        try:
            output_json = self.parse_to_json(output_str)
        except:
            print("Failed to parse the output")
            output_json = None
        
        print("output_json:", output_json)
        
        return output_json


    def _generate_graph(self,text_content, messages=None,save_message=False):
        
        # with open('data/llama_format_ja_input.txt', 'r', encoding='utf-8') as f:
        #     example_input = f.read()
        
        # デバッグ
        print('text_content', text_content)
        
        with open('data/llama_format_ja.txt', 'r', encoding='utf-8') as f:
            example_output = f.read()
        
        if messages is None:
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
            
            
            messages.append({"role": "system", "content": "あなたは料理の専門家でありレシピから知識グラフを作成するロボットです"})
            messages.append({"role": "system", "content": "次のフォーマットに従って知識グラフを作成してください．また，知識グラフのみを返答してください．ただし，料理名は一般的な名前を使用し，リード文は削除してください．"})
            messages.append({"role": "system", "content": "【フォーマット】\n" + example_output})
            # メインのプロンプトを追加
            # messages.append({"role": "user", "content": f"スクレイピングしたWebページのテキストが与えられます，その中からレシピを抜き出し，知識グラフを作成してください．【Webページ全体のテキスト】{example_input}"})
            # messages.append({"role": "assistant", "content": example_output})
            # messages.append({"role": "system", "content": "次のフォーマットに従って知識グラフを作成してください．また，知識グラフのみを返答してください．"})
            # messages.append({"role": "user", "content": "スクレイピングしたWebページ全体のテキストが与えられます，その中からレシピを抜き出し，知識グラフを作成してください"})
            # messages.append({"role": "assistant", "content": "【Webページ全体のテキスト】" + text_content})
            # messages.append({"role": "system", "content": "次のフォーマットに従って知識グラフを作成してください．また，知識グラフのみを返答してください．"})
            

            messages.append({"role": "user", "content": f"スクレイピングしたWebページのテキストが与えられます，その中からレシピを抜き出し，知識グラフを作成してください．【Webページ全体のテキスト】{text_content}"})
        
        output_str = None

        if self.USE_LOCAL_LLM:
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            token_ids = self.tokenizer.encode(
                prompt, add_special_tokens=False, return_tensors="pt"
            )

            with torch.no_grad():
                output_ids = self.model.generate(
                    token_ids.to(self.model.device),
                    max_new_tokens=1200,
                    do_sample=True,
                    temperature=0.6,
                    top_p=0.9,
                )
            output_str = self.tokenizer.decode(
                output_ids.tolist()[0][token_ids.size(1):], skip_special_tokens=True
            )
        else:
            #GPTをAPI経由で利用する
            try:
                # print("=================================")
                # print(f"messages:\n{messages}")
                # response = openai.chat.completions.create(
                #     # model="gpt-3.5-turbo",
                #     model="gpt-4o",
                #     messages=messages,
                # )
                # output_str = response.choices[0].message.content
                # messages.append({"role": "assistant", "content": output_str})
                
                client = OpenAI(api_key=self.api_key)
                response = client.chat.completions.create(
                    model=self.GPT_MODEL,
                    messages=messages,
                )
                
                output_str = response.choices[0].message.content
                
                if save_message:
                    data = {"messages":messages, "output_str":output_str}
                    with open(f"./data/GPT_messages_outputs/{time.time()}.json","w",encoding="utf-8") as f:
                        json.dump(data,f)
            except Exception as e:
                print(f"Error: {e}")

        # else:
        #     raise ValueError("SELECT_LLM must be 'LLama' or 'ChatGPT'")
            
        # デバッグ
        print("=================================")
        print('output_str:\n', output_str)


        return output_str, messages
