import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

def remove_extra_newlines(input_string):
    # 2回以上連続した改行を1つの改行に置き換える
    return re.sub(r'\n\s*\n+', '\n', input_string)

def fetch_soup(url, headers):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
            return None
    except:
        print("Failed to retrieve the webpage")
        return None

# クラシル用のスクレイピング
def extract_kurashiru(soup):
    result = []
    
    # Extract title
    title = soup.find("h1", class_="title").get_text(strip=True)
    result.append(f"タイトル: {title}")

    # Extract ingredients
    ingredients_section = soup.find("ul", class_="ingredient-list")
    ingredients_items = ingredients_section.find_all("li", class_="ingredient-list-item")

    result.append("材料:")
    group_name = None
    for item in ingredients_items:
        # Check for group title
        group_title = item.find('span', class_='ingredient-title')
        if group_title:
            group_name = group_title.get_text(strip=True)
            result.append(f"\n{group_name}:")
            continue
        
        # Extract ingredient name
        name = item.find('a', class_='DlyLink ingredient-name')
        quantity = item.find('span', class_='ingredient-quantity-amount')
        if name:
            ingredient_text = name.get_text(strip=True)
            if quantity:
                ingredient_text += " " + quantity.get_text(strip=True)
            result.append(ingredient_text)

    # Extract instructions
    instructions_section = soup.find("section", class_="instructions")
    instructions_items = instructions_section.find_all("li", class_="instruction-list-item")

    result.append("\n手順:")
    for item in instructions_items:
        instruction = item.find("span", class_="content").get_text()
        result.append(instruction)
    
    return '\n'.join(result)

# デリッシュキッチン用のスクレイピング
def extract_delish_kitchen(soup):
    result = []
    
    # Extract title
    lead_title = soup.find("span", class_="lead")
    main_title = soup.find("span", class_="title")
    if lead_title and main_title:
        result.append(f"タイトル: {lead_title.get_text(strip=True)} {main_title.get_text(strip=True)}")

    # Extract ingredients
    ingredients_section = soup.find("ul", class_="ingredient-list")
    ingredients_items = ingredients_section.find_all("li")

    result.append("材料:")
    group_name = None
    for item in ingredients_items:
        # Check for group title
        if "ingredient-group__header" in item.get("class", []):
            group_name = item.get_text(strip=True)
            result.append(f"\n{group_name}:")
        else:
            # Extract ingredient name and serving
            ingredient_name = item.find("a", class_="ingredient-name")
            if not ingredient_name:
                ingredient_name = item.find("span", class_="ingredient-name")
            ingredient_serving = item.find("span", class_="ingredient-serving")
            
            if ingredient_name:
                ingredient_text = ingredient_name.get_text(strip=True)
                if ingredient_serving:
                    ingredient_text += " " + ingredient_serving.get_text(strip=True)
                result.append(ingredient_text)

    # Extract instructions
    steps_section = soup.find("ol", class_="steps")
    steps_items = steps_section.find_all("div", class_="delish-recipe-step-item")

    result.append("\n手順:")
    for step in steps_items:
        description = step.find("p", class_="step-desc")
        if description:
            result.append(description.get_text())

    return '\n'.join(result)

# 白ごはん.com用のスクレイピング
def extract_sirogohan_com(soup):
    result = []

    # Extract title
    title = soup.find("h1", id="recipe-name").get_text(strip=True)
    result.append(f"タイトル: {title}")

    # Extract ingredients
    ingredients_section = soup.find("div", class_="material-halfbox")
    ingredient_groups = ingredients_section.find_all("ul")

    result.append("材料:")
    for group in ingredient_groups:
        group_class = group.get("class", [])
        if "a-list" in group_class:
            result.append("\nA:")
        elif "b-list" in group_class:
            result.append("\nB:")
        elif "c-list" in group_class:
            result.append("\nC:")
        elif "d-list" in group_class:
            result.append("\nD:")
        elif "e-list" in group_class:
            result.append("\nE:")
        
        group_items = group.find_all("li")
        for item in group_items:
            ingredient_text = item.get_text(strip=True)
            result.append(ingredient_text)

    # Extract instructions
    instructions_section = soup.find("section", class_="howto inner-main")
    instruction_blocks = instructions_section.find_all("div", class_="howto-block")

    result.append("\n手順:")
    for block in instruction_blocks:
        step_number = block.find("h3")
        if step_number:
            result.append(step_number.get_text(strip=True))
        descriptions = block.find_all("p")
        for desc in descriptions:
            result.append(desc.get_text(strip=True))
    
    return '\n'.join(result)


# クックパッド用のスクレイピング
def extract_cookpad(soup):
    result = []
    
    # Extract title
    title = soup.find("h1", class_="recipe-title").get_text(strip=True)
    result.append(f"タイトル: {title}")

    # Extract ingredients
    ingredients_section = soup.find("div", id="ingredients_list")
    ingredients_items = ingredients_section.find_all("div", class_="ingredient_row")

    result.append("材料:")
    for item in ingredients_items:
        name = item.find("span", class_="name").get_text(strip=True)
        quantity = item.find("div", class_="ingredient_quantity amount").get_text(strip=True)
        result.append(f"{name} {quantity}")

    # Extract instructions
    instructions_section = soup.find("section", id="steps_wrapper")
    steps_items = instructions_section.find_all("li", class_="step")

    result.append("\n手順:")
    for item in steps_items:
        step_number = item.find("dt", class_="step_number").get_text(strip=True)
        instruction_div = item.find("dd", class_="instruction")
        instruction_text = instruction_div.find("p", class_="step_text").get_text(strip=True)
        result.append(f"{step_number} {instruction_text}")
        print(f"{step_number} {instruction_text}")
    
    return '\n'.join(result)


def extract_rakuten_recipe(url,html=None):

    if not html:
        # URLからHTMLを取得
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    
    else:
        soup = BeautifulSoup(html, 'html.parser') #保存したファイルを利用する
    
    result = []
    
    # タイトルの抽出
    title_tag = soup.find("h1", class_="page_title__text")
    if title_tag:
        result.append(f"タイトル: {title_tag.get_text(strip=True)}")
    
    # 材料の抽出
    result.append("\n材料:")
    materials_section = soup.find("ul", class_="recipe_material__list")
    if materials_section:
        material_items = materials_section.find_all("li", class_="recipe_material__item")
        for item in material_items:
            name_tag = item.find("span", class_="recipe_material__item_name")
            serving_tag = item.find("span", class_="recipe_material__item_serving")
            if name_tag:
                material = name_tag.get_text(strip=True)
                if serving_tag:
                    material += " " + serving_tag.get_text(strip=True)
                result.append(material)
    
    # 手順の抽出
    result.append("\n手順:")
    steps_section = soup.find("ol", class_="recipe_howto__list")
    if steps_section:
        step_items = steps_section.find_all("li", class_="recipe_howto__item")
        for step in step_items:
            text_tag = step.find("span", class_="recipe_howto__text")
            if text_tag:
                result.append(text_tag.get_text(strip=True))
    
    return '\n'.join(result)



def scrape(url,html=None):
    # Define headers for the request

    if html:
        return extract_rakuten_recipe(url=None,html=html) #LLM学習用に利用する。すでにlocalに保存しているhtmlを利用する場合
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }
    
    # Get the domain
    domain = urlparse(url).netloc
    soup = fetch_soup(url, headers)
    
    if soup is None:
        return
    
    # 特定のサイト用にスクレイピング，エラーが発生した場合は通常のテキストを返す
    try:
        if 'kurashiru' in domain:
            return extract_kurashiru(soup)
        elif 'delishkitchen' in domain:
            return extract_delish_kitchen(soup)
        elif 'sirogohan' in domain:
            return extract_sirogohan_com(soup)
        elif 'cookpad' in domain:
            return extract_cookpad(soup)
        elif 'recipe.rakuten' in domain:
            return extract_rakuten_recipe(url)
        else:
            return remove_extra_newlines(soup.get_text(separator='\n'))
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        return remove_extra_newlines(soup.get_text(separator='\n'))