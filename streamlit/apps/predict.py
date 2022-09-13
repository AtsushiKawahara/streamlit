# coding:utf-8
"""
検証用データの取得プログラム
ver_1.0

# 使用モデル：light_gbm

# 説明変数
主な説明変数：体重、体重変化、血統、馬、騎手、枠番、斤量、年齢、着順、賞金、着差、各コーナーでの順位、天気、芝・ダートでの分割(labelencode)、性別
※ 賞金、着順、着差は過去の５、９、allの平均値をそれぞれ説明変数として使用している
使用していない説明変数：オッズ、人気 → 的中率は上がるけど回収率は下がるため不使用
これから使用したい説明変数：調教師、風速、風向、湿度、スピード指数、各馬の得意な距離（複勝圏内に入ったときの平均距離など）

# 目的変数
使用している目的変数：着順１位・・・『1』、着順2位以下・・・『0』
→これにより『その馬が１位になる確率』が算出できる
→これを使用して、各馬券の発生確率を算出している(ハーヴィルの公式)

# 評価指標
回収率、的中率を評価指標としている（thresholdsにより閾値を設定）

# 馬券の購入方法
以下の２通りの購入方法を実装

## 購入方法その１ モデル予測による買い方(model)
学習したモデルが"勝つ"と予想した馬券を購入する買い方(出力確率が高いものから順に購入する)

## 購入方法その２ オッズの歪みに着目した買い方(diff)
これは『AI競馬』で読んだ馬券の買い方
簡単に説明すると・・・
- オッズから算出した勝率
- 学習モデルが予測した勝率
上２つの勝率を比較して、差が大きい馬券 = "ウマい馬券"(オッズの勝率の歪みに着目)を購入する

# その他機能
## 機能その１ optunaによるハイパラメーターチューニング
## 機能その２ 標準化・正規化の選択設定
## 機能その３ 適正回収率の実装（現在これは停止中）
## 機能その４ 各馬券の回収率・的中率の算出

"""

# 必要な関数のインポート
# import time
# import re
# from scipy.special import comb
# import requests
# from bs4 import BeautifulSoup
# from urllib.request import urlopen
import numpy as np
# # XGBoost
# import xgboost as xgb
# from sklearn.metrics import accuracy_score, confusion_matrix
# # ROC曲線を作成する
# from sklearn.metrics import roc_curve, roc_auc_score
# import matplotlib.pyplot as plt
# from sklearn.preprocessing import StandardScaler
# from sklearn.preprocessing import MinMaxScaler
# import math
from sklearn.preprocessing import LabelEncoder
# # 出馬表のデータを作成する-------------------------------------------------------
# from selenium.webdriver import Chrome, ChromeOptions
# from webdriver_manager.chrome import ChromeDriverManager
# import re
# # 組み合わせ馬券の計算に使用
# from scipy.special import comb, perm  # nCr nPr
import itertools
# # pycaretライブラリのインポート
# from pycaret.datasets import get_data
# from pycaret.regression import *
# from pycaret.classification import *

# streamlit用に必要なライブラリのインポート
import sys
import os
import pandas as pd
import re
from tqdm import tqdm
# from pycaret.regression import *  # pycaretのpredict_modelで使うかも

# main()関数を実行するために必要な関数をimportしておく
import matplotlib.pyplot as plt

# 辞書型定義

PLACE_DICT = {
    "札幌": "01", "函館": "02", "福島": "03", "新潟": "04",
    "東京": "05", "中山": "06", "中京": "07", "京都": "08",
    "阪神": "09", "小倉": "10"}

RACE_TYPE_DICT = {
    "ダ": "ダート", "芝": "芝", "障": "障害"
    }

# 競馬サイトのurl（メモとしておいとくだけ）
# url = "https://db.netkeiba.com/race/201901010101/"

# 学習データとして使用する年を設定
GET_DATA_YEAR_LIST = [2017, 2018, 2019, 2020, 2021, 2022]  # 取得したい年を指定
GET_DATA_YEAR_LIST = [2017]  # 取得したい年を指定
GET_DATA_YEAR = "2017-2022"

# 自作関数のインポート

# PATHの設定(相対パス)

# hydrogen実行用
FILE_PATH = "/Users/kawaharaatsushi/work_streamlit/streamlit/streamlit"
sys.path.append(FILE_PATH)
# path: ~/streamlit/base_data
FILE_PATH_BASE_DATA = FILE_PATH+'/data/base_data'
sys.path.append(FILE_PATH_BASE_DATA)
# path: ~/streamlit/fit_data
FILE_PATH_FIT_DATA = FILE_PATH+'/data/fit_data'
sys.path.append(FILE_PATH_BASE_DATA)
# path: ~/streamlit/result_data
FILE_PATH_RESULT_DATA = f'{FILE_PATH}/data/result_data/{GET_DATA_YEAR}'
sys.path.append(FILE_PATH_RESULT_DATA)

# path: ~/streamlit/apps/predict.py
# print(f"__file__:{__file__}")

# このファイルの場所を取得してパスを通す(別階層のファイルから呼び出しても変化しない)
# 参考)__file__: ~/streamlit/apps/predict.py
# path: ~/streamlit/apps/
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-1])+'/')
# path: ~/streamlit/
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-2])+'/')
# path: ~/streamlit/base_data
FILE_PATH_BASE_DATA = '/'.join(os.path.abspath(__file__).split('/')[:-2])+'/data/base_data'
sys.path.append(FILE_PATH_BASE_DATA)
# path: ~/streamlit/fit_data
FILE_PATH_FIT_DATA = '/'.join(os.path.abspath(__file__).split('/')[:-2])+'/data/fit_data'
sys.path.append(FILE_PATH_FIT_DATA)
# path: ~/streamlit/result_data
FILE_PATH_RESULT_DATA = '/'.join(os.path.abspath(__file__).split('/')[:-2])+f'/data/result_data/{GET_DATA_YEAR}'
sys.path.append(FILE_PATH_RESULT_DATA)

from functions.data_proessing import load_pickle
from functions.data_proessing import save_pickle
from functions.data_proessing import train_test_split
from functions.data_proessing import roc_graph_plot


class Preprocessing_Horse_Result:
    """
    過去レースの賞金と着順の平均を算出して説明変数に使用するためのclass
    """

    def __init__(self, pd_horse_results):
        self.pd_horse_results = pd_horse_results[["着順", "賞金", "日付", "着差", "通過", "開催", "距離"]]
        self.preprocessing_horse_result()  # 説明変数にするための前処理

    @classmethod
    def load_pickle(cls, GET_DATA_YEAR_LIST):
        print(FILE_PATH_BASE_DATA)
        # あらかじめスクレイピングしてある馬の過去成績データを読み込む(pd_horse_results_〇〇〇〇: DataFrame型)
        df = pd.concat([load_pickle(FILE_PATH_BASE_DATA, f"pd_horse_results_{GET_DATA_YEAR}") for GET_DATA_YEAR in GET_DATA_YEAR_LIST])
        return cls(df)  # dfがclass内のpd_horse_resultsとして扱われる

    def preprocessing_horse_result(self):
        """
        サイトから取得してきたデータの加工
        - 欠損値を削除
        - 型の変更（str - int）
        - 不要なcloumnの削除
        - 1つのcolomnの中に２つの情報があるデータの分割・抽出
        """
        df = self.pd_horse_results.copy()

        # 着順の変なデータを削除する
        df["着順"] = pd.to_numeric(df["着順"], errors="coerce")  # to_numericにてstr型の数値をfloat型に変換する.
        df.dropna(subset=["着順"], inplace=True)  # "中"などの不要な文字列をnanに変換後にnanを着順のnanを全て削除
        df["着順"] = df["着順"].astype(int)
        df["賞金"].fillna(0, inplace=True)  # 賞金の欠損値NaNを0にする

        # 着差を追加する １位のときは２位との差になっている(数値がマイナスになっている)ため最大値を0にする
        df["着差"] = df["着差"].map(lambda x : 0 if x < 0 else x)  # マイナスの値は全て"0"に変換
        # df["着差"] = df["着差"].map(lambda x : x + abs(df_diff))  # マイナス部分を全体に足し算して最大値が"0"になるように変換

        # レース展開データ
        # signal = "first": 最初のコーナー位置, signal = "final": 最終コーナー位置
        def corner(x, signal):
            if type(x) != str:
                return x
            elif signal == "final":
                return int(re.findall(r'\d+', x)[-1])
            elif signal == "first":
                return int(re.findall(r'\d+', x)[0])

        df['first_corner'] = df['通過'].map(lambda x: corner(x, "first"))  # 最初のコーナーでの通過順位
        df['final_corner'] = df['通過'].map(lambda x: corner(x, "final"))  # 最後のコーナーでの通過順位

        # レース展開の情報を作成
        df['final_to_rank'] = df['final_corner'] - df['着順']  # (最終コーナー順位 - 最終順位): ex)大→ラスト強い 小andマイナス¬ラスト弱い
        df['first_to_rank'] = df['first_corner'] - df['着順']  # (最初コーナー順位 - 最終順位)
        df['first_to_final'] = df['first_corner'] - df['final_corner']  # (最終コーナー順位 - 最初コーナー順位)

        # 日付データを変更
        df['date'] = pd.to_datetime(df["日付"])
        df.drop(["日付"], axis=1, inplace=True)

        # 開催は”3京都4”のような形状をしているため文字列箇所を抽出する
        # [0]でpandas→Series型に変換している, fillna(11):nanを"11"に変換　1-10は場所が決まっているためその他という意味で11にしている
        df["開催"] = df["開催"].str.extract(r"(\D+)")[0].map(PLACE_DICT).fillna("11")

        # 距離は”芝1200”みたいな形状をしているため race_type:芝 距離:1200 それぞれ分割する
        df["race_type"] = df["距離"].str.extract(r"(\D+)")[0].map(RACE_TYPE_DICT)

        # レーズ距離は細かく分かれているため１００m単位でまとめる(100で割ってあまりを切り捨てる)
        df["距離"] = df["距離"].str.extract(r"(\d+)")
        df["course_len"] = df["距離"].astype(int) // 100  # 後々レース結果データと結合するときのためにcolumn名を"course_len"とする

        # "course_len"のcolumnを作成して不要となった"距離"を削除
        df.drop(["距離"], axis=1, inplace=True)

        # dfのindexに名前をつける(unstackを使用して平均とるため)
        df.index.name = "horse_id"

        self.pd_horse_results = df

        # 過去レースデータから平均を求めるcolumn名をlistにしておく
        self.target_list = ['着順', '賞金', '着差',
                            'first_corner', 'final_corner',
                            'final_to_rank', 'first_to_rank',
                            'first_to_final']

    def average(self, date, horse_id_list, sample_n="all"):
        """
        過去データから獲得賞金や着順の平均値を算出して説明変数に追加する(self.targe_listに格納しているcolumn名の平均を算出する)
        """
        target_df = self.pd_horse_results.query("index in @horse_id_list")  # horse_id_listにある馬ごとの成績表を指定
        if sample_n == "all":
            filtered_df = target_df[target_df["date"] < date]  # 成績表の着順と賞金の平均を求める
        elif sample_n > 0:
            # acending = False のときは降順(dateが新しいものが上にくる)となる
            filtered_df = target_df[target_df["date"] < date].sort_values("date", ascending=False).groupby(level=0).head(sample_n)
        else:
            raise Exception("n_samples must be >0")

        # "non_category", "race_type", "course_len", "開催"の４つで平均を計算したdataframeを格納する
        self.average_dict = {}

        # 特に共通事項を設けずに平均を算出
        self.average_dict["non_category"] = filtered_df.groupby(level=0)[self.target_list].mean().add_suffix(f"_{sample_n}R")  # 成績表の着順と賞金の平均を求める

        # columnに指定している項目を共通事項として、平均を算出する.
        # 例："race_type"は芝、ダート、障害、の３種類あるが、芝のレースの平均、ダートの平均・・・って感じでそれぞれのレースタイプごとに計算する
        # 芝が得意な馬、ダートが得意な馬それぞれいるから、それをモデルにわかりやすく判別してもらうために実装する
        for column in ["race_type", "course_len", "開催"]:
            self.average_dict[column] = filtered_df.groupby(["horse_id", column])\
                [self.target_list].mean().add_suffix(f"_{column}_{sample_n}R")

    def merge(self, pd_results, date, sample_n="all"):
        df = pd_results[pd_results["date"] == date]
        horse_id_list = df["horse_id"]
        self.average(date, horse_id_list, sample_n)  # self.average_dictを作成するために実行

        # "non_caregory"は他の３つとは、コードが少し違うために下のforの中には入れない
        merged_df = df.merge(self.average_dict["non_category"], how="left", left_on="horse_id", right_index=True)

        # averageモジュールで作成したレースデータ平均値を結合する
        # 結合方法: race_type, course_len, 開催が同じものだけで平均値をとる.
        # →芝が得意な馬、ダートが得意な馬など異なるため,ダートだけの過去成績などをそれぞれ算出しておく必要がある
        # 例）過去５レースが全てダードの場合で今回のレースが芝の場合は過去５レース平均値はNaNとなる。
        for column in ["race_type", "course_len", "開催"]:
            merged_df = merged_df.merge(self.average_dict[column], how="left", left_on=["horse_id", column], right_index=True)
        return merged_df

    def merge_all(self, pd_results, sample_n="all"):
        date_list = pd_results["date"].unique()
        # sample_nで指定されたサンプル数で過去データたから平均データを作成する(mergeモジュールにて作成する)
        merged_df = pd.concat([self.merge(pd_results, date, sample_n) for date in tqdm(date_list)])
        return merged_df


class Return:
    '''
    レースの払い戻しデータテーブル(df)の作成
    各馬券ごとの払い戻しデータを取得.(@propertyにより呼び出し可能)
    '''

    def __init__(self, return_tables):
        self.return_tables = return_tables
        self.return_tables.columns = ["type", "win", "return", "人気"]

    @classmethod
    def load_pickle(cls, GET_DATA_YEAR_LIST):
        # あらかじめスクレイピングしてある馬券ごとの払い戻しデータを読み込む(pd_return_tables_test_〇〇〇〇: DataFrame型)
        df = pd.concat([load_pickle(FILE_PATH_BASE_DATA, f"pd_return_tables_test_{GET_DATA_YEAR}") for GET_DATA_YEAR in GET_DATA_YEAR_LIST])
        return cls(df)  # dfがclass内のreturn_tablesとして扱われる

    @property
    def single(self):
        # 単勝

        # memo------------------------------------------------------------------
        # rt = Return.load_pickle(GET_DATA_YEAR_LIST)
        # return_tables = rt.return_tables.copy()
        # memo------------------------------------------------------------------

        # return_tableから単勝の箇所を取得
        return_tables = self.return_tables.rename(columns={"win": "umaban"}).copy()  # 他の馬券と呼び方をあわせるため、renameで変換しておく
        single_win = return_tables[return_tables["type"] == "単勝"].drop(["type"], axis=1)

        # 重複行を削除しておく
        single_win = single_win.groupby(level=0).first().copy()

        # 単勝のデータにたまに1着が２頭いる場合があるので１着に絞る処理を行う
        df_append = pd.DataFrame(columns=["umaban", "return", "人気"])

        # 1着が2頭いるのかを判定する(2着いる場合は"br"が文字列に含まれている ex:"1br3")
        if len(single_win[single_win["umaban"].str.contains("br")]) > 0:
            # 文字列に"br"を含む行を抽出する
            df_contain_br = single_win[single_win["umaban"].str.contains("br")].copy()
            for index in df_contain_br.index:

                # brで分割して1つ目(1着が２頭いるうちの１馬目)のデータのみ取得する
                info = df_contain_br.loc[index].str.split("br", expand=True).T[0:1]  # "1br3"の場合は"1"を抽出する
                info.index = [f"{index}"]

                # 元データからbrを含む行を削除する(分割して得たデータはあとで結合するためデータ数は変化なし)
                single_win = single_win.drop(index=index, axis=0)  # "br"を含んでいた処理前の行を削除する
                df_append = pd.concat([df_append, info])  # 変換後のdfを繋げておく

        # brで分けて取得したデータを元データに結合する
        df_single_win_return = pd.concat([single_win, df_append])
        df_single_win_return["return"] = df_single_win_return["return"].str.replace(",", "")
        df_single_win_return = df_single_win_return.fillna(0).astype(int)
        df_single_win_return = df_single_win_return.apply(lambda x: pd.to_numeric(x, errors="coerce")).copy()  # to_numericにより文字列型を不動小数点型に変換　coerceにより変換できない値はnanに変換される

        return df_single_win_return.add_suffix("_true")

    @property  # propertyを使うと関数に引数を指定しなくても使用できる
    def fukushou(self):
        # 複勝

        # memo------------------------------------------------------------------
        # rt = Return.load_pickle(GET_DATA_YEAR_LIST)
        # return_tables = rt.return_tables.copy()
        # memo------------------------------------------------------------------

        return_tables = self.return_tables.rename(columns={"win": "umaban"}).copy()  # 他の馬券と呼び方をあわせるため、renameで変換しておく
        return_fukushou = return_tables[return_tables["type"] == "複勝"]

        # 重複行を削除しておく
        return_fukushou = return_fukushou.groupby(level=0).first().copy()

        # 勝った馬が”4br8br3”のように記載されているため、"br"を目印にしてデータを分割する
        wins = return_fukushou["umaban"].str.split("br", expand = True)[[0, 1, 2]].add_prefix("umaban_")

        # 払い戻し額が”4000br800br300”のように記載されているため、"br"を目印にしてデータを分割する
        returns = return_fukushou["return"].str.split("br", expand = True)[[0, 1, 2]].add_prefix("return_")
        returns = returns.apply(lambda x: x.str.replace(",", "")).copy()  # データの中に、"1,999"のように","が含まれて文字列型から整数型に変換できないデータがあるため","を削除しておく

        # 勝った馬、払い戻し額、人気データを1つのdataframeにしておく
        df_fukushou_return = pd.concat([wins, returns], axis=1)

        # 他の馬券で行っている"br"を取り除く処理は上で"br"の文字列を起点にデータ分割をするため行わない(行う必要がない)

        # "return"columnの中に金額が5,300みたいに","が含まれている場合があるため、それを取り除いている
        df_fukushou_return = df_fukushou_return.fillna(0).astype(int).copy()  # 欠損値を0に変換する
        df_fukushou_return = df_fukushou_return.apply(lambda x: pd.to_numeric(x, errors="coerce")).copy()  # to_numericにより文字列型を不動小数点型に変換　errors="coerce"とすると変換できない値はnanに変換される

        return df_fukushou_return.add_suffix("_true")

    @property
    def umatan(self):
        # 馬単

        # memo------------------------------------------------------------------
        # rt = Return.load_pickle(GET_DATA_YEAR_LIST)
        # return_table = rt.return_tables.copy()
        # memo------------------------------------------------------------------

        return_tables = self.return_tables.copy()
        return_umatan = return_tables[return_tables["type"] == "馬単"]

        # 重複行を削除しておく
        return_umatan = return_umatan.groupby(level=0).first().copy()

        # 勝った馬が”4→8”のように記載されているため、"→"を目印にしてデータを分割する
        wins = return_umatan["win"].str.split(" → ", expand = True)[[0, 1]].add_prefix("win_")

        # 勝った馬、払い戻し額、人気データを1つのdataframeにしておく
        df_umatan_return = pd.concat([wins, return_umatan["return"], return_umatan["人気"]], axis=1)

        # 同着がいるレースがあるので１頭に絞る処理を行う
        df_append = pd.DataFrame(columns=["win_0", "win_1", "return", "人気"])
        # 1着が2頭いるのかを判定する(2着いる場合は"br"が文字列に含まれている ex:"1br3")
        for i in range(2):  # 馬単は勝ち馬が３頭でwin_〇〇が2列あるためrange(2)
            if len(df_umatan_return[f"win_{i}"].str.contains("br")) > 0:
                # 文字列に"br"を含む行を抽出する
                df_contain_br = df_umatan_return[df_umatan_return[f"win_{i}"].str.contains("br")].copy()
                for index in df_contain_br.index:

                    # memo-----------------------------------------------------
                    # index = "201905040709"
                    # memo-----------------------------------------------------

                    # brで分割して1つ目(1着が２頭いるうちの１馬目)のデータのみ取得する
                    info = df_contain_br.loc[index].str.split("br", expand=True).T[0:1]  # "1br3"の場合は"1"を抽出する
                    info.index = [f"{index}"]

                    # 元データからbrを含む行を削除する(分割して得たデータはあとで結合するためデータ数は変化なし)
                    df_umatan_return = df_umatan_return.drop(index=index, axis=0)  # "br"を含んでいた処理前の行を削除する
                    df_append = pd.concat([df_append, info])  # 変換後のdfを繋げておく

        # brで分けて取得したデータを元データに結合する
        df_umatan_return = pd.concat([df_umatan_return, df_append])

        # "return"columnの中に金額が5,300みたいに","が含まれている場合があるため、それを取り除いている
        df_umatan_return["return"] = df_umatan_return["return"].str.replace(",", "")

        df_umatan_return = df_umatan_return.fillna(0).astype(int).copy()  # 欠損値を0に変換する
        df_umatan_return = df_umatan_return.apply(lambda x: pd.to_numeric(x, errors="coerce")).copy()  # to_numericにより文字列型を不動小数点型に変換　coerceにより変換できない値はnanに変換される

        # 勝ち馬の文字列を作成する 例：勝った馬が 9,5の場合→9-5の文字列の作成する 欠損値の処理が終わった後にする
        df_win_str = df_umatan_return[["win_0", "win_1"]].astype(str).copy()
        df_umatan_return["umaban"] = df_win_str["win_0"].str.cat(df_win_str[["win_1"]], sep="-")
        df_umatan_return.drop(["win_0", "win_1"], axis=1, inplace=True)
        return df_umatan_return.add_suffix("_true")

    @property
    def umaren(self):

        # memo------------------------------------------------------------------
        # rt = Return.load_pickle(GET_DATA_YEAR_LIST)
        # return_tables = rt.return_tables.copy()
        # memo------------------------------------------------------------------

        return_tables = self.return_tables.copy()
        df_umaren_return = return_tables[return_tables["type"] == "馬連"].copy()

        # 重複行を削除しておく
        df_umaren_return = df_umaren_return.groupby(level=0).first().copy()

        # 上位2頭をdataframeで列ごとに抽出(同着の削除処理に使用した後削除する)
        df_wins = df_umaren_return["win"].str.split(" - ", expand = True)[[0, 1]].add_prefix("win_")  # 上位３頭が "3 - 5 - 7" みたいな文字列になっているため、splitして抽出している

        # 勝った馬、払い戻し額、人気データを1つのdataframeにしておく
        df_umaren_return = pd.concat([df_wins, df_umaren_return["return"], df_umaren_return["人気"]], axis=1)

        # 同着がいるレースがあるので１頭に絞る処理を行う
        df_append = pd.DataFrame(columns=["win_0", "win_1", "return", "人気"])  # 処理した後のデータを一旦この変数に追加しておく（全データの処理が終わったら元データと結合する）

        # 1着が2頭いるのかを判定する(2着いる場合は"br"が文字列に含まれている ex:"1br3")
        for i in range(2):  # 馬連は勝ち馬が2頭でwin_〇〇が2列あるためrange(2)
            if len(df_umaren_return[f"win_{i}"].str.contains("br")) > 0:
                # 文字列に"br"を含む行を抽出する
                df_contain_br = df_umaren_return[df_umaren_return[f"win_{i}"].str.contains("br")].copy()
                for index in df_contain_br.index:

                    # memo-----------------------------------------------------
                    # index = "201905040709"
                    # memo-----------------------------------------------------

                    # brで分割して1つ目(1着が２頭いるうちの１馬目)のデータのみ取得する
                    info = df_contain_br.loc[index].str.split("br", expand=True).T[0:1]  # "1br3"の場合は"1"を抽出する
                    info.index = [f"{index}"]

                    # 元データからbrを含む行を削除する(分割して得たデータはあとで結合するためデータ数は変化なし)
                    df_umaren_return = df_umaren_return.drop(index=index, axis=0)  # "br"を含んでいた処理前の行を削除する
                    df_append = pd.concat([df_append, info])  # 変換後のdfを繋げておく

        # brで分けて取得したデータを元データに結合する
        df_umaren_return = pd.concat([df_umaren_return, df_append])
        df_umaren_return["umaban"] = df_umaren_return["win_0"].str.cat(df_umaren_return[["win_1"]], sep="-").str.split("-").apply(set)  # 上位2頭をset型に変換
        df_umaren_return.drop(["win_0", "win_1"], axis=1, inplace=True)

        # "return"columnの中に金額が5,300みたいに","が含まれている場合があるため、それを取り除いている
        df_umaren_return["return"] = df_umaren_return["return"].str.replace(",", "")

        # df_umaren_return = df_umaren_return[["return", "人気"]].fillna(0).astype(int).copy()  # 欠損値を0に変換する
        df_umaren_return[["return", "人気"]] = df_umaren_return[["return", "人気"]].fillna(0).astype(int).copy()  # 欠損値を0に変換する
        df_umaren_return[["return", "人気"]] = df_umaren_return[["return", "人気"]].apply(lambda x: pd.to_numeric(x, errors="coerce")).copy()  # to_numericにより文字列型を不動小数点型に変換　coerceにより変換できない値はnanに変換される
        return df_umaren_return.add_suffix("_true")

    @property
    def sannrenntann(self):

        # memo------------------------------------------------------------------
        # rt = Return.load_pickle(GET_DATA_YEAR_LIST)
        # return_table = rt.return_tables.copy()
        # memo------------------------------------------------------------------

        return_tables = self.return_tables.copy()
        return_sannrenntann = return_tables[return_tables["type"] == "三連単"]

        # 重複行を削除しておく
        return_sannrenntann = return_sannrenntann.groupby(level=0).first().copy()

        # 勝った馬が”4→8”のように記載されているため、"→"を目印にしてデータを分割する
        wins = return_sannrenntann["win"].str.split(" → ", expand = True)[[0, 1, 2]].add_prefix("win_")

        # 勝った馬、払い戻し額、人気データを1つのdataframeにしておく
        df_sannrenntann_return = pd.concat([wins, return_sannrenntann["return"], return_sannrenntann["人気"]], axis=1)

        # 同着がいるレースがあるので１頭に絞る処理を行う
        df_append = pd.DataFrame(columns=["win_0", "win_1", "win_2", "return", "人気"])

        # 1着が2頭いるのかを判定する(2着いる場合は"br"が文字列に含まれている ex:"1br3")
        for i in range(3):  # ３連単は勝ち馬が３頭でwin_〇〇が３列あるためrange(3)
            if len(df_sannrenntann_return[f"win_{i}"].str.contains("br")) > 0:
                # 文字列に"br"を含む行を抽出する
                df_contain_br = df_sannrenntann_return[df_sannrenntann_return[f"win_{i}"].str.contains("br")].copy()
                for index in df_contain_br.index:

                    # memo-----------------------------------------------------
                    # index = "201905040709"
                    # memo-----------------------------------------------------

                    # brで分割して1つ目(1着が２頭いるうちの１馬目)のデータのみ取得する
                    info = df_contain_br.loc[index].str.split("br", expand=True).T[0:1]  # "1br3"の場合は"1"を抽出する
                    info.index = [f"{index}"]

                    # 元データからbrを含む行を削除する(分割して得たデータはあとで結合するためデータ数は変化なし)
                    df_sannrenntann_return = df_sannrenntann_return.drop(index=index, axis=0)  # "br"を含んでいた処理前の行を削除する
                    df_append = pd.concat([df_append, info])  # 変換後のdfを繋げておく

        # brで分けて取得したデータを元データに結合する
        df_sannrenntann_return = pd.concat([df_sannrenntann_return, df_append])

        # "return"columnの中に金額が5,300みたいに","が含まれている場合があるため、それを取り除いている
        df_sannrenntann_return["return"] = df_sannrenntann_return["return"].str.replace(",", "")
        df_sannrenntann_return = df_sannrenntann_return.fillna(0).astype(int).copy()  # 欠損値を0に変換する
        df_sannrenntann_return = df_sannrenntann_return.apply(lambda x: pd.to_numeric(x, errors="coerce")).copy()  # to_numericにより文字列型を不動小数点型に変換　coerceにより変換できない値はnanに変換される

        # 勝ち馬の文字列を作成する 例：勝った馬が 9,5の場合→9-5の文字列の作成する 欠損値の処理が終わった後にする
        df_win_str = df_sannrenntann_return[["win_0", "win_1", "win_2"]].astype(str).copy()
        df_sannrenntann_return["umaban"] = df_win_str["win_0"].str.cat(df_win_str[["win_1", "win_2"]], sep="-")
        df_sannrenntann_return.drop(["win_0", "win_1", "win_2"], axis=1, inplace=True)
        return df_sannrenntann_return.add_suffix("_true")

    @property
    def sannrennpuku(self):

        # memo------------------------------------------------------------------
        # rt = Return.load_pickle(GET_DATA_YEAR_LIST)
        # return_tables = rt.return_tables.copy()
        # memo------------------------------------------------------------------

        return_tables = self.return_tables.copy()
        df_sannrennpuku_return = return_tables[return_tables["type"] == "三連複"].copy()

        # 重複行を削除しておく
        df_sannrennpuku_return = df_sannrennpuku_return.groupby(level=0).first().copy()

        # 上位３頭をdataframeで列ごとに抽出(同着の削除処理に使用した後削除する)
        df_wins = df_sannrennpuku_return["win"].str.split(" - ", expand = True)[[0, 1, 2]].add_prefix("win_")  # 上位３頭が "3 - 5 - 7" みたいな文字列になっているため、splitして抽出している

        # 勝った馬、払い戻し額、人気データを1つのdataframeにしておく
        df_sannrennpuku_return = pd.concat([df_wins, df_sannrennpuku_return["return"], df_sannrennpuku_return["人気"]], axis=1)

        # 同着がいるレースがあるので１頭に絞る処理を行う
        df_append = pd.DataFrame(columns=["win_0", "win_1", "win_2", "return", "人気"])  # 処理した後のデータを一旦この変数に追加しておく（全データの処理が終わったら元データと結合する）

        # 1着が2頭いるのかを判定する(2着いる場合は"br"が文字列に含まれている ex:"1br3")
        for i in range(3):  # ３連複は勝ち馬が３頭でwin_〇〇が３列あるためrange(3)
            if len(df_sannrennpuku_return[f"win_{i}"].str.contains("br")) > 0:
                # 文字列に"br"を含む行を抽出する
                df_contain_br = df_sannrennpuku_return[df_sannrennpuku_return[f"win_{i}"].str.contains("br")].copy()
                for index in df_contain_br.index:

                    # memo-----------------------------------------------------
                    # index = "201905040709"
                    # memo-----------------------------------------------------

                    # brで分割して1つ目(1着が２頭いるうちの１馬目)のデータのみ取得する
                    info = df_contain_br.loc[index].str.split("br", expand=True).T[0:1]  # "1br3"の場合は"1"を抽出する
                    info.index = [f"{index}"]

                    # 元データからbrを含む行を削除する(分割して得たデータはあとで結合するためデータ数は変化なし)
                    df_sannrennpuku_return = df_sannrennpuku_return.drop(index=index, axis=0)  # "br"を含んでいた処理前の行を削除する
                    df_append = pd.concat([df_append, info])  # 変換後のdfを繋げておく
        # brで分けて取得したデータを元データに結合する
        df_sannrennpuku_return = pd.concat([df_sannrennpuku_return, df_append])
        df_sannrennpuku_return["umaban"] = df_sannrennpuku_return["win_0"].str.cat(df_sannrennpuku_return[["win_1", "win_2"]], sep="-").str.split("-").apply(set)  # 上位３頭をset型に変換
        df_sannrennpuku_return.drop(["win_0", "win_1", "win_2"], axis=1, inplace=True)

        # "return"columnの中に金額が5,300みたいに","が含まれている場合があるため、それを取り除いている
        df_sannrennpuku_return["return"] = df_sannrennpuku_return["return"].str.replace(",", "")

        # df_sannrennpuku_return = df_sannrennpuku_return[["return", "人気"]].fillna(0).astype(int).copy()  # 欠損値を0に変換する
        df_sannrennpuku_return[["return", "人気"]] = df_sannrennpuku_return[["return", "人気"]].fillna(0).astype(int).copy()  # 欠損値を0に変換する
        df_sannrennpuku_return[["return", "人気"]] = df_sannrennpuku_return[["return", "人気"]].apply(lambda x: pd.to_numeric(x, errors="coerce")).copy()  # to_numericにより文字列型を不動小数点型に変換　coerceにより変換できない値はnanに変換される
        return df_sannrennpuku_return.add_suffix("_true")


# 回収率を算出するためのclassを作成する
class Calucurate_Return:
    """
    回収率を各馬券の払い戻しデータとモデルからの予測をもとに計算する

    以下の２通りの馬券の買い方をしている
    - モデル予測をそのまま採用する場合
    - うまい馬券(モデル予測値とオッズからの勝率の差を重視)を優先的に購入する場合

    """

    def __init__(self, model, GET_DATA_YEAR_LIST, X_test_add_tansho_ninnki, X_test, baken_type, is_standard_scarer=True, is_use_pycaret=True):
        self.model = model
        self.rt = Return.load_pickle(GET_DATA_YEAR_LIST)

        self.baken_type = baken_type
        self.pred_table_base = X_test_add_tansho_ninnki.copy()[["馬番", "単勝"]]  # ここにいろいろ情報を追加してpred_tableを完成させる

        self.is_standard_scarer = is_standard_scarer
        self.is_use_pycaret = is_use_pycaret
        self.time_list = []

        self.judge_threshold_func = np.frompyfunc(self.judge_threshold, 2, 1)  # thresholdにより賭ける・賭けないを判定する関数を作成
        self.judge_true_win_func = np.frompyfunc(self.judge_win, 2, 1)  # thresholdにより賭ける・賭けないを判定する関数を作成

        # プログラムの構成的に、"単勝、複勝"、"馬単、馬連","三連単、三連複"は同様の処理で作成する
        if self.baken_type == "single_and_fukushou":
            self.pred_table = 0
            self.return_table_single = self.rt.single
            self.return_table_fukushou = self.rt.fukushou
        elif self.baken_type == "umatan_and_umaren":
            self.pred_table_umaren = 0
            self.pred_table_umatan = 0
            self.return_table_umaren = self.rt.umaren
            self.return_table_umatan = self.rt.umatan
        elif self.baken_type == "sannrenntann_and_sannrennpuku":
            self.pred_table_sannrenntann = 0
            self.pred_table_sannrennpuku = 0
            self.return_table_sannrenntann = self.rt.sannrenntann
            self.return_table_sannrennpuku = self.rt.sannrennpuku
        else:
            raise Exception(f"{self.baken_type} is error. Please check baken_type")
        self.create_pred_table(X_test)  # pred_tableを作成する

    def create_pred_table(self, X_test):
        """
        modelから１着になる確率を算出してから、それをthresholds(域値)を設定して判定する
        return: y_pred(list)
        """
        # レースidごとに標準化をして全体でmin_maxスケーリングする(Rごとにprobaの価値が異なるため、この処理を行う)
        if self.is_standard_scarer:
            """
            現段階(20220601)ではまだ標準化の実装はしない
            - pycaretによる検証
            などを実装してから行う
            """

            raise Exception("Standardization not yet implemented")

            # 実装途中memo-------------------------------------------------------
            # proba_table = X[["horse_id"]].copy()

            # proba_table["proba"] = pd.Series(self.model.predict_proba(X)[:, 1], index=X_test.index)

            # proba_ss_dict = {}  # この中にrace_idごとにprobaを標準化したデータを格納する key: race_id, item: proba_ss

            # # レースidごとに標準化を行う index = レースid
            # for index in proba_table.index.unique():
            #     proba_ss_dict[index] = pd.DataFrame(StandardScaler().fit_transform(proba_table["proba"].loc[index].values.reshape(-1, 1)))

            # # 標準化をしたindexをレースidにする
            # for key in proba_ss_dict.keys():
            #     proba_ss_dict[key].index = [key]*len(proba_ss_dict[key])

            # # 全てのレースデータを結合
            # # proba_ss_dict['201909050809']
            # proba_table["proba_ss"] = pd.concat([proba_ss_dict[key] for key in proba_ss_dict.keys()], sort=False)
            # proba_table["proba_ss_min_max"] = MinMaxScaler().fit_transform(proba_table["proba_ss"].values.reshape(-1, 1))
            # y_pred = [1 if predict > thresholds else 0 for predict in proba_table["proba_ss_min_max"].values]
            # self.return_table_base["y_proba"] = MinMaxScaler().fit_transform(proba_table["proba_ss"].values.reshape(-1, 1))
            # return y_pred
            # 実装途中memo-------------------------------------------------------

        if self.is_standard_scarer is False:
            # 的中率算出用データ加工 モデル予測値と正解ラベルを追加しておく

            # memo----------------------------------------------------------
            # pred_table_base = X_test_add_tansho_ninnki.copy()[["馬番", "単勝"]]  # ここにいろいろ情報を追加してpred_tableを完成させる
            # pred_table_base["predict"] = lgb_clf_X_train.predict(X_test)
            # pred_table_base["model_before"] = lgb_clf_X_train.predict_proba(X_test)[:, 1]  # モデルからの予測値(実数値)これを加工して、合計が"1"になるようにする
            # pred_table_base

            # lgb_clf_X_train.predict_proba(X_test)[:]  # モデルからの予測値(実数値)これを加工して、合計が"1"になるようにする
            # pred_table_base["model_before"] = lgb_clf_X_train.predict_proba(X_test)[:, 1]  # モデルからの予測値(実数値)これを加工して、合計が"1"になるようにする

            # # pycaret使用時
            # final_gbc = load_model("tuned_gbc")
            # pred_table_base["predict"] = predict_model(final_gbc, data = X_test)["Label"]
            # pred_table_base["model_before"] = 1 - predict_model(final_gbc, data = X_test)["Score"]
            # pred_table_base["model_before"] = predict_model(final_gbc, data = X_test_add_tansho_ninnki)["Score"]

            # X_train = test_data.drop(["rank"], axis=1)
            # time_list = []
            # time_list.append(time.time())
            # pred_table_base = X_test_add_tansho_ninnki.copy()[["馬番", "単勝"]]  # ここにいろいろ情報を追加してpred_tableを完成させる
            # memo----------------------------------------------------------

            pred_table_base = self.pred_table_base.copy()

            # pycaretで取得したモデルの場合はpredict方法が違うため分岐させておく(streamlit実装の際はpycaretのライブラリを使用するとエラーが生じるためとりあえずコメントアウトしておく)-----------
            # if self.is_use_pycaret:
            #     pred_table_base["predict"] = predict_model(self.model, data = X_test)["Label"]
            #     pred_table_base["model_before"] = 1 - predict_model(self.model, data = X_test)["Score"]  # (1 - ○)としているのは、predict_modelから出力されるのは、"１位以外になる確率"だからである
            # else:
                # pred_table_base["predict"] = self.model.predict(X_test)
            # pycaretで取得したモデルの場合はpredict方法が違うため分岐させておく(streamlit実装の際はpycaretのライブラリを使用するとエラーが生じるためとりあえずコメントアウトしておく)-----------

            pred_table_base["model_before"] = self.model.predict_proba(X_test)[:, 1]  # モデルからの予測値(実数値)これを加工して、合計が"1"になるようにする

            # odd(単勝)を勝率に変換する
            odd_prob_list = [(0.75 / odd) for odd in pred_table_base["単勝"].values]  # 勝率 = 0.75 / オッズ  (競馬の場合は全体掛け金の２５％運営が持っていくから0.75)
            pred_table_base["odd_before"] = odd_prob_list  # オッズから変換いた勝率　これを加工して、合計が"1"になるようにする

            # モデル、オッズの勝率の合計が1になるように、計算する
            model_proba_list = []  # モデル予測用
            odd_proba_list = []  # オッズ予測用

            for race_id in pred_table_base.index.unique():
                # model からの出力確率の合計を1.0に加工
                model_proba_list_before = pred_table_base.loc[race_id]["model_before"].values  # 各馬の１位になる確率
                model_proba_list_after = model_proba_list_before / model_proba_list_before.sum()  # 確率の合計が1.00になるようにする→各馬券の発生確率の計算に使用する
                model_proba_list = np.append(model_proba_list, model_proba_list_after)
                # odd からの出力確率の合計を1.0に加工
                odd_proba_list_before = pred_table_base.loc[race_id]["odd_before"].values  # 各馬の１位になる確率
                odd_proba_list_after = odd_proba_list_before / odd_proba_list_before.sum()  # 確率の合計が1.00になるようにする→各馬券の発生確率の計算に使用する
                odd_proba_list = np.append(odd_proba_list, odd_proba_list_after)

            pred_table_base["model_proba"] = model_proba_list  # modelからの予測値
            pred_table_base["odd_proba"] = odd_proba_list  # オッズからの予測値
            pred_table_base = pred_table_base.drop(["model_before", "odd_before"], axis=1).copy()  # 加工前のデータは不要のため削除する

            if self.baken_type == "single_and_fukushou":
                self.pred_table = pred_table_base.rename(columns={"馬番": "umaban_pred", "model_proba": "model", "odd_proba": "odd"})  # 他の馬券とcolumn名を統一しておく
                self.pred_table["diff"] = self.pred_table["odd"] - self.pred_table["model"]  # オッズ勝率 - モデル予測勝率 → 大：うまい馬券、小：割の悪い馬券

            if self.baken_type == "sannrenntann_and_sannrennpuku":
                # race_idごとに馬番の組み合わせlistを作成する
                sannrenntann_dict = {}
                sannrennpuku_dict = {}

                # memo----------------------------------------------------------
                # pred_table_base = pred_table_base.loc[race_id].copy()

                # time_list_1 = []
                # time_list_2 = []
                # time_list_3 = []

                # print(time_list_1[-1] - time_list_1[0])
                # for i in range(len(time_list_1)):
                #     print(time_list_1[i + 1] - time_list_1[i])

                # print(time_list_2[-1] - time_list_2[0])
                # for i in range(len(time_list_2)):
                #     print(time_list_2[i + 1] - time_list_2[i])

                # time_list_1.append(time.time())
                # time_list_2.append(time.time())
                # time_list_3.append(time.time())
                # memo----------------------------------------------------------

                for race_id in tqdm(pred_table_base.index.unique().values):

                    df = pred_table_base.loc[race_id].copy()

                    # モデル、オッズからの勝率で辞書を作成しておく(dfのままはおそくなるため)
                    model_dict = dict(zip(df["馬番"].values, df["model_proba"].values))  # key: 馬番, values: モデルから予測した勝率
                    odd_dict = dict(zip(df["馬番"].values, df["odd_proba"].values))  # key: 馬番, values: オッズから予測した勝率

                    # 組み合わせリストの作成　nCr で計算している
                    model_sannrennpuku_dict = {}
                    model_sannrenntann_dict = {}
                    odd_sannrennpuku_dict = {}
                    odd_sannrenntann_dict = {}

                    # 組み合わせ馬券の確率の計算
                    for comb_ in itertools.combinations(df["馬番"].values, 3):  # １回for回すと使用できなくなる仕様

                        # memo--------------------------------------------------
                        # print(comb_)
                        # comb_ = (3, 6, 6)
                        # memo--------------------------------------------------

                        model_sannrennpuku_prob = 0  # modelの3連複確率
                        odd_sannrennpuku_prob = 0  # oddからの3連複確率
                        for perm_ in itertools.permutations(comb_, 3):

                            # memo----------------------------------------------
                            # print(f"perm_:{perm_}")
                            # perm_ = (6, 6, 2)
                            # memo----------------------------------------------

                            # memo----------------------------------------------
                            # この処理は遅かった
                            # p1 = df[df["馬番"] == perm_[0]]["model_proba"].values[0]  # perm_の1頭目が1位になる確率
                            # q1 = df[df["馬番"] == perm_[1]]["model_proba"].values[0]  # perm_の2頭目が1位になる確率
                            # r1 = df[df["馬番"] == perm_[2]]["model_proba"].values[0]  # perm_の3頭目が1位になる確率

                            # p1 = model_dict[perm_[0]]  # perm_の1頭目が1位になる確率
                            # q1 = model_dict[perm_[1]]  # perm_の2頭目が1位になる確率
                            # r1 = model_dict[perm_[2]]  # perm_の3頭目が1位になる確率
                            # memo----------------------------------------------

                            # モデルからの勝率から３連単、３連腹の確率計算
                            # comb_で取り出した馬番の順番を並べ替えてそれぞれの勝率を計算する
                            # perm_は馬番に対応, perm_は馬番が格納しているlistで全通りの馬を選択するようにforで回している

                            # perm_の２頭目が２位になる確率
                            q2 = model_dict[perm_[1]] / (1 - model_dict[perm_[0]])

                            # perm_の3頭目が3位になる確率
                            r3 = model_dict[perm_[2]] / (1 - model_dict[perm_[0]] - model_dict[perm_[1]])

                            # ３連単の確率
                            model_sannrenntann_prob = model_dict[perm_[0]] * q2 * r3  # ３連単確率
                            model_sannrenntann_dict[f"{perm_[0]}-{perm_[1]}-{perm_[2]}"] = model_sannrenntann_prob
                            model_sannrennpuku_prob += model_sannrenntann_prob

                            # memo----------------------------------------------
                            # p1 = odd_dict[perm_[0]]  # perm_の1頭目が1位になる確率
                            # q1 = odd_dict[perm_[1]]  # perm_の2頭目が1位になる確率
                            # r1 = odd_dict[perm_[2]]  # perm_の3頭目が1位になる確率

                            # こっちは遅い
                            # p1 = df[df["馬番"] == perm_[0]]["odd_proba"].values[0]  # perm_の1頭目が1位になる確率
                            # q1 = df[df["馬番"] == perm_[1]]["odd_proba"].values[0]  # perm_の2頭目が1位になる確率
                            # r1 = df[df["馬番"] == perm_[2]]["odd_proba"].values[0]  # perm_の3頭目が1位になる確率
                            # memo----------------------------------------------

                            # オッズからの勝率から３連単、３連腹の確率計算
                            # comb_で取り出した馬番の順番を並べ替えてそれぞれの勝率を計算する
                            # perm_は馬番に対応, perm_は馬番が格納しているlistで全通りの馬を選択するようにforで回している

                            # perm_の２頭目が２位になる確率
                            q2 = odd_dict[perm_[1]] / (1 - odd_dict[perm_[0]])
                            # perm_の3頭目が3位になる確率
                            r3 = odd_dict[perm_[2]] / (1 - odd_dict[perm_[0]] - odd_dict[perm_[1]])
                            # ３連単の確率
                            odd_sannrenntann_prob = odd_dict[perm_[0]] * q2 * r3  # ３連単確率
                            odd_sannrenntann_dict[f"{perm_[0]}-{perm_[1]}-{perm_[2]}"] = odd_sannrenntann_prob
                            odd_sannrennpuku_prob += odd_sannrenntann_prob

                        # ３連複の確率
                        model_sannrennpuku_dict[f"{comb_[0]}-{comb_[1]}-{comb_[2]}"] = model_sannrennpuku_prob
                        odd_sannrennpuku_dict[f"{comb_[0]}-{comb_[1]}-{comb_[2]}"] = odd_sannrennpuku_prob

                    # 上で作成したdictをdataframeに変換
                    model_sannrennpuku_dict
                    sannrennpuku_df = pd.DataFrame(data=model_sannrennpuku_dict.values(), index=model_sannrennpuku_dict.keys(), columns=["model"])
                    sannrennpuku_df["odd"] = odd_sannrennpuku_dict.values()
                    sannrennpuku_df["diff"] = sannrennpuku_df["odd"] - sannrennpuku_df["model"]  # diffの値は大きほど"上手い馬券"である
                    sannrennpuku_df["race_id"] = [race_id] * len(sannrennpuku_df)
                    sannrennpuku_df.index.name = "umaban_pred"
                    sannrennpuku_df = sannrennpuku_df.set_index("race_id", append=True)
                    sannrennpuku_dict[race_id] = sannrennpuku_df

                    # 上で作成したdictをdataframeに変換
                    sannrenntann_df = pd.DataFrame(data=model_sannrenntann_dict.values(), index=odd_sannrenntann_dict.keys(), columns=["model"])
                    sannrenntann_df["odd"] = odd_sannrenntann_dict.values()
                    sannrenntann_df["diff"] = sannrenntann_df["odd"] - sannrenntann_df["model"]
                    sannrenntann_df["race_id"] = [race_id] * len(sannrenntann_df)
                    sannrenntann_df.index.name = "umaban_pred"
                    sannrenntann_df = sannrenntann_df.set_index("race_id", append=True)
                    sannrenntann_dict[race_id] = sannrenntann_df

                self.pred_table_sannrenntann = pd.concat([sannrenntann_dict[key] for key in sannrenntann_dict.keys()], axis=0)
                self.pred_table_sannrennpuku = pd.concat([sannrennpuku_dict[key] for key in sannrennpuku_dict.keys()], axis=0)

                # betする馬番をそれぞれcolumnsに分ける(後でset関数により比較をするため)
                # self.pred_table[["pred_0", "pred_1", "pred_2"]] = self.pred_table["umaban_pred"].str.split("-", expand=True).astype(int)
                # 三連単・三連複両方の処理する
                self.pred_table_sannrenntann.index = self.pred_table_sannrenntann.index.swaplevel("race_id", "umaban_pred")
                self.pred_table_sannrennpuku.index = self.pred_table_sannrennpuku.index.swaplevel("race_id", "umaban_pred")

                # multiindexの"umaban"をcolumnに戻す
                # 三連単・三連複両方の処理する
                # 三連単
                self.pred_table_sannrenntann = self.pred_table_sannrenntann.reset_index(level="umaban_pred").copy()

                # 三連複
                self.pred_table_sannrennpuku = self.pred_table_sannrennpuku.reset_index(level="umaban_pred").copy()
                self.pred_table_sannrennpuku["umaban_pred"] = self.pred_table_sannrennpuku["umaban_pred"].str.split("-").apply(set)

            if self.baken_type == "umatan_and_umaren":
                # race_idごとに馬番の組み合わせlistを作成する
                umatan_dict = {}
                umaren_dict = {}

                for race_id in tqdm(pred_table_base.index.unique().values):

                    # memo------------------------------------------------------
                    # race_id = "201905040801"
                    # print(race_id)
                    # memo------------------------------------------------------

                    df = pred_table_base.loc[race_id].copy()

                    # モデル、オッズからの勝率で辞書を作成しておく(dfのままはおそくなるため)
                    model_dict = dict(zip(df["馬番"], df["model_proba"]))
                    odd_dict = dict(zip(df["馬番"], df["odd_proba"]))

                    # 組み合わせリストの作成　nCr で計算している
                    model_umaren_dict = {}
                    model_umatan_dict = {}
                    odd_umaren_dict = {}
                    odd_umatan_dict = {}

                    # 組み合わせ馬券の確率の計算
                    for comb_ in itertools.combinations(df["馬番"].values, 3):  # １回for回すと使用できなくなる仕様

                        # memo--------------------------------------------------
                        # print(f"comb_:{comb_}")
                        # comb_ = (3, 6, 8)
                        # memo--------------------------------------------------

                        model_umaren_prob = 0  # modelの3連複確率
                        odd_umaren_prob = 0  # oddからの3連複確率
                        for perm_ in itertools.permutations(comb_, 3):

                            # memo----------------------------------------------
                            # print(f"perm_:{perm_}")
                            # perm_ = (6, 3, 2)
                            # memo----------------------------------------------

                            # モデルからの勝率から馬連、馬単の確率計算
                            # comb_で取り出した馬番の順番を並べ替えてそれぞれの勝率を計算する
                            # perm_は馬番に対応, perm_は馬番が格納しているlistで全通りの馬を選択するようにforで回している

                            p1 = model_dict[perm_[0]]  # perm_の1頭目が1位になる確率
                            q1 = model_dict[perm_[1]]  # perm_の2頭目が1位になる確率
                            # perm_の２頭目が２位になる確率
                            q2 = model_dict[perm_[1]] / (1 - model_dict[perm_[0]])
                            # 馬連の確率
                            model_umatan_prob = model_dict[perm_[0]] * q2  # 馬連確率
                            model_umatan_dict[f"{perm_[0]}-{perm_[1]}"] = model_umatan_prob
                            model_umaren_prob += model_umatan_prob

                            # オッズからの勝率から馬連、馬単の確率計算
                            # comb_で取り出した馬番の順番を並べ替えてそれぞれの勝率を計算する
                            # perm_は馬番に対応, perm_は馬番が格納しているlistで全通りの馬を選択するようにforで回している

                            p1 = odd_dict[perm_[0]]  # perm_の1頭目が1位になる確率
                            q1 = odd_dict[perm_[1]]  # perm_の2頭目が1位になる確率
                            # perm_の２頭目が２位になる確率
                            q2 = odd_dict[perm_[1]] / (1 - odd_dict[perm_[0]])
                            # 馬単の確率
                            odd_umatan_prob = odd_dict[perm_[0]] * q2  # 馬単確率
                            odd_umatan_dict[f"{perm_[0]}-{perm_[1]}"] = odd_umatan_prob
                            odd_umaren_prob += odd_umatan_prob

                        model_umaren_dict[f"{comb_[0]}-{comb_[1]}"] = model_umaren_prob
                        odd_umaren_dict[f"{comb_[0]}-{comb_[1]}"] = odd_umaren_prob

                    # dataframeに変換
                    umaren_df = pd.DataFrame(data=model_umaren_dict.values(), index=model_umaren_dict.keys(), columns=["model"])
                    umaren_df["odd"] = odd_umaren_dict.values()
                    umaren_df["diff"] = umaren_df["odd"] - umaren_df["model"]  # diffの値は大きほど"上手い馬券"である
                    umaren_df["race_id"] = [race_id] * len(umaren_df)
                    umaren_df.index.name = "umaban_pred"
                    umaren_df = umaren_df.set_index("race_id", append=True)
                    umaren_dict[race_id] = umaren_df

                    umatan_df = pd.DataFrame(data=model_umatan_dict.values(), index=odd_umatan_dict.keys(), columns=["model"])
                    umatan_df["odd"] = odd_umatan_dict.values()
                    umatan_df["diff"] = umatan_df["odd"] - umatan_df["model"]
                    umatan_df["race_id"] = [race_id] * len(umatan_df)
                    umatan_df.index.name = "umaban_pred"
                    umatan_df = umatan_df.set_index("race_id", append=True)
                    umatan_dict[race_id] = umatan_df

                self.pred_table_umatan = pd.concat([umatan_dict[key] for key in umatan_dict.keys()], axis=0)
                self.pred_table_umaren = pd.concat([umaren_dict[key] for key in umaren_dict.keys()], axis=0)

                # betする馬番をそれぞれcolumnsに分ける(後でset関数により比較をするため)
                # self.pred_table[["pred_0", "pred_1", "pred_2"]] = self.pred_table["umaban_pred"].str.split("-", expand=True).astype(int)
                # 馬単・馬連の両方処理する

                self.pred_table_umatan.index = self.pred_table_umatan.index.swaplevel("race_id", "umaban_pred")
                self.pred_table_umaren.index = self.pred_table_umaren.index.swaplevel("race_id", "umaban_pred")

                # multiindexの"umaban"をcolumnに戻す
                # 馬単・馬連の両方処理する
                # 馬単
                self.pred_table_umatan = self.pred_table_umatan.reset_index(level="umaban_pred").copy()

                # 馬連
                self.pred_table_umaren = self.pred_table_umaren.reset_index(level="umaban_pred").copy()
                self.pred_table_umaren["umaban_pred"] = self.pred_table_umaren["umaban_pred"].str.split("-").apply(set)

        else:
            raise Exception("is_standard_scarer baken_type is invalid please check is_standard_scarer")

    def calucurate_return_money(self, pred_return_table, trade_type, pred_signal, thresholds, hit_back_money, is_proper=True):
        """
        params:
        X:モデルへの入力データ
        y_true:正解ラベルのデータ(Xとy_trueのデータ数は同一とすること)
        thresholds:モデルの出力値を判定するための閾値
        hit_back_money:予想が的中した場合に獲得できる金額(多いほど賭ける金額は増える)
        is_proper: Trueの場合は的中回収率にて回収率を計算する　的中回収率・・・hit_back_money(予想的中したときに獲得できるお金)を設定して計算する
                   Flaseの場合は取引する場合は１回あたり100円をbetする方法で回収率を計算する
        return
        """

        # memo----------------------------------------------------------
        # time_list = []
        # for i in range(len(time_list) - 1):
        #     print(time_list[i+1] - time_list[i])
        # time_list.append(time.time())

        # is_proper の処理
        # is_properによって的中回収率が1bet=100円で賭けるかを判定する
        #     if is_proper:
        #         """
        #         現段階(20220601)ではproperの実装はしない
        #         - pycaretによる検証
        #         - 学習データ期間の拡大
        #         などを実装してから行う
        #         """
        #         raise Exception("is_proper not yet implemented")
        #         win_money = len(pred_table.query(" win == 馬番 & y_pred == 1")) * hit_back_money  # 賭けると判定したうちで予想が的中した回数 * hit_back_money
        #         # bet_money算出式の説明・・・ 的中したら回収できるお金 / 1円かけたら回収できるお金 = 的中したら回収できるお金をゲットするためにbetするお金
        #         bet_money = int((hit_back_money / pred_table.query("y_pred == 1")["単勝"]).sum())
        # memo----------------------------------------------------------

        # モデルからの勝率 or オッズからの勝率 を pred_signalにて選択している方で馬券を購入する

        if pred_signal == "model":
            thresholds_list = pred_return_table["model"].to_numpy()
            trade_pred_table = pred_return_table[thresholds_list > thresholds]  # after:a: 0.094s
        elif pred_signal == "diff":

            thresholds_list = pred_return_table["diff"].to_numpy()
            trade_pred_table = pred_return_table[thresholds_list > thresholds]  # after:a: 0.094s

            # memo-------------------------------------------------------------
            # 昔の処理 memo-----------------------------------------------------
            # pred_return_table["y_pred"] = pred_return_table["diff"].map(lambda x: 1 if x > thresholds else 0)  # 0.9
            # pred_return_table["y_pred"] = [1 if x > thresholds else 0 for x in pred_return_table["diff"]]  # 0.7
            # pred_return_table["y_pred"] = judge_threshold_func(pred_return_table["diff"], thresholds).astype(int)  # 0.4
            # pred_return_table["y_pred"] = judge_threshold_func(pred_return_table["diff"].to_list(), thresholds)  # 0.4
            # 昔の処理 memo-----------------------------------------------------

            # after: 0.094s----------------------------------------------------
            thresholds_list = pred_return_table["diff"].to_numpy()
            trade_pred_table = pred_return_table[thresholds_list > thresholds]  # after:a: 0.094s
            # trade_pred_table = pred_return_table[pred_return_table["diff"].to_numpy() > thresholds]  # before: 0.096s
            # after: 0.094s----------------------------------------------------

            # before: 0.5s-----------------------------------------------------
            # pred_return_table["y_pred"] = judge_threshold_func(pred_return_table["diff"].to_numpy(), thresholds)  # y_pred(実際にbetするレース)列を作成
            # trade_pred_table = pred_return_table[pred_return_table["y_pred"].values == 1].copy()  # 実際に取引するレースを抽出
            # before: 0.6s-----------------------------------------------------

            # 昔の処理 memo-----------------------------------------------------
            # 1 trade_pred_table = pred_return_table[pred_return_table["y_pred"] == 1].copy()  # 実際に取引するレースを抽出
            # 2 trade_pred_table = pred_return_table[pred_return_table["y_pred"].values == 1].copy()  # 実際に取引するレースを抽出
            # 3 trade_pred_table = pred_return_table[pred_return_table["y_pred"].to_numpy() == 1].copy()  # 実際に取引するレースを抽出
            # 昔の処理 memo-----------------------------------------------------
            # memo-------------------------------------------------------------

        trade_count = len(trade_pred_table)  # 取引回数

        if trade_type == "fukushou":

            # after: 0.0022s-------------------------------------------------------------
            # 複勝は3着以内に入っていれば的中なので、forを3回まわして計算する
            hit_count = 0
            win_money = 0
            for i in range(3):
                hit_pred_table = trade_pred_table[trade_pred_table[f"umaban_{i}_true"] == trade_pred_table["umaban_pred"]]  # 的中したレースを抽出
                hit_count += len(hit_pred_table)
                win_money += hit_pred_table[f"return_{i}_true"].sum()
            bet_money = trade_count * 100
            # after: 0.0022s-------------------------------------------------------------

            # before: 0.0064s-------------------------------------------------------------
            # 複勝は3着以内に入っていれば的中なので、forを3回まわして計算する
            # hit_count = 0
            # win_money = 0
            # for i in range(3):
            #     hit_count += len(pred_return_table[pred_return_table[f"win_{i}_true"] == pred_return_table["umaban_pred"]])  # 的中したデータ数
            #     win_money += pred_return_table[pred_return_table[f"win_{i}_true"]
            #                            == pred_return_table["umaban_pred"]][f"return_{i}_true"].sum()
            # bet_money = trade_count * 100
            # before: 0.0064s-------------------------------------------------------------

        elif trade_type == "sannrenntann" or trade_type == "umatan" or trade_type == "single":

            # after: 0.033s-------------------------------------------------------------
            # after(single): 478 µs ± 15.7 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
            umaban_pred_list = trade_pred_table["umaban_pred"].to_numpy()
            umaban_true_list = trade_pred_table["umaban_true"].to_numpy()
            hit_pred_table = trade_pred_table[umaban_pred_list == umaban_true_list].copy()  # after: 0.032s
            # hit_pred_table = trade_pred_table[trade_pred_table["umaban_pred"].to_numpy() == trade_pred_table["umaban_true"].to_numpy()].copy()  # before: 0.04s
            # hit_pred_table = trade_pred_table[trade_pred_table["umaban_pred"] == trade_pred_table["umaban_true"]].copy()  # before: 0.12s
            # hit_count: 的中回数, win_money: 勝ったお金, bet_money: 賭けたお金をそれぞれ算出する
            hit_count = len(hit_pred_table)
            bet_money = trade_count * 100
            win_money = hit_pred_table["return_true"].sum()
            # after: 0.033s-------------------------------------------------------------

            # before: 0.52s-------------------------------------------------------------
            # 実際に賭けた馬券が的中していれば　1(True) 外れていれば 0(False) を表示する y_true の列を作成する
            # trade_pred_table["y_true"] = judge_true_win_func(trade_pred_table["umaban_pred"].values, trade_pred_table["umaban_true"].values).astype(int)  # 約0.4秒
            # trade_pred_table["y_true"] = judge_true_win_func(trade_pred_table["umaban_pred"].to_numpy(), trade_pred_table["umaban_true"].to_numpy()).astype(int)  # 約0.4秒
            # # hit_count: 的中回数, win_money: 勝ったお金, bet_money: 賭けたお金をそれぞれ算出する
            # hit_count = len(trade_pred_table[trade_pred_table["y_true"].to_numpy() == 1])
            # win_money = trade_pred_table[trade_pred_table["y_true"].to_numpy() == 1]["return_true"].sum()
            # bet_money = trade_count * 100
            # before: 0.52s-------------------------------------------------------------

        elif trade_type == "sannrennpuku" or trade_type == "umaren":

            # after:0.023s-----------------------------------------------------------------------------------
            hit_pred_table = trade_pred_table[trade_pred_table["umaban_pred"] == trade_pred_table["umaban_true"]]
            # hit_count: 的中回数, win_money: 勝ったお金, bet_money: 賭けたお金をそれぞれ算出する
            hit_count = len(hit_pred_table)
            bet_money = trade_count * 100
            win_money = hit_pred_table["return_true"].sum()
            # after:0.023s-----------------------------------------------------------------------------------

            # before:1.1s-----------------------------------------------------------------------------------
            # y_true_list = [1 if set(pred_umaban) == set(win_umaban) else 0 for pred_umaban, win_umaban in zip(trade_pred_table[["pred_0", "pred_1", "pred_2"]].values, trade_pred_table[["win_0_true", "win_1_true", "win_2_true"]].values)]
            # trade_pred_table["y_true"] = y_true_list
            # hit_count = len(trade_pred_table[trade_pred_table["y_true"] == 1])
            # win_money = trade_pred_table[trade_pred_table["y_true"] == 1]["return_true"].sum()
            # bet_money = trade_count * 100
            # before:1.1s-----------------------------------------------------------------------------------
        else:
            raise Exception(f"{trade_type} is error. Please check trade_type")
        print(f"thresholds: {thresholds}, hit_count: {hit_count}, trade_count: {trade_count}, bet_money: {bet_money}, win_money: {win_money}, return(%): {(win_money / bet_money) * 100}")
        return trade_count, hit_count, bet_money, win_money, hit_pred_table

    def judge_sannrennpuku(pred, win):
        """
        frompyfunc用の関数
        賭けた馬券が的中しているか判定する(三連複専用)
        """
        print(pred, win)
        # if set(pred) == set(win):
        #     return 1
        # else:
        #     return 0

    def judge_threshold(self, pred_value, thresholds):
        """
        frompyfunc用の関数
        thresholdでbetするか判定する
        """
        if pred_value > thresholds:
            return 1
        else:
            return 0

    def judge_win(self, umaban_pred, umaban_true):
        """
        frompyfunc用の関数
        賭けた馬券が的中しているか判定する
        umaban_pred: 賭けた馬券の馬番
        umaban_true: 勝つ馬番
        """
        if umaban_pred == umaban_true:
            return 1
        else:
            return 0

    def feature_importances(self, X, n_samples=20):
        """
        訓練時の説明変数の重要度を評価(上位のほど相関関係が高いと判断された説明変数)
        """
        # 特徴量の評価
        importance = pd.DataFrame({"features": X.columns, "importance": self.model.feature_importances_})
        return importance.sort_values("importance", ascending=False)[0:n_samples]  # 重要な説明変数ほど上位に来ている

    def for_calucurate_return_money(self, trade_type, pred_signal, hit_back_money=10000, is_proper=True, max_threshold=1.0, min_threshold=0.5, n_separate=50, lowest_trade_count=50):
        """
        thresholdを変化させて回収率を計算する
        params:
        trade_type(str): どの馬券かを指定
        y_true: 検証用正解ラベル(pred_tableに正解ラベルを付与するためだけに使用)
        min_threshold: thresholdの最低値を設定してそこから検証をはじめる
        hit_back_money: 適性回収率→1回的中したら○円儲かるかの設定
        n_separate: min_thresholdからthreshold:1.0になるまでを何分割するのか
        lowest_trade_count: 最低取引回数を指定(それ以下の取引回数の場合はgainに記録しない)

        return:
        gain(dict): key: 取引回数 item: 獲得金額
        """

        # memo------------------------------------------------------
        # cr_sann = Calucurate_Return(lgb_clf_X_train, GET_DATA_YEAR_LIST, X_test_add_tansho_ninnki, X_test, "single_and_fukushou", is_standard_scarer=False, is_use_pycaret=False)
        # pred_table = cr_sann.pred_table_sannrenntann.copy()
        # return_table = cr_sann.return_table_sannrenntann.copy()
        # pred_return_table = pd.merge(pred_table, return_table, how="left", left_index=True, right_index=True)
        # cr_sann = Calucurate_Return(lgb_clf_X_train, GET_DATA_YEAR_LIST, X_test_add_tansho_ninnki, X_test, "sannrenntann_and_sannrennpuku", is_standard_scarer=False, is_use_pycaret=False)
        # pred_table = cr_sann.pred_table_sannrennpuku.copy()
        # return_table = cr_sann.return_table_sannrennpuku.copy()
        # pred_return_table = pd.merge(pred_table, return_table, how="left", left_index=True, right_index=True)
        # # 一度pickleファイルに保存することで、高速化を期待している
        # save_pickle(FILE_PATH, "pred_return_table.pickle", pred_return_table)
        # pred_return_table
        # pred_return_table = load_pickle(FILE_PATH, "pred_return_table.pickle")[["diff", "model", "umaban_pred", "umaban_true", "return_true"]].copy()
        # trade_count, hit_count, bet_money, win_money, pred_table = cr_sann.calucurate_return_money(pred_return_table,trade_type="single", pred_signal="diff", thresholds=pred_return_table["diff"].min(), hit_back_money=100, is_proper=False)
        # time_list = []
        # print(time_list[-1] - time_list[0])
        # memo------------------------------------------------------

        # 上で実行した create_pred_table メソッドにより作成した pred_table と return_tabnle を結合してpred_return_table を作成する(回収率計算に使用する)
        if trade_type == "single":
            pred_table = self.pred_table.copy()
            return_table = self.return_table_single.copy()
        elif trade_type == "fukushou":
            pred_table = self.pred_table.copy()
            return_table = self.return_table_fukushou.copy()
        elif trade_type == "umatan":
            pred_table = self.pred_table_umatan.copy()
            return_table = self.return_table_umatan.copy()
        elif trade_type == "umaren":
            pred_table = self.pred_table_umaren.copy()
            return_table = self.return_table_umaren.copy()
        elif trade_type == "sannrenntann":
            pred_table = self.pred_table_sannrenntann.copy()
            return_table = self.return_table_sannrenntann.copy()
        elif trade_type == "sannrennpuku":
            pred_table = self.pred_table_sannrennpuku.copy()
            return_table = self.return_table_sannrennpuku.copy()
        else:
            raise Exception(f"{trade_type} is error. Please check trade_type")

        # pred_table(モデルが予測した値などのdataframe)とreturn_table(買った時の賞金などのdataframe)結合する ・・・回収率算出用
        self.pred_return_table = pd.merge(pred_table, return_table, how="left", left_index=True, right_index=True)

        # 一度pickleファイルに保存することで、高速化を期待している
        save_pickle(FILE_PATH_FIT_DATA, "pred_return_table.pickle", self.pred_return_table)

        # 一度pickleファイルに保存したファイルを際読み込みすることで、高速化を狙っている.
        # 必要なcolumnのみ読み込む. 高速化のため.
        if trade_type == "fukushou":
            pred_return_table = load_pickle(FILE_PATH_FIT_DATA, "pred_return_table.pickle")[["umaban_pred", "diff", "model", "umaban_0_true", "umaban_1_true", "umaban_2_true", "return_0_true", "return_1_true", "return_2_true"]].copy()
        else:
            # 複勝以外の馬券は同様のcolumns
            pred_return_table = load_pickle(FILE_PATH_FIT_DATA, "pred_return_table.pickle")[["diff", "model", "umaban_pred", "umaban_true", "return_true"]].copy()

        gain_accuracy = {}  # トレード回数ごとの正解率の算出
        gain_return = {}  # トレード回数ごとの回収率の算出
        gain_pred_table = {}  # thresholdsごとのpred_table

        for i in tqdm(range(n_separate + 1)):
            thresholds = (max_threshold - min_threshold)/n_separate * i + min_threshold
            trade_count, hit_count, bet_money, win_money, pred_table = self.calucurate_return_money(pred_return_table,trade_type, pred_signal, thresholds, hit_back_money, is_proper)
            if trade_count > lowest_trade_count:
                # print(trade_count, win_money)
                gain_return[trade_count] = (win_money / bet_money)
                gain_pred_table[trade_count] = pred_table
                gain_accuracy[trade_count] = hit_count / trade_count * 100
            else:
                break
        return gain_accuracy, gain_return, gain_pred_table


class Data_Processer:
    """
    訓練用データと出馬テーブルの処理の共通部分のclassを作成する(継承用)
    """
    def __init__(self):
        self.data = pd.DataFrame()
        self.data_p = pd.DataFrame()  # after preprocessing
        self.data_r = pd.DataFrame()  # appned n_samples
        self.data_ped = pd.DataFrame()  # append ped_datas
        self.data_id = pd.DataFrame()  # append new id

    def merge_n_samples(self, hr, samples_n_list=[5, 9, "all"]):
        """
        過去レースデータの平均値を計算して説明変数にする(賞金や着順など)
        何レース分の平均値とするかは sample_n_list により指定する
        """

        # memo------------------------------------------------------------------
        # hr = preprocessing_horse_result(pd_horse_results)
        # samples_n_list = [5, 9, "all"]
        # memo------------------------------------------------------------------

        df = self.data_p.rename_axis("race_id").copy()  # horse_idとrace_idをベースにmerge_all関数で作成するデータと結合するためにrace_idを一旦columにしておく
        df['date'] = pd.to_datetime(df["date"])

        for sample_n in samples_n_list:
            df_m = hr.merge_all(df, sample_n=sample_n)  # 過去５,9,allのレースの成績を作成する
            filter_columns = np.append(df_m.filter(like=f"{sample_n}", axis=1).columns.values, "horse_id")  # merge_all関数によって作成したデータとhorse_idの列だけ残す
            df_n_samples = df_m.filter(items=filter_columns).rename_axis("race_id").reset_index()  # race_idを一旦columnにしておく(データ結合のため)

            df = df.merge(df_n_samples, how="left", on=["race_id", "horse_id"]).set_index("race_id")  # horse_idとrace_idをkeyとして結合する
        df.drop(["開催"], axis=1, inplace=True)
        self.data_r = df.copy()

    def merge_ped_data(self, pd_ped_datas):
        """
        血統データを説明変数に追加
        """
        self.data_ped = self.data_r.merge(pd_ped_datas, left_on="horse_id", right_index=True, how="left")
        no_peds = self.data_ped[self.data_ped["ped_0"].isnull()]["horse_id"].unique()
        if len(no_peds) > 0:
            print(f" need scrape peds at horse_id : {no_peds}")
        self.no_peds = no_peds

    def labelencoder_id(self, le_horse_id, le_jockey_id, le_trainer_id, weather_unique, race_type_unique, ground_state_unique, gender_categories_unique):
        """
        horse_id, jockey_id, trainer_id
        天気(weather),  レースタイプ(race_type)
        馬場(ground_state), 性別(gender_categories)
        をラベルエンコーディングする
        """
        # memo------------------------------------------------------------------
        # df = rt.data_ped.copy()
        # weather_unique = rt.data_ped["weather"].unique()
        # race_type_unique = rt.data_ped["race_type"].unique()
        # ground_state_unique = rt.data_ped["ground_state"].unique()
        # gender_categories_unique = rt.data_ped["性別"].unique()
        # df["weather"] = pd.Categorical(df["weather"], categories=weather_unique)
        # df["race_type"] = pd.Categorical(df["race_type"], categories=race_type_unique)
        # df["ground_state"] = pd.Categorical(df["ground_state"], categories=ground_state_unique)
        # df["性別"] = pd.Categorical(df["性別"], categories=gender_categories_unique)
        # memo------------------------------------------------------------------

        df = self.data_ped.copy()

        #  horse_id, jockey_idをラベルエンコーディング: 0からはじまる整数に変換
        # mask関数
        mask_horse = df["horse_id"].isin(le_horse_id.classes_)
        mask_jockey = df["jockey_id"].isin(le_jockey_id.classes_)
        mask_trainer = df["trainer_id"].isin(le_trainer_id.classes_)

        # mask関数はisin()などでFalseとなった箇所を取得できる(whereはその逆でTrueを取得できる)
        new_horse_id_list = df["horse_id"].mask(mask_horse).dropna().unique()
        new_jockey_id_list = df["jockey_id"].mask(mask_jockey).dropna().unique()
        new_trainer_id_list = df["trainer_id"].mask(mask_trainer).dropna().unique()

        # 新たに追加するidを追加する
        le_horse_id.classes_ = np.concatenate([le_horse_id.classes_, new_horse_id_list])
        le_jockey_id.classes_ = np.concatenate([le_jockey_id.classes_, new_jockey_id_list])
        le_trainer_id.classes_ = np.concatenate([le_trainer_id.classes_, new_trainer_id_list])

        # カテゴリ化を実行
        df["horse_id"] = le_horse_id.transform(df["horse_id"])
        df["jockey_id"] = le_jockey_id.transform(df["jockey_id"])
        df["trainer_id"] = le_trainer_id.transform(df["trainer_id"])

        # weathr, race_type, ground_state, 性別をpandas category型に変換(説明変数の列を揃えるため)
        df["weather"] = pd.Categorical(df["weather"], categories=weather_unique)
        df["race_type"] = pd.Categorical(df["race_type"], categories=race_type_unique)
        df["ground_state"] = pd.Categorical(df["ground_state"], categories=ground_state_unique)
        df["性別"] = pd.Categorical(df["性別"], categories=gender_categories_unique)

        df = pd.get_dummies(df, columns=["weather", "race_type", "ground_state", "性別"])
        self.data_id = df


class Result_Table(Data_Processer):
    """
    訓練データ作成のためのclass
    過去レースデータの前処理(preprocessing)・エンコーディングするための準備(lavelencodr_id)
    """

    def __init__(self, data):
        super(Result_Table, self).__init__()
        self.data = data

    @classmethod
    def load_pickle(cls, GET_DATA_YEAR_LIST):

        pd_race_results = load_pickle(FILE_PATH_BASE_DATA, f"pd_race_results_{GET_DATA_YEAR_LIST[0]}")
        pd_race_infos = load_pickle(FILE_PATH_BASE_DATA, f"pd_race_infos_{GET_DATA_YEAR_LIST[0]}")  # レース情報
        # pd_race_infos = pd.DataFrame(pd_race_infos_tmp).T

        # レース結果とレース情報を結合する
        df = pd.merge(pd_race_results, pd_race_infos, how="inner", left_index=True, right_index=True)
        if len(GET_DATA_YEAR_LIST) > 1:
            for GET_DATA_YEAR in GET_DATA_YEAR_LIST[1:]:
                pd_race_results = load_pickle(FILE_PATH_BASE_DATA, f"pd_race_results_{GET_DATA_YEAR}")
                pd_race_infos_tmp = load_pickle(FILE_PATH_BASE_DATA, f"pd_race_infos_{GET_DATA_YEAR}")  # レース情報
                pd_race_infos = pd.DataFrame(pd_race_infos_tmp)
                # レース結果とレース情報を結合する
                df_add = pd.merge(pd_race_results, pd_race_infos, how="inner", left_index=True, right_index=True)
                df = pd.concat([df, df_add])
        return cls(df)

    def preprocessing(self):
        """
        サイトから取得してきた過去レースデータ前処理
        - 欠損値を削除
        - 型の変更（str - int）
        - 不要なcloumnの削除
        - colomnで分割したデータを分割
        """

        # memo------------------------------------------------------------------
        # rt.data.columns
        # rt.data.head(1)
        # memo------------------------------------------------------------------

        df = self.data.copy()

        # 開催場所をrace_idから取得する. race_id:2019040101のような形状となっていて、この場合は2019の後の"04"が場所を表しているためそこ[4:6]を取得する
        df["開催"] = df.index.map(lambda x: str(x)[4:6])

        # レーズ距離は細かく分かれているため１００m単位でまとめる(100で割ってあまりを切り捨てる)
        df["course_len"] = df["course_len"].astype(int) // 100

        # 着順のデータ型を確認
        df["着順"].value_counts()
        df["着順"].astype(str).value_counts()

        # 着順の変なデータを削除する
        df["着順"] = pd.to_numeric(df["着順"], errors="coerce")  # to_numericにてstr型の数値をfloat型に変換する.また"中"などの文字をnanに変換する
        df.dropna(subset=["着順"], inplace=True)  # "中"などの不要な文字列をnanに変換後にnanを着順のnanを全て削除
        df["着順"] = df["着順"].astype(int)

        # 枠番は変なデータなさそう
        df["枠番"].value_counts()

        # 馬番は変なデータなさそう
        df["馬番"].value_counts()

        # 性齢は性別と年齢を分ける処理をする
        df["性齢"].value_counts()
        df["性別"] = df["性齢"].map(lambda x: str(x)[0])  # 性別をとりだして文字列型に変換する
        df["年齢"] = df["性齢"].map(lambda x: str(x)[1]).astype(int)  # 性別をとりだして文字列型に変換する
        df["体重"] = df["馬体重"].str.split("(", expand= True)[0].astype(int)  # 前体重と体重増減分割する
        df["体重変化"] = df["馬体重"].str.split("(", expand= True)[1].str[:-1].astype(int)  # 体重増減の最後の")"を削除

        # 型の変更
        df["着順"] = df["着順"].astype(int)
        df["course_len"] = df["course_len"].astype(int)
        df["単勝"] = df["単勝"].astype(float)

        # 日付データを変更
        df['date'] = pd.to_datetime(df["date"], format='%Y年%m月%d日')

        # race_type の中のいろんな障害レースの名称を”障害”に統一しておく
        df["race_type"] = df["race_type"].map(lambda x: "障害" if "障" in x else x)

        # 分割して不要になったcolumnを削除
        df.drop(["性齢", "馬体重"], axis=1, inplace=True)

        # とりま不要なcolumnsを削除
        df.drop(["着差", "調教師", "タイム", "騎手", "馬名"], axis=1, inplace=True)
        # df.info()

        self.data_p = df

    def labelencoder_id(self):
        self.le_horse_id = LabelEncoder().fit(self.data_ped["horse_id"])
        self.le_jockey_id = LabelEncoder().fit(self.data_ped["jockey_id"])
        self.le_trainer_id = LabelEncoder().fit(self.data_ped["trainer_id"])
        self.weather_unique = self.data_ped["weather"].unique()
        self.race_type_unique = self.data_ped["race_type"].unique()
        self.ground_state_unique = self.data_ped["ground_state"].unique()
        self.gender_categories_unique = self.data_ped["性別"].unique()
        super().labelencoder_id(self.le_horse_id, self.le_jockey_id,
                                self.le_trainer_id, self.weather_unique,
                                self.race_type_unique, self.ground_state_unique,
                                self.gender_categories_unique)


class labelencoder_ped:
    """
    pedデータをlabelencoderするclass
    """

    def __init__(self, pd_ped_datas):
        self.pd_ped_datas = pd_ped_datas
        self.pd_ped_datas_la = pd.DataFrame()  # after labelencoder

    @classmethod
    def load_pickle(cls, GET_DATA_YEAR_LIST):
        df = pd.concat([load_pickle(FILE_PATH_BASE_DATA, f"pd_ped_datas_{GET_DATA_YEAR}") for GET_DATA_YEAR in GET_DATA_YEAR_LIST])
        return cls(df)

    def labelencode_ped(self):
        df = self.pd_ped_datas.copy()
        for column in df.columns:
            df[column] = LabelEncoder().fit_transform(df[column].fillna("Na"))
        df.astype("category")
        self.pd_ped_datas_la = df


# 検証結果を表示するための関数まとめ---------------------------------------------------
def graph_plot(graph_data_list, graph_name_list, graph_title, x_label, y_label):
    """
    グラフ描写(dict型をグラフにする)　複数可
    params:
    plot_data_list(list in dict):描写したいデータをlist型で渡す.listの中はdict
    graph_name_list(list in str):描写したいデータの凡例の名前.listの中はstr.日本語だと表示されないため英語で記載.
    graph_title(str):グラフのタイトル.英語で書くこと.
    return:
    graphの描写
    """

    # memo---------------------------------------------------------------------
    # graph_data_list = [gain_accuracy_diff_sannrenntann_graph, gain_accuracy_model_sannrenntann_graph]
    # graph_name_list = ["diff", "model"]
    # graph_title = "sannrenntann_accuracy"
    # x_label = "trade_count"
    # y_label = "accuracy"
    # memo---------------------------------------------------------------------

    fig, ax = plt.subplots()
    ax.set_title(graph_title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    for plot_data, graph_name in zip(graph_data_list, graph_name_list):
        ax.plot(plot_data.keys(), plot_data.values(), label=graph_name)
        # pd.Series(data=plot_data).rename(graph_name).plot(legend=True)  # 上の行のどちらの処理でも可能
    ax.grid()
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0, fontsize=9)
    # plt.close(fig)


def get_appropriate_thresholds(pred_table, bins, ratio_threshold, pred_signal):
    """
    calucurate_return_money　クラスの　3連単と３連複の回収率を算出するための
    適切なthresholdを見つけてくれる関数
    この関数を使用する理由・・・
    pred_table["model"] と　pred_talbe["diff"]は小さい範囲に値が密集しているため
    広範囲のthoresholdで回収率計算をすると検証の意味がなくなってしまうため、この関数により
    適当なthoresholdをヒストグラムを使用して求める
    params:
    bins(int):ヒストグラムを作成する際のデータの区切りの数・・・大きい方が細かく区切るため適切なthresholdになりやすい
    ratio_threshold(int):区切った範囲のデータ割合がどの程度でよしとするか. 単位は％.
    return:
    max_thoreshold and min_thoreshold:
    →算出した閾値・・・これをそのままcalucurate_return_money クラスに使用する
    """

    # memo---------------------------------------------------------------------
    # pred_table = cr_sann.pred_table_sannrenntann
    # bins = 100
    # ratio_threshold = 20
    # pred_signal = "diff"
    # max_index
    # patches
    # bins
    # n_ratio
    # n_ratio[max_index]
    # memo---------------------------------------------------------------------

    fig, ax = plt.subplots()  # ヒストグラムの準備
    n, bins, patches = ax.hist(pred_table[pred_signal], bins=bins)  # データ数を確認したいデータでヒストグラムを作成
    total_num = int(sum(n))  # pred_tableのデータ合計個数
    n_ratio = [(int(i) / total_num) * 100 for i in n]  # 閾値で区切った各範囲のデータ数の割合を算出
    max_index = n_ratio.index(max(n_ratio))  # データ数が一番大きい箇所のindexを取得
    plt.close(fig)
    # 上で計算したデータ割合が多い箇所を抜き出す
    print(f"データ数割合:{(n_ratio[max_index])} % ")
    if n_ratio[max_index] > ratio_threshold:
        # 一番多い割合の箇所がratio_thresholdより大きければ。その閾値の両端数個を入れた値を取得する
        min_appropriate_threshold = bins[max_index]
        # max_threshold = bins[max_index + 2]
    else:
        raise Exception("please fix n_ratio because ratio is wide range")
    return min_appropriate_threshold, n, bins


def multi_graph_plot(graph_data_diff, graph_data_model, graph_title_list, graph_main_title, x_label, y_label, rows, columns, figsize_width, figsize_height):
    """
    複数のグラフをプロットするための関数
    prams:
    graph_data_diff(list):diffによるデータリスト
    graph_data_model(list):modelによるデータリスト
    graph_title_list(list):グラフのタイトルのリスト(複数のグラフのそれぞれのタイトル)
    graph_main_title(str):グラフのメインタイトル
    x_label(str):x軸の名前(複数グラフは同じ種類のグラフをプロットするため名前は１つでいい)
    y_label(str):y軸の名前(複数グラフは同じ種類のグラフをプロットするため名前は１つでいい)
    return:
    複数のグラフ
    """

    # memo---------------------------------------------------------------------
    # multi_graph_plot(accuracy_diff_single_list, accuracy_model_single_list, graph_title_single_list, graph_main_title=f"accuracy_single_{GET_DATA_YEAR}", x_label="trade_count", y_label="accuracy(%)", rows=1, columns=2, figsize_width=20, figsize_height=5)
    # graph_data_diff = accuracy_diff_single_list
    # graph_data_model = accuracy_model_single_list
    # graph_title_list = graph_title_single_list
    # graph_main_title= f"accuracy_single_{GET_DATA_YEAR}"
    # x_label="trade_count"
    # y_label="accuracy(%)"
    # rows=1
    # columns=2
    # figsize_width=20
    # figsize_height=5
    # memo---------------------------------------------------------------------

    # グラフを表示する領域を作成
    fig, ax = plt.subplots(nrows=rows, ncols=columns, figsize=(figsize_width, figsize_height))  # nrows:複数グラフの行数指定, ncols:列数指定
    plt.suptitle(graph_main_title)
    ax = ax.flatten()
    for i, diff, model, graph_title in zip(range(len(graph_data_diff)), graph_data_diff, graph_data_model, graph_title_list):
        ax[i].set_title(graph_title)
        ax[i].set_xlabel(x_label)
        ax[i].set_ylabel(y_label)
        ax[i].plot(diff.keys(), diff.values(), label="diff")
        ax[i].plot(model.keys(), model.values(), label="model")
        ax[i].legend(loc='upper right', borderaxespad=0, fontsize=9)
        # ax[i].legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0, fontsize=9)
        ax[i].grid(True)
    fig.tight_layout()
    # レイアウトの設定
    # plt.show()
    fig.savefig(f"{FILE_PATH_RESULT_DATA}/{graph_main_title}.png")
    (f"{FILE_PATH_RESULT_DATA}/{graph_main_title}.png")
    plt.close(fig)


def main():

    # 1.データの取得・加工

    # 馬ごとの成績データの処理(過去データの着順・賞金の平均を説明変数にするために使用する)
    hr = Preprocessing_Horse_Result.load_pickle(GET_DATA_YEAR_LIST)
    # hr.pd_horse_results

    # pd_resultsを加工
    rt = Result_Table.load_pickle(GET_DATA_YEAR_LIST)
    # rt.data

    # preprocessing
    rt.preprocessing()
    # rt.data_p.shape

    # 過去データから賞金データを説明変数に追加
    rt.merge_n_samples(hr)
    # rt.data_r

    # 血統データをlabelencodeするためのclassをインスタンス化
    la = labelencoder_ped.load_pickle(GET_DATA_YEAR_LIST)
    # la.pd_ped_datas.shape

    # 重複して取得してしまっている血統データを削除する
    la.pd_ped_datas["horse_id"] = la.pd_ped_datas.index  # horse_idが同一の行を削除するため一時的にcolumnにhorse_idを加える
    # la.pd_ped_datas.shape

    # horse_idが同一データの行を削除する(この処理をするためにhorse_idをcolumnに加える)
    # subsetに指定したcolumnで重複行を探す
    # keep:重複した場合にlastの行を削除する
    la.pd_ped_datas = la.pd_ped_datas.drop_duplicates(subset=["horse_id"], keep="last")
    la.pd_ped_datas.drop(["horse_id"], axis=1, inplace=True)
    # la.pd_ped_datas.shape
    la.labelencode_ped()

    # 血統データを説明変数に追加
    rt.merge_ped_data(la.pd_ped_datas_la)
    # rt.data_ped

    # 訓練データをhorse_id, jockey_idをラベルエンコードする
    # weather, ground_state, race_type, 性別もカテゴライズしてダミー変数化する
    rt.labelencoder_id()

    # 実取引データ加工用(ラベルエンコーディング)に使用するため保存しておく
    # その前に少し前処理・・・天気、レースタイプ、馬場状態、性別のunique値を取得しておく
    # →実取引の予測の時にラベルエンコーディングするために使用する
    weather_unique = rt.data_ped["weather"].unique()
    race_type_unique = rt.data_ped["race_type"].unique()
    ground_state_unique = rt.data_ped["ground_state"].unique()
    gender_categories_unique = rt.data_ped["性別"].unique()

    save_pickle(FILE_PATH_FIT_DATA, "le_horse_id.pickle", rt.le_horse_id)
    save_pickle(FILE_PATH_FIT_DATA, "le_jockey_id.pickle", rt.le_jockey_id)
    save_pickle(FILE_PATH_FIT_DATA, "le_trainer_id.pickle", rt.le_trainer_id)
    # save_pickle(FILE_PATH_FIT_DATA, "data_ped.pickle", rt.data_ped)
    save_pickle(FILE_PATH_FIT_DATA, "weather_unique.pickle", weather_unique)
    save_pickle(FILE_PATH_FIT_DATA, "race_type_unique.pickle", race_type_unique)
    save_pickle(FILE_PATH_FIT_DATA, "ground_state_unique.pickle", ground_state_unique)
    save_pickle(FILE_PATH_FIT_DATA, "gender_categories_unique.pickle", gender_categories_unique)
    # rt.data_id

    # 一旦コピーしておく(result_3Rは下でまた使用するため)
    results_d = rt.data_id.copy()
    # --------------------------------------------------------------------------

    # 2.学習

    # 2-1.lightgbm(単勝)にて回収率を算出-----------------------------------------------------

    # 正解ラベル rank の作成(単勝)
    results_d_single = results_d.copy()

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
    X_train_add_tansho_ninnki = X_train.copy()
    X_test_add_tansho_ninnki = X_test.copy()
    X_train.drop(["単勝", "人気"], axis=1, inplace=True)
    X_test.drop(["単勝", "人気"], axis=1, inplace=True)

    import lightgbm as lgb

    params = {"num_leaves": 4,
              "n_estimators": 80,
              # "min_data_in_leaf": 15,
              "class_weight": "balanced",
              "random_state": 100
              }

    lgb_clf_X_train = lgb.LGBMClassifier(**params)
    lgb_clf_X_train.fit(X_train.values, y_train.values)  # 学習

    # memo---------------------------------------------------------------------
    # 訓練データとテストデータに分割しないver.(実運用の際に使用する)
    X = results_d_single.drop(["rank", "date"], axis=1)
    y = results_d_single["rank"].copy()
    X.drop(["単勝", "人気"], axis=1, inplace=True)
    lgb_clf_X = lgb.LGBMClassifier(**params)
    lgb_clf_X.fit(X.values, y.values)  # 学習
    # memo---------------------------------------------------------------------

    # 学習モデルの保存
    save_pickle(FILE_PATH_FIT_DATA, "lgb_clf_X.pickle", lgb_clf_X)
    save_pickle(FILE_PATH_FIT_DATA, "lgb_clf_X_train.pickle", lgb_clf_X_train)
    save_pickle(FILE_PATH_FIT_DATA, "X_train.pickle", X_train)
    save_pickle(FILE_PATH_FIT_DATA, "X.pickle", X)

    # 訓練データのroc
    # roc_graph_plot(y_train, lgb_clf_X_train.predict_proba(X_train)[:, 1])  # roc_graphをplot
    # print(f"roc_score:{roc_auc_score(y_train, lgb_clf_X_train.predict_proba(X_train)[:, 1])}")  # この値が大きいと過学習している(テストデータのrocと比較して判断する)

    # テストデータのroc
    # roc_graph_plot(y_test, lgb_clf_X_train.predict_proba(X_test)[:, 1])  # roc_graphをplot
    # print(f"roc_score:{roc_auc_score(y_test, lgb_clf_X_train.predict_proba(X_test)[:, 1])}")

    # features_importance(モデルがどの説明変数を重要視しているのか確認できる指標)
    # importance = pd.DataFrame({"features": X_test.columns, "importance": lgb_clf_X_train.feature_importances_})
    # importance.sort_values("importance", ascending=False)[0: 30]  # 重要な説明変数ほど上位に来ている

    # 回収率・的中率をグラフ化する際に、表示する最大取引回数を設定する(可視化したときに見やすくするため)
    max_trade_count = X_test.index.nunique() * 2  # レースの数 * 2 "2"はとりまの値

    # 各馬券ごとに回収率を算出していくーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    # 1.三連単ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    # 1-1.オッズとモデル予測値の差から”うまい馬券”の購入をする買い方
    # key: 取引回数, items: 獲得金額 の辞書を取得
    print("---------------------------------------------------------------パラメーター調整前--------------------------------------------------------------")
    print("--------------------------------三連単/三連複--------------------------------")
    cr_sann = Calucurate_Return(lgb_clf_X_train, GET_DATA_YEAR_LIST, X_test_add_tansho_ninnki, X_test, "sannrenntann_and_sannrennpuku", is_standard_scarer=False, is_use_pycaret=False)
    print("--------------------------------三連単--------------------------------")
    print("---------------------diff-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sann.pred_table_sannrenntann, bins=1000, ratio_threshold=20, pred_signal="diff")
    max_threshold = cr_sann.pred_table_sannrenntann["diff"].max()
    gain_accuracy_diff_sannrenntann, gain_return_diff_sannrenntann, gain_pred_table_diff_sannrenntann = cr_sann.for_calucurate_return_money(trade_type="sannrenntann", pred_signal="diff", hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_diff_sannrenntann[max(gain_return_diff_sannrenntann.keys())]

    # 1-2.モデルからの予測値により勝率が高いものから購入する買い方
    print("---------------------model-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sann.pred_table_sannrenntann, bins=100, ratio_threshold=20, pred_signal="model")
    max_threshold = cr_sann.pred_table_sannrenntann["model"].max()
    gain_accuracy_model_sannrenntann, gain_return_model_sannrenntann, gain_pred_table_model_sannrenntann = cr_sann.for_calucurate_return_money(trade_type="sannrenntann", pred_signal="model", hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_model_sannrenntann[max(gain_return_model_sannrenntann.keys())]

    # グラフにする箇所を抽出する
    max_trade_count = X_test.index.nunique() * 2  # レースの数 * 2 "2"はとりまの値
    gain_return_diff_sannrenntann_graph = {k: i for k, i in gain_return_diff_sannrenntann.items() if max_trade_count > k}
    gain_return_model_sannrenntann_graph = {k: i for k, i in gain_return_model_sannrenntann.items() if max_trade_count > k}
    gain_accuracy_diff_sannrenntann_graph = {k: i for k, i in gain_accuracy_diff_sannrenntann.items() if max_trade_count > k}
    gain_accuracy_model_sannrenntann_graph = {k: i for k, i in gain_accuracy_model_sannrenntann.items() if max_trade_count > k}

    # シミュレーション結果をグラフにする　x軸:取引回数(回), y軸:回収率(%)
    graph_plot([gain_accuracy_diff_sannrenntann_graph, gain_accuracy_model_sannrenntann_graph], ["diff", "model"], "sannrenntann_accuracy", "trade_count", "accuracy(%)")
    graph_plot([gain_return_diff_sannrenntann_graph, gain_return_model_sannrenntann_graph], ["diff", "model"], "sannrenntann_return", "trade_count", "return(%)")

    # 2.三連複ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    # 2-1.オッズとモデル予測値の差から”うまい馬券”の購入をする買い方
    # key: 取引回数, items: 獲得金額 の辞書を取得
    print("--------------------------------三連複--------------------------------")
    print("---------------------diff-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sann.pred_table_sannrennpuku, bins=100, ratio_threshold=20, pred_signal="diff")
    max_threshold = cr_sann.pred_table_sannrennpuku["diff"].max()
    gain_accuracy_diff_sannrennpuku, gain_return_diff_sannrennpuku, gain_pred_table_diff_sannrennpuku = cr_sann.for_calucurate_return_money(trade_type="sannrennpuku", pred_signal="diff",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_diff_sannrennpuku[max(gain_return_diff_sannrennpuku.keys())]

    # 2-2.モデルからの予測値により勝率が高いものから購入する買い方
    print("---------------------model-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sann.pred_table_sannrennpuku, bins=100, ratio_threshold=20, pred_signal="model")
    max_threshold = cr_sann.pred_table_sannrennpuku["model"].max()
    gain_accuracy_model_sannrennpuku, gain_return_model_sannrennpuku, gain_pred_table_model_sannrennpuku = cr_sann.for_calucurate_return_money(trade_type="sannrennpuku", pred_signal="model",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_model_sannrennpuku[max(gain_return_model_sannrennpuku.keys())]

    # グラフにする箇所を抽出する
    max_trade_count = X_test.index.nunique() * 2  # レースの数 * 2 "2"はとりまの値
    gain_return_diff_sannrennpuku_graph = {k: i for k, i in gain_return_diff_sannrennpuku.items() if max_trade_count > k}
    gain_return_model_sannrennpuku_graph = {k: i for k, i in gain_return_model_sannrennpuku.items() if max_trade_count > k}
    gain_accuracy_diff_sannrennpuku_graph = {k: i for k, i in gain_accuracy_diff_sannrennpuku.items() if max_trade_count > k}
    gain_accuracy_model_sannrennpuku_graph = {k: i for k, i in gain_accuracy_model_sannrennpuku.items() if max_trade_count > k}

    # シミュレーション結果をグラフにする　x軸:取引回数(回), y軸:回収率(%)
    graph_plot([gain_accuracy_diff_sannrennpuku_graph, gain_accuracy_model_sannrennpuku_graph], ["diff", "model"], "sannrennpuku_accuracy", "trade_count", "accuracy(%)")
    graph_plot([gain_return_diff_sannrennpuku_graph, gain_return_model_sannrennpuku_graph], ["diff", "model"], "sannrennpuku_return", "trade_count", "return(%)")

    # 3.単勝ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    # 3-1.オッズとモデル予測値の差から”うまい馬券”の購入をする買い方
    # key: 取引回数, items: 獲得金額 の辞書を取得
    print("--------------------------------単勝/複勝--------------------------------")
    cr_sin = Calucurate_Return(lgb_clf_X_train, GET_DATA_YEAR_LIST, X_test_add_tansho_ninnki, X_test, "single_and_fukushou", is_standard_scarer=False, is_use_pycaret=False)
    print("--------------------------------単勝--------------------------------")
    print("---------------------diff-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sin.pred_table, bins=10, ratio_threshold=20, pred_signal="diff")
    max_threshold = cr_sin.pred_table["diff"].max()
    gain_accuracy_diff_single, gain_return_diff_single, gain_pred_table_diff_single = cr_sin.for_calucurate_return_money(trade_type="single", pred_signal="diff",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_diff_single[max(gain_return_diff_single.keys())]

    # 3-2.モデルからの予測値により勝率が高いものから購入する買い方
    print("---------------------model-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sin.pred_table, bins=5, ratio_threshold=20, pred_signal="model")
    max_threshold = cr_sin.pred_table["model"].max()
    gain_accuracy_model_single, gain_return_model_single, gain_pred_table_model_single = cr_sin.for_calucurate_return_money(trade_type="single", pred_signal="model",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_model_single[max(gain_return_model_single.keys())]

    # グラフにする箇所を抽出する
    max_trade_count = X_test.index.nunique() * 2  # レースの数 * 2 "2"はとりまの値
    gain_return_diff_single_graph = {k: i for k, i in gain_return_diff_single.items() if max_trade_count > k}
    gain_return_model_single_graph = {k: i for k, i in gain_return_model_single.items() if max_trade_count > k}
    gain_accuracy_diff_single_graph = {k: i for k, i in gain_accuracy_diff_single.items() if max_trade_count > k}
    gain_accuracy_model_single_graph = {k: i for k, i in gain_accuracy_model_single.items() if max_trade_count > k}

    # シミュレーション結果をグラフにする　x軸:取引回数(回), y軸:回収率(%)
    graph_plot([gain_accuracy_diff_single_graph, gain_accuracy_model_single_graph], ["diff", "model"], "single_accuracy", "trade_count", "accuracy(%)")
    graph_plot([gain_return_diff_single_graph, gain_return_model_single_graph], ["diff", "model"], "single_return", "trade_count", "return(%)")

    # 4.複勝ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    # 4-1.オッズとモデル予測値の差から”うまい馬券”の購入をする買い方
    # key: 取引回数, items: 獲得金額 の辞書を取得
    print("--------------------------------複勝--------------------------------")
    print("---------------------diff-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sin.pred_table, bins=5, ratio_threshold=20, pred_signal="diff")
    max_threshold = cr_sin.pred_table["diff"].max()
    gain_accuracy_diff_fukushou, gain_return_diff_fukushou, gain_pred_table_diff_fukushou = cr_sin.for_calucurate_return_money(trade_type="fukushou", pred_signal="diff",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_diff_fukushou[max(gain_return_diff_fukushou.keys())]

    # 4-2.モデルからの予測値により勝率が高いものから購入する買い方
    print("---------------------model-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sin.pred_table, bins=5, ratio_threshold=20, pred_signal="model")
    max_threshold = cr_sin.pred_table["model"].max()
    gain_accuracy_model_fukushou, gain_return_model_fukushou, gain_pred_table_model_fukushou = cr_sin.for_calucurate_return_money(trade_type="fukushou", pred_signal="model",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_model_fukushou[max(gain_return_model_fukushou.keys())]

    # グラフにする箇所を抽出する
    max_trade_count = X_test.index.nunique() * 2  # レースの数 * 2 "2"はとりまの値
    gain_return_diff_fukushou_graph = {k: i for k, i in gain_return_diff_fukushou.items() if max_trade_count > k}
    gain_return_model_fukushou_graph = {k: i for k, i in gain_return_model_fukushou.items() if max_trade_count > k}
    gain_accuracy_diff_fukushou_graph = {k: i for k, i in gain_accuracy_diff_fukushou.items() if max_trade_count > k}
    gain_accuracy_model_fukushou_graph = {k: i for k, i in gain_accuracy_model_fukushou.items() if max_trade_count > k}

    # シミュレーション結果をグラフにする　x軸:取引回数(回), y軸:回収率(%)
    graph_plot([gain_accuracy_diff_fukushou_graph, gain_accuracy_model_fukushou_graph], ["diff", "model"], "fukushou_accuracy", "trade_count", "accuracy(%)")
    graph_plot([gain_return_diff_fukushou_graph, gain_return_model_fukushou_graph], ["diff", "model"], "fukushou_return", "trade_count", "return(%)")

    # 5.馬連ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    # 5-1.オッズとモデル予測値の差から”うまい馬券”の購入をする買い方
    # key: 取引回数, items: 獲得金額 の辞書を取得
    print("--------------------------------馬単/馬連--------------------------------")
    cr_two = Calucurate_Return(lgb_clf_X_train, GET_DATA_YEAR_LIST, X_test_add_tansho_ninnki, X_test, "umatan_and_umaren", is_standard_scarer=False, is_use_pycaret=False)
    print("--------------------------------馬連--------------------------------")
    print("---------------------diff-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_two.pred_table_umaren, bins=10, ratio_threshold=20, pred_signal="diff")
    max_threshold = cr_two.pred_table_umaren["diff"].max()
    gain_accuracy_diff_umaren, gain_return_diff_umaren, gain_pred_table_diff_umaren = cr_two.for_calucurate_return_money(trade_type="umaren", pred_signal="diff",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_diff_umaren[max(gain_return_diff_umaren.keys())]

    # 5-2.モデルからの予測値により勝率が高いものから購入する買い方
    print("---------------------model-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_two.pred_table_umaren, bins=10, ratio_threshold=20, pred_signal="model")
    max_threshold = cr_two.pred_table_umaren["model"].max()
    gain_accuracy_model_umaren, gain_return_model_umaren, gain_pred_table_model_umaren = cr_two.for_calucurate_return_money(trade_type="umaren", pred_signal="model",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_model_umaren[max(gain_return_model_umaren.keys())]

    # グラフにする箇所を抽出する
    max_trade_count = X_test.index.nunique() * 2  # レースの数 * 2 "2"はとりまの値
    gain_return_diff_umaren_graph = {k: i for k, i in gain_return_diff_umaren.items() if max_trade_count > k}
    gain_return_model_umaren_graph = {k: i for k, i in gain_return_model_umaren.items() if max_trade_count > k}
    gain_accuracy_diff_umaren_graph = {k: i for k, i in gain_accuracy_diff_umaren.items() if max_trade_count > k}
    gain_accuracy_model_umaren_graph = {k: i for k, i in gain_accuracy_model_umaren.items() if max_trade_count > k}

    # シミュレーション結果をグラフにする　x軸:取引回数(回), y軸:回収率(%)
    graph_plot([gain_accuracy_diff_umaren_graph, gain_accuracy_model_umaren_graph], ["diff", "model"], "umaren_accuracy", "trade_count", "accuracy(%)")
    graph_plot([gain_return_diff_umaren_graph, gain_return_model_umaren_graph], ["diff", "model"], "umaren_return", "trade_count", "return(%)")

    # 6.馬単ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    # 6-1.オッズとモデル予測値の差から”うまい馬券”の購入をする買い方
    # key: 取引回数, items: 獲得金額 の辞書を取得
    print("--------------------------------馬単--------------------------------")
    print("---------------------diff-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_two.pred_table_umatan, bins=20, ratio_threshold=20, pred_signal="diff")
    max_threshold = cr_two.pred_table_umatan["diff"].max()
    gain_accuracy_diff_umatan, gain_return_diff_umatan, gain_pred_table_diff_umatan = cr_two.for_calucurate_return_money(trade_type="umatan", pred_signal="diff",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_diff_umatan[max(gain_return_diff_umatan.keys())]

    # 6-2.モデルからの予測値により勝率が高いものから購入する買い方
    print("---------------------model-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_two.pred_table_umatan, bins=20, ratio_threshold=20, pred_signal="model")
    max_threshold = cr_two.pred_table_umatan["model"].max()
    gain_accuracy_model_umatan, gain_return_model_umatan, gain_pred_table_model_umatan = cr_two.for_calucurate_return_money(trade_type="umatan", pred_signal="model",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_model_umatan[max(gain_return_model_umatan.keys())]

    # グラフにする箇所を抽出する
    max_trade_count = X_test.index.nunique() * 2  # レースの数 * 2 "2"はとりまの値
    gain_return_diff_umatan_graph = {k: i for k, i in gain_return_diff_umatan.items() if max_trade_count > k}
    gain_return_model_umatan_graph = {k: i for k, i in gain_return_model_umatan.items() if max_trade_count > k}
    gain_accuracy_diff_umatan_graph = {k: i for k, i in gain_accuracy_diff_umatan.items() if max_trade_count > k}
    gain_accuracy_model_umatan_graph = {k: i for k, i in gain_accuracy_model_umatan.items() if max_trade_count > k}

    # シミュレーション結果をグラフにする　x軸:取引回数(回), y軸:回収率(%)
    graph_plot([gain_accuracy_diff_umatan_graph, gain_accuracy_model_umatan_graph], ["diff", "model"], "umatan_accuracy", "trade_count", "accuracy(%)")
    graph_plot([gain_return_diff_umatan_graph, gain_return_model_umatan_graph], ["diff", "model"], "umatan_return", "trade_count", "return(%)")

    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------

    # optunaを使用してパラメータチューニングをする
    # 正解ラベル rank の作成(単勝)
    results_d_single = results_d.copy()
    # results_d_single.drop(["単勝", "人気"], axis=1, inplace=True)  適性回収率で単勝データが必要なためここではdropしない
    results_d_single["rank"] = results_d_single["着順"].map(lambda x: 1 if x == 1 else 0)
    # results_d_single["rank"] = results_d_single["着順"].map(lambda x: 1 if x < 3 else 0)  # 馬連
    results_d_single.drop(["着順"], axis=1, inplace=True)

    # 訓練データ、検証データ、テストデータに分割する
    train, test = train_test_split(results_d_single, 0.3)
    train, valid = train_test_split(train, 0.3)
    # 正解ラベルと説明変数に分ける
    X_train = train.drop(["rank", "date"], axis=1)
    y_train = train["rank"].copy()
    X_valid = valid.drop(["rank", "date"], axis=1)
    y_valid = valid["rank"].copy()
    X_test = test.drop(["rank", "date"], axis=1)
    y_test = test["rank"].copy()

    # Calucurate_Return classで回収率を算出するために"単勝, 人気"データが必要
    # "単勝, 人気"データを削除する前に必要だからX_test_add_tansho_ninnki変数を作成しておく
    X_test_add_tansho_ninnki = X_test.copy()
    X_train.drop(["単勝", "人気"], axis=1, inplace=True)
    X_test.drop(["単勝", "人気"], axis=1, inplace=True)

    import optuna.integration.lightgbm as lgb_o

    # パラメータチューニングするためのdatasetaを作成
    lgb_train = lgb_o.Dataset(X_train.values, y_train.values)
    lgb_valid = lgb_o.Dataset(X_valid.values, y_valid.values)

    # チューニングのためのparamsを作成
    params = {
              "objective": "binary",
              "random_state": 100,
    }

    # チューニング
    lgb_clf_X_train_o = lgb_o.train(params,
                            lgb_train,
                            valid_sets=(lgb_train, lgb_valid),
                            verbose_eval=100,
                            early_stopping_rounds=10)

    # チューニング後のパラメータの確認
    """
    各パラメータの説明をしておく
    {'objective': 'binary',
     'random_state': 100,
     'feature_pre_filter': False,
     'lambda_l1': 0.0,
     'lambda_l2': 0.0,
     'num_leaves': 6,
     'feature_fraction': 0.5,
     'bagging_fraction': 0.9639752945972611,
     'bagging_freq': 6,
     'min_child_samples': 20,
     'num_iterations': 1000,
     'early_stopping_round': 10}
    """
    lgb_clf_X_train_o.params

    # ハイパラメータ調整後の値をここにメモしておく
    del lgb_clf_X_train_o.params["num_iterations"], lgb_clf_X_train_o.params["early_stopping_round"]

    params_o = {'objective': 'binary',
                'random_state': 100,
                'feature_pre_filter': False,
                'lambda_l1': 0.11295238575624765,
                'lambda_l2': 1.1831583771042914e-08,
                'num_leaves': 103,
                'feature_fraction': 0.6839999999999999,
                'bagging_fraction': 0.4393321382892497,
                'bagging_freq': 7,
                'min_child_samples': 50
                }
    params_o = lgb_clf_X_train_o.params

    # チューニング後のパラメータで学習してみる

    # validなしで再度訓練データを作成
    train, test = train_test_split(results_d_single, 0.3)

    # 正解ラベルと説明変数に分ける
    X_train = train.drop(["rank", "date"], axis=1)
    y_train = train["rank"].copy()
    X_test = test.drop(["rank", "date"], axis=1)
    y_test = test["rank"].copy()
    X_train.drop(["単勝", "人気"], axis=1, inplace=True)
    X_test.drop(["単勝", "人気"], axis=1, inplace=True)

    lgb_clf_X_train_o = lgb.LGBMClassifier(**params_o)
    lgb_clf_X_train_o.fit(X_train.values, y_train.values)

    # 訓練データのroc
    # roc_graph_plot(y_train, lgb_clf_X_train_o.predict_proba(X_train)[:, 1])  # roc_graphをplot
    # print(f"roc_score:{roc_auc_score(y_train, lgb_clf_X_train_o.predict_proba(X_train)[:, 1])}")  # この値が大きいと過学習している(テストデータのrocと比較して判断する)

    # テストデータのroc
    # roc_graph_plot(y_test, lgb_clf_X_train_o.predict_proba(X_test)[:, 1])  # roc_graphをplot
    # print(f"roc_score:{roc_auc_score(y_test, lgb_clf_X_train_o.predict_proba(X_test)[:, 1])}")

    # features_importance(モデルがどの説明変数を重要視しているのか確認できる指標)
    # importance = pd.DataFrame({"features": X_test.columns, "importance": lgb_clf_X_train_o.feature_importances_})
    # importance.sort_values("importance", ascending=False)[0: 30]  # 重要な説明変数ほど上位に来ている

    print("---------------------------------------------------------------パラメーター調整後--------------------------------------------------------------")
    # 各馬券ごとに回収率を算出していくーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    # 1.三連単ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    # 1-1.オッズとモデル予測値の差から”うまい馬券”の購入をする買い方
    # key: 取引回数, items: 獲得金額 の辞書を取得
    print("--------------------------------三連単/三連複--------------------------------")
    cr_sann_o = Calucurate_Return(lgb_clf_X_train_o, GET_DATA_YEAR_LIST, X_test_add_tansho_ninnki, X_test, "sannrenntann_and_sannrennpuku", is_standard_scarer=False, is_use_pycaret=False)
    print("--------------------------------三連単--------------------------------")
    print("---------------------diff-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sann_o.pred_table_sannrenntann, bins=100, ratio_threshold=20, pred_signal="diff")
    max_threshold = cr_sann_o.pred_table_sannrenntann["diff"].max()
    gain_accuracy_diff_sannrenntann_o, gain_return_diff_sannrenntann_o, gain_pred_table_diff_sannrenntann_o = cr_sann_o.for_calucurate_return_money(trade_type="sannrenntann", pred_signal="diff",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_diff_sannrenntann_o[max(gain_return_diff_sannrenntann_o.keys())]

    # 1-2.モデルからの予測値により勝率が高いものから購入する買い方
    print("---------------------model-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sann_o.pred_table_sannrenntann, bins=100, ratio_threshold=20, pred_signal="model")
    max_threshold = cr_sann_o.pred_table_sannrenntann["model"].max()
    gain_accuracy_model_sannrenntann_o, gain_return_model_sannrenntann_o, gain_pred_table_model_sannrenntann_o = cr_sann_o.for_calucurate_return_money(trade_type="sannrenntann", pred_signal="model",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_model_sannrenntann_o[max(gain_return_model_sannrenntann_o.keys())]

    # グラフにする箇所を抽出する
    max_trade_count = X_test.index.nunique() * 2  # レースの数 * 2 "2"はとりまの値
    gain_return_diff_sannrenntann_o_graph = {k: i for k, i in gain_return_diff_sannrenntann_o.items() if max_trade_count > k}
    gain_return_model_sannrenntann_o_graph = {k: i for k, i in gain_return_model_sannrenntann_o.items() if max_trade_count > k}
    gain_accuracy_diff_sannrenntann_o_graph = {k: i for k, i in gain_accuracy_diff_sannrenntann_o.items() if max_trade_count > k}
    gain_accuracy_model_sannrenntann_o_graph = {k: i for k, i in gain_accuracy_model_sannrenntann_o.items() if max_trade_count > k}

    # シミュレーション結果をグラフにする　x軸:取引回数(回), y軸:回収率(%)
    graph_plot([gain_accuracy_diff_sannrenntann_o_graph, gain_accuracy_model_sannrenntann_o_graph], ["diff", "model"], "sannrenntann_o_accuracy", "trade_count", "accuracy(%)")
    graph_plot([gain_return_diff_sannrenntann_o_graph, gain_return_model_sannrenntann_o_graph], ["diff", "model"], "sannrenntann_o_return", "trade_count", "return(%)")

    # 2.三連複ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    # 2-1.オッズとモデル予測値の差から”うまい馬券”の購入をする買い方
    # key: 取引回数, items: 獲得金額 の辞書を取得
    print("--------------------------------三連複--------------------------------")
    print("---------------------diff-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sann_o.pred_table_sannrennpuku, bins=100, ratio_threshold=20, pred_signal="diff")
    max_threshold = cr_sann_o.pred_table_sannrennpuku["diff"].max()
    gain_accuracy_diff_sannrennpuku_o, gain_return_diff_sannrennpuku_o, gain_pred_table_diff_sannrennpuku_o = cr_sann_o.for_calucurate_return_money(trade_type="sannrennpuku", pred_signal="diff",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_diff_sannrennpuku_o[max(gain_return_diff_sannrennpuku_o.keys())]

    # 2-2.モデルからの予測値により勝率が高いものから購入する買い方
    print("---------------------model-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sann_o.pred_table_sannrennpuku, bins=100, ratio_threshold=20, pred_signal="model")
    max_threshold = cr_sann_o.pred_table_sannrennpuku["model"].max()
    gain_accuracy_model_sannrennpuku_o, gain_return_model_sannrennpuku_o, gain_pred_table_model_sannrennpuku_o = cr_sann_o.for_calucurate_return_money(trade_type="sannrennpuku", pred_signal="model",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_model_sannrennpuku_o[max(gain_return_model_sannrennpuku_o.keys())]

    # グラフにする箇所を抽出する
    max_trade_count = X_test.index.nunique() * 2  # レースの数 * 2 "2"はとりまの値
    gain_return_diff_sannrennpuku_o_graph = {k: i for k, i in gain_return_diff_sannrennpuku_o.items() if max_trade_count > k}
    gain_return_model_sannrennpuku_o_graph = {k: i for k, i in gain_return_model_sannrennpuku_o.items() if max_trade_count > k}
    gain_accuracy_diff_sannrennpuku_o_graph = {k: i for k, i in gain_accuracy_diff_sannrennpuku_o.items() if max_trade_count > k}
    gain_accuracy_model_sannrennpuku_o_graph = {k: i for k, i in gain_accuracy_model_sannrennpuku_o.items() if max_trade_count > k}

    # シミュレーション結果をグラフにする　x軸:取引回数(回), y軸:回収率(%)
    graph_plot([gain_accuracy_diff_sannrennpuku_o_graph, gain_accuracy_model_sannrennpuku_o_graph], ["diff", "model"], "sannrennpuku_o_accuracy", "trade_count", "accuracy(%)")
    graph_plot([gain_return_diff_sannrennpuku_o_graph, gain_return_model_sannrennpuku_o_graph], ["diff", "model"], "sannrennpuku_o_return", "trade_count", "return(%)")

    # 3.単勝ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    # 3-1.オッズとモデル予測値の差から”うまい馬券”の購入をする買い方
    # key: 取引回数, items: 獲得金額 の辞書を取得
    print("--------------------------------単勝/複勝--------------------------------")
    cr_sin_o = Calucurate_Return(lgb_clf_X_train_o, GET_DATA_YEAR_LIST, X_test_add_tansho_ninnki, X_test, "single_and_fukushou", is_standard_scarer=False, is_use_pycaret=False)
    print("--------------------------------単勝--------------------------------")
    print("---------------------diff-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sin_o.pred_table, bins=10, ratio_threshold=20, pred_signal="diff")
    max_threshold = cr_sin_o.pred_table["diff"].max()
    gain_accuracy_diff_single_o, gain_return_diff_single_o, gain_pred_table_diff_single_o = cr_sin_o.for_calucurate_return_money(trade_type="single", pred_signal="diff",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_diff_single_o[max(gain_return_diff_single_o.keys())]

    # 3-2.モデルからの予測値により勝率が高いものから購入する買い方
    print("---------------------model-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sin_o.pred_table, bins=5, ratio_threshold=20, pred_signal="model")
    max_threshold = cr_sin_o.pred_table["model"].max()
    gain_accuracy_model_single_o, gain_return_model_single_o, gain_pred_table_model_single_o = cr_sin_o.for_calucurate_return_money(trade_type="single", pred_signal="model",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_model_single_o[max(gain_return_model_single_o.keys())]

    # グラフにする箇所を抽出する
    max_trade_count = X_test.index.nunique() * 2  # レースの数 * 2 "2"はとりまの値
    gain_return_diff_single_o_graph = {k: i for k, i in gain_return_diff_single_o.items() if max_trade_count > k}
    gain_return_model_single_o_graph = {k: i for k, i in gain_return_model_single_o.items() if max_trade_count > k}
    gain_accuracy_diff_single_o_graph = {k: i for k, i in gain_accuracy_diff_single_o.items() if max_trade_count > k}
    gain_accuracy_model_single_o_graph = {k: i for k, i in gain_accuracy_model_single_o.items() if max_trade_count > k}

    # シミュレーション結果をグラフにする　x軸:取引回数(回), y軸:回収率(%)
    graph_plot([gain_accuracy_diff_single_o_graph, gain_accuracy_model_single_o_graph], ["diff", "model"], "single_o_accuracy", "trade_count", "accuracy(%)")
    graph_plot([gain_return_diff_single_o_graph, gain_return_model_single_o_graph], ["diff", "model"], "single_o_return", "trade_count", "return(%)")

    # 4.複勝ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    # 4-1.オッズとモデル予測値の差から”うまい馬券”の購入をする買い方
    # key: 取引回数, items: 獲得金額 の辞書を取得
    print("--------------------------------複勝--------------------------------")
    print("---------------------diff-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sin_o.pred_table, bins=5, ratio_threshold=20, pred_signal="diff")
    max_threshold = cr_sin_o.pred_table["diff"].max()
    gain_accuracy_diff_fukushou_o, gain_return_diff_fukushou_o, gain_pred_table_diff_fukushou_o = cr_sin_o.for_calucurate_return_money(trade_type="fukushou", pred_signal="diff", hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_diff_fukushou_o[max(gain_return_diff_fukushou_o.keys())]

    # 4-2.モデルからの予測値により勝率が高いものから購入する買い方
    print("---------------------model-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_sin_o.pred_table, bins=5, ratio_threshold=20, pred_signal="model")
    max_threshold = cr_sin_o.pred_table["model"].max()
    gain_accuracy_model_fukushou_o, gain_return_model_fukushou_o, gain_pred_table_model_fukushou_o = cr_sin_o.for_calucurate_return_money(trade_type="fukushou", pred_signal="model", hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_model_fukushou_o[max(gain_return_model_fukushou_o.keys())]

    # グラフにする箇所を抽出する
    max_trade_count = X_test.index.nunique() * 2  # レースの数 * 2 "2"はとりまの値
    gain_return_diff_fukushou_o_graph = {k: i for k, i in gain_return_diff_fukushou_o.items() if max_trade_count > k}
    gain_return_model_fukushou_o_graph = {k: i for k, i in gain_return_model_fukushou_o.items() if max_trade_count > k}
    gain_accuracy_diff_fukushou_o_graph = {k: i for k, i in gain_accuracy_diff_fukushou_o.items() if max_trade_count > k}
    gain_accuracy_model_fukushou_o_graph = {k: i for k, i in gain_accuracy_model_fukushou_o.items() if max_trade_count > k}

    # シミュレーション結果をグラフにする　x軸:取引回数(回), y軸:回収率(%)
    graph_plot([gain_accuracy_diff_fukushou_o_graph, gain_accuracy_model_fukushou_o_graph], ["diff", "model"], "fukushou_o_accuracy", "trade_count", "accuracy(%)")
    graph_plot([gain_return_diff_fukushou_o_graph, gain_return_model_fukushou_o_graph], ["diff", "model"], "fukushou_o_return", "trade_count", "return(%)")

    # 5.馬連ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    # 5-1.オッズとモデル予測値の差から”うまい馬券”の購入をする買い方
    # key: 取引回数, items: 獲得金額 の辞書を取得
    print("--------------------------------馬単/馬連--------------------------------")
    cr_two_o = Calucurate_Return(lgb_clf_X_train_o, GET_DATA_YEAR_LIST, X_test_add_tansho_ninnki, X_test, "umatan_and_umaren", is_standard_scarer=False, is_use_pycaret=False)
    print("--------------------------------馬連--------------------------------")
    print("---------------------diff-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_two_o.pred_table_umaren, bins=7, ratio_threshold=20, pred_signal="diff")
    max_threshold = cr_two_o.pred_table_umaren["diff"].max()
    gain_accuracy_diff_umaren_o, gain_return_diff_umaren_o, gain_pred_table_diff_umaren_o = cr_two_o.for_calucurate_return_money(trade_type="umaren", pred_signal="diff",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_diff_umaren_o[max(gain_return_diff_umaren_o.keys())]

    # 5-2.モデルからの予測値により勝率が高いものから購入する買い方
    print("---------------------model-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_two_o.pred_table_umaren, bins=7, ratio_threshold=20, pred_signal="model")
    max_threshold = cr_two_o.pred_table_umaren["model"].max()
    gain_accuracy_model_umaren_o, gain_return_model_umaren_o, gain_pred_table_model_umaren_o = cr_two_o.for_calucurate_return_money(trade_type="umaren", pred_signal="model",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_model_umaren_o[max(gain_return_model_umaren_o.keys())]

    # グラフにする箇所を抽出する
    max_trade_count = X_test.index.nunique() * 2  # レースの数 * 2 "2"はとりまの値
    gain_return_diff_umaren_o_graph = {k: i for k, i in gain_return_diff_umaren_o.items() if max_trade_count > k}
    gain_return_model_umaren_o_graph = {k: i for k, i in gain_return_model_umaren_o.items() if max_trade_count > k}
    gain_accuracy_diff_umaren_o_graph = {k: i for k, i in gain_accuracy_diff_umaren_o.items() if max_trade_count > k}
    gain_accuracy_model_umaren_o_graph = {k: i for k, i in gain_accuracy_model_umaren_o.items() if max_trade_count > k}

    # シミュレーション結果をグラフにする　x軸:取引回数(回), y軸:回収率(%)
    graph_plot([gain_accuracy_diff_umaren_o_graph, gain_accuracy_model_umaren_o_graph], ["diff", "model"], "umaren_o_accuracy", "trade_count", "accuracy(%)")
    graph_plot([gain_return_diff_umaren_o_graph, gain_return_model_umaren_o_graph], ["diff", "model"], "umaren_o_return", "trade_count", "return(%)")

    # 6.馬単ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
    # 6-1.オッズとモデル予測値の差から”うまい馬券”の購入をする買い方
    # key: 取引回数, items: 獲得金額 の辞書を取得
    print("--------------------------------馬単--------------------------------")
    print("---------------------diff-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_two_o.pred_table_umatan, bins=20, ratio_threshold=20, pred_signal="diff")
    max_threshold = cr_two_o.pred_table_umatan["diff"].max()
    gain_accuracy_diff_umatan_o, gain_return_diff_umatan_o, gain_pred_table_diff_umatan_o = cr_two_o.for_calucurate_return_money(trade_type="umatan", pred_signal="diff",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_diff_umatan_o[max(gain_return_diff_umatan_o.keys())]

    # 6-2.モデルからの予測値により勝率が高いものから購入する買い方
    print("---------------------model-----------------------")
    min_appropriate_threshold, n, bins_ = get_appropriate_thresholds(cr_two_o.pred_table_umatan, bins=20, ratio_threshold=20, pred_signal="model")
    max_threshold = cr_two_o.pred_table_umatan["model"].max()
    gain_accuracy_model_umatan_o, gain_return_model_umatan_o, gain_pred_table_model_umatan_o = cr_two_o.for_calucurate_return_money(trade_type="umatan", pred_signal="model",hit_back_money=10000, is_proper=False, max_threshold=max_threshold, min_threshold=min_appropriate_threshold, n_separate=500, lowest_trade_count=50)
    del gain_return_model_umatan_o[max(gain_return_model_umatan_o.keys())]

    # グラフにする箇所を抽出する
    max_trade_count = X_test.index.nunique() * 2  # レースの数 * 2 "2"はとりまの値
    gain_return_diff_umatan_o_graph = {k: i for k, i in gain_return_diff_umatan_o.items() if max_trade_count > k}
    gain_return_model_umatan_o_graph = {k: i for k, i in gain_return_model_umatan_o.items() if max_trade_count > k}
    gain_accuracy_diff_umatan_o_graph = {k: i for k, i in gain_accuracy_diff_umatan_o.items() if max_trade_count > k}
    gain_accuracy_model_umatan_o_graph = {k: i for k, i in gain_accuracy_model_umatan_o.items() if max_trade_count > k}

    # シミュレーション結果をグラフにする　x軸:取引回数(回), y軸:回収率(%)
    graph_plot([gain_accuracy_diff_umatan_o_graph, gain_accuracy_model_umatan_o_graph], ["diff", "model"], "umatan_o_accuracy", "trade_count", "accuracy(%)")
    graph_plot([gain_return_diff_umatan_o_graph, gain_return_model_umatan_o_graph], ["diff", "model"], "umatan_o_return", "trade_count", "return(%)")

    # グラフにする---------------------------------------------------------------------------------------------
    graph_title_single_list = ["single", "single_o"]
    graph_title_fukushou_list = ["fukushou", "fukushou_o"]
    graph_title_sannrenntann_list = ["sannrenntann", "sannrenntann_o"]
    graph_title_sannrennpuku_list = ["sannrennpuku", "sannrennpuku_o"]
    graph_title_umatan_list = ["umatan", "umatan_o"]
    graph_title_umaren_list = ["umaren", "umaren_o"]

    # accuracy(diff)のデータプロットのためのデータをリストにまとめる
    accuracy_diff_single_list = [gain_accuracy_diff_single_graph, gain_accuracy_diff_single_o_graph]
    accuracy_diff_fukushou_list = [gain_accuracy_diff_fukushou_graph, gain_accuracy_diff_fukushou_o_graph]
    accuracy_diff_sannrenntann_list = [gain_accuracy_diff_sannrenntann_graph, gain_accuracy_diff_sannrenntann_o_graph]
    accuracy_diff_sannrennpuku_list = [gain_accuracy_diff_sannrennpuku_graph, gain_accuracy_diff_sannrennpuku_o_graph]
    accuracy_diff_umatan_list = [gain_accuracy_diff_umatan_graph, gain_accuracy_diff_umatan_o_graph]
    accuracy_diff_umaren_list = [gain_accuracy_diff_umaren_graph, gain_accuracy_diff_umaren_o_graph]

    # accuracy(model)のデータプロットのためのデータをリストにまとめる
    accuracy_model_single_list = [gain_accuracy_model_single_graph, gain_accuracy_model_single_o_graph]
    accuracy_model_fukushou_list = [gain_accuracy_model_fukushou_graph, gain_accuracy_model_fukushou_o_graph]
    accuracy_model_sannrenntann_list = [gain_accuracy_model_sannrenntann_graph, gain_accuracy_model_sannrenntann_o_graph]
    accuracy_model_sannrennpuku_list = [gain_accuracy_model_sannrennpuku_graph, gain_accuracy_model_sannrennpuku_o_graph]
    accuracy_model_umatan_list = [gain_accuracy_model_umatan_graph, gain_accuracy_model_umatan_o_graph]
    accuracy_model_umaren_list = [gain_accuracy_model_umaren_graph, gain_accuracy_model_umaren_o_graph]

    # return(diff)のデータプロットのためのデータをリストにまとめる
    return_diff_single_list = [gain_return_diff_single_graph, gain_return_diff_single_o_graph]
    return_diff_fukushou_list = [gain_return_diff_fukushou_graph, gain_return_diff_fukushou_o_graph]
    return_diff_sannrenntann_list = [gain_return_diff_sannrenntann_graph, gain_return_diff_sannrenntann_o_graph]
    return_diff_sannrennpuku_list = [gain_return_diff_sannrennpuku_graph, gain_return_diff_sannrennpuku_o_graph]
    return_diff_umatan_list = [gain_return_diff_umatan_graph, gain_return_diff_umatan_o_graph]
    return_diff_umaren_list = [gain_return_diff_umaren_graph, gain_return_diff_umaren_o_graph]

    # return(model)のデータプロットのためのデータをリストにまとめる
    return_model_single_list = [gain_return_model_single_graph, gain_return_model_single_o_graph]
    return_model_fukushou_list = [gain_return_model_fukushou_graph, gain_return_model_fukushou_o_graph]
    return_model_sannrenntann_list = [gain_return_model_sannrenntann_graph, gain_return_model_sannrenntann_o_graph]
    return_model_sannrennpuku_list = [gain_return_model_sannrennpuku_graph, gain_return_model_sannrennpuku_o_graph]
    return_model_umatan_list = [gain_return_model_umatan_graph, gain_return_model_umatan_o_graph]
    return_model_umaren_list = [gain_return_model_umaren_graph, gain_return_model_umaren_o_graph]

    # accuracy のグラフ描写(各馬券ごとにまとめている)
    multi_graph_plot(accuracy_diff_single_list, accuracy_model_single_list, graph_title_single_list, graph_main_title=f"accuracy_single_{GET_DATA_YEAR}", x_label="trade_count", y_label="accuracy(%)", rows=1, columns=2, figsize_width=20, figsize_height=5)
    multi_graph_plot(accuracy_diff_fukushou_list, accuracy_model_fukushou_list, graph_title_fukushou_list, graph_main_title=f"accuracy_fukushou_{GET_DATA_YEAR}", x_label="trade_count", y_label="accuracy(%)", rows=1, columns=2, figsize_width=20, figsize_height=5)
    multi_graph_plot(accuracy_diff_sannrenntann_list, accuracy_model_sannrenntann_list, graph_title_sannrenntann_list, graph_main_title=f"accuracy_sannrenntann_{GET_DATA_YEAR}", x_label="trade_count", y_label="accuracy(%)", rows=1, columns=2, figsize_width=20, figsize_height=5)
    multi_graph_plot(accuracy_diff_sannrennpuku_list, accuracy_model_sannrennpuku_list, graph_title_sannrennpuku_list, graph_main_title=f"accuracy_sannrennpuku_{GET_DATA_YEAR}", x_label="trade_count", y_label="accuracy(%)", rows=1, columns=2, figsize_width=20, figsize_height=5)
    multi_graph_plot(accuracy_diff_umatan_list, accuracy_model_umatan_list, graph_title_umatan_list, graph_main_title=f"accuracy_umatan_{GET_DATA_YEAR}", x_label="trade_count", y_label="accuracy(%)", rows=1, columns=2, figsize_width=20, figsize_height=5)
    multi_graph_plot(accuracy_diff_umaren_list, accuracy_model_umaren_list, graph_title_umaren_list, graph_main_title=f"accuracy_umaren_{GET_DATA_YEAR}", x_label="trade_count", y_label="accuracy(%)", rows=1, columns=2, figsize_width=20, figsize_height=5)

    # return のグラフ描写(各馬券ごとにまとめている)
    multi_graph_plot(return_diff_single_list, return_model_single_list, graph_title_single_list, graph_main_title=f"return_single_{GET_DATA_YEAR}", x_label="trade_count", y_label="return(%)", rows=1, columns=2, figsize_width=20, figsize_height=5)
    multi_graph_plot(return_diff_fukushou_list, return_model_fukushou_list, graph_title_fukushou_list, graph_main_title=f"return_fukushou_{GET_DATA_YEAR}", x_label="trade_count", y_label="return(%)", rows=1, columns=2, figsize_width=20, figsize_height=5)
    multi_graph_plot(return_diff_sannrenntann_list, return_model_sannrenntann_list, graph_title_sannrenntann_list, graph_main_title=f"return_sannrenntann_{GET_DATA_YEAR}", x_label="trade_count", y_label="return(%)", rows=1, columns=2, figsize_width=20, figsize_height=5)
    multi_graph_plot(return_diff_sannrennpuku_list, return_model_sannrennpuku_list, graph_title_sannrennpuku_list, graph_main_title=f"return_sannrennpuku_{GET_DATA_YEAR}", x_label="trade_count", y_label="return(%)", rows=1, columns=2, figsize_width=20, figsize_height=5)
    multi_graph_plot(return_diff_umatan_list, return_model_umatan_list, graph_title_umatan_list, graph_main_title=f"return_umatan_{GET_DATA_YEAR}", x_label="trade_count", y_label="return(%)", rows=1, columns=2, figsize_width=20, figsize_height=5)
    multi_graph_plot(return_diff_umaren_list, return_model_umaren_list, graph_title_umaren_list, graph_main_title=f"return_umaren_{GET_DATA_YEAR}", x_label="trade_count", y_label="return(%)", rows=1, columns=2, figsize_width=20, figsize_height=5)
