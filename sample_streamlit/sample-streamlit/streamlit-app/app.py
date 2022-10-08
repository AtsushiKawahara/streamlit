# coding:utf-8

import os
print(os.system("ls"))
print(os.system("pwd"))
# 必要なパッケージのインストール
from selenium import webdriver
from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import streamlit as st
import sys
import pickle

# pathの設定(スクレイピングしてきたデータを保存するディレクトリpathを取得)
FILE_PATH_FIT_DATA = '/'.join(os.path.abspath(__file__).split('/')[:-1])
sys.path.append(FILE_PATH_FIT_DATA)


def load_pickle(file_path, file_name):
    """
    pickleファイルをloadする関数
    """
    with open("{}/{}".format(file_path, file_name), 'rb') as f:
        return pickle.load(f)


def save_pickle(file_path, file_name, var_name):
    """
    pickleファイルをsaveする関数
    """
    with open("{}/{}".format(file_path, file_name), 'wb') as f:
        pickle.dump(var_name, f)


def main():

    # "is_horse_name_view"のkeyが存在しない場合に実行する(=1度しか実行されない)
    # st.sessionstateに格納する変数は再読み込みされても保持される
    if "is_horse_name_view" not in st.session_state:
        st.session_state["is_horse_name_view"] = None

    # ボタンを押すとスクレイピングを開始する
    press_button = st.button("スクレイピング開始")

    # ボタンが押されたときに実行される
    if press_button:

        # スクレイピングした馬名を表示する信号をONにする
        st.session_state["is_horse_name_view"] = True

        # スクレイピングをするためのoptionsを設定(今回は特に設定はなし)
        options = ChromeOptions()

        # docker
        driver = webdriver.Remote(command_executor="http://selenium:4444/wd/hub", options=options)

        # normal
        # driver = Chrome(ChromeDriverManager().install(), options=options)

        # 競馬サイトに接続
        url = "https://race.netkeiba.com/race/result.html?race_id=202206040401&rf=race_list"
        driver.get(url)

        # 競馬サイトの馬名が記載されている element を取得する
        horse_name_class_list = driver.find_elements(By.CLASS_NAME, "Horse_Name")

        # 馬名を抽出してlistに格納する
        horse_name_list = [horse_name.text for horse_name in horse_name_class_list]

        # 取得した馬名を格納したlistをpickleファイル形式で保存
        save_pickle(FILE_PATH_FIT_DATA, "horse_name_list.pickle", horse_name_list)

        # ブラウザを閉じる
        driver.close()

    # st.session_stateを定義しておくことでページが更新されても
    # スクレイピング開始ボタンが押されない限り馬名のradioは表示され続ける
    if st.session_state["is_horse_name_view"]:
        # 上で保存した馬名listを読み込む
        horse_name_list = load_pickle(FILE_PATH_FIT_DATA, "horse_name_list.pickle")
        # 取得した馬名をradioで表示する
        st.radio('出場する馬の一覧', (horse_name_list))


if __name__ == '__main__':
    main()
