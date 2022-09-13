# coding: UTF-8

"""
multiapp.pyの実装内容
→create_predict_table関数が実行される

(create_predict_table関数の実装内容)
1.seleniumを使ったshutuba_table or result_tableのスクレイピング(どちらをスクレイピングするかはtable_typeで指定する)
2.スクレイピングしたtableのデータ加工(データ型の変更、データの分割、過去成績データの追加、血統データの追加、ラベルエンコーディング)
3.モデルの読み込み(モデルは事前に用意しておく)
4.各馬券の予測テーブルを作成
"""

import sys
import pandas as pd
import os

# memo-------------------------------------------------------------------------
# # pathの設定(hydrogen用)
# FILE_PATH = "/Users/kawaharaatsushi/work_streamlit/streamlit/streamlit"
# sys.path.append(FILE_PATH)
# FILE_PATH_BASE_DATA = FILE_PATH + '/data/base_data'
# sys.path.append(FILE_PATH_BASE_DATA)
# FILE_PATH_FIT_DATA = FILE_PATH + '/data/fit_data'
# sys.path.append(FILE_PATH_FIT_DATA)
# memo-------------------------------------------------------------------------

# このファイルの場所を取得してパスを通す(別階層のファイルから呼び出しても変化しない)
# 参考)__file__: ~/streamlit/app.py
# path: ~/streamlit/
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-1])+'/')
# path: ~/streamlit/data/base_data
FILE_PATH_BASE_DATA = '/'.join(os.path.abspath(__file__).split('/')[:-1])+'/data/base_data'
sys.path.append(FILE_PATH_BASE_DATA)
# path: ~/streamlit/data/fit_data
FILE_PATH_FIT_DATA = '/'.join(os.path.abspath(__file__).split('/')[:-1])+'/data/fit_data'
sys.path.append(FILE_PATH_FIT_DATA)

# 学習データとして使用する年を設定
GET_DATA_YEAR_LIST = [2017, 2018, 2019, 2020, 2021, 2022]  # 取得したい年を指定

# 自作関数のimport
from apps.predict import Preprocessing_Horse_Result
from apps.predict import Calucurate_Return
from apps.predict import Return
from apps.predict import Data_Processer
from apps.predict import Result_Table
from apps.predict import labelencoder_ped
from apps.data_get_program_file.horse_ped_get import scrape_horse_ped
from apps.data_get_program_file.horse_result_get import scrape_horse_result
from apps.scraping_shutuba_table import Start_Horse_Table
from functions.data_proessing import load_pickle
from functions.data_proessing import save_pickle


def create_predict_table(target_date, is_real_time, table_type):

    # 1.学習データの読み込み-------------------------------------------------------

    # 学習時に使用したデータを用意(ラベルエンコーディング等をするときに必要なため)
    # 馬ごとの成績データの処理(過去データの着順・賞金の平均を説明変数にするために使用する)
    hr = Preprocessing_Horse_Result.load_pickle(GET_DATA_YEAR_LIST)

    # 2.出馬テーブルを取得---------------------------------------------------------

    # 取得したいレース日を指定してスクレイピングする
    # 出馬テーブルのスクレイピング(target_dateにより取得するレースの日付を指定する方法)
    sht = Start_Horse_Table()  # 予測したいレースのrace_id_listを渡す
    sht.scrape_by_ChromeDriverManager_at_target_date(target_date, is_real_time, table_type)  # 予測したいレースのrace_id_listを渡す

    # memo---------------------------------------------------------------------
    # 出馬テーブルのスクレイピング(race_id_listを作成して出馬テーブルを取得する方法)
    # race_id_list = ["202201010411", "202201010604"]
    # sht.scrape_by_ChromeDriverManager_at_race_id_list(race_id_list, table_type="shutuba_table", )  # 予測したいレースのrace_id_listを渡す
    # memo---------------------------------------------------------------------

    save_pickle(FILE_PATH_FIT_DATA, "race_info_dict.pickle", sht.race_info_dict)  # レースごとのレース名、出走時刻などのデータdictを保存しておく(key: race_id)
    save_pickle(FILE_PATH_FIT_DATA, "shutuba_tables.pickle", sht.shutuba_tables)

    # 3.出馬テーブルの加工(データ型の変更やデータの分割など)------------------------------

    sht.preprocessing_shutuba_table()

    # 3-1.過去成績データを追加------------------------------------------------------

    # データベースに過去成績データが存在しない馬のhorse_idを取得
    not_exist_horse_results_horse_id_list = sht.data_p[~sht.data_p["horse_id"].isin(hr.pd_horse_results.index)]["horse_id"]

    # データベースに過去成績データが存在しない馬のhorse_idがある場合の処理
    if len(not_exist_horse_results_horse_id_list) != 0:

        # 過去成績データがないhorse_idの過去成績データをスクレイピングする
        pd_horse_results_dict_add = scrape_horse_result(not_exist_horse_results_horse_id_list)

        # 馬ごとのレース成績データをレースIDに変更
        for key in pd_horse_results_dict_add.keys():
            pd_horse_results_dict_add[key].index = [key]*len(pd_horse_results_dict_add[key])

        if len(pd_horse_results_dict_add) > 0:

            # スクレイピングしてきた過去成績データをhorse_idをindexにして結合する(dict → dataframe)
            pd_horse_results_add = pd.concat([pd_horse_results_dict_add[key] for key in pd_horse_results_dict_add.keys()], axis=0)

            # 新たに取得した過去成績データを加工してデータベースと同じ形状にする
            hr_add = Preprocessing_Horse_Result(pd_horse_results_add)
            hr_add.pd_horse_results.shape  # 新たに取得した過去成績データ

            # データベースに新たにスクレイピングした過去成績データを結合する
            hr.pd_horse_results = pd.concat([hr.pd_horse_results, hr_add.pd_horse_results], axis=0)
        else:
            # 新たに取得できたデータがない場合(ネット上にもその馬の過去成績データが存在していない場合→まだ勝ったことがない馬等)
            pass

    sht.merge_n_samples(hr)  # 過去成績データからレースの賞金データを出馬表に追加する

    # 3-2.血統データを追加---------------------------------------------------------

    # 血統データをlabelencodeするためのclassをインスタンス化
    la = labelencoder_ped.load_pickle(GET_DATA_YEAR_LIST)

    # 重複して取得してしまっている血統データを削除する(年度ごとに血統データを取得すると重複データが存在するため)
    la.pd_ped_datas["horse_id"] = la.pd_ped_datas.index  # horse_idが同一の行を削除するため一時的にcolumnにhorse_idを加える

    # horse_idが同一データの行を削除する(この処理をするためにhorse_idをcolumnに加える)
    # subsetに指定したcolumnで重複行を探す
    # keep:重複した場合にlastの行を削除する
    la.pd_ped_datas = la.pd_ped_datas.drop_duplicates(subset=["horse_id"], keep="last")
    la.pd_ped_datas.drop(["horse_id"], axis=1, inplace=True)

    # 血統データがデータベースに存在しない馬のhorse_idを取得
    not_exist_pd_ped_datas_horse_id_list = sht.data_r[~sht.data_r["horse_id"].isin(la.pd_ped_datas.index)]["horse_id"]

    # 血統データがデータベースに存在しない馬のhorse_idがある場合の処理
    if len(not_exist_pd_ped_datas_horse_id_list) != 0:

        # 血統データがないhorse_idの血統データをスクレイピングする
        pd_ped_datas_dict_add = scrape_horse_ped(not_exist_pd_ped_datas_horse_id_list)
        pd_ped_datas_add = pd.concat([pd_ped_datas_dict_add[key] for key in pd_ped_datas_dict_add.keys()], axis=1).T  # スクレイピングしてきたデータをhorse_idをindexにして結合する(dict → dataframe)
        pd_ped_datas_add = pd_ped_datas_add.add_prefix("ped_")

        # 血統データベースに新たにスクレイピングした血統データを結合する
        la.pd_ped_datas = pd.concat([la.pd_ped_datas, pd_ped_datas_add], axis=0)

    la.labelencode_ped()  # 血統データをラベルエンコーディング

    sht.merge_ped_data(la.pd_ped_datas_la)  # pd_ped_datas_laは血統データのデータベースをラベルエンコディングしたやつ

    # 必要な行も削除している可能性があるため確認しておく
    if len(sht.data_ped) == len(sht.data_r):
        print("不要行削除完了(必要な行は削除していない)")
    else:
        raise Exception("please check sht.data_ped len")

    # 3-3.ラベルエンコーディング-----------------------------------------------------

    # 学習したときのエンコーディングデータを読み込む(同一データは同一ラベルに変換するため)
    le_horse_id = load_pickle(FILE_PATH_FIT_DATA, "le_horse_id.pickle")
    le_jockey_id = load_pickle(FILE_PATH_FIT_DATA, "le_jockey_id.pickle")
    le_trainer_id = load_pickle(FILE_PATH_FIT_DATA, "le_trainer_id.pickle")
    weather_unique = load_pickle(FILE_PATH_FIT_DATA, "weather_unique.pickle")
    race_type_unique = load_pickle(FILE_PATH_FIT_DATA, "race_type_unique.pickle")
    ground_state_unique = load_pickle(FILE_PATH_FIT_DATA, "ground_state_unique.pickle")
    gender_categories_unique = load_pickle(FILE_PATH_FIT_DATA, "gender_categories_unique.pickle")
    # data_ped = load_pickle(FILE_PATH_FIT_DATA, "data_ped.pickle")

    # ラベルエンコーディングを実行
    sht.labelencoder_id(le_horse_id, le_jockey_id,
                        le_trainer_id, weather_unique,
                        race_type_unique, ground_state_unique,
                        gender_categories_unique)

    # 3-4.説明変数の形状を整える(不要なデータは削除)
    X = sht.data_id.drop(["date"], axis=1)
    X_add_tansho_ninnki = X.copy()  # Calucurate_Return classで"うまい馬券"の予測テーブルを作成するために"単勝, 人気"データが必要なため"X_add_tansho_ninnki"変数を作成しておく
    X.drop(["単勝", "人気"], axis=1, inplace=True)

    # 学習済みのモデルを読み込み
    model = load_pickle(FILE_PATH_FIT_DATA, "lgb_clf_X.pickle")

    # 三連単・三連複の予測テーブルの作成
    cr_sann = Calucurate_Return(model, GET_DATA_YEAR_LIST, X_add_tansho_ninnki, X, "sannrenntann_and_sannrennpuku", is_standard_scarer=False, is_use_pycaret=False)
    save_pickle(FILE_PATH_FIT_DATA, "predict_table_sannrenntann.pickle", cr_sann.pred_table_sannrenntann)  # 三連単予測テーブル保存
    save_pickle(FILE_PATH_FIT_DATA, "predict_table_sannrennpuku.pickle", cr_sann.pred_table_sannrennpuku)  # 三連複予測テーブル保存

    # 単勝・複勝の予測テーブルの作成
    cr_single = Calucurate_Return(model, GET_DATA_YEAR_LIST, X_add_tansho_ninnki, X, "single_and_fukushou", is_standard_scarer=False, is_use_pycaret=False)
    save_pickle(FILE_PATH_FIT_DATA, "predict_table.pickle", cr_single.pred_table)  # 単勝・複勝(単勝と複勝は同じ予測テーブル)予測テーブル保存

    # 馬単・馬蓮の予測テーブルの作成
    cr_two = Calucurate_Return(model, GET_DATA_YEAR_LIST, X_add_tansho_ninnki, X, "umatan_and_umaren", is_standard_scarer=False, is_use_pycaret=False)
    save_pickle(FILE_PATH_FIT_DATA, "predict_table_umatan.pickle", cr_two.pred_table_umatan)  # 馬単予測テーブル保存
    save_pickle(FILE_PATH_FIT_DATA, "predict_table_umaren.pickle", cr_two.pred_table_umaren)  # 馬連予測テーブル保存
