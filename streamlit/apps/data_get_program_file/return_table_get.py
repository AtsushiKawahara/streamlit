# coding:utf-8

import requests
from bs4 import BeautifulSoup
import re
import sys
from tqdm import tqdm
import time
import pandas as pd
import datetime
from urllib.request import urlopen
import os
import numpy as np

# pathの設定
FILE_PATH = '/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/'
sys.path.append(FILE_PATH)
FILE_PATH2 = '/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/function/'
sys.path.append(FILE_PATH2)
FILE_PATH_DATA = '/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/data/'
sys.path.append(FILE_PATH_DATA)
FILE_PATH_PREDICT = '/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/predict_file/'
sys.path.append(FILE_PATH_PREDICT)
FILE_PATH_DATA_RE = '/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/data_re/'
sys.path.append(FILE_PATH_DATA_RE)

# 自作関数のインポート
from data_proessing import load_pickle
from data_proessing import save_pickle
from data_proessing import train_test_split
from data_proessing import preprocessing
from predict import Preprocessing_Horse_Result
from predict import Result_Table
from predict import labelencoder_ped


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

    for GET_DATA_YEAR in GET_DATA_YEAR_LIST:
        print(f"--------------------------------{GET_DATA_YEAR}--------------------------------------------")

        # 馬ごとの成績データの処理(過去データの着順・賞金の平均を説明変数にするために使用する)
        hr = Preprocessing_Horse_Result.load_pickle([GET_DATA_YEAR])

        # pd_resultsを加工
        rt = Result_Table.load_pickle([GET_DATA_YEAR])
        # rt.data

        # preprocessing
        rt.preprocessing()
        # rt.data_p

        # 過去データから賞金データを説明変数に追加
        rt.merge_n_samples(hr)
        # rt.data_r

        # 血統データをlabelencodeするためのclassをインスタンス化
        la = labelencoder_ped.load_pickle([GET_DATA_YEAR])
        la.labelencode_ped()
        # la.pd_ped_datas_la

        # 血統データを説明変数に追加
        rt.merge_ped_data(la.pd_ped_datas_la)
        # rt.no_peds
        # rt.data_ped

        # 訓練データをhorse_id, jockey_idをラベルエンコードする
        # weather, ground_state, race_type, 性別もカテゴライズしてダミー変数化する
        rt.labelencoder_id()
        # rt.data_id

        # 一旦コピーしておく(result_3Rは下でまた使用するため)
        results_d = rt.data_id.copy()
        # columns_check(results_d)
        # --------------------------------------------------------------------------

        # 2.学習

        # 2-1.lightgbm(単勝)にて回収率を算出-----------------------------------------------------

        # 正解ラベル rank の作成(単勝)
        results_d_single = results_d.copy()

        # results_d_single.drop(["単勝", "人気"], axis=1, inplace=True)  適性回収率で単勝データが必要なためここではdropしない
        results_d_single["rank"] = results_d_single["着順"].map(lambda x: 1 if x == 1 else 0)  # 単勝
        # results_d_single["rank"] = results_d_single["着順"].map(lambda x: 0 if x == 1 else 1 if x < 4 else 2)  # 単勝
        # results_d_single["rank"] = results_d_single["着順"].map(lambda x: 1 if x < 3 else 0)  # 馬連
        results_d_single.drop(["着順"], axis=1, inplace=True)

        train, test = train_test_split(results_d_single, 0.3)
        X_train = train.drop(["rank", "date"], axis=1)
        y_train = train["rank"].copy()
        X_test = test.drop(["rank", "date"], axis=1)
        y_test = test["rank"].copy()

        # Calucurate_Return classで回収率を算出するために"単勝, 人気"データが必要なため"X_add_tansho_ninnki"変数を作成しておく
        # X_train, X_testには"単勝・人気"のデータは入れていない（的中率は上がるけど、回収率は下がるため）
        X_train.drop(["単勝", "人気"], axis=1, inplace=True)
        X_test.drop(["単勝", "人気"], axis=1, inplace=True)

        # return_tableの取得--------------------------------------------------

        race_id_list = X_test.index.unique()  # test_dataで回収率を計算するためtest_dataのrace_idを取得

        # 途中まで読み込んでいるpd_ped_datas_"year"ファイルがある場合は残りのhorse_idの結果を読み込む
        if os.path.isfile(f"{FILE_PATH_DATA_RE}/pd_return_tables_test_{GET_DATA_YEAR}"):
            print(f"pd_return_tables_test_{GET_DATA_YEAR}　is exist")

            pd_return_tables_test_load = load_pickle(FILE_PATH_DATA_RE, f"pd_return_tables_test_{GET_DATA_YEAR}")  # 途中まで抽出しているファイルを読み込み
            drop_lists = pd_return_tables_test_load.index.unique()  # 読み込み完了しているhorse_idを取得
            race_id_list = np.array([race_id for race_id in race_id_list if not race_id in drop_lists])  # まだ読み込みが完了していないhorse_idを取得

            print(f"残:{len(race_id_list)}")
            if len(race_id_list) == 0:  # 読み込みが完了している年はスキップする
                continue
        else:
            pass
        pd_return_tables_test = scrape_return_tables(race_id_list)  # レースごとの予想が的中した場合の報酬の情報を取得
        for key in pd_return_tables_test.keys():
            pd_return_tables_test[key].index = [key]*len(pd_return_tables_test[key])

        pd_return_tables_test = pd.concat([pd_return_tables_test[key] for key in pd_return_tables_test])

        # 途中まで読み込みファイルがある場合は、新たに読み込んだデータと結合しておく
        if os.path.isfile(f"{FILE_PATH_DATA_RE}/pd_return_tables_test_{GET_DATA_YEAR}"):
            pd_return_tables_test = pd.concat([pd_return_tables_test_load, pd_return_tables_test], axis=0)
        # 報酬情報の保存と読み込み
        save_pickle(FILE_PATH_DATA_RE, f"pd_return_tables_test_{GET_DATA_YEAR}", pd_return_tables_test)
        # ---------------------------------------------------------------------------


if __name__ == '__main__':
    main()
