# coding:utf-8

"""
出馬テーブルのスクレイピングの機能を実装したStart_Horse_Table_classファイル
"""

# 必要な関数のインポート
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
# streamlit用に必要なライブラリのインポート
import sys
import os

# 辞書型定義

PLACE_DICT = {
    "札幌": "01", "函館": "02", "福島": "03", "新潟": "04",
    "東京": "05", "中山": "06", "中京": "07", "京都": "08",
    "阪神": "09", "小倉": "10"}

PLACE_DICT_REVERSE = {
    "01": "札幌", "02": "函館", "03": "福島", "04": "新潟",
    "05": "東京", "06": "中山", "07": "中京", "08": "京都",
    "09": "阪神", "10": "小倉"}

RACE_TYPE_DICT = {
    "ダ": "ダート", "芝": "芝", "障": "障害"
    }

# 学習データとして使用する年を設定
GET_DATA_YEAR_LIST = [2017, 2018, 2019, 2020, 2021, 2022]  # 取得したい年を指定

# pathの設定
# PATHの設定(絶対パス)
# このファイルの場所を取得してパスを通す(別階層のファイルから呼び出しても変化しない)
# 参考)__file__: ~/streamlit/apps/data_get_program_file/scraping_shutuba_table.py
# path: ~/streamlit/
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-3])+'/')
# path: ~/streamlit/apps/
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-2])+'/')

# memo-------------------------------------------------------------------------
# # hydrogen実行用
# # streamlitリポジトリ用
# FILE_PATH = "/Users/kawaharaatsushi/work_streamlit/streamlit/streamlit"
# # dailydevリポジトリ用
# FILE_PATH = "/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit"
# sys.path.append(FILE_PATH)
# # path: ~/streamlit/base_data
# FILE_PATH_BASE_DATA = FILE_PATH+'/data/base_data'
# sys.path.append(FILE_PATH_BASE_DATA)
# # path: ~/streamlit/fit_data
# FILE_PATH_FIT_DATA = FILE_PATH+'/data/fit_data'
# sys.path.append(FILE_PATH_BASE_DATA)
# memo-------------------------------------------------------------------------

# sys.path.append(FILE_PATH_TMP)

# 自作関数のインポート
from apps.create_model import Data_Processer


class Start_Horse_Table(Data_Processer):
    def __init__(self):
        super(Start_Horse_Table, self).__init__()
        self.data = 0  # 説明変数作成用
        self.race_info_dict = 0
        self.shutuba_tables = 0  # streamlitで表示用の出馬テーブル
        self.result_tables = 0  # 回収率算出用のresultテーブル

    # def scrape_by_ChromeDriverManager_at_target_date(self, target_date):
    def start_up_chromedriver(self):
        """
        class内で使用するドライバーを作成
        """
        # googleを起動
        options = ChromeOptions()  # ここで拡張機能を本来は設定するけど今回は省略
        # Chromeのoptionを設定（メインの理由はメモリの削減）
        # options.add_argument("--headless")
        # options.add_argument('--disable-gpu')
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('--remote-debugging-port=9222')

        # dockerを使用する場合とそれ以外の場合でseleniumの起動方法が違うため例外処理により、どっちがの方法が適用できるようにしている
        try:
            # docker使用時
            self.driver = webdriver.Remote(command_executor="http://selenium:4444/wd/hub", options=options)
        except Exception as e:
            # docker未使用時
            print(f"selenium error RemoteではないためChrome(~)により起動 error code:{e}")
            # self.driver = Chrome(ChromeDriverManager().install(), options=options)
            # webdriver_managerによりwebdriverをインストール
            # CHROMEDRIVER = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()  # chromiumを使用したいので引数でchromiumを指定しておく
            CHROMEDRIVER = ChromeDriverManager().install()  # chromiumを使用したいので引数でchromiumを指定しておく
            service = fs.Service(CHROMEDRIVER)
            self.driver = webdriver.Chrome(
                options=options,
                service=service,
                )

        # memo------------------------------------------------------------------
        # # streamlit cloudで使用するためのchromedrive起動方法は以下
        # # googleを起動
        # options = ChromeOptions()  # ここで拡張機能を本来は設定するけど今回は省略
        # # Chromeのoptionを設定（メインの理由はメモリの削減）
        # options.add_argument("--headless")
        # options.add_argument('--disable-gpu')
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('--remote-debugging-port=9222')
        # CHROMEDRIVER = ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()  # chromiumを使用したいので引数でchromiumを指定しておく
        # service = fs.Service(CHROMEDRIVER)
        # self.driver = webdriver.Chrome(
        #         options=options,
        #         service=service,
        #         )
        # memo------------------------------------------------------------------

    def scrape_specified_date_race_id(self, target_date):
        """
        target_dateで指定した日に開催れるレースのrace_id_listを取得(ChromeDriverManagerにより取得)

        params:
        target_date(str): 出馬表を取得したい月日を○月○日の形で指定する ex)"7月23日"

        return:
        race_id_list(list): target_dateで指定した日に開催されるレースidが格納されたリスト
        """
        # memo-----------------------------------------------------------------
        # target_date = "2022年10月30日"
        # table_type = "shutuba_table"
        # create_predict_table(target_date, is_real_time=True, table_type="shutuba_table")
        # memo-----------------------------------------------------------------

        # 日付を入力するとその日のレース情報(説明変数情報)を取得できるようにする

        url = "https://race.netkeiba.com/top/"

        # 競馬サイトのレース情報ページのトップを表示
        self.driver.get(url)

        # target_dateの部分のelementを取得する
        element = self.driver.find_element(By.CSS_SELECTOR, f'li[date="{target_date}"]')  # class_nameに空白がある場合はcss_selectorを使う.行頭と空白部分は"."とする.
        element_tag_a = element.find_element(By.TAG_NAME, "a")
        target_date_url = element_tag_a.get_attribute("href")  # 出馬テーブルのurlの文字列を取得する
        self.driver.get(target_date_url)

        # target_dateで指定した日にレースがある会場名を取得(基本２会場)
        place_list = []  # レース会場名(ex:中京)を格納するlist
        # 開催される会場でのレース情報があるclassを取得する
        elements_at_place = self.driver.find_elements(By.CLASS_NAME, "RaceList_DataTitle")  # class_nameに空白がある場合はcss_selectorを使う.行頭と空白部分は"."とする.
        # 会場ごとのレース情報が入っている部分から会場名のみ取得
        for element_at_place in elements_at_place:
            place_contain_str_list = element_at_place.text.split(" ")  # ex)['5回', '中京', '4日目']
            for str_ in place_contain_str_list:
                # 数字を含んでいない会場を表す文字列のみを抽出
                if not any(chr.isdigit() for chr in str_):
                    place_list.append(str_)
        # target_dateで指定した日に開催されるレースidを取得する
        all_race_id_list = []  # 取得したrace_idを格納するリストを作成
        # 会場ごとにレースごとの出走実行を把握するための辞書を作成する(基本２会場でレースが開催されるため2つの辞書を用意)
        start_time_and_race_id_dict_place_1 = {}  # key: race_id, value: timeの辞書を作成
        start_time_and_race_id_dict_place_2 = {}  # key: race_id, value: timeの辞書を作成
        # ２つの会場のレース情報が格納されている箇所を取得(1会場だいたい12レース(R)ある)
        elements_at_all_place_race_list = self.driver.find_elements(By.CLASS_NAME, "RaceList_Data")  # class_nameに空白がある場合はcss_selectorを使う.行頭と空白部分は"."とする.
        # memo-------------------------------------------------------------
        # element_at_all_place_race_list = elements_at_all_place_race_list[0]
        # memo-------------------------------------------------------------
        # １会場ごとにrace_idを取得する
        # レース会場ごとに格納するdictを分けるためzip()を使用している→もっといい方法ありそうだけどとりまこれで
        for element_at_all_place_race_list, i in zip(elements_at_all_place_race_list, range(len(elements_at_all_place_race_list))):
            elements_at_all_race_list = element_at_all_place_race_list.find_elements(By.TAG_NAME, "a")
            # memo----------------------------------------------------------
            # element = elements_at_all_race_list[0]
            # memo----------------------------------------------------------
            for element in elements_at_all_race_list:
                # １つのrace_idに出馬テーブルか動画テーブルがあるから動画テーブルの方はpassする
                if not "movie" in element.get_attribute("href"):
                    start_time = element.find_element(By.CLASS_NAME, "RaceList_Itemtime").text  # レースの出走時刻
                    href_str = element.get_attribute("href")  # 出馬テーブルのurlの文字列
                    # hrefは"https://race.netkeiba.com/race/movie.html?race_id=202207050412&rf=race_list"
                    # ↑こんな形状をしていて"race_id=〇〇"の部分を取得する処理を以下で行っている
                    target_str = "race_id="  # href(url)のrace_id以降の文字列を取得するためにtarget_strを設定
                    idx = href_str.find(target_str)  # href(url)のrace_idが始まる文字列の位置を取得(それ以降を取得する)
                    race_id = re.findall(r"\d+", href_str[idx+len(target_str):])[0]
                    all_race_id_list.append(race_id)
                    if i == 0:  # 1会場目のレースidを格納
                        start_time_and_race_id_dict_place_1[race_id] = start_time
                    if i == 1:  # 2会場目のレースidを格納
                        start_time_and_race_id_dict_place_2[race_id] = start_time

        # 取得したrade_id_listの重複するidを削除かつ昇順にソートする
        race_id_list = sorted(set(all_race_id_list), key=all_race_id_list.index)
        return race_id_list

    def shutuba_tables_scrape(self, race_id_list):
        """
        race_idから出馬テーブルを取得する

        以下の２つのclassmethodで共通の処理をするため別でメソッドにしている
        scrape_by_ChromeDriverManager_at_race_id_list(cls, race_id_list):
        scrape_by_ChromeDriverManager_at_target_date(cls, target_date, is_real_time):
        """

        # memo-----------------------------------------------------------------
        # race_id = 202203030309
        # memo-----------------------------------------------------------------

        race_id_dict = {}  # 説明変数を作成するのに必要なデータを格納する
        race_info_dict = {}  # レース名 出走時刻 何レース目 の情報を格納する
        shutuba_table_dict = {}  # 出馬テーブルを格納する(streamlit用)

        for race_id in tqdm(race_id_list):

            df = pd.DataFrame()

            url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}&rf=race_list"

            self.driver.get(url)

            # elements = driver.find_elements_by_class_name("HorseList")  # find_element"s"にすると指定のclass_nameを複数取得する"s"をつけないと１つだけ取得する
            elements = self.driver.find_elements(By.CLASS_NAME, "HorseList")  # find_element"s"にすると指定のclass_nameを複数取得する"s"をつけないと１つだけ取得する

            # 馬、騎手、調教師情報が記載されている箇所を取得する
            for element in elements:
                # tds = element.find_elements_by_tag_name("td")
                tds = element.find_elements(By.TAG_NAME, "td")
                info = []
                for td in tds:
                    if td.get_attribute("class") in ["HorseInfo", "Jockey", "Trainer"]:
                        # find_text = td.find_element_by_tag_name("a").get_attribute("href")
                        find_text = td.find_element(By.TAG_NAME, "a").get_attribute("href")
                        # td.find_element_by_tag_name("a").text
                        td.find_element(By.TAG_NAME, "a").text
                        info.append(re.findall(r"\d+", find_text)[0])
                    info.append(td.text)
                # df = df.append(pd.Series(info, name=race_id))
                df = pd.concat([df, pd.DataFrame([info], index=[race_id])])
            # RaceData01 = self.driver.find_element_by_class_name("RaceData01").text
            RaceData01 = self.driver.find_element(By.CLASS_NAME, "RaceData01").text
            RaceData01_texts = re.findall(r"\w+", RaceData01)

            for text in RaceData01_texts:
                if text in ['曇', '晴', '雨', '小雨', '小雪', '雪']:  # 天気を判別
                    df['weather'] = [text] * len(df)
                if "芝" in text:  # raceが芝かダートなのかを判別
                    df['race_type'] = ["芝"] * len(df)
                if "ダ" in text:  # raceが芝かダートなのかを判別
                    df['race_type'] = ["ダート"] * len(df)
                if '障' in text:  # 障害物があるかないか判別
                    df['race_type'] = [text] * len(df)
                if text in ['稍重', '良', '重', '不良']:  # グラウンドの状態
                    df["ground_state"] = [text] * len(df)
                if '稍' in text:
                    df["ground_state"] = ['稍重'] * len(df)
                if "不" in text:  # グラウンドの状態
                    df["ground_state"] = ["不良"] * len(df)
                if 'm' in text:  # レースの距離を抽出
                    if '周' in text:
                        text_1 = re.findall(r'(.*)(?=m)', text) * len(df)  # 'm'より前の文字列を取得
                        text_2 = re.findall(r'(?<=周)(.*)', text_1) * len(df)  # '周'より後の文字列を取得
                        df["course_len"] = text_2 * len(df)
                    else:
                        df["course_len"] = re.findall(r'\d+', text) * len(df)

            # レースの日付を取得しておく
            date_text = self.driver.title
            pattern = r'\d+[年]\d+[月]\d+[日]'  # 0000年0月0日を取得できる正規表現のパターンを作成
            date_ = re.findall(pattern, str(date_text))[0]  # 日付を抽出
            df['date'] = pd.to_datetime([date_] * len(df), format='%Y年%m月%d日')  # datetime型に変更しつつdfの列を作成

            df_shutuba_table = df[[0, 1, 4, 5, 6, 8, 10, 11, 12, 13]].copy()  # streamlitで出馬テーブルを表示する用
            df_shutuba_table.columns = ["枠", "馬番", "馬名", "性齢", "斤量", "騎手", "調教師", "馬体重(増減)", "オッズ", "人気"]
            df = df[[0, 1, 5, 6, 12, 13, 11, 3, 7, 9, "course_len", "weather", "race_type", "ground_state", "date"]].copy()
            df.columns = ["枠", "馬番", "性齢", "斤量", "単勝", "人気", "馬体重(増減)", "horse_id", "jockey_id", "trainer_id", "course_len", "weather", "race_type", "ground_state", "date"]

            race_id_dict[race_id] = df
            shutuba_table_dict[race_id] = df_shutuba_table

            # レース名を文字列で取得
            # race_name_str = self.driver.find_element_by_class_name("RaceName").text
            race_name_str = self.driver.find_element(By.CLASS_NAME, "RaceName").text

            # 出走時刻を文字列で取得
            # start_time_element = self.driver.find_element_by_class_name("RaceData01").text  # 出走時刻が記載されたelementを取得
            start_time_element = self.driver.find_element(By.CLASS_NAME, "RaceData01").text  # 出走時刻が記載されたelementを取得
            start_time_str = re.search(r"(.+)発走", start_time_element).group()  # 出走時刻を正規表現により文字列で抽出

            # レース開催箇所をrace_idから取得する.race_idは８桁の整数により表される.
            # ex)2022"01"020405: ４〜５桁目が開催箇所を表ているのでそれを辞書で開催箇所に変換する
            place_str = PLACE_DICT_REVERSE[race_id[4:6]]

            # レース名と出走時刻を結合してrace_idをkeyとした辞書に格納しておく(streamlitで使用するため)
            race_info_dict[race_id] = place_str + " " + race_name_str + " " + start_time_str

            time.sleep(1)
        print("取り込み完了!!")
        self.driver.close()

        df_shutuba_tables_X = pd.concat([race_id_dict[key] for key in race_id_dict.keys()])
        df_shutuba_tables = pd.concat([shutuba_table_dict[key] for key in shutuba_table_dict.keys()])

        # self.preprocessing(self.data)
        self.data = df_shutuba_tables_X  # 説明変数作成用
        self.shutuba_tables = df_shutuba_tables  # streamlitで表示用の出馬テーブル
        self.race_info_dict = race_info_dict

    def preprocessing_shutuba_table(self):
        """
        スクレイピングした出馬テーブルの前処理
        """
        # memo-----------------------------------------------------------------
        # df_shutuba_tables_X, df_shutuba_tables, race_info_dict = self.shutuba_tables_scrape(race_id_list, driver)
        # self.data = df_shutuba_tables_X  # 説明変数作成用
        # self.shutuba_tables = df_shutuba_tables  # streamlitで表示用の出馬テーブル
        # self.race_info_dict = race_info_dict
        # df = df_shutuba_tables_X.copy()
        # df
        # memo-----------------------------------------------------------------

        df = self.data.copy()
        # 使用するcolumnsのみを抽出
        # 使用するcolumns:開催, course_len, 枠番, 馬番, 性齢, 馬体重(増減), race_type,
        df = df[["枠", "馬番", "性齢", "斤量", "単勝", "人気", "馬体重(増減)", "horse_id", "jockey_id",
                 "trainer_id", "course_len", "weather", "race_type", "ground_state", "date",]].copy()
        df = df.rename(columns={"枠": "枠番", "馬体重(増減)": "馬体重"})

        df = df[~(df["単勝"] == "")].copy()  # 棄権する馬を削除しておく

        # 開催場所をrace_idから取得する. race_id:2019040101のような形状となっていて、この場合は2019の後の"04"が場所を表しているためそこ[4:6]を取得する
        df["開催"] = df.index.map(lambda x: str(x)[4:6])

        # レーズ距離は細かく分かれているため１００m単位でまとめる(100で割ってあまりを切り捨てる)
        df["course_len"] = df["course_len"].astype(int) // 100

        # 各データの型変更
        df["枠番"] = df["枠番"].astype(int)
        df["斤量"] = df["斤量"].astype(float).astype(int)
        df["馬番"] = df["馬番"].astype(int)
        df["単勝"] = df["単勝"].astype(float)
        df["course_len"] = df["course_len"].astype(int)

        # 性齢は性別と年齢を分ける処理をする
        df["性別"] = df["性齢"].map(lambda x: str(x)[0])  # 性別をとりだして文字列型に変換する
        df["年齢"] = df["性齢"].map(lambda x: str(x)[1]).astype(int)  # 性別をとりだして文字列型に変換する
        df["体重"] = pd.to_numeric(df["馬体重"].str.split("(", expand=True)[0], errors="coerce")  # 前体重と体重増減分割する
        df["体重変化"] = pd.to_numeric(df["馬体重"].str.split("(", expand= True)[1].str[:-1], errors="coerce").fillna(0).astype(int) # 計測していない馬は"計不となるためそれを検知して0に変換している"

        # 日付データを変更
        df['date'] = pd.to_datetime(df["date"], format='%Y/%m/%d')

        # race_type の中のいろんな障害レースの名称を”障害”に統一しておく
        df["race_type"] = df["race_type"].map(lambda x: "障害" if "障" in x else x)

        # 分割して不要になったcolumnを削除
        df.drop(["性齢", "馬体重"], axis=1, inplace=True)

        # #出走数追加
        # df['n_horses'] = df.index.map(df.index.value_counts())

        self.data_p = df
