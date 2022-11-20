# coding: utf-8

import requests
from bs4 import BeautifulSoup
import re
import sys
from tqdm import tqdm
import time
import pandas as pd
import numpy as np
import os

# pathの設定

# memo-------------------------------------------------------------------------
# hydrogen実行用
# streamlitリポジトリ用
FILE_PATH = "/Users/kawaharaatsushi/work_streamlit/streamlit/streamlit"
# dailydevリポジトリ用
FILE_PATH = "/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit"
sys.path.append(FILE_PATH)
# path: ~/streamlit/data/base_data
FILE_PATH_BASE_DATA = FILE_PATH+'/data/base_data'
sys.path.append(FILE_PATH_BASE_DATA)
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


def scrape_race_result(race_id_list):
    """
    race_id_listからデータを取得する関数
    """
    race_results = {}
    for race_id in tqdm(race_id_list):
        try:
            url = f"https://db.netkeiba.com/race/{race_id}"  # urlを作成
            # https://db.netkeiba.com/race/'202210010701
            race_results[race_id] = pd.read_html(url)[0]  # データをpandasにより取得
            # BeautifulSoupにて馬名id、騎手id,調教師idを取得する
            html = requests.get(url)
            html.encoding = 'EUC-JP'
            soup = BeautifulSoup(html.text, "html.parser")

            # htmlから馬_idを取得
            horse_id_texts = soup.find("table", attrs={"summary":"レース結果"}).find_all("a", attrs={"href": re.compile(r"^/horse")})
            horse_id_list = [re.findall(r"\d+",text["href"])[0] for text in horse_id_texts]

            # htmlから騎手_idを取得
            jockey_id_texts = soup.find("table", attrs={"summary":"レース結果"}).find_all("a", attrs={"href": re.compile(r"^/jockey")})
            jockey_id_list = [re.findall(r"\d+",text["href"])[0] for text in jockey_id_texts]

            # htmlから調教師_idを取得
            trainer_id_texts = soup.find("table", attrs={"summary":"レース結果"}).find_all("a", attrs={"href": re.compile(r"^/trainer")})
            trainer_id_list = [re.findall(r"\d+",text["href"])[0] for text in trainer_id_texts]

            # 取得したデータをdataframeに追加
            race_results[race_id]["horse_id"] = horse_id_list
            race_results[race_id]["jockey_id"] = jockey_id_list
            race_results[race_id]["trainer_id"] = trainer_id_list

            time.sleep(1)  # サイトに負荷をかけないように１秒待機

        except IndexError as e:  # urlが存在しないurlの場合は飛ばす
            print(f"{e}:{race_id}")
            time.sleep(1)
            continue
        except Exception as e:  # 処理が途中で終わってしまったら、そこまで取得したリストを返す
            print(e)
            break
    return race_results


def main():
    # race_results(レース結果)の取得-----------------------------------------------------------

    # GET_DATA_YEAR_LIST = ["2017", "2018", "2019", "2020", "2021", "2022"]
    GET_DATA_YEAR_LIST = ["2022"]  # 追加で取得したいのは最新年だけ

    for GET_DATA_YEAR in GET_DATA_YEAR_LIST:
        print(f"--------------------------------{GET_DATA_YEAR}--------------------------------------------")
        # race_idリストの作成
        # race_idは合計１０桁の数字によって表されるため全てのレースを取得できるようにrace_idリストを作成する
        # ex)202201020304の場合：2022→開催年、 01→place(開催場所), 02→kai(回), 03→day(日目), 04→R(race) を表ている
        race_id_list = []
        for place in range(1, 11, 1):  # place(開催場所)は中央競馬の場合は１０ヶ所あるため,range(1, 11, 1)以下同じ要領にて決定
            for kai in range(1, 13, 1):  # kai(回)は開催場所によって、最大６
                for day in range(1, 13, 1):  # day(日目)は最大１２
                    for r in range(1, 13, 1):  # r(R)は基本１２
                        race_id = f"{GET_DATA_YEAR}{str(place).zfill(2)}{str(kai).zfill(2)}{str(day).zfill(2)}{str(r).zfill(2)}"
                        race_id_list.append(race_id)

        # 途中まで読み込んでいるpd_race_results_"year"ファイルがある場合は残りのhorse_idの結果を読み込む
        if os.path.isfile(f"{FILE_PATH_BASE_DATA}/pd_race_results_{GET_DATA_YEAR}"):
            print(f"pd_race_results_{GET_DATA_YEAR}　is exist")

            pd_race_results_load = load_pickle(FILE_PATH_BASE_DATA, f"pd_race_results_{GET_DATA_YEAR}")  # 途中まで抽出しているファイルを読み込み
            drop_lists = pd_race_results_load.index.unique()  # 読み込み完了しているhorse_idを取得
            race_id_list = np.array([race_id for race_id in race_id_list if not race_id in drop_lists])  # まだ読み込みが完了していないhorse_idを取得

            print(f"残:{len(race_id_list)}")
            if len(race_id_list) == 0:  # 読み込みが完了している年はスキップする
                continue
        else:
            pass

        # GET_DATA_YEARで指定した年のrace_resultsの取得
        race_results_dict = scrape_race_result(race_id_list)
        # レースデータのインデックスをレースIDに変更
        for key in race_results_dict.keys():
            race_results_dict[key].index = [key]*len(race_results_dict[key])

        if len(race_results_dict) == 0:
            # 新たに取得したデータがない場合(すでに全データを取得できている場合)は保存はしない
            print(f"{GET_DATA_YEAR} DATA is already completed ")
            pass
        else:
            # dictに格納したdfを全て結合する
            pd_race_results = pd.concat([race_results_dict[key] for key in race_results_dict.keys()], sort=False)
            # 途中まで読み込みファイルがある場合は、新たに読み込んだデータと結合しておく
            if os.path.isfile(f"{FILE_PATH_BASE_DATA}/pd_race_results_{GET_DATA_YEAR}"):
                pd_race_results = pd.concat([pd_race_results_load, pd_race_results], axis=0)
            else:
                pass
            # race_resultsデータを保存
            save_pickle(FILE_PATH_BASE_DATA, f"pd_race_results_{GET_DATA_YEAR}", pd_race_results.sort_index())  # レース結果を保存


if __name__ == '__main__':
    main()
