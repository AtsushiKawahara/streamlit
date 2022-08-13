# coding:utf-8

import requests
from bs4 import BeautifulSoup
import re
import sys
from tqdm import tqdm
import time
import pandas as pd
import datetime
import numpy as np
import os

# pathの設定
FILE_PATH = '/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/'
sys.path.append(FILE_PATH)
FILE_PATH2 = '/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/function/'
sys.path.append(FILE_PATH2)
FILE_PATH_DATA = '/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/data/'
sys.path.append(FILE_PATH_DATA)
FILE_PATH_DATA_RE = '/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/data_re/'
sys.path.append(FILE_PATH_DATA_RE)

# 取得する年を指定
# GET_DATA_YEAR = 2019

# 自作関数のインポート
from data_proessing import load_pickle
from data_proessing import save_pickle


def scrape_horse_result(horse_id_list):
    """
    race_id_listから馬ごとのレース結果を取得する関数
    """
    horse_race_results = {}
    for horse_id in tqdm(horse_id_list):
        try:
            url = f"https://db.netkeiba.com/horse/{horse_id}/"
            # memo-------------------------------------------------------------
            # url = "https://db.netkeiba.com/horse/2008104268/"  # 受賞歴あり
            # horse_id = "2008104268"
            # url = "https://db.netkeiba.com/horse/2017103442/"  # 受賞歴なし
            # horse_id = "2017103442"
            # memo-------------------------------------------------------------
            horse_result = pd.read_html(url)  # データをpandasにより取得
            horse_race_results[horse_id] = horse_result[3]  # データをpandasにより取得
            if horse_result[3].columns[0] != "日付":
                horse_race_results[horse_id] = horse_result[4]  # データをpandasにより取得
                print(f"-------------------------受賞歴あり臭いid:horse_id{horse_id}----------------------------")
            time.sleep(1)  # サイトに負荷をかけないように１秒待機
        except IndexError as e:  # urlが存在しないurlの場合は飛ばす
            print(f"{e}:{horse_id}")
            time.sleep(1)
            continue
        except Exception as e:  # 処理が途中で終わってしまったら、そこまで取得したリストを返す
            print(e)
            break
    return horse_race_results


def main():
    # horse_results(過去成績データ)の取得

    GET_DATA_YEAR_LIST = ["2018", "2019", "2020", "2021", "2022"]
    # GET_DATA_YEAR_LIST = ["2017"]

    for GET_DATA_YEAR in GET_DATA_YEAR_LIST:
        print(f"--------------------------------{GET_DATA_YEAR}--------------------------------------------")

        # race_results(レース結果)データの読み込み
        pd_race_results = load_pickle(FILE_PATH_DATA_RE, f"pd_race_results_{GET_DATA_YEAR}")  # レース結果を読み込み

        horse_id_list = pd_race_results["horse_id"].sort_values().unique()  # レース結果からhorse_idを作成して、その馬の過去成績を取得

        # 途中まで読み込んでいるpd_horse_results_"year"ファイルがある場合は残りのhorse_idの結果を読み込む
        if os.path.isfile(f"{FILE_PATH_DATA_RE}/pd_horse_results_{GET_DATA_YEAR}"):
            print(f"pd_horse_results_{GET_DATA_YEAR}　is exist")

            pd_horse_results_load = load_pickle(FILE_PATH_DATA_RE, f"pd_horse_results_{GET_DATA_YEAR}")  # 途中まで抽出しているファイルを読み込み
            drop_lists = pd_horse_results_load.index.unique()  # 読み込み完了しているhorse_idを取得
            horse_id_list = np.array([horse_id for horse_id in horse_id_list if not horse_id in drop_lists])  # まだ読み込みが完了していないhorse_idを取得

            print(f"残:{len(horse_id_list)}")
            if len(horse_id_list) == 0:  # 読み込みが完了している年はスキップする
                continue
        else:
            pass

        # GET_DATA_YEARで指定した年のhorse_result(過去成績データ)を取得　
        horse_results_dict = scrape_horse_result(horse_id_list)

        # 馬ごとのレース成績データをレースIDに変更
        for key in horse_results_dict.keys():
            horse_results_dict[key].index = [key]*len(horse_results_dict[key])

        if len(horse_results_dict) == 0:
            # 新たに取得したデータがない場合(すでに全データを取得できている場合)は保存はしない
            print(f"{GET_DATA_YEAR} DATA is already completed ")
            pass
        else:
            # dictに格納したdfを全て結合する
            pd_horse_results = pd.concat([horse_results_dict[key] for key in horse_results_dict.keys()], sort=False)

            # 途中まで読み込みファイルがある場合は、新たに読み込んだデータと結合しておく
            if os.path.isfile(f"{FILE_PATH_DATA_RE}/pd_horse_results_{GET_DATA_YEAR}"):
                pd_horse_results = pd.concat([pd_horse_results_load, pd_horse_results], axis=0)

            # 馬ごとの成績データを保存
            save_pickle(FILE_PATH_DATA_RE, f"pd_horse_results_{GET_DATA_YEAR}", pd_horse_results.sort_index())  # レース結果を保存


if __name__ == '__main__':
    main()
