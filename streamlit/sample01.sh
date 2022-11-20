#!/bin/bash
# cd /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/
# /Users/kawaharaatsushi/.pyenv/shims/python3 /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/apps/data_get_program_file/race_result_get.py >> /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/cron.log 2>&1
# /Users/kawaharaatsushi/.pyenv/shims/python3 /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/apps/data_get_program_file/every_week_alldate_get.py >> /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/cron.log 2>&1

cd /Users/kawaharaatsushi/work_streamlit/streamlit/streamlit/
/Users/kawaharaatsushi/.pyenv/shims/python3 /Users/kawaharaatsushi/work_streamlit/streamlit/streamlit/hello.py >> /Users/kawaharaatsushi/work_streamlit/streamlit/streamlit/cron.log 2>&1
# 追加データの取得
/Users/kawaharaatsushi/.pyenv/shims/python3 /Users/kawaharaatsushi/work_streamlit/streamlit/streamlit/apps/data_get_program_file/every_week_alldate_get.py >> /Users/kawaharaatsushi/work_streamlit/streamlit/streamlit/cron.log 2>&1
# モデルの更新
/Users/kawaharaatsushi/.pyenv/shims/python3 /Users/kawaharaatsushi/work_streamlit/streamlit/streamlit/apps/create_model.py >> /Users/kawaharaatsushi/work_streamlit/streamlit/streamlit/cron.log 2>&1

# 新たに更新したbase_dataをgitにupする-----------------------------------------------
# commit メッセージの作成
ct="$(date +%Y:%m:%d-%H:%M:%S)"

git add .
git commit -m $ct
git push
