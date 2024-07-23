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


def scrape(url):
    # Define headers for the request
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
        else:
            return remove_extra_newlines(soup.get_text(separator='\n'))
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        return remove_extra_newlines(soup.get_text(separator='\n'))