# coding:utf-8
"""
馬の血統データをスクレイピングするファイル
"""

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


def scrape_horse_ped(horse_id_list):
    """
    race_id_listから馬ごとのレース結果を取得する関数
    """
    ped_data = {}
    for horse_id in tqdm(horse_id_list):

        try:
            url = f"https://db.netkeiba.com/horse/ped/{horse_id}/"
            # https://db.netkeiba.com/horse/ped/2015101529/
            # 2015101529
            df = pd.read_html(url)[0]

            generations = {}

            # 血統データの同じ行データは削除しながら右端のデータのみ取得していく
            for i in reversed(range(5)):
                generations[i] = df[i]  # 右端のデータを取得して辞書に格納
                df = df.drop([i], axis=1)  # 右端のデータを削除
                df = df.drop_duplicates()  # 全く同じ行データがあれば削除して１つ残す
            df_ped = pd.concat([generations[i] for i in range(5)]).rename(horse_id).reset_index(drop=True)
            ped_data[horse_id] = df_ped
            time.sleep(1)  # サイトに負荷をかけないように１秒待機
        except IndexError as e:  # urlが存在しないurlの場合は飛ばす
            print(f"{e}:{horse_id}")
            time.sleep(1)
            continue
        except Exception as e:  # 処理が途中で終わってしまったら、そこまで取得したリストを返す
            print(f"Error:{e}", f"horse_id:{horse_id}")
            break
    return ped_data


def main():
    # 血統データの取得

    # url = "https://db.netkeiba.com/horse/ped/2008102636/"

    GET_DATA_YEAR_LIST = ["2017", "2018", "2019", "2020", "2021", "2022"]

    for GET_DATA_YEAR in GET_DATA_YEAR_LIST:
        print(f"--------------------------------{GET_DATA_YEAR}--------------------------------------------")

        # race_resultsデータの読み込み
        pd_race_results = load_pickle(FILE_PATH_DATA_RE, f"pd_race_results_{GET_DATA_YEAR}")  # レース結果を読み込み

        # レース結果をから血統データをスクレイプするhorse_idを取得
        horse_id_list = pd_race_results["horse_id"].sort_values().unique()

        # 途中まで読み込んでいるpd_ped_datas_"year"ファイルがある場合は残りのhorse_idの結果を読み込む
        if os.path.isfile(f"{FILE_PATH_DATA_RE}/pd_ped_datas_{GET_DATA_YEAR}"):
            print(f"pd_ped_datas_{GET_DATA_YEAR}　is exist")

            pd_ped_datas_load = load_pickle(FILE_PATH_DATA_RE, f"pd_ped_datas_{GET_DATA_YEAR}")  # 途中まで抽出しているファイルを読み込み
            drop_lists = pd_ped_datas_load.index.unique()  # 読み込み完了しているhorse_idを取得
            horse_id_list = np.array([horse_id for horse_id in horse_id_list if not horse_id in drop_lists])  # まだ読み込みが完了していないhorse_idを取得
            print(f"horse_id: {horse_id_list[0]} から取得開始")
            print(f"残:{len(horse_id_list)}")
            if len(horse_id_list) == 0:  # 読み込みが完了している年はスキップする
                continue
        else:
            pass

        # GET_DATA_YEARで指定した年のped_datas(血統データ)を取得　
        ped_datas_dict = scrape_horse_ped(horse_id_list)

        if len(ped_datas_dict) == 0:
            # 新たに取得したデータがない場合(すでに全データを取得できている場合)は保存はしない
            print(f"{GET_DATA_YEAR} DATA is already completed ")
            pass
        else:
            # dictに格納したdfを全て結合する
            pd_ped_datas = pd.concat([ped_datas_dict[key] for key in ped_datas_dict.keys()], axis=1).T
            pd_ped_datas = pd_ped_datas.add_prefix("ped_")

            # 途中まで読み込みファイルがある場合は、新たに読み込んだデータと結合しておく
            if os.path.isfile(f"{FILE_PATH_DATA_RE}/pd_ped_datas_{GET_DATA_YEAR}"):
                pd_ped_datas = pd.concat([pd_ped_datas_load, pd_ped_datas], axis=1)

            # 馬ごとの成績データを保存
            save_pickle(FILE_PATH_DATA_RE, f"pd_ped_datas_{GET_DATA_YEAR}", pd_ped_datas.sort_index())  # レース結果を保存


if __name__ == '__main__':
    main()
