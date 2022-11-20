# coding:utf-8

import requests
from bs4 import BeautifulSoup
import re
import sys
from tqdm import tqdm
import time
import pandas as pd
import numpy as np
import os

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

# 取得する年を指定
# GET_DATA_YEAR = 2019


def scrape_race_info(race_id_list):
    """
    BeautifulSoupで必要データを競馬サイトから抽出する
    """
    race_info = {}  # 必要なデータを取り出すための辞書の作成

    # 各race_idでそのレースの情報を取り出していく
    # race_id = "201907020611"
    for race_id in tqdm(race_id_list):
        try:
            url = "https://db.netkeiba.com/race/" + race_id
            html = requests.get(url)
            html.encoding = 'EUC-JP'
            soup = BeautifulSoup(html.text, "html.parser")
            # htmlから欲しい箇所を抽出
            text_1 = soup.find("div", attrs={"class": "data_intro"}).find_all("p")[0].text + \
                soup.find("div", attrs={"class": "data_intro"}).find_all("p")[1].text
            info_1 = re.findall(r'\w+', text_1)
            # text = info_1[1]
            # text
            # text_1 = re.findall(r'(.*)(?=m)', text)[0]
            # text_1
            # re.findall(r'(?<=周)(.*)', text_1)[0]
            # print(len(info_1), info_1)

            info_dict = {}
            for text in info_1:
                if text in ['芝', 'ダート']:  # raceが芝かダートなのかを判別
                    info_dict['race_type'] = text
                if text in ['曇', '晴', '雨', '小雨', '小雪', '雪']:  # 天気を判別
                    info_dict['weather'] = text
                if 'm' in text:  # レースの距離を抽出
                    if '周' in text:
                        text_1 = re.findall(r'(.*)(?=m)', text)[0]  # 'm'より前の文字列を取得
                        text_2 = re.findall(r'(?<=周)(.*)', text_1)[0]  # '周'より後の文字列を取得
                        info_dict["course_len"] = text_2
                    else:
                        info_dict["course_len"] = re.findall(r'\d+', text)[0]
                if text in ['稍重', '良', '重', '不良']:  # グラウンドの状態
                    info_dict["ground_state"] = text
                if '障' in text:  # 障害物があるかないか判別
                    info_dict['race_type'] = text
                if '年' in text:  # レースの日付を判別
                    info_dict['date'] = text
            race_info[race_id] = info_dict
            time.sleep(1)
        except IndexError as e:  # urlが存在しないurlの場合は飛ばす
            print(f"IndexError:{e}:{race_id}")
            time.sleep(1)
            continue
        except AttributeError as e:  # urlが存在しないurlの場合は飛ばす
            print(f"AttributeError:{e}:{race_id}")
            time.sleep(1)
            continue
        except Exception as e:  # 処理が途中で終わってしまったら、そこまで取得したリストを返す
            print(e)
            break

    return race_info


def main():
    # horse_info(馬場の種類・状態、　天気、　レース距離等)の取得
    # GET_DATA_YEAR = "2018"

    GET_DATA_YEAR_LIST = ["2017", "2018", "2019", "2020", "2021", "2022"]
    for GET_DATA_YEAR in GET_DATA_YEAR_LIST:
        print(f"--------------------------------{GET_DATA_YEAR}--------------------------------------------")

        # race_id_listを作成するためにrace_resultデータを読み込む
        pd_race_results = load_pickle(FILE_PATH_BASE_DATA, f"pd_race_results_{GET_DATA_YEAR}")

        # race_resultsからレースidを取得
        race_id_list = pd_race_results.index.unique()
        print(f"race_id_list数:{len(race_id_list)}")

        # 途中まで読み込んでいるpd_race_infos_"year"ファイルがある場合は残りのhorse_idの結果を読み込む
        if os.path.isfile(f"{FILE_PATH_BASE_DATA}/pd_race_infos_{GET_DATA_YEAR}"):
            print(f"pd_race_infos_{GET_DATA_YEAR}　is exist")

            pd_race_infos_load = load_pickle(FILE_PATH_BASE_DATA, f"pd_race_infos_{GET_DATA_YEAR}")  # 途中まで抽出しているファイルを読み込み
            drop_lists = pd_race_infos_load.index.unique()  # 取得済みのrace_idのリストを作成
            race_id_list = np.array([race_id for race_id in race_id_list if not race_id in drop_lists])  # まだ読み込みが完了していないhorse_idを取得
            print(f"残:{len(race_id_list)}")
            if len(race_id_list) == 0:  # 読み込みが完了している年はスキップする
                print(f"{GET_DATA_YEAR}年はデータ取得完了しているためスキップ")
                continue
        else:
            pass

        # GET_DATA_YEARで指定した年のrace_info(レース情報)を取得　
        race_infos_dict = scrape_race_info(race_id_list)

        if len(race_infos_dict) == 0:
            # 新たに取得したデータがない場合(すでに全データを取得できている場合)は保存はしない
            print(f"{GET_DATA_YEAR} DATA is already completed ")
            pass
        else:
            # dictに格納したdfを全て結合する
            pd_race_infos = pd.DataFrame(race_infos_dict).T
            # 途中まで読み込みファイルがある場合は、新たに読み込んだデータと結合しておく
            if os.path.isfile(f"{FILE_PATH_BASE_DATA}/pd_race_infos_{GET_DATA_YEAR}"):
                pd_race_infos = pd.concat([pd_race_infos_load, pd_race_infos], axis=0)
            else:
                pass

        save_pickle(FILE_PATH_BASE_DATA, f"pd_race_infos_{GET_DATA_YEAR}", pd_race_infos)


if __name__ == '__main__':
    main()
