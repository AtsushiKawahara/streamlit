# coding:utf-8
# 必要なライブラリのimport
import streamlit as st
# import urllib3
import json
from selenium.webdriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
# import requests
# from bs4 import BeautifulSoup
import os
import subprocess as sp
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome import service as fs

st.write("pathの確認")
# print(f"pwd:{os.system('pwd')}")
# print(f"cd ~ :{os.system('cd ..')}")
# print(f"pwd:{os.system('pwd')}")
print(f"os.getcwd:{os.getcwd()}")
# print(os.system('find . -type f -name "*hrome*river*"'))
print(os.system('find ../../. -type f -name "*hrome*"'))
# print(os.system('find ../../. -type f -name "*"'))
press_button = st.button("出馬テーブル取得開始")
# ボタンが押されたときに実行される箇所
if press_button:

    url = 'https://example.com/'
    # url = "https://race.netkeiba.com/top/"
    # urllib3によるサーバーへのhttpリクエスト
    # st.write("urllib3によるhttpリクエスト")
    # http = urllib3.PoolManager()
    # r = http.request('GET', url)
    # st.write(r.status)
    # st.write(json.dumps(dict(r.headers), ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': ')))
    # st.write(r.data.decode('ascii', errors="ignore"))
    # request(サードパーティー)によるhttpリクエスト
    # st.write("requestによるhttpリクエスト")
    # response = requests.get(url)
    # st.write(response)
    # st.write(response.text)
    # BeautifulSoupによるデータ取得(requestsにより取得したデータから抽出)
    # st.write("beautifulsoupによるhttpリクエスト")
    # soup = BeautifulSoup(response.text)
    # st.write(soup.find_all("body"))
    # seleniumnによる通信
    # chrome_driver_path = "../.././home/appuser/.wdm/drivers/chromedriver/linux64/106.0.5249/chromedriver"
    # chrome_driver_path = "/home/appuser/.wdm/drivers/chromedriver/linux64/106.0.5249/chromedriver"
    # chrome_driver_path = "/home/appuser/.wdm/drivers/chromedriver"
    # chrome_driver_path = "./benchmark-auto/chromedriver.exe"
    # chrome_driver_path = "../.././app/streamlit/benchmark-auto/chromedriver.exe"
    # chrome_driver_path = os.getcwd() + "\chromedriver.exe"
    # chrome_driver_path = "/app/streamlit/benchmark-auto/chromedriver.exe"
    # CHROMEDRIVER  = "/app/streamlit/sample_python/chromedriver"
    options = ChromeOptions()  # ここで拡張機能を本来は設定するけど今回は省略
    options.add_argument("--headless")
    # driver = webdriver.Remote(command_executor="http://127.0.0.1:4444/wd/hub", options=options)
    # driver = Chrome(ChromeDriverManager().install(), options=options)
    # driver = Chrome(chrome_driver_path, options=options)
    # print(CHROMEDRIVER)

    CHROMEDRIVER = ChromeDriverManager().install()
    chrome_service = fs.Service(executable_path=CHROMEDRIVER)
    driver = Chrome(service=chrome_service, options=options)
    # driver = Chrome(ChromeDriverManager().install(), options=options)
    driver.get(url)
    driver.close()
