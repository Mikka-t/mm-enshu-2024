import requests
import json
import pandas as pd
import time
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
import re
from openai import OpenAI

# 定数設定
CSV_PATH = './data/rakuten_recipe_category.csv'
# QUERY_URL = 'https://www.sirogohan.com/recipe/meatball/'
# QUERY_URL = 'https://www.sirogohan.com/recipe/oden/'
# QUERY_URL = 'https://www.sirogohan.com/recipe/kakuni/'

ALPHA = 0.8
LAMBDA = 0.5
# K = 10
K = 5
# MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'

# スクレイピング関数
import sys
# sys.path.append('./app')
from scrape import scrape

def parse_recipe_text(recipe_text):
    """レシピテキストをパースしてタイトル，材料，手順を抽出する"""
    title_idx = recipe_text.find('タイトル:')
    material_idx = recipe_text.find('材料:')
    content_idx = recipe_text.find('手順:')

    title = recipe_text[title_idx+5:material_idx].strip()
    material = recipe_text[material_idx+4:content_idx].strip()
    # content = recipe_text[content_idx+4:].strip()

    material_list = []
    for m in material.split('\n'):
        tmp = re.split(r'[ \n\u3000]', m)
        if tmp[0] == '':
            continue
        material_list.append(tmp[0])
    
    return title, material_list

# def extract_main_word(title, material_list):
#     """タイトルに含まれる主材料を抽出する"""
#     for material in material_list:
#         if material in title:
#             return material
#     return 'None'

# GPTを使用して主材料の特定精度を向上
def extract_main_word(title, material_list):
    """
    Few-Shot プロンプトを使用して ChatGPT API でタイトルに含まれる主材料をランキング形式で抽出する
    """
    # Few-Shot例を作成
    few_shot_prompt = """
        You are a helpful assistant for identifying the main ingredients in a recipe based on its title and a given list of ingredients.
        Each ingredient may contain additional information (e.g., "beef tendon (boiled)"). Return only the simplified ingredient names in a plain list format.
        Rank the ingredients from the most relevant to the least relevant. If no ingredients match the title, return "None".

        Examples:
        1. Title: "Tomato Basil Pasta"
        Ingredients: ["tomato (fresh)", "basil (chopped)", "pasta", "cheese"]
        Output: ["tomato", "basil", "pasta"]

        2. Title: "Cheesy Garlic Bread"
        Ingredients: ["garlic (minced)", "bread (whole grain)", "cheese (shredded)", "butter (unsalted)"]
        Output: ["cheese", "garlic", "bread"]

        3. Title: "Spicy Chicken Curry"
        Ingredients: ["chicken (diced)", "curry powder", "tomato (pureed)", "onion (sliced)"]
        Output: ["chicken", "curry powder", "tomato"]

        4. Title: "Vegetarian Stir Fry"
        Ingredients: ["tofu (firm)", "broccoli (steamed)", "carrot (julienned)", "soy sauce"]
        Output: ["tofu", "broccoli", "carrot"]

        Now, analyze the following:
        Title: "{title}"
        Ingredients: {material_list}
        Output:
        """

    # プロンプトを構築
    prompt = few_shot_prompt.format(title=title, material_list=material_list)

    try:
        with open('./.token/openai_api_key', 'r') as f:
            api_key = f.read().strip()
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for recipe analysis."},
                {"role": "user", "content": prompt}
            ],
        )
        # ChatGPTの応答から結果を抽出
        ranked_ingredients = response.choices[0].message.content

        # 結果をリスト化
        ranked_list = ranked_ingredients.strip("[]").replace('"', '').split(", ")
        return ranked_list
    
    except Exception as e:
        print(f"Error: {e}")
        return ['Error']

def fetch_rakuten_recipes(df_keyword):
    """楽天レシピからカテゴリごとのレシピを取得する"""
    
    with open('./.token/rakuten_api_key') as f:
        api_key = f.read().strip()
            
    df_recipe = pd.DataFrame(columns=[
        'recipeId', 'recipeTitle', 'foodImageUrl', 'recipeUrl',
        'recipeMaterial', 'recipeCost', 'recipeIndication', 'categoryId', 'categoryName'
    ])

    for _, row in df_keyword.iterrows():
        url = f"https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?applicationId={api_key}&categoryId={row['categoryId']}"
        res = requests.get(url)
        json_data = json.loads(res.text)

        recipes = json_data.get('result', [])
        recipe_rows = [
            {
                'recipeId': recipe.get('recipeId'),
                'recipeTitle': recipe.get('recipeTitle'),
                'foodImageUrl': recipe.get('foodImageUrl'),
                'recipeUrl': recipe.get('recipeUrl'),
                'recipeMaterial': recipe.get('recipeMaterial'),
                'recipeCost': recipe.get('recipeCost'),
                'recipeIndication': recipe.get('recipeIndication'),
                'categoryId': row['categoryId'],
                'categoryName': row['categoryName']
            } for recipe in recipes
        ]

        if recipe_rows:
            df_recipe = pd.concat([df_recipe, pd.DataFrame(recipe_rows)], ignore_index=True)
            
        time.sleep(1)  # アクセスマナーとしてスリープ

    return df_recipe.drop_duplicates(subset='recipeId')

def compute_similarity_scores(model, title, material_list, df_recipe):
    """タイトルと材料の類似度スコアを計算"""
    
    # クエリのタイトルと一致するレシピを除外
    df_recipe = df_recipe[df_recipe['recipeTitle'] != title]
    
    # タイトルの類似度
    titles = [title] + df_recipe['recipeTitle'].to_list()
    embeddings = model.encode(titles)
    title_scores = cosine_similarity([embeddings[0]], embeddings[1:])[0]

    # 材料の類似度
    query_material_embedding = model.encode(material_list)
    data_materials = df_recipe['recipeMaterial'].to_list()
    data_materials_embeddings = [model.encode(material) for material in data_materials]

    material_scores = []
    for i, data_materials_embedding in enumerate(data_materials_embeddings):
        similarity_matrix = cosine_similarity(data_materials_embedding, query_material_embedding)
        max_similarities = np.max(similarity_matrix, axis=1)
        score = (max_similarities[max_similarities > ALPHA].sum()) / len(data_materials[i])
        material_scores.append(score)

    material_scores = np.array(material_scores)

    # 合計スコア
    total_scores = LAMBDA * title_scores + (1 - LAMBDA) * material_scores
    return total_scores

def recommend_recipe(QUERY_URL):
    recipe_text = scrape(QUERY_URL)
    title, material_list = parse_recipe_text(recipe_text)
    keywords = extract_main_word(title, material_list)
    df = pd.read_csv(CSV_PATH)
    
    # 主材料でカテゴリの検索
    for keyword in keywords:
        df_keyword = df[df['categoryName'].str.contains(keyword, na=False)]
        if not df_keyword.empty:
            break
    
    # 全ての材料でカテゴリの検索
    if df_keyword.empty:
        for material in material_list:
            
            # print(material)
            
            # keyword = material
            keyword = material[:3]
            df_keyword = df[df['categoryName'].str.contains(keyword, na=False)]
            if not df_keyword.empty:
                break
        
    if df_keyword.empty:
        print('レシピが見つかりませんでした')
        return
    
    # print('recipe_text:', recipe_text)
    # print('タイトル:', title)
    # print('材料:', material_list)
    print('検索キーワード:', keyword)
    # print(df_keyword)
    # return
    
    # df_recipe = fetch_rakuten_recipes(df_keyword)
    df_recipe = fetch_rakuten_recipes(df_keyword[:5]) # レスポンス時間の関係で5つまでに制限

    model = SentenceTransformer(MODEL_NAME)
    total_scores = compute_similarity_scores(model, title, material_list, df_recipe)

    top_k_idx = total_scores.argsort()[-K:][::-1]
    top_recipes = df_recipe.iloc[top_k_idx][['recipeTitle', 'recipeUrl']]

    json_list = json.loads(top_recipes.to_json(orient='records', force_ascii=False))
    
    return json_list


if __name__ == "__main__":
    
    QUERY_URL = sys.argv[1]
    print(recommend_recipe(QUERY_URL))

    # sample
    # python /Users/nakayama_itsuki/Documents/mm-enshu-2024/recipe_recommend.py "https://www.sirogohan.com/recipe/meatball/"
    
    
    
    