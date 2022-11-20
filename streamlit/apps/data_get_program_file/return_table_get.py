# coding:utf-8

import sys
from tqdm import tqdm
import time
import pandas as pd
from urllib.request import urlopen
import os
import numpy as np

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
from functions.date_split_plot_pickle_functions import train_test_split
from apps.create_model import Preprocessing_Horse_Result
from apps.create_model import Result_Table
from apps.create_model import labelencoder_ped


def scrape_return_tables(race_id_list):
    """
    race_id_listからデータを取得する関数
    """
    return_tables = {}
    # race_id = "201601020612"
    for race_id in tqdm(race_id_list):
        try:
            url = f"https://db.netkeiba.com/race/{race_id}"  # urlを作成
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
    return return_tables


def main():

    # GET_DATA_YEAR_LIST = [2017, 2018, 2019, 2020, 2021]  # 取得したい年を指定
    GET_DATA_YEAR_LIST = [2022]  # 取得したい年を指定

    # GET_DATA_YEAR = 2022  # 取得したい年を指定

    for GET_DATA_YEAR in GET_DATA_YEAR_LIST:
        print(f"--------------------------------{GET_DATA_YEAR}--------------------------------------------")

        # race_id_listを作成するためにrace_resultデータを読み込む
        pd_race_results = load_pickle(FILE_PATH_BASE_DATA, f"pd_race_results_{GET_DATA_YEAR}")

        # race_resultsからレースidを取得
        race_id_list = pd_race_results.index.unique()
        print(f"race_id_list数:{len(race_id_list)}")

        # 途中まで読み込んでいるpd_ped_datas_"year"ファイルがある場合は残りのhorse_idの結果を読み込む
        if os.path.isfile(f"{FILE_PATH_BASE_DATA}/pd_return_tables_{GET_DATA_YEAR}"):
            print(f"pd_return_tables_{GET_DATA_YEAR}　is exist")

            pd_return_tables_load = load_pickle(FILE_PATH_BASE_DATA, f"pd_return_tables_{GET_DATA_YEAR}")  # 途中まで抽出しているファイルを読み込み
            drop_lists = pd_return_tables_load.index.unique()  # 読み込み完了しているhorse_idを取得
            race_id_list = np.array([race_id for race_id in race_id_list if not race_id in drop_lists])  # まだ読み込みが完了していないhorse_idを取得

            print(f"残:{len(race_id_list)}")
            if len(race_id_list) == 0:  # 読み込みが完了している年はスキップする
                continue
        else:
            pass

        pd_return_tables_dict = scrape_return_tables(race_id_list)  # レースごとの予想が的中した場合の報酬の情報を取得

        for key in pd_return_tables_dict.keys():
            pd_return_tables_dict[key].index = [key]*len(pd_return_tables_dict[key])

        pd_return_tables = pd.concat([pd_return_tables_dict[key] for key in pd_return_tables_dict])

        # 途中まで読み込みファイルがある場合は、新たに読み込んだデータと結合しておく
        if os.path.isfile(f"{FILE_PATH_BASE_DATA}/pd_return_tables_{GET_DATA_YEAR}"):
            pd_return_tables = pd.concat([pd_return_tables_load, pd_return_tables], axis=0)

        # 重複を削除
        pd_return_tables["race_id"] = pd_return_tables.index  # columnにrace_idを一時的に追加(次の処理で重複行を削除するときに消したらいけない行を消さないため)
        pd_return_tables = pd_return_tables.drop_duplicates().drop("race_id", axis=1).copy()  # 重複行の削除とrace_idの列を削除

        # 報酬情報の保存と読み込み
        save_pickle(FILE_PATH_BASE_DATA, f"pd_return_tables_{GET_DATA_YEAR}", pd_return_tables)
        # ---------------------------------------------------------------------------


if __name__ == '__main__':
    main()
