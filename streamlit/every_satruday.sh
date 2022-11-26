#!/bin/bash
# cd /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/
# /Users/kawaharaatsushi/.pyenv/shims/python3 /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/apps/data_get_program_file/race_result_get.py >> /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/cron.log 2>&1
# /Users/kawaharaatsushi/.pyenv/shims/python3 /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/apps/data_get_program_file/every_week_alldate_get.py >> /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/cron.log 2>&1

cd /Users/kawaharaatsushi/work_streamlit/streamlit/streamlit/
# レース予測テーブルの作成（レース当日の0時になったら予測を開始する・・・天気情報が当日にならないとサイトに記載されないため）
/Users/kawaharaatsushi/.pyenv/shims/python3 /Users/kawaharaatsushi/work_streamlit/streamlit/streamlit/apps/create_predict_table.py >> /Users/kawaharaatsushi/work_streamlit/streamlit/streamlit/cron.log 2>&1

# 更新したbase_data・model・予測テーブルをgitにupする-----------------------------------------------

# commit メッセージの作成
ct="$(date +%Y:%m:%d-%H:%M:%S)"

# gitへ更新したデータupする(add, commit, push)
# git add .
# git commit -m $ct
# git push
