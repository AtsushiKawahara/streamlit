# ベースのコンテナイメージを設定　FROM ~
FROM python:3.9-slim

# ユーザーの指定(ここではrootユーザーを指定)
USER root

# コンテナイメージ作成時に実行するコマンドを設定　RUN ~
# && コマンドでインストールするパッケージをまとめる方がイメージサイズを小さくできる
RUN apt update
RUN apt install -y python3.9
RUN apt install -y python3-pip

# ローカルのファイルをコンテナ側にコピー
COPY requirements.txt .

# requirements.txt に記載しているパッケージをpython pipを使ってインストール
RUN python3.9 -m pip install -r requirements.txt

# 環境変数を設定
ENV SITE_DOMAIN=ohenzi.com

# 作業ディレクトリを変更
WORKDIR /var

# COPY ADD 違い
# COPY: リモートのファイルを扱えない　urlを指定してコピーができない ＆　圧縮ファイルをそのままコピーする
# ADD : リモートのファイルを扱える　urlを指定してコピーができる　＆　圧縮ファイルを解凍してくれる
# 基本的にはCOPYで必要な時にのみADDを使用する感覚でいい

# iris_data(ファイル)の追加
# ADD [追加元のファイルパス][追加先のファイルパス]
ADD https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data .

# コンテナ実行時に動かしたいシェルコマンドを指定 ENTRYPOINT ["実行ファイル", ”パラメータ１", ”パラメータ2"]
#  RUN: コンテナイメージ作成時に時刻
# ENTRYPOINT: コンテナ実行時(docker run)に実行
COPY script.py .
ENTRYPOINT ["python3.9", "script.py"]
