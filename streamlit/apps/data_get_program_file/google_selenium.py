# coding:utf-8
"""
seleniumによる出馬表のスクレイピング

pd.read_html(url)では読み込めない場合にこの方法を使用して読み込みを行う
pd.read_html(url)はjavascriptで作られているwebページは読み込めないことがある
"""

import pandas as pd
from selenium.webdriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
import re
from tqdm import tqdm
import sys
import os

# pathの設定

# memo-------------------------------------------------------------------------
# # hydrogen実行用
# # streamlitリポジトリ用
# FILE_PATH = "/Users/kawaharaatsushi/work_streamlit/streamlit/streamlit"
# # dailydevリポジトリ用
# FILE_PATH = "/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit"
# sys.path.append(FILE_PATH)
# # path: ~/streamlit/data/base_data
# FILE_PATH_BASE_DATA = FILE_PATH+'/data/base_data'
# sys.path.append(FILE_PATH_BASE_DATA)
# memo-------------------------------------------------------------------------

# このファイルの場所を取得してパスを通す(別階層のファイルから呼び出しても変化しない)
# 参考)__file__: ~/streamlit/apps/data_get_program_file/race_result_get.py
# path: ~/streamlit/
FILE_PATH = '/'.join(os.path.abspath(__file__).split('/')[:-3])+'/'
sys.path.append(FILE_PATH)
# path: ~/streamlit/data/base_data
FILE_PATH_BASE_DATA = '/'.join(os.path.abspath(__file__).split('/')[:-3])+'/data/base_data'
sys.path.append(FILE_PATH_BASE_DATA)

# 自作関数のインポート
from functions.date_split_plot_pickle_functions import load_pickle
from functions.date_split_plot_pickle_functions import save_pickle

url = "https://race.netkeiba.com/race/shutuba.html?race_id=202206010801&rf=race_list"

# この方法ではオッズ・人気が取り出せない(取り出せない部分はjavascriptで書かれている場合が多い)
# pd.read_htmlでは取り出せない場合はseleniumにてその部分を取得する
# pd.read_html(url)[0]


class start_table:
    """
    出馬表をchromeで取得する
    pd.read_htmlではjavascriptで書かれている部分が取得できないためこの方法で取得する
    """

    def __init__(self):
        self.start_table = pd.DataFrame()

    def scrape_start_table(self, race_id_list):
        """
        指定したrace_id_listの出馬表を取得する
        """
        options = ChromeOptions()  # ここで拡張機能を本来は設定するけど今回は省略
        driver = Chrome(ChromeDriverManager().install(), options=options)
        # race_id = "202206010801"
        for race_id in tqdm(race_id_list):
            url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}&rf=race_list"
            driver.get(url)
            elements = driver.find_elements_by_class_name("HorseList")  # find_element"s"にすると指定のclass_nameを複数取得する"s"をつけないと１つだけ取得する
            for element in elements:
                tds = element.find_elements_by_tag_name("td")
                info = []
                for td in tds:
                    if td.get_attribute("class") in ["HorseInfo", "Jockey", "Trainer"]:
                        find_text = td.find_element_by_tag_name("a").get_attribute("href")
                        info.append(re.findall(r"\d+", find_text)[0])
                    info.append(td.text)
                self.start_table = self.start_table.append(pd.Series(info, name=race_id))
                # print(info)
            # print("break!")
        print("取り込み完了!!")
        driver.close()

    def preprocessing(self):
        """
        scrape_start_tableで取得したデータの前処理
        必要なデータの取得(いらない--などのデータは取得しない)
        cloumn名を指定する
        """
        df = self.start_table.copy()
        df = df[[0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]]
        df.columns = ["枠", "馬番", "horse_id", "馬名", "性齢", "斤量", "Jockey_id", "騎手", "Trainer_id", "調教師", "馬体重", "オッズ", "人気"]
        self.start_table = df

    def merge_start_table(self, df_horse_results, columns, n_samples):
        """
        horse_id
        """
        for column in columns:
            # race_idでgroupby→head(n_samples)で取得するデータ数を指定→必要な部分のcolumnを指定して抽出→applyで行ごとに結合する.join()をするためにastype(str)で文字型にして結合する
            df = df_horse_results.astype(str).groupby(level=0).head(n_samples)[f"{column}"].apply(lambda x: ",".join(x))
            # 上で結合した文字列を分割　expand=Trueにしてdataframe型で分割する .add_prefix()でcolumn名を指定
            df.str.split(",",expand=True).add_prefix(f"{column}_")
            # horse_idを元にmergeする
            self.start_table = pd.merge(self.start_table, df, right_index=True, left_on="horse_id", how="left")


def main():

    df_horse_results = load_pickle(FILE_PATH_BASE_DATA, "pd_horse_results_2019")

    sst = start_table()
    sst.scrape_start_table(["202206010801"])
    sst.preprocessing()
    df_start_table = sst.merge_start_table(df_horse_results, ["着順", "賞金"], 5)

    a = sst.start_table["horse_id"].values

    # 出馬表の馬が過去データにあるか確認
    for i in a:
        # print(i, type(i))
        if i in df_horse_results.index:
            print("exist")
        else:
            print("not exist")


if __name__ == '__main__':
    main()
