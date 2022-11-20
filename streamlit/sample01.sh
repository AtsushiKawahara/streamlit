#!/bin/bash
# cd /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/
# /Users/kawaharaatsushi/.pyenv/shims/python3 /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/apps/data_get_program_file/race_result_get.py >> /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/cron.log 2>&1
# /Users/kawaharaatsushi/.pyenv/shims/python3 /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/apps/data_get_program_file/every_week_alldate_get.py >> /Users/kawaharaatsushi/work2/daily-dev/atsushi/競馬予測/streamlit/cron.log 2>&1

cd /Users/kawaharaatsushi/work_streamlit/streamlit/streamlit/
echo "$tmp"
echo "$ct"
/Users/kawaharaatsushi/.pyenv/shims/python3 /Users/kawaharaatsushi/work_streamlit/streamlit/streamlit/hello.py >> /Users/kawaharaatsushi/work_streamlit/streamlit/streamlit/cron.log 2>&1
/Users/kawaharaatsushi/.pyenv/shims/python3 /Users/kawaharaatsushi/work_streamlit/streamlit/streamlit/apps/data_get_program_file/every_week_alldate_get.py >> /Users/kawaharaatsushi/work_streamlit/streamlit/streamlit/cron.log 2>&1
