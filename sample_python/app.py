# coding:utf-8

# 必要なライブラリのimport
import streamlit as st
import urllib3
import json
from selenium.webdriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

press_button = st.button("出馬テーブル取得開始")

# ボタンが押されたときに実行される箇所
if press_button:
    url = 'https://example.com/'
    http = urllib3.PoolManager()
    r = http.request('GET', url)
    st.write(json.dumps(dict(r.headers), ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': ')))

    url = "https://race.netkeiba.com/top/"
    options = ChromeOptions()  # ここで拡張機能を本来は設定するけど今回は省略
    options.add_argument("--headless")
    # driver = webdriver.Remote(command_executor="http://selenium:4444/wd/hub", options=options)
    driver = Chrome(ChromeDriverManager().install(), options=options)
    driver.get(url)
    driver.close()
