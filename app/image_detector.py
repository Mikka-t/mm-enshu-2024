import os
from ultralytics import YOLO
from PIL import Image, ImageDraw
from deep_translator import GoogleTranslator
import openai

with open('./.token/openai_api_key', 'r') as f:
    api_key = f.read().strip()
openai.api_key = api_key

model = YOLO("combined.pt")  # モデルをロード

translator = GoogleTranslator(source='en', target='ja')
def translate_to_japanese(english_name):
    """英語を日本語に翻訳"""
    try:
        result = translator.translate(english_name)
        # print(f"Translated '{english_name}' to '{result}'")  # デバッグログ
        return result
    except Exception as e:
        print(f"Translation error for {english_name}: {e}")
        return english_name  # 翻訳失敗時、元の英語名を返す


def detect_and_crop(image_path, output_dir):
    """
    画像内の食材を検出し、結果画像を指定ディレクトリに保存。
    :param image_path: ユーザーがアップロードした画像のパス
    :param output_dir: 検出結果を保存するディレクトリ
    :return: 検出結果 [{label: 食材名, cropped_path: 切り取られた画像のパス}]
    """
    os.makedirs(output_dir, exist_ok=True)

    # 画像内の対象を検出
    results = model.predict(source=image_path, conf=0.25)
    img = Image.open(image_path)
    detected_items = []

    for result in results:
        # 各対象のクラスと位置を検出
        for box, cls in zip(result.boxes.xyxy, result.boxes.cls):
            label = result.names[int(cls)]  # クラス名（英語）を取得
            label = label.replace("zone_", "")  # "zone_" プレフィックスを削除
            label_jp = translate_to_japanese(label)  # 日本語に翻訳
            # print(f"Detected: {label} -> {label_jp}")  # デバッグログ
            x1, y1, x2, y2 = map(int, box)  # バウンディングボックスの座標

            # 画像を切り取り
            cropped_img = img.crop((x1, y1, x2, y2))
            cropped_path = os.path.join(output_dir, f"{label}_{x1}_{y1}.jpg")
            cropped_img.save(cropped_path)

            detected_items.append({"label": label_jp, "cropped_path": cropped_path})

    return detected_items

def generate_recipes(detected_ingredients):
    """
    OpenAI API を使用してレシピ提案を生成。
    :param detected_ingredients: 検出された食材のリスト
    :return: 2種類のレシピ提案
    """
    # 現在の食材で作れるレシピを生成
    prompt_1 = (
        f"以下は食材リストです：{', '.join(detected_ingredients)}。"
        "これらの食材だけを使って作れる料理をリストアップし、簡単な手順を添えてください。"
    )
    messages_1 = [
        {"role": "system", "content": "あなたはプロの料理アシスタントです。以下のフォーマットに従って、ユーザーに食材を基にした読みやすいレシピを作成してください：各ステップを1行ずつで書いてください。"},
        {"role": "user", "content": prompt_1}
    ]
    try:
        response_1 = openai.chat.completions.create(
            model="gpt-4o",  # 正しいモデルを指定
            messages=messages_1
        )
        recipes_1 = response_1.choices[0].message.content
    except Exception as e:
        print(f"Error generating recipes based on detected ingredients: {e}")
        recipes_1 = "検出された食材を基にしたレシピを生成できませんでした。"

    # 拡張食材を使ったレシピを生成
    prompt_2 = (
        f"以下は食材リストです：{', '.join(detected_ingredients)}。"
        "これらの食材を基に、他の食材を追加して作れる料理をリストアップし、簡単な手順を添えてください。"
    )
    messages_2 = [
        {"role": "system", "content": "あなたはプロの料理アシスタントです。以下のフォーマットに従って、ユーザーに拡張食材（いくつの推薦食材を増えるだけ、数は多過ぎないよう）を使った読みやすいレシピを作成してください：各ステップを1行ずつで書いてください。"},
        {"role": "user", "content": prompt_2}
    ]
    try:
        response_2 = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages_2
        )
        recipes_2 = response_2.choices[0].message.content
    except Exception as e:
        print(f"Error generating recipes with extended ingredients: {e}")
        recipes_2 = "拡張食材を使用したレシピを生成できませんでした。"

    return recipes_1, recipes_2