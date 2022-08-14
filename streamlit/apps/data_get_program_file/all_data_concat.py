# coding:utf-8
"""
pd_results
pd_horse_results
pd_ped_datas
pd_race_infos
pd_return_tables_test

上記の各年データを全て結合してpd_○○_all.pickleファイルとして保存する関数
"""
# 必要な関数のインポート
import pandas as pd
import sys
import os

# pathの設定

# memo-------------------------------------------------------------------------
# pathの設定(hydrogen用)
# FILE_PATH = "/Users/kawaharaatsushi/work2/daily-dev/atsushi/memo/競馬予想AI/streamlit_for_predict_race_result/streamlit"
# sys.path.append(FILE_PATH)
# FILE_PATH_BASE_DATA = FILE_PATH + '/data/base_data'
# sys.path.append(FILE_PATH_BASE_DATA)
# memo-------------------------------------------------------------------------

# 取得する年を指定
# GET_DATA_YEAR = 2019
# このファイルの場所を取得してパスを通す(別階層のファイルから呼び出しても変化しない)
# 参考)__file__: ~/streamlit/apps/data_get_program_file/horse_ped_get.py
# path: ~/streamlit/data_get_program_file
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-1])+'/')
# path: ~/streamlit
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-2])+'/')
# path: ~/streamlit/data/base_data
FILE_PATH_BASE_DATA = '/'.join(os.path.abspath(__file__).split('/')[:-2])+'/data/base_data'
sys.path.append(FILE_PATH_BASE_DATA)

# 自作関数のインポート
from functions.data_proessing import load_pickle
from functions.data_proessing import save_pickle
from functions.data_proessing import preprocessing


def concat_old_new(df_old, df_new):
    """
    df_old(df_newに存在しないデータ)とdf_newを結合する
    """
    df_old_non_exist_new = df_old[~df_old.index.isin(df_new.index)]
    df_concat = pd.concat([df_old_non_exist_new, df_new])
    return df_concat


def main():
    # レース結果の結合(race_infoも結合しておく)----------------------------------------
    # データの読み込み
    GET_DATA_YEAR = "2017"
    pd_race_results = load_pickle(FILE_PATH_BASE_DATA, f"pd_race_results_{GET_DATA_YEAR}")  # レース結果
    pd_race_infos_tmp = load_pickle(FILE_PATH_BASE_DATA, f"pd_race_infos_{GET_DATA_YEAR}")  # レース情報
    pd_race_infos = pd.DataFrame(pd_race_infos_tmp).T
    # レース結果とレース情報を結合する
    pd_results = pd.merge(pd_race_results, pd_race_infos, how="inner", left_index=True, right_index=True)

    # ベースとして作成した2017年にそれぞれの年のデータを結合する
    GET_DATA_YEAR_LIST = ["2018", "2019", "2020", "2021"]

    for GET_DATA_YEAR in GET_DATA_YEAR_LIST:
        pd_race_results = load_pickle(FILE_PATH_BASE_DATA, f"pd_race_results_{GET_DATA_YEAR}")  # レース結果
        pd_race_infos_tmp = load_pickle(FILE_PATH_BASE_DATA, f"pd_race_infos_{GET_DATA_YEAR}")  # レース情報
        pd_race_infos = pd.DataFrame(pd_race_infos_tmp).T
        # レース結果とレース情報を結合する
        pd_results_add_infos = pd.merge(pd_race_results, pd_race_infos, how="inner", left_index=True, right_index=True)

        pd_results = pd.concat([pd_results, pd_results_add_infos])

    save_pickle(FILE_PATH_BASE_DATA, "pd_race_results_all", pd_results)

    # --------------------------------------------------------------------------

    # horse_resultsの結合--------------------------------------------------------
    # データの読み込み
    GET_DATA_YEAR = "2017"
    pd_horse_results = load_pickle(FILE_PATH_BASE_DATA, f"pd_horse_results_{GET_DATA_YEAR}")  # レース結果
    pd_horse_results
    # ベースとして作成した2018年にそれぞれの年のデータを結合する
    GET_DATA_YEAR_LIST = ["2018", "2019", "2020", "2021"]

    for GET_DATA_YEAR in GET_DATA_YEAR_LIST:
        pd_horse_results_new = load_pickle(FILE_PATH_BASE_DATA, f"pd_horse_results_{GET_DATA_YEAR}")  # レース結果

        pd_horse_results = concat_old_new(pd_horse_results, pd_horse_results_new)

    save_pickle(FILE_PATH_BASE_DATA, "pd_horse_results_all", pd_horse_results)

    # --------------------------------------------------------------------------

    # ped_datasの結合------------------------------------------------------------
    # データの読み込み
    GET_DATA_YEAR = "2017"
    pd_ped_datas = load_pickle(FILE_PATH_BASE_DATA, f"pd_ped_datas_{GET_DATA_YEAR}")  # レース結果

    # ベースとして作成した2018年にそれぞれの年のデータを結合する
    GET_DATA_YEAR_LIST = ["2018", "2019", "2020", "2021"]

    for GET_DATA_YEAR in GET_DATA_YEAR_LIST:
        pd_ped_datas_new = load_pickle(FILE_PATH_BASE_DATA, f"pd_ped_datas_{GET_DATA_YEAR}")  # レース結果

        pd_ped_datas = concat_old_new(pd_ped_datas, pd_ped_datas_new)

    save_pickle(FILE_PATH_BASE_DATA, "pd_ped_datas_all", pd_ped_datas)

    # --------------------------------------------------------------------------

    # return_tables_testの結合------------------------------------------------------------
    # データの読み込み
    GET_DATA_YEAR = "2017"
    pd_return_tables_test = load_pickle(FILE_PATH_BASE_DATA, f"pd_return_tables_test_{GET_DATA_YEAR}")  # レース結果

    # ベースとして作成した2018年にそれぞれの年のデータを結合する
    GET_DATA_YEAR_LIST = ["2018", "2019", "2020", "2021"]

    for GET_DATA_YEAR in GET_DATA_YEAR_LIST:
        pd_return_tables_test_new = load_pickle(FILE_PATH_BASE_DATA, f"pd_return_tables_test_{GET_DATA_YEAR}")  # レース結果

        pd_return_tables_test = concat_old_new(pd_return_tables_test, pd_return_tables_test_new)

    save_pickle(FILE_PATH_BASE_DATA, "pd_return_tables_test_all", pd_return_tables_test)

    # --------------------------------------------------------------------------


if __name__ == '__main__':
    main()
