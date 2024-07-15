#!/bin/bash

# 引数のチェック
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <container_id>"
    exit 1
fi

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")

# 引数から変数を設定
CONTAINER_ID=$1
APP_FOLDER_PATH="$SCRIPT_DIR/../app"
CONTAINER_FOLDER_PATH="/app"

# コンテナ内のフォルダを削除
docker exec $CONTAINER_ID rm -rf $CONTAINER_FOLDER_PATH

# ホストマシンのフォルダをコンテナ内にコピー
docker cp $APP_FOLDER_PATH $CONTAINER_ID:$CONTAINER_FOLDER_PATH

docker restart $CONTAINER_ID

# Get the IP address
IP_ADDR=$(hostname -I | awk '{print $1}')

# Construct the URL
URL="http://$IP_ADDR:8000/"

# Echo the URL
echo "Access the application at: $URL"