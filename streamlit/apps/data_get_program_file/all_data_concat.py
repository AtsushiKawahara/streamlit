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

# pathの設定
FILE_PATH = '/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測'
sys.path.append(FILE_PATH)
FILE_PATH3 = '/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/function'
sys.path.append(FILE_PATH3)
FILE_PATH_DATA = '/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/data'
sys.path.append(FILE_PATH_DATA)

# 自作関数のインポート
from data_proessing import load_pickle
from data_proessing import save_pickle
from data_proessing import re_specific_text_get
from data_proessing import train_test_split
from data_proessing import roc_graph_plot
from data_proessing import preprocessing


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
    pd_race_results = load_pickle(FILE_PATH_DATA, f"pd_race_results_{GET_DATA_YEAR}")  # レース結果
    pd_race_infos_tmp = load_pickle(FILE_PATH_DATA, f"pd_race_infos_{GET_DATA_YEAR}")  # レース情報
    pd_race_infos = pd.DataFrame(pd_race_infos_tmp).T
    # レース結果とレース情報を結合する
    pd_results = pd.merge(pd_race_results, pd_race_infos, how="inner", left_index=True, right_index=True)

    # ベースとして作成した2017年にそれぞれの年のデータを結合する
    GET_DATA_YEAR_LIST = ["2018", "2019", "2020", "2021"]

    for GET_DATA_YEAR in GET_DATA_YEAR_LIST:
        pd_race_results = load_pickle(FILE_PATH_DATA, f"pd_race_results_{GET_DATA_YEAR}")  # レース結果
        pd_race_infos_tmp = load_pickle(FILE_PATH_DATA, f"pd_race_infos_{GET_DATA_YEAR}")  # レース情報
        pd_race_infos = pd.DataFrame(pd_race_infos_tmp).T
        # レース結果とレース情報を結合する
        pd_results_add_infos = pd.merge(pd_race_results, pd_race_infos, how="inner", left_index=True, right_index=True)

        pd_results = pd.concat([pd_results, pd_results_add_infos])

    save_pickle(FILE_PATH_DATA, "pd_race_results_all", pd_results)

    # --------------------------------------------------------------------------

    # horse_resultsの結合--------------------------------------------------------
    # データの読み込み
    GET_DATA_YEAR = "2017"
    pd_horse_results = load_pickle(FILE_PATH_DATA, f"pd_horse_results_{GET_DATA_YEAR}")  # レース結果
    pd_horse_results
    # ベースとして作成した2018年にそれぞれの年のデータを結合する
    GET_DATA_YEAR_LIST = ["2018", "2019", "2020", "2021"]

    for GET_DATA_YEAR in GET_DATA_YEAR_LIST:
        pd_horse_results_new = load_pickle(FILE_PATH_DATA, f"pd_horse_results_{GET_DATA_YEAR}")  # レース結果

        pd_horse_results = concat_old_new(pd_horse_results, pd_horse_results_new)

    save_pickle(FILE_PATH_DATA, "pd_horse_results_all", pd_horse_results)

    # --------------------------------------------------------------------------

    # ped_datasの結合------------------------------------------------------------
    # データの読み込み
    GET_DATA_YEAR = "2017"
    pd_ped_datas = load_pickle(FILE_PATH_DATA, f"pd_ped_datas_{GET_DATA_YEAR}")  # レース結果

    # ベースとして作成した2018年にそれぞれの年のデータを結合する
    GET_DATA_YEAR_LIST = ["2018", "2019", "2020", "2021"]

    for GET_DATA_YEAR in GET_DATA_YEAR_LIST:
        pd_ped_datas_new = load_pickle(FILE_PATH_DATA, f"pd_ped_datas_{GET_DATA_YEAR}")  # レース結果

        pd_ped_datas = concat_old_new(pd_ped_datas, pd_ped_datas_new)

    save_pickle(FILE_PATH_DATA, "pd_ped_datas_all", pd_ped_datas)

    # --------------------------------------------------------------------------

    # return_tables_testの結合------------------------------------------------------------
    # データの読み込み
    GET_DATA_YEAR = "2017"
    pd_return_tables_test = load_pickle(FILE_PATH_DATA, f"pd_return_tables_test_{GET_DATA_YEAR}")  # レース結果

    # ベースとして作成した2018年にそれぞれの年のデータを結合する
    GET_DATA_YEAR_LIST = ["2018", "2019", "2020", "2021"]

    for GET_DATA_YEAR in GET_DATA_YEAR_LIST:
        pd_return_tables_test_new = load_pickle(FILE_PATH_DATA, f"pd_return_tables_test_{GET_DATA_YEAR}")  # レース結果

        pd_return_tables_test = concat_old_new(pd_return_tables_test, pd_return_tables_test_new)

    save_pickle(FILE_PATH_DATA, "pd_return_tables_test_all", pd_return_tables_test)

    # --------------------------------------------------------------------------


if __name__ == '__main__':
    main()
