# ベースのコンテナイメージを設定　FROM ~
# FROM python:3.9-slim
FROM python:3.9

# EXPOSE 80 → 指定したポートをリッスンするようになる
# docker run -p コマンドと合わせて使用することで初めて意味がある
EXPOSE 8501

# ユーザーの指定(ここではrootユーザーを指定)
USER root

# コンテナイメージ作成時に実行するコマンドを設定　RUN ~
# && コマンドでインストールするパッケージをまとめる方がイメージサイズを小さくできる
# apt install -y: 問い合わせがあればすべてyesと答える
# RUN build-essential: debian(OS)環境を構築するためのパッケージ一覧を一通りインストールできる

# RUN apt-get update && apt-get install -y
# RUN build-essential
# RUN software-properties-common
# RUN git
# RUN rm -rf /var/lib/apt/lists/*

# RUN apt install -y python3.9
RUN apt update
RUN apt install -y
RUN apt install -y python3-pip
RUN pip install --upgrade pip

# ローカルのファイルをコンテナ側にコピー
COPY requirements.txt .

# requirements.txt に記載しているパッケージをpython pipを使ってインストール
RUN python3.9 -m pip install -r requirements.txt

# 環境変数を設定
ENV SITE_DOMAIN=ohenzi.com
ENV PYTHONIOENCODING utf-8

# 作業ディレクトリを変更
WORKDIR /app

# COPY ADD 違い
# COPY: リモートのファイルを扱えない　urlを指定してコピーができない ＆　圧縮ファイルをそのままコピーする
# ADD : リモートのファイルを扱える　urlを指定してコピーができる　＆　圧縮ファイルを解凍してくれる
# 基本的にはCOPYで必要な時にのみADDを使用する感覚でいい

# iris_data(ファイル)の追加
# ADD [追加元のファイルパス][追加先のファイルパス]
# ADD https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data .

# コンテナ実行時に動かしたいシェルコマンドを指定 ENTRYPOINT ["実行ファイル", ”パラメータ１", ”パラメータ2"]
#  RUN: コンテナイメージ作成時に時刻
# ENTRYPOINT: コンテナ実行時(docker run)に実行
COPY . /app
COPY app.py .
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
