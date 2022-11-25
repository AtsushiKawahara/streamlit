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
import configparser
# from webdriver_manager.core.utils import ChromeType

# 自作関数のインポート
from functions.date_split_plot_pickle_functions import load_pickle
from functions.date_split_plot_pickle_functions import save_pickle

# config.iniから変数を読み込んでおく
config_ini = configparser.ConfigParser()
config_ini.read("config.ini", encoding="utf-8")
ID = config_ini["oddspark.com/keiba/"]["ID"]
PASSWORD = config_ini["oddspark.com/keiba/"]["password"]
PERSONAL_NUMBER = config_ini["oddspark.com/keiba/"]["personal_number"]

# 固定条件を設定
BET_MONEY = 1  # この数値 * 100 の金額を１レースでbetする

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

    # ログインフォームにパスワードとIDを入力(オッズパークTopページ)
    text_box_account_id = driver.find_element(By.NAME, 'SSO_ACCOUNTID')
    text_box_account_id.send_keys(f"{ID}")
    text_box_password = driver.find_element(By.NAME, 'SSO_PASSWORD')
    text_box_password.send_keys(f"{PASSWORD}")

    # ログイン(オッズパークTopページ)
    login_form = driver.find_element(By.NAME, 'loginForm')
    login_button = login_form.find_element(By.PARTIAL_LINK_TEXT, "ログイン")
    login_button.click()  # ログイン実行し暗証番号入力ページへ移動

    # 暗証番号入力(暗証番号入力ページ)
    text_box_pin = driver.find_element(By.NAME, "INPUT_PIN")
    text_box_pin.send_keys(f"{PERSONAL_NUMBER}")

    # 暗証番号を送信(暗証番号入力ページ)
    login_button = driver.find_element(By.NAME, "送信")
    login_button.click()  # マイページへ移動

    # マイページから投票のトップページへ移動(マイページ→投票ページTop)
    vote_keiba_top_page = driver.find_element(By.CLASS_NAME, "nv4")
    vote_keiba_top_url = vote_keiba_top_page.get_attribute("href")
    driver.get(vote_keiba_top_url)

    # 投票トップページから指定日の投票ページへ移動(投票ページTop→指定日の投票ページ)
    now_date = datetime.datetime.now().date()  # 現在日付 ex)datetime.date(2022, 11, 3)
    target_date = f"{now_date.year}{now_date.month}{now_date.day}"  # 今日の年月日の８桁を文字列に変換
    vote_keiba_target_date_page = driver.find_element(By.XPATH, f"//a[@data-kaisaibi={target_date}]")
    vote_keiba_target_date_page.click()

    # 購入する馬券を選択-----------------------------------------------------------
    # 中央競馬場(net.keiba.com)
    place_dict = {
                  "札幌": "01", "函館": "02", "福島": "03", "新潟": "04",
                  "東京": "05", "中山": "06", "中京": "07", "京都": "08",
                  "阪神": "09", "小倉": "10"}
    # 地方競馬場(オッズパーク)
    place_dict = {
                  "帯広": "03", "門別": "06", "盛岡": "11", "水沢": "12",
                  "金沢": "41", "笠松": "42", "名古屋": "43", "園田": "51",
                  "姫路": "52", "高知": "55", "佐賀": "61"
                  }
    # レーズまとめタクを選択(指定日の投票ページ)
    vote_keiba_race_matome_tag = driver.find_element(By.XPATH, f"//ul[@id='course']/li[@value='00']")
    vote_keiba_race_matome_tag.click()

    # セット金額を設定
    bet_money_text_box = driver.find_element(By.XPATH, "//div[@id='section3']/div[@class='bl-left10']/input")
    bet_money_text_box.clear()  # 初期値で１が入力されているため削除
    bet_money_text_box.send_keys(BET_MONEY)

    # 賭式を選択(とりあえず三連単の馬券のみをチェック仕様としている)
    """
    各馬券が初期状態でチェックされている場合があるため
    全てのチェック状態を確認して以下の処理を行う(→全ての賭式のチェックを外す)
    - チェックあり・・・チェックを外す
    - チェックなし・・・なにもしない
    上記の処理後に三連単のチェックボックスにチェックをいれる
    """

    baken_type_count = len(driver.find_elements(By.XPATH, "//tr[@class='bg-6-pl']/td"))  # 馬券の種類
    baken_type_count

    # 馬券の数だけチェックボックスの状態を確認する処理を行う
    for i in range(1, baken_type_count + 1):  # i = 1~9
        # memo------------------------------------------------------------------
        # i = 1
        # memo------------------------------------------------------------------
        is_check_selected = driver.find_element(By.XPATH, f"//tr[@class='bg-6-pl']/td[@class='bt{i}']/input")  # ex)bt1:単勝, bt2:複勝,・・・bt9:３連単
        # 各馬券のチェックボックスの状態を確認
        if is_check_selected.is_selected():  # is_selected():checkされているとTrueをかえす
            # チェックされている場合・・・チェックを外す
            is_check_selected.click()

    # ３連単にチェック
    sannrenntan_check_box = driver.find_element(By.XPATH, "//tr[@class='bg-6-pl']/td[@class='bt9']/input")  # bt9:３連単のチェックボックス
    sannrenntan_check_box.click()

    # 開催される日付と場所を取得(開催場所が複数であれば要素も複数となる)して各場所で購入する馬券を指定
    for i in len(driver.find_elements(By.XPATH, "//td[@rowspan='2']")):  # 開催場所分処理
        # memo-----------------------------------------------------------------
        # i = 0
        # driver.find_elements(By.XPATH, "//td[@rowspan='2']")
        # memo-----------------------------------------------------------------
        date_and_place_str = driver.find_elements(By.XPATH, "//td[@rowspan='2']")[i].text  # ex)'11/23\n名古屋'
        date_and_place_str
        # target_date = date_and_place_str.split("\n")[0]  # 改行箇所(\n)で分割して前が日付
        target_place = date_and_place_str.split("\n")[1]  # 改行箇所(\n)で分割して後ろが馬場
        target_place_num = place_dict[target_place]  # 馬場を馬場idへ変換 ex)"名古屋"→"43"
        # memo-----------------------------------------------------------------
        i
        target_place_num
        target_date
        # memo-----------------------------------------------------------------

        # 1R~12Rまでの投票(各馬券ごと)
        for j in range(1, 13, 1):  # j = 1~12
            # memo--------------------------------------------------------------
            j = 12
            # memo--------------------------------------------------------------

            round_str = str(j).zfill(2)  # ラウンド数を文字列で２桁にしておく
            round_str

            # レース選択→ラウンドのチェックボックスにチェック
            target_round = driver.find_element(By.XPATH, f"//input[@value='{target_date}_{target_place_num}_{j}']")
            target_round.click()

            # 賭ける馬番にチェック
            # 予測テーブルから勝つと予想した馬番を取得
            df = load_pickle(FILE_PATH_FIT_DATA, "predict_table_sannrenntann.pickle")  # 予測テーブル
            pattern = rf"[0-9][0-9][{target_place_num[0]}][{target_place_num[1]}][0-9][0-9][0-9][0-9][{round_str[0]}][{round_str[1]}]"  # 会場の２桁を含むrace_idを抽出するための正規表現
            # pattern = rf"[0-9][0-9][0][5][0-9][0-9][0-9][0-9][{round_str[0]}][{round_str[1]}]"  # 会場の２桁を含むrace_idを抽出するための正規表現

            # 正規表現でラウンドと会場が一致しているrace_idの予測テーブルを抽出
            predict_sannrenntann_umaban_str = df[df.index.str.contains(pattern)].sort_values("diff", ascending=False).head(1)["umaban_pred"].values[0]

            first_umaban = int(predict_sannrentann_umaban_str.split("-")[0])  # 1着予想の馬番
            second_umaban = int(predict_sannrentann_umaban_str.split("-")[1])  # 2着予想の馬番
            third_umaban = int(predict_sannrentann_umaban_str.split("-")[2])  # 3着予想の馬番
            first_umaban
            second_umaban
            third_umaban

            # 1着と予想する馬番にチャックをいれる
            first_umaban_check_boxs = driver.find_elements(By.XPATH, f"//td[@name='horse1']")  # 1着の馬番をチェックする箇所(1~12番まである)
            for first_umaban_check_box in first_umaban_check_boxs: # first_umaban_check_box: 1~12の該当する馬番の箇所にチェックを入れる
                if int(first_umaban_check_box.text) == first_umaban:
                    first_umaban_check_box.click()

            # 2着と予想する馬番にチャックをいれる
            second_umaban_check_boxs = driver.find_elements(By.XPATH, f"//td[@name='horse2']")  # 2着の馬番をチェックする箇所(1~12番まである)
            for second_umaban_check_box in second_umaban_check_boxs: # second_umaban_check_box: 1~12の該当する馬番の箇所にチェックを入れる
                if int(second_umaban_check_box.text) == second_umaban:
                    second_umaban_check_box.click()

            # 3着と予想する馬番にチャックをいれる
            third_umaban_check_boxs = driver.find_elements(By.XPATH, f"//td[@name='horse3']")  # 3着の馬番をチェックする箇所(1~12番まである)
            for third_umaban_check_box in third_umaban_check_boxs: # third_umaban_check_box: 1~12の該当する馬番の箇所にチェックを入れる
                if int(third_umaban_check_box.text) == third_umaban:
                    third_umaban_check_box.click()

            # 入力完了後にセットボタンを推して購入する馬券一覧に追加する
            set_button = driver.find_element(By.XPATH, "//a[@id='multiSet']")  # セットボタン(これを押すと選択した馬券が買い目一覧に追加される)
            vote_set_button.click()

        # 投票のセットが完了したら購入確認ページへ移動(指定日の投票ページ→購入確認画面)
        vote_data_send_button = driver.find_element(By.XPATH, "//a[@id='gotobuy']")
        vote_data_send_button.click()

        # 購入を実行
        vote_zikkou = driver.find_element(By.XPATH, "//a[@id='buy']")
        # vote_zikkou.click()
