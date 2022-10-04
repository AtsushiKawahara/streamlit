# python3.8をベースイメージとする
FROM python:3.8

# コンテナ内にappディレクトリを作成
WORKDIR /app

# pythonパッケージをインストールするための準備
RUN apt update
RUN apt install -y
RUN apt install -y python3-pip
RUN pip install --upgrade pip

# app.pyで使用するパッケージをインストール
RUN pip install pandas
RUN pip install numpy

# ローカルのapp.pyファイルをコンテナ内容appディレクトリにコピーする
COPY app.py /app
