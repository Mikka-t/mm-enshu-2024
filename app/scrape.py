import requests
from bs4 import BeautifulSoup
import re

def remove_extra_newlines(input_string):
    # 2回以上連続した改行を1つの改行に置き換える
    return re.sub(r'\n\s*\n+', '\n', input_string)

def scrape(url):
    # URL of the webpage to scrape
    # url = 'https://www.allrecipes.com/recipe/10813/best-chocolate-chip-cookies/'

    # ブラウザを模倣するためのヘッダーを定義
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    }

    # Send a GET request to fetch the raw HTML content
    # TODO: 例外を限定する．そもそもtry-exceptを使うべきか．
    try:
        response = requests.get(url, headers=headers)
    except:
        print("Failed to retrieve the webpage")
        return None

    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract all text content
        text_content = soup.get_text(separator='\n')
        
        # Print the extracted text content
        return remove_extra_newlines(text_content)
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None
