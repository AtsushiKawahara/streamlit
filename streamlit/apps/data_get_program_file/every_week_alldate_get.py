# coding: UTF-8

"""
出馬テーブルをネット(https://race.netkeiba.com/top/)からスクレイピングしてAIが扱えるデータに加工するプログラム

(create_predict_table関数の実装内容)
1.seleniumを使ったスクレイピングにより出馬テーブルを取得
2.スクレイピングしたtableのデータ加工(データ型の変更、データの分割、過去成績データの追加、血統データの追加、ラベルエンコーディング)
3.モデルの読み込み(モデルは事前に用意しておく)
4.各馬券の予測テーブルを作成(ここで作成したデータをstreamlitアプリ上に表示する)

"""

import sys
import pandas as pd
import os
import datetime

# memo-------------------------------------------------------------------------
# hydrogen実行用
# streamlitリポジトリ用
FILE_PATH = "/Users/kawaharaatsushi/work_streamlit/streamlit/streamlit"
# dailydevリポジトリ用
FILE_PATH = "/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit"
sys.path.append(FILE_PATH)
FILE_PATH_BASE_DATA = FILE_PATH + '/data/base_data'
sys.path.append(FILE_PATH_BASE_DATA)
FILE_PATH_FIT_DATA = FILE_PATH + '/data/fit_data'
sys.path.append(FILE_PATH_FIT_DATA)
# memo-------------------------------------------------------------------------

# このファイルの場所を取得してパスを通す(別階層のファイルから呼び出しても変化しない)
# 参考)__file__: ~/streamlit/app.py
# path: ~/streamlit/
FILE_PATH = '/'.join(os.path.abspath(__file__).split('/')[:-2])+'/'
sys.path.append(FILE_PATH)
# path: ~/streamlit/data/base_data
FILE_PATH_BASE_DATA = '/'.join(os.path.abspath(__file__).split('/')[:-2])+'/data/base_data'
sys.path.append(FILE_PATH_BASE_DATA)
# path: ~/streamlit/data/fit_data
FILE_PATH_FIT_DATA = '/'.join(os.path.abspath(__file__).split('/')[:-2])+'/data/fit_data'
sys.path.append(FILE_PATH_FIT_DATA)

# 学習データとして使用する年を設定
GET_DATA_YEAR_LIST = [2017, 2018, 2019, 2020, 2021, 2022]  # 取得したい年を指定

# 自作関数のimport
from apps.create_model import Preprocessing_Horse_Result
from apps.create_model import Calucurate_Return
from apps.create_model import Return
from apps.create_model import Data_Processer
from apps.create_model import Result_Table
from apps.create_model import labelencoder_ped
from apps.data_get_program_file.race_result_get import scrape_race_result
from apps.data_get_program_file.horse_info_get import scrape_race_info
from apps.data_get_program_file.horse_ped_get import scrape_horse_ped
from apps.data_get_program_file.return_table_get import scrape_return_tables
from apps.data_get_program_file.horse_result_get import scrape_horse_result
from apps.data_get_program_file.scraping_shutuba_table import Start_Horse_Table
from functions.date_split_plot_pickle_functions import load_pickle
from functions.date_split_plot_pickle_functions import save_pickle


def main():
    # memo---------------------------------------------------------------------
    # def create_predict_table(target_date, is_real_time, table_type):
    # target_date = "9月18日"
    # is_real_time = True
    # table_type = "shutuba_table"
    # memo---------------------------------------------------------------------

    """
    現在の日時から取得する出馬テーブルを取得する日にちを決定する
    指定の仕方は以下のとおり
    日曜日18時〜土曜日18時 → target_weekday = 5(土曜日)
    土曜日18時〜日曜日18時 → target_weekday = 6(土曜日)
    上記の設定に指定している理由は・・・
    - 基本的にレースがあるのは土日のみのため、指定日は土曜日か日曜日のみ
    - レースは当日の16時頃が最終レースのことが多い
    → それまでは当日の出馬テーブルを取得する必要があるため安全側するため境界を18時としている
    """
    # 新たに取得する日のレースidを取得------------------------------------------------
    now_date = datetime.datetime.now().date()  # 現在日付 ex)datetime.date(2022, 11, 3)
    now_time = datetime.datetime.now().time()  # 現在時刻 ex)datetime.time(23, 37, 22, 964472)
    current_weekday = now_date.weekday()  # 曜日を取得(0:月曜日 1:火曜日 ... 6:日曜日)

    # 直近の土曜日の日付を取得
    target_date_at_saturday = (now_date - datetime.timedelta(days=(current_weekday + 2))).strftime('%Y%m%d')
    target_date_at_saturday
    # 直近の日曜日の日付を取得
    target_date_at_sunday = (now_date - datetime.timedelta(days=(current_weekday + 1))).strftime('%Y%m%d')
    target_date_at_sunday

    print(f"target_date{target_date_at_saturday}")
    # 機能確認ようにとりあえず上の部分はとりまコメントアウト
    # target_date = "20221105"  # とりまの値

    # 取得したいレース日を取得(直近の土日のレース日を取得)
    sht = Start_Horse_Table()
    sht.start_up_chromedriver()  # chromedriverを起動

    # 直近の土曜日・日曜日に開催されたレースのIDを取得
    race_id_list_saturday = sht.scrape_specified_date_race_id(target_date_at_saturday)
    race_id_list_sunday = sht.scrape_specified_date_race_id(target_date_at_sunday)

    # 土日のrace_id を結合
    race_id_list = race_id_list_saturday + race_id_list_sunday

    # レース結果(race_result)の取得------------------------------------------------
    race_results_dict = scrape_race_result(race_id_list)

    # レースデータのインデックスをレースIDに変更
    for key in race_results_dict.keys():
        race_results_dict[key].index = [key]*len(race_results_dict[key])
    race_results_dict

    # dictに格納したdfを全て結合する
    pd_race_results_new = pd.concat([race_results_dict[key] for key in race_results_dict.keys()], sort=False)
    pd_race_results_new

    # 新たに取得したレース結果を取得済みのbase_dataに追記する
    GET_DATA_YEAR = target_date_at_saturday[0:4]  # 指定した日の書式は ex)"20221010"のように年月日のため最初の4文字の年を取得
    pd_race_results_base = load_pickle(FILE_PATH_BASE_DATA, f"pd_race_results_{GET_DATA_YEAR}")  # base_data
    pd_race_results = pd.concat([pd_race_results_base, pd_race_results_new], axis=0)  # 新しいデータをベースデータを結合
    pd_race_results_new.shape
    pd_race_results_base.shape
    pd_race_results.shape

    # race_resultsデータを保存
    save_pickle(FILE_PATH_BASE_DATA, f"pd_race_results_{GET_DATA_YEAR}", pd_race_results.sort_index())  # レース結果を保存

    # レース情報(race_info)を取得--------------------------------------------------
    # race_infos_dict = scrape_race_info_soup(race_id_list)
    race_infos_dict = scrape_race_info(race_id_list)
    # dictに格納したdfを全て結合する
    pd_race_infos = pd.DataFrame(race_infos_dict).T
    # 途中まで読み込みファイルがある場合は、新たに読み込んだデータと結合しておく
    pd_race_infos_base = load_pickle(FILE_PATH_BASE_DATA, f"pd_race_infos_{GET_DATA_YEAR}")  # 途中まで抽出しているファイルを読み込み
    pd_race_infos_base.shape
    pd_race_infos.shape
    pd_race_infos = pd.concat([pd_race_infos_base, pd_race_infos], axis=0)
    pd_race_infos.shape

    save_pickle(FILE_PATH_BASE_DATA, f"pd_race_infos_{GET_DATA_YEAR}", pd_race_infos)

    # return_tablesの取得--------------------------------------------------------
    pd_return_tables_dict = scrape_return_tables(race_id_list)  # レースごとの予想が的中した場合の報酬の情報を取得

    for key in pd_return_tables_dict.keys():
        pd_return_tables_dict[key].index = [key]*len(pd_return_tables_dict[key])

    pd_return_tables_new = pd.concat([pd_return_tables_dict[key] for key in pd_return_tables_dict])
    pd_return_tables_new

    pd_return_tables_base = load_pickle(FILE_PATH_BASE_DATA, f"pd_return_tables_{GET_DATA_YEAR}")  # 途中まで抽出しているファイルを読み込み
    pd_return_tables_test = pd.concat([pd_return_tables_base, pd_return_tables_new], axis=0)

    pd_return_tables_test["race_id"] = pd_return_tables_test.index  # columnにrace_idを一時的に追加(次の処理で重複行を削除するときに消したらいけない行を消さないため)
    pd_return_tables_test = pd_return_tables_test.drop_duplicates().drop("race_id", axis=1).copy()  # 重複行の削除とhorse_idの列を削除

    # return_tablesの保存
    save_pickle(FILE_PATH_BASE_DATA, f"pd_return_tables_{GET_DATA_YEAR}", pd_return_tables_test)

    # 馬の過去成績(horse_result)を取得---------------------------------------------
    # レースに出馬した馬のhorse_idを取得
    horse_id_list = pd_race_results_new["horse_id"].sort_values().unique()

    horse_results_dict = scrape_horse_result(horse_id_list)
    horse_results_dict

    # 馬ごとのレース成績データをレースIDに変更
    for key in horse_results_dict.keys():
        horse_results_dict[key].index = [key]*len(horse_results_dict[key])

    # dictに格納したdfを全て結合する
    pd_horse_results_new = pd.concat([horse_results_dict[key] for key in horse_results_dict.keys()], sort=False)

    # 途中まで読み込みファイルがある場合は、新たに読み込んだデータと結合しておく
    pd_horse_results_base = load_pickle(FILE_PATH_BASE_DATA, f"pd_horse_results_{GET_DATA_YEAR}")  # 途中まで抽出しているファイルを読み込み
    pd_horse_results = pd.concat([pd_horse_results_base, pd_horse_results_new], axis=0)
    pd_horse_results_base.shape
    pd_horse_results_new.shape
    pd_horse_results.shape

    # 馬の過去成績(horse_result)を保存
    # ベースデータと重複するデータがあれば削除して保存(drop_duplicates)
    save_pickle(FILE_PATH_BASE_DATA, f"pd_horse_results_{GET_DATA_YEAR}", pd_horse_results.drop_duplicates().sort_index())  # レース結果を保存

    # 血統データ(ped_datas)を取得--------------------------------------------------
    ped_datas_dict = scrape_horse_ped(horse_id_list)

    # dictに格納したdfを全て結合する
    pd_ped_datas = pd.concat([ped_datas_dict[key] for key in ped_datas_dict.keys()], axis=1).T
    pd_ped_datas_new = pd_ped_datas.add_prefix("ped_")

    # 途中まで読み込みファイルがある場合は、新たに読み込んだデータと結合しておく
    pd_ped_datas_base = load_pickle(FILE_PATH_BASE_DATA, f"pd_ped_datas_{GET_DATA_YEAR}")  # 途中まで抽出しているファイルを読み込み
    pd_ped_datas = pd.concat([pd_ped_datas_base, pd_ped_datas_new], axis=1)
    pd_ped_datas_base.shape
    pd_ped_datas_new.shape
    pd_ped_datas.shape

    # 馬ごとの成績データを保存
    save_pickle(FILE_PATH_BASE_DATA, f"pd_ped_datas_{GET_DATA_YEAR}", pd_ped_datas.sort_index())  # レース結果を保存


if __name__ == '__main__':
    main()
