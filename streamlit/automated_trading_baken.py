# coding: UTF-8

# """
# automated_trading_baken.pyの実装内容
# →馬券の自動購入
#
# -
# -
# -
# """

# 必要な関数のインポート
import sys
import seaborn as sns
import os
from datetime import date
from datetime import datetime
import pandas as pd
import time
import datetime
from tqdm import tqdm
import re
from urllib.request import urlopen
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.common.keys import Keys
# from webdriver_manager.core.utils import ChromeType

# memo-------------------------------------------------------------------------
# pathの設定(hydrogen用)
# streamlitリポジトリ用
FILE_PATH = "/Users/kawaharaatsushi/work_streamlit/streamlit/streamlit"
# dailydevリポジトリ用
FILE_PATH = "/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit"
sys.path.append(FILE_PATH)
FILE_PATH_BASE_DATA = FILE_PATH + '/data/base_data'
sys.path.append(FILE_PATH_BASE_DATA)
FILE_PATH_FIT_DATA = FILE_PATH + '/data/fit_data'
sys.path.append(FILE_PATH_FIT_DATA)
# memo-------------------------------------------------------------------------

# このファイルの場所を取得してパスを通す(別階層のファイルから呼び出しても変化しない)
# 参考)__file__: ~/streamlit/app.py
# path: ~/streamlit/
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-1])+'/')
# path: ~/streamlit/data/base_data
FILE_PATH_BASE_DATA = '/'.join(os.path.abspath(__file__).split('/')[:-1])+'/data/base_data'
sys.path.append(FILE_PATH_BASE_DATA)
# path: ~/streamlit/data/fit_data
FILE_PATH_FIT_DATA = '/'.join(os.path.abspath(__file__).split('/')[:-1])+'/data/fit_data'
sys.path.append(FILE_PATH_FIT_DATA)

# 自作関数のimport
from apps import create_predict_table
from functions.date_split_plot_pickle_functions import load_pickle


def main():
    options = ChromeOptions()  # ここで拡張機能を本来は設定するけど今回は省略
    # Chromeのoptionを設定（メインの理由はメモリの削減）
    # options.add_argument("--headless")
    # options.add_argument('--disable-gpu')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--remote-debugging-port=9222')
    # dockerを使用する場合とそれ以外の場合でseleniumの起動方法が違うため例外処理により、どっちがの方法が適用できるようにしている
    # self.driver = Chrome(ChromeDriverManager().install(), options=options)
    # webdriver_managerによりwebdriverをインストール
    # CHROMEDRIVER = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()  # chromiumを使用したいので引数でchromiumを指定しておく
    CHROMEDRIVER = ChromeDriverManager().install()  # chromiumを使用したいので引数でchromiumを指定しておく
    service = fs.Service(CHROMEDRIVER)
    driver = webdriver.Chrome(
        options=options,
        service=service,
        )

    url = "https://www.oddspark.com/keiba/"
    # url = "https://race.netkeiba.com/top/"
    # 競馬サイトのレース情報ページのトップを表示
    driver.get(url)

    # target_dateの部分のelementを取得する
    text_box = driver.find_element(By.NAME, 'SSO_PASSWORD')  # class_nameに空白がある場合はcss_selectorを使う.行頭と空白部分は"."とする.
    text_box.send_keys("id")
    text_box.text
    element = driver.find_element(By.CSS_SELECTOR, f'li[date="{target_date}"]')  # class_nameに空白がある場合はcss_selectorを使う.行頭と空白部分は"."とする.
    element_tag_a = element.find_element(By.TAG_NAME, "a")
    target_date_url = element_tag_a.get_attribute("href")  # 出馬テーブルのurlの文字列を取得する
    driver.get(target_date_url)
