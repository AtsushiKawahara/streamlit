# coding: UTF-8

"""
automated_trading_tyuuou.pyの実装内容
→中央競馬場のレースの馬券の自動購入
- "https://jra.jp"のサイトからseleniumにより馬券を自動購入する
- 予測モデルで勝つと予測した馬の馬券を購入する
-
"""

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

# memo-------------------------------------------------------------------------
# pathの設定(hydrogen用)
# streamlitリポジトリ用
FILE_PATH = "/Users/kawaharaatsushi/work_streamlit/streamlit/streamlit"
# dailydevリポジトリ用
# FILE_PATH = "/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit"
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
from functions.date_split_plot_pickle_functions import save_pickle
from functions.date_split_plot_pickle_functions import get_swap_dict

# config.iniから変数を読み込んでおく
config_ini = configparser.ConfigParser()
config_ini.read(f"{FILE_PATH}/config.ini", encoding="utf-8")
SUBSCRIBER_NUMBER = config_ini["https://jra.jp"]["SUBSCRIBER_NUMBER"]
P_ARS_NUMBER = config_ini["https://jra.jp"]["P_ARS_NUMBER"]
INET_ID = config_ini["https://jra.jp"]["INET_ID"]
PASSWORD = config_ini["https://jra.jp"]["PASSWORD"]

# 固定条件を設定
BET_MONEY = 1  # この数値 * 100 の金額を１レースでbetする


def click(driver_, elem):
    """
    seleniumでjavascriptによりbuttonをクリックするための関数
    seleniumのデフォルトにclick()関数では、画面外のボタンはClickできなため
    (javascriptの仕組み)
    argumentsは引数がリスト形式で格納されている[0],[1]などで引数を指定
    arguments[0]にはelemが渡されている
    引数に渡したelem要素をclickする
    javascriptで実行するとなぜ、画面外のボタンがclickできるようになるかはわからなかった!!!
    (注)xpathで要素を指定した場合にしか利用できない
    """
    driver_.execute_script('arguments[0].click();', elem)


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
    url = "https://jra.jp"
    # url = "oddspark.com/keiba/"
    # 競馬サイトのレース情報ページのトップを表示
    driver.get(url)

    # INET_ID入力画面へ移動(Topページ→INET-ID入力画面)
    login_page_button = driver.find_element(By.CLASS_NAME, 'header_login_btn')
    login_page_button.click()  # これでINET-ID入力画面が新しいwindowでページが開かれる

    # INET_IDは新しいウィンドウで表示されるためドライバーのウィンドウハンドルを切り替える
    new_hangles = driver.window_handles  # 新しいwindowで開いたページのウィンドウハンドルを取得する(リスト形式)
    driver.switch_to.window(new_hangles[1])  # [0]: Topページ, [1]: INET_ID入力ページ

    # INET_IDを入力(INET-ID入力画面→加入者情報入力画面)
    text_box_inet_id = driver.find_element(By.NAME, "inetid")
    text_box_inet_id.send_keys(f"{INET_ID}")  # INET_IDを入力
    login_page_button = driver.find_element(By.CLASS_NAME, 'button')  # ログインボタン　
    login_page_button.click()  # ログインボタンを押して加入者情報入力画面

    # 加入者番号、暗証番号、P-PAS番号を入力(加入者情報入力画面→Myページ(ログイン完了))
    text_box_subscribe_number = driver.find_element(By.NAME, "i")  # 加入者番号入力覧
    text_box_subscribe_number.send_keys(f"{SUBSCRIBER_NUMBER}")
    text_box_password = driver.find_element(By.NAME, "p")  # 暗証番号入力覧
    text_box_password.send_keys(f"{PASSWORD}")
    text_box_p_ars_number = driver.find_element(By.NAME, "r")  # P_ARS番号入力覧
    text_box_p_ars_number.send_keys(f"{P_ARS_NUMBER}")
    login_page_button = driver.find_element(By.CLASS_NAME, "buttonModern")  # ログインボタン
    login_page_button.click()  # ログインボタンを押してログインが完了する

    # Myページ(ネット投票画面→通常投票画面)
    normal_vote_page_button = driver.find_element(By.XPATH, f"//div/button[@ui-sref='bet.basic']")  # 通常投票ページ移動ボタン
    click(driver, normal_vote_page_button)

    # 通常投票ページボタンを押すと入金指示を喚起する表示がでるため、『このまま進む』ボタンを押して通常投票ページへ移動する(口座に残高があればこの表示はされないか確認しておく必要あり)
    kakuninn_button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-default.btn-lg.btn-ok.ng-binding")
    kakuninn_button.click()

    # 予測テーブルなどの必要なデータを読み込んでおく
    predict_table = load_pickle(FILE_PATH_FIT_DATA, "predict_table.pickle")  # 予測テーブルを読み込む
    predict_table_sannrenntann = load_pickle(FILE_PATH_FIT_DATA, "predict_table_sannrenntann.pickle")  # 三連単用予測テーブル

    # 開催されるレースのrace_idからレース会場情報を取り出す(race_idは12桁で5,6文字目が会場を示している)
    # ex)sample_race_id = 2022"05"050801: "05"は東京を示している
    # 会場と数字の紐付けは以下の辞書のとおり
    # 中央競馬場(net.keiba.com)
    place_dict = {
                  "札幌": "01", "函館": "02", "福島": "03", "新潟": "04",
                  "東京": "05", "中山": "06", "中京": "07", "京都": "08",
                  "阪神": "09", "小倉": "10"}
    place_swap_dict = get_swap_dict(place_dict)  # 上記の辞書の逆引き辞書を作成しておく(会場コードから会場名(str)を取得するため)
    race_id_list = predict_table.index.unique()  # 予測テーブルからrace_idを取り出す(indexがrace_id)
    target_place_code_list_tmp = [race_id[4:6] for race_id in race_id_list]  # 会場コードを格納するリスト([4:6]→5・６文字目を取得)
    target_place_code_list = list(set(target_place_code_list_tmp))  # 重複する会場をset()関数で削除した後リスト型に戻す

    # 会場ごとに馬券を購入していく
    for target_place_code in target_place_code_list:

        # memo-----------------------------------------------------------------
        # target_place_code = target_place_code_list[0]
        # target_place_code = '09'
        # target_place = "東京"
        # target_place = "阪神"
        # target_place_code
        # target_place
        # memo-----------------------------------------------------------------

        # 会場コードから会場名(str)を取得
        target_place = place_swap_dict[target_place_code]  # ex)"05"→"東京"

        # target_placeで指定している会場の選択(通常投票画面設定)
        # 要素の指定方法は以下のurl参照:https://ai-inter1.com/xpath/
        target_place_button = driver.find_element(By.XPATH, f"//div[@class='place-name']/span[contains(text(), '{target_place}')]/ancestor::button[contains(@class, 'btn')]")
        # target_place_button.click()
        click(driver, target_place_button)

        # レースごとに馬券を購入していく(全レース投票画面)
        target_race_id_list = [race_id for race_id in race_id_list if race_id[4:6] == target_place_code]  # 指定会場で開催されるrace_idを抽出
        target_race_id_list
        for race_id in target_race_id_list:

            # memo-------------------------------------------------------------
            # race_id = target_race_id_list[-1]
            # race_id
            # target_race_id_list
            # R = 12
            # R = 22
            # R
            # memo-------------------------------------------------------------

            # race_idからラウンド数を整数型で取得(race_idの１１・１２文字がラウンド数を示している)
            R = int(race_id[10:12])

            # ラウンドごとのレース画面へ
            race_page_button = driver.find_element(By.XPATH, f"//div[@class='race-no']/span[contains(text(), {R})]/parent::div[@class='race-no']/parent::button")
            click(driver, race_page_button)

            # 全レースを投票画面へ移動(通常投票画面設定→全レース投票画面)
            # click(driver, target_place_all_race_vote_page_button)
            # target_place_all_race_vote_page_button = driver.find_element(By.XPATH, "//button[contains(@ng-click, 'ALL_RACE_NUM')]")
            # target_place_all_race_vote_page_button.click()
            # click(driver, target_place_all_race_vote_page_button)

            # 購入する馬券を選択(全レース投票画面)
            baken_type_button = driver.find_element(By.XPATH, "//option[@label='３連単']")
            baken_type_button.click()
            # click(driver, baken_type_button)

            # # ラウンドからレースを選択(指定したラウンドのレースが終了している場合は例外処理により次のレース購入に移る)
            # try:
            #     # (全レース投票画面→各レース投票画面)
            #     target_race_button = driver.find_element(By.XPATH, f"//option[contains(@label, '{R}')]")
            #     target_race_button.click()
            #     # click(driver, third_umaban_button)
            # except Exception as e:
            #     print(f"error code:{e}")
            #     print(f"{R}のレースは終了しているため次のレース購入処理を行う")
            #     continue

            # 予測テーブルから購入する馬番を決定
            bet_umaban_str = predict_table_sannrenntann[predict_table_sannrenntann.index == race_id].sort_values("diff", ascending=False).head(1)["umaban_pred"][0]  # ex)'14-6-15'
            bet_umaban_str
            first_umaban = int(bet_umaban_str.split("-")[0])  # 1着予想の馬番
            second_umaban = int(bet_umaban_str.split("-")[1])  # 2着予想の馬番
            third_umaban = int(bet_umaban_str.split("-")[2])  # 3着予想の馬番

            # 1着,2着,3着をそれぞれ選択する
            first_umaban_button = driver.find_element(By.XPATH, f"//td[contains(@class, 'racer-first')]/label[contains(@for, 'horse1_no{first_umaban}')]/span")
            click(driver, first_umaban_button)
            # 2着予想の馬番にチェックを入れる(各レース投票画面)
            second_umaban_button = driver.find_element(By.XPATH, f"//td[contains(@class, 'racer-second')]/label[contains(@for, 'horse2_no{second_umaban}')]/span")
            click(driver, second_umaban_button)
            # 3着予想の馬番にチェックを入れる(各レース投票画面)
            third_umaban_button = driver.find_element(By.XPATH, f"//td[contains(@class, 'racer-third')]/label[contains(@for, 'horse3_no{third_umaban}')]/span")
            click(driver, third_umaban_button)

            # 金額をセットする(各レース投票画面)
            bet_money_text_box = driver.find_element(By.XPATH, "//input[@aria-labelledby='select-list-amount-unit']")
            bet_money_text_box.send_keys(BET_MONEY)

            # セットボタンを押す(各レース投票画面)
            set_button = driver.find_element(By.XPATH, "//button[@ng-click='vm.onSet()']")
            set_button.click()  # これでこのラウンドでの馬券の購入が完了

            # 購入画面へ進む
            driver.find_element(By.XPATH, "//button[contains(@class, 'btn-vote-list')]").click()
            # 合計金額入力
            driver.find_element(By.XPATH, "//td[contains(@class, 'text-right')]/span[contains(text(), '合計金額入力')]/following-sibling::input").send_keys(int(str(BET_MONEY) + "00"))

            # 購入確定
            kounyuu_button = driver.find_element(By.XPATH, "//button[contains(text(), '購入する')]")
            click(driver, kounyuu_button)

            # 最終確認
            kounyuu_kakutei_button = driver.find_element(By.XPATH, "//button[contains(text(), 'OK')]")
            click(driver, kounyuu_kakutei_button)

            # 続けて購入ボタン
            """
            限度額を超えた場合の例外処理をいれること
            """
            kounyuu_continue_button = driver.find_element(By.XPATH, "//button[contains(text(), '続けて投票する')]")
            click(driver, kounyuu_continue_button)


if __name__ == '__main__':
    main()
