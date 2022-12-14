# coding: UTF-8

# """
# app.pyの実装内容
# →streamlitの表示画面の作成
#
# - 予測するレースをstreamlit画面上で選択して選択した日の予測結果と出馬テーブルを表示する
# - 各馬券の予測結果を表示できる
# - 勝率が高い馬券からsortできる
# """

import streamlit as st
import sys
import seaborn as sns
import os
from datetime import date
from datetime import datetime

# memo-------------------------------------------------------------------------
# # pathの設定(hydrogen用)
# # streamlitリポジトリ用
# FILE_PATH = "/Users/kawaharaatsushi/work_streamlit/streamlit/streamlit"
# # dailydevリポジトリ用
# FILE_PATH = "/Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit"
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

# 自作関数のimport
from apps import create_predict_table
from functions.date_split_plot_pickle_functions import load_pickle


def get_swap_dict(d):
    """
    逆引き辞書を作成できる関数(dictのkeyとvalueを入れ替えたdictを返す)
    """
    return {v: k for k, v in d.items()}


def main():

    # タイトル表示
    st.title("AIによる競馬予測")

    # あらかじめ予測したレースの日付・予測結果を更新した時刻を読み込む
    # 予測したレースの年月日
    target_date = datetime.strptime(load_pickle(FILE_PATH_FIT_DATA, 'target_date.pickle'), "%Y%m%d")  # pickleに保存している年月日の８桁の数字をdatetime型に変換
    target_year = target_date.year  # 年
    target_month = target_date.month  # 月
    target_day = target_date.day  # 日
    # 予測レース情報をスクレイピングした時間
    scraping_time = load_pickle(FILE_PATH_FIT_DATA, "scrape_time.pickle")
    scraping_hour = scraping_time.hour  # 時
    scraping_minute = scraping_time.minute  # 分

    # 予測したレース日を表示
    st.write(f"レース予測日:{target_year}年{target_month}月{target_day}日")
    st.write(f"更新時間:{scraping_hour}時{scraping_minute}分")

    # "is_table_view"のkeyが存在しない場合に実行される(=一度しか実行されない)
    # st.sessionstateに格納する変数は際読み込みされても保持される
    if "is_table_view" not in st.session_state:
        st.session_state["is_table_view"] = None

    # このボタンを押すとtarget_dataで指定している日の出馬テーブルの取得を開始する
    press_button = st.button("予測結果表示")

    # ボタンが押されたときに実行される箇所
    if press_button:

        # 出馬テーブル・予測テーブルを表示する信号をONにする
        st.session_state["is_table_view"] = True

    # スクレイピングした出馬テーブル・予測テーブルをstreamlit上に表示する
    # target_dateが変更されるとst.session_state["is_table_view"]がsession_change関数が実行されFalseになるため非表示となる
    if st.session_state["is_table_view"]:

        # 1.targe_dateで指定した日の全レースの各馬券の出馬テーブル・予測テーブルを読み込み

        pred_tables_sannrenntann = load_pickle(FILE_PATH_FIT_DATA, "predict_table_sannrenntann.pickle").reset_index().sort_values("race_id")  # 三連単予測テーブル
        pred_tables_sannrennpuku = load_pickle(FILE_PATH_FIT_DATA, "predict_table_sannrennpuku.pickle").reset_index().sort_values("race_id")  # 三連複予測テーブル
        pred_tables_umatan = load_pickle(FILE_PATH_FIT_DATA, "predict_table_umatan.pickle").reset_index().sort_values("race_id")  # 馬単予測テーブル
        pred_tables_umaren = load_pickle(FILE_PATH_FIT_DATA, "predict_table_umaren.pickle").reset_index().sort_values("race_id")  # 馬蓮予測テーブル
        pred_tables = load_pickle(FILE_PATH_FIT_DATA, "predict_table.pickle").reset_index().sort_values("race_id")  # 単勝・複勝予測テーブル
        race_info_dict = load_pickle(FILE_PATH_FIT_DATA, "race_info_dict.pickle")  # レース情報 key: race_id, value: race_info の辞書
        shutuba_tables = load_pickle(FILE_PATH_FIT_DATA, "shutuba_tables.pickle").reset_index().sort_values("index")  # 出馬テーブル

        # 2.表示のためのcolumn名の変更(わかりやすい名称へ変更)

        pred_tables_sannrenntann = pred_tables_sannrenntann.rename(columns={"umaban_pred": "馬券", "model": "モデル予測", "odd": "オッズ予測", "diff": "うまい馬券"})
        pred_tables_sannrennpuku = pred_tables_sannrennpuku.rename(columns={"umaban_pred": "馬券", "model": "モデル予測", "odd": "オッズ予測", "diff": "うまい馬券"})
        pred_tables_umatan = pred_tables_umatan.rename(columns={"umaban_pred": "馬券", "model": "モデル予測", "odd": "オッズ予測", "diff": "うまい馬券"})
        pred_tables_umaren = pred_tables_umaren.rename(columns={"umaban_pred": "馬券", "model": "モデル予測", "odd": "オッズ予測", "diff": "うまい馬券"})
        pred_tables = pred_tables.rename(columns={"umaban_pred": "馬券", "model": "モデル予測", "odd": "オッズ予測", "diff": "うまい馬券"})
        shutuba_tables = shutuba_tables.rename(columns={"index": "race_id"})

        # 3.dataframeの着色設定

        cm = sns.light_palette("blue", as_cmap=True)

        # 4.表示するレースを選択できるように race_info(レース名 + 出走時刻)のセレクトボックスを作成
        race_info_list = list(race_info_dict.values())  # レース名＋出走時刻をlistにしておく(selectbox表示用)
        race_info = st.selectbox(
            "予測結果を表示するレースを選択してください",
            (race_info_list))

        # 上のセレクトボックスで選択したレースのrace_idを特定するための辞書を作成
        # key: race_info, value: race_id の辞書を作成
        race_info_dict_swap = get_swap_dict(race_info_dict)

        # 作成した辞書からrace_idを取得
        race_id = race_info_dict_swap[race_info]  # selectboxにより選択したレースのrace_idを取得

        # 5.予測テーブルの表示する

        # それぞれの馬券の該当レースのみを抽出
        pred_table_sannrenntann = pred_tables_sannrenntann[pred_tables_sannrenntann["race_id"] == race_id].sort_values("うまい馬券", ascending=False).reset_index(drop=True)
        pred_table_sannrennpuku = pred_tables_sannrennpuku[pred_tables_sannrennpuku["race_id"] == race_id].sort_values("うまい馬券", ascending=False).reset_index(drop=True)
        pred_table_umatan = pred_tables_umatan[pred_tables_umatan["race_id"] == race_id].sort_values("うまい馬券", ascending=False).reset_index(drop=True)
        pred_table_umaren = pred_tables_umaren[pred_tables_umaren["race_id"] == race_id].sort_values("うまい馬券", ascending=False).reset_index(drop=True)
        pred_table = pred_tables[pred_tables["race_id"] == race_id].sort_values("うまい馬券", ascending=False).reset_index(drop=True)
        shutuba_tables["馬番"] = shutuba_tables["馬番"].astype(int)
        shutuba_table = shutuba_tables[shutuba_tables["race_id"] == race_id].sort_values("馬番").reset_index(drop=True)

        # 不要なcolumnの削除
        pred_table_sannrenntann.drop(["race_id", "オッズ予測"], axis=1, inplace=True)  # 予測結果表示するときにはrace_idの列は不要のため削除する
        pred_table_sannrennpuku.drop(["race_id", "オッズ予測"], axis=1, inplace=True)  # 予測結果表示するときにはrace_idの列は不要のため削除する
        pred_table_umatan.drop(["race_id", "オッズ予測"], axis=1, inplace=True)  # 予測結果表示するときにはrace_idの列は不要のため削除する
        pred_table_umaren.drop(["race_id", "オッズ予測"], axis=1, inplace=True)  # 予測結果表示するときにはrace_idの列は不要のため削除する
        pred_table.drop(["単勝", "race_id", "オッズ予測"], axis=1, inplace=True)  # 予測結果表示するときにはrace_idの列は不要のため削除する
        shutuba_table.drop(["race_id"], axis=1, inplace=True)  # 出馬テーブルするときにはrace_idの列は不要のため削除する

        # race_infoの表示
        st.write(f"●レース名:{race_info}")

        # 出馬テーブルを実際に載せているサイトのurlを作成
        url = f"https://race.netkeiba.com/race/shutuba.html?race_id={race_id}&rf=race_list"

        # steramlitに必要情報を記載
        st.write("●公式サイトの出馬テーブルはこちらから")
        st.write(f"レース情報公式HPはこちら{url}")
        st.write("●出馬テーブル")
        st.dataframe(shutuba_table.sort_values("馬番"))
        st.write("●各馬券の予測テーブル")

        # 表示したい馬券の予測テーブルを選択できるradioを作成
        baken_type = st.radio("表示する馬券タイプを選択してください",
                              ("三連単", "三連複", "馬単", "馬連", "単勝・複勝"))

        # radioで選択した馬券の予測テーブルが表示される
        if baken_type == "三連単":
            st.dataframe(pred_table_sannrenntann.sort_values("うまい馬券", ascending=False).style.background_gradient(cmap=cm, axis=0))
        if baken_type == "三連複":
            st.dataframe(pred_table_sannrennpuku.sort_values("うまい馬券", ascending=False).style.background_gradient(cmap=cm, axis=0))
        if baken_type == "馬単":
            st.dataframe(pred_table_umatan.sort_values("うまい馬券", ascending=False).style.background_gradient(cmap=cm, axis=0))
        if baken_type == "馬連":
            st.dataframe(pred_table_umaren.sort_values("うまい馬券", ascending=False).style.background_gradient(cmap=cm, axis=0))
        if baken_type == "単勝・複勝":
            st.dataframe(pred_table.sort_values("うまい馬券", ascending=False).style.background_gradient(cmap=cm, axis=0))


if __name__ == '__main__':
    main()
