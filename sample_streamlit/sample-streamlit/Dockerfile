# ベースイメージ
FROM python:3.8

# 環境変数を設定
ENV PYTHONIOENCODING utf-8

# app/ディレクトリを作成
WORKDIR /app

# パッケージをインストールする準備
RUN apt update
RUN apt install -y
RUN apt install -y python3-pip
RUN pip install --upgrade pip

# requirements.txtをコンテナ側にコピー
COPY requirements.txt .

# requirements.txtに記載されたパッケージをインストールする
RUN python3.8 -m pip install -r requirements.txt

# ローカル側のstreamlit-appディレクトリ配下にあるファイルをコンテナ側のappディレクトリにコピー
COPY ./sample-streamlit/streamlit-app/ /app
