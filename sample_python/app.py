# coding:utf-8

# 必要なライブラリのimport
import streamlit as st
import urllib3
import json

http = urllib3.PoolManager()
r = http.request('GET', 'https://example.com/')

st.write(json.dumps(dict(r.headers), ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': ')))
