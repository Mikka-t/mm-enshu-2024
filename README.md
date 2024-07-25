# 2024年度MM工学演習
## 料理のレシピ検索アプリ

開発中，ブランチはちゃんと分けましょう

## 動かし方

restartしてからurlを表示するスクリプト
```
$ chmod u+x scripts/run.sh  # 初回のみ
$ ./scripts/run.sh
```
appの内容をコンテナ内にコピーし，コンテナをrestart
```
$ chmod u+x scripts/replace_app.sh  # 初回のみ
$ ./scripts/replace_app.sh
```
エラーの確認
```
$ docker logs [コンテナ名]
```
## 動かし方 (ローカル)

```
$ cd app
$ docker-compose up --build -d --force-recreate
```
その後，localhost:8001に接続

## API Keys

llamaを使う際はapp/.token/lammaにtokenを入れる．（generate_graph.pyでtokenを読込む）

ChatGPTを使う際はapp/.token/openai_api_key を入れる．

例：app/.token/lamma 内
```
r8_Ae7dJFIefdfaejfaioejfioajef
```
tokenは[replicateのサイト](https://replicate.com/account/api-tokens)で作る．

## 日程
| 日時                     | イベント                  | 目標                                    |
|--------------------------|--------------------------|----------------------------------------|
| 2024年7月26日 (金)    | 中間報告                  | 最低限の動作，DB構築とレシピ検索

## 報告
gunicornおよびnginx，Flaskは動作確認のために使用しています．担当者が自由に置き換えてください

## メモ：githubリポジトリ
https://github.com/Mikka-t/mm-enshu-2024
