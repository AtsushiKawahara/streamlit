# coding:utf-8
# https://db.netkeiba.com/race/{race_id}"  # urlを作成
"""
出馬表からのデータ回収
"""

# 必要な関数のインポート
import pandas as pd
import time
from tqdm import tqdm
import re
from urllib.request import urlopen
from selenium.webdriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.core.utils import ChromeType
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
# 参考)__file__: ~/streamlit/apps/scraping_shutuba_table.py
# path: ~/streamlit/apps/
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-1])+'/')
print('/'.join(os.path.abspath(__file__).split('/')[:-1])+'/')
# path: ~/streamlit/
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-2])+'/')
print('/'.join(os.path.abspath(__file__).split('/')[:-2])+'/')

# memo-------------------------------------------------------------------------
# hydrogen実行用
FILE_PATH = "/Users/kawaharaatsushi/work_streamlit/streamlit/streamlit"
sys.path.append(FILE_PATH)
# path: ~/streamlit/base_data
FILE_PATH_BASE_DATA = FILE_PATH+'/data/base_data'
sys.path.append(FILE_PATH_BASE_DATA)
# path: ~/streamlit/fit_data
FILE_PATH_FIT_DATA = FILE_PATH+'/data/fit_data'
sys.path.append(FILE_PATH_BASE_DATA)
# memo-------------------------------------------------------------------------

# sys.path.append(FILE_PATH_TMP)

# 自作関数のインポート
from apps.predict import Preprocessing_Horse_Result  # 不要
from apps.predict import Data_Processer


class Start_Horse_Table(Data_Processer):
    def __init__(self):
        super(Start_Horse_Table, self).__init__()
        self.data = 0  # 説明変数作成用
        self.race_info_dict = 0
        self.shutuba_tables = 0  # streamlitで表示用の出馬テーブル
        self.result_tables = 0  # 回収率算出用のresultテーブル

    def scrape_by_ChromeDriverManager_at_target_date(self, target_date, is_real_time, table_type="shutuba_table"):
        """
        target_dateで指定した日に開催されるraceの出馬テーブルを取得(ChromeDriverManagerにより取得)

        params:
        target_date(str): 出馬表を取得したい月日を○月○日の形で指定する ex)"7月23日"
        real_time(bool): リアルタイムで次に開催されるレース情報を取得する場合はTrue(馬体重の増減が更新されている開催される直前レースのみ取得する)
                         targe_dateで指定した日のレースが終了している出馬テーブル全てを取得する場合はFalse(予測結果の確認の際に使用)

        return:
        pd_shutuba_table(DataFrame): target_dateで指定した日に開催されるレースの出馬テーブルをすべて結合したもの
        """
        # memo-----------------------------------------------------------------
        target_date = "9月2日"
        # memo-----------------------------------------------------------------

        # 日付を入力するとその日のレース情報(説明変数情報)を取得できるようにする

        url = "https://race.netkeiba.com/top/"

        # googleを起動
        options = ChromeOptions()  # ここで拡張機能を本来は設定するけど今回は省略
        # options.add_argument("--headless")
        driver = Chrome(ChromeDriverManager().install(), options=options)

        # 競馬サイトのレース情報ページのトップを表示
        driver.get(url)

        if is_real_time:
            # 次に出走するレースのclassを取得
            # elements_at_active_race = driver.find_elements_by_css_selector(".RaceList_DataItem.Race_Main")  # class_nameに空白がある場合はcss_selectorを使う.行頭と空白部分は"."とする.
            elements_at_active_race = driver.find_elements(By.CSS_SELECTOR, ".RaceList_DataItem.Race_Main")  # class_nameに空白がある場合はcss_selectorを使う.行頭と空白部分は"."とする.

            # 次のレースのurlを入れるlistを作成
            target_date_race_url_list = []

            # 次のレースのurlを取得
            for element_at_active_race in elements_at_active_race:
                # elements = element_at_active_race.find_elements_by_tag_name("a")
                elements = element_at_active_race.find_elements(By.TAG_NAME, "a")
                #  elementsの中に出馬テーブルとレース動画のhrefも存在するため出馬テーブルのみ取得する
                for element in elements:
                    if "movie" not in element.get_attribute("href"):
                        target_date_race_url_list.append(element.get_attribute("href"))
        else:
            # 最近開催されるレース情報が掲載されている箇所を取得する
            elements = driver.find_elements(By.CLASS_NAME, "ui-tabs-anchor")
            elements
            elements
            # target_dateで指定した日の出馬テーブル一覧が取得できるurlを取得
            target_element = [element for element in elements if target_date in element.get_attribute("title")][0]
            target_date_url = target_element.get_attribute("href")

            # target_dateで指定したレース一覧が表示されるページへ移動
            driver.get(target_date_url)

            # target_dateで指定した日に開催予定のレース一覧情報を取得する
            elements = driver.find_elements(By.XPATH, "//li/a")

            # target_dateで指定した日に開催されるレースの出馬テーブルのurlが格納されたリストを作成
            target_date_race_url_list = [element.get_attribute("href") for element in elements if "movie" not in element.get_attribute("href")]

        # urlからrace_idを取得(set()で重複するrace_idは削除しておく)
        race_id_list = sorted(list(set([re.findall(r"\d+", url)[0] for url in target_date_race_url_list])))

        if table_type == "shutuba_table":
            print("通過")
            df_shutuba_tables_X, df_shutuba_tables, race_info_dict = self.shutuba_tables_scrape(race_id_list, driver)
            self.data = df_shutuba_tables_X  # 説明変数作成用
            self.shutuba_tables = df_shutuba_tables  # streamlitで表示用の出馬テーブル
            self.race_info_dict = race_info_dict
        elif table_type == "result_table":
            df_result_tables = self.result_tables_scrape(race_id_list)
            self.result_tables = df_result_tables
        else:
            raise Exception("table_type is not match please check table_type")

    def scrape_by_ChromeDriverManager_at_race_id_list(self, race_id_list, table_type="shutuba_table"):
        """
        race_id_listで指定したraceの出馬テーブルを取得(ChromeDriverManagerにより取得)

        params:
        race_id_list(list): 取得したいレースのrace_idをlist形式で入力する

        return:
        pd_shutuba_table(DataFrame): race_idで指定したレースの出馬テーブルをすべて結合したもの
        """

        # memo-----------------------------------------------------------------
        # race_id = 202204020201
        # memo-----------------------------------------------------------------

        # googleを起動
        options = ChromeOptions()  # ここで拡張機能を本来は設定するけど今回は省略
        options.add_argument("--headless")
        driver = Chrome(ChromeDriverManager().install(), options=options)

        if table_type == "shutuba_table":
            df_shutuba_tables_X, df_shutuba_tables, race_info_dict = self.shutuba_tables_scrape(race_id_list, driver)
            self.data = df_shutuba_tables_X  # 説明変数作成用
            self.shutuba_tables = df_shutuba_tables  # streamlitで表示用の出馬テーブル
            self.race_info_dict = race_info_dict
        elif table_type == "result_table":
            # result_tableの取得にはdriverは使用しないため閉じておく
            driver.close()
            df_result_tables = self.result_tables_scrape(race_id_list)
            self.result_tables = df_result_tables
        else:
            raise Exception("table_type is not match please check table_type")

    def shutuba_tables_scrape(self, race_id_list, driver):
        """
        race_idから出馬テーブルを取得する

        以下の２つのclassmethodで共通の処理をするため別でメソッドにしている
        scrape_by_ChromeDriverManager_at_race_id_list(cls, race_id_list):
        scrape_by_ChromeDriverManager_at_target_date(cls, target_date, is_real_time):
        """

        # memo-----------------------------------------------------------------
        # race_id = 202206040201
        # memo-----------------------------------------------------------------

        print(race_id_list)
        race_id_dict = {}  # 説明変数を作成するのに必要なデータを格納する
        race_info_dict = {}  # レース名 出走時刻 何レース目 の情報を格納する
        shutuba_table_dict = {}  # 出馬テーブルを格納する(streamlit用)

        for race_id in tqdm(race_id_list):

            df = pd.DataFrame()

            url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}&rf=race_list"

            driver.get(url)

            # elements = driver.find_elements_by_class_name("HorseList")  # find_element"s"にすると指定のclass_nameを複数取得する"s"をつけないと１つだけ取得する
            elements = driver.find_elements(By.CLASS_NAME, "HorseList")  # find_element"s"にすると指定のclass_nameを複数取得する"s"をつけないと１つだけ取得する
            elements

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
            # RaceData01 = driver.find_element_by_class_name("RaceData01").text
            RaceData01 = driver.find_element(By.CLASS_NAME, "RaceData01").text
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
            date_text = driver.title
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
            # race_name_str = driver.find_element_by_class_name("RaceName").text
            race_name_str = driver.find_element(By.CLASS_NAME, "RaceName").text

            # 出走時刻を文字列で取得
            # start_time_element = driver.find_element_by_class_name("RaceData01").text  # 出走時刻が記載されたelementを取得
            start_time_element = driver.find_element(By.CLASS_NAME, "RaceData01").text  # 出走時刻が記載されたelementを取得
            start_time_str = re.search(r"(.+)発走", start_time_element).group()  # 出走時刻を正規表現により文字列で抽出

            # レース開催箇所をrace_idから取得する.race_idは８桁の整数により表される.
            # ex)2022"01"020405: ４〜５桁目が開催箇所を表ているのでそれを辞書で開催箇所に変換する
            place_str = PLACE_DICT_REVERSE[race_id[4:6]]

            # レース名と出走時刻を結合してrace_idをkeyとした辞書に格納しておく(streamlitで使用するため)
            race_info_dict[race_id] = place_str + " " + race_name_str + " " + start_time_str

            time.sleep(1)
        print("取り込み完了!!")
        driver.close()

        df_shutuba_tables_X = pd.concat([race_id_dict[key] for key in race_id_dict.keys()])
        df_shutuba_tables = pd.concat([shutuba_table_dict[key] for key in shutuba_table_dict.keys()])

        # self.preprocessing(self.data)
        return df_shutuba_tables_X, df_shutuba_tables, race_info_dict

    def result_tables_scrape(self, race_id_list):
        """
        race_id_listで指定したrace_resultを取得する(pd.read_htmlにより取得)
        """

        # memo------------------------------------------------------------------
        # race_id = "202204020201"
        # race_id_list = ['202201010401', '202201010402']
        # memo------------------------------------------------------------------

        return_tables = {}  # レース結果データを格納する
        pd_return_tables = pd.DataFrame()  # 後でデータを格納するdataframeを作成しておく

        for race_id in tqdm(race_id_list):
            try:
                time.sleep(1)
                url = f"https://race.netkeiba.com/race/result.html?race_id={race_id}&rf=race_list"

                return_tables[race_id] = pd.read_html(url)  # データをpandasにより取得
                f = urlopen(url)  # urlを取得する
                html = f.read()
                html = html.replace(b'<br />', b'br')  # b'はバイト型 <br />は省略されるためbrに変換して目印をつける(brは別になんでもいい)
                dfs = pd.read_html(html)  # 変換したurlでtableを再取得
                if dfs[1].loc[0][0] == '単勝':
                    return_tables[race_id] = pd.concat([dfs[1], dfs[2]])
                else:
                    print(f"エラーrace_id:{race_id}")
                    raise Exception("html table Irregular")
                    break
                time.sleep(1)  # サイトに負荷をかけないように１秒待機
            except IndexError as e:  # urlが存在しないurlの場合は飛ばす
                print(f"{e}:{race_id}")
                time.sleep(1)
                continue
            except Exception as e:  # 処理が途中で終わってしまったら、そこまで取得したリストを返す
                print(e)
                break
        for key in return_tables.keys():
            return_tables[key].index = [key]*len(return_tables[key])

        pd_return_tables = pd.concat([return_tables[key] for key in return_tables])
        return pd_return_tables

    def preprocessing_shutuba_table(self):
        """
        スクレイピングした出馬テーブルの前処理
        """

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
        df["体重変化"] = df["馬体重"].str.split("(", expand= True)[1].str[:-1].fillna(0).astype(int)

        # 日付データを変更
        df['date'] = pd.to_datetime(df["date"], format='%Y/%m/%d')

        # race_type の中のいろんな障害レースの名称を”障害”に統一しておく
        df["race_type"] = df["race_type"].map(lambda x: "障害" if "障" in x else x)

        # 分割して不要になったcolumnを削除
        df.drop(["性齢", "馬体重"], axis=1, inplace=True)

        # #出走数追加
        # df['n_horses'] = df.index.map(df.index.value_counts())

        self.data_p = df
