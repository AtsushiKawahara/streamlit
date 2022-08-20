import streamlit as st
import os, sys

@st.experimental_singleton
def installff():
  os.system('sbase install geckodriver')
  os.system('ln -s /home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')
  # os.system('ln -s /home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver')
  # sys.path.append('/home/appuser/venv/lib/python3.9/site-packages/selenium/webdriver/firefox.exe')
  sys.path.append('/home/appuser/venv/bin/geckodriver')

# from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver import FirefoxOptions
# from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

# memo----------------------------------------------
# https://discuss.streamlit.io/t/issue-with-selenium-on-a-streamlit-app/11563/25?page=2
# _ = installff()
# firefoxOptions = Options()
# firefoxOptions.add_argument("--headless")
# # FirefoxBinary(r'/home/appuser/venv/lib/python3.9/site-packages/selenium/webdriver/firefox.exe')
# firefoxOptions.binary_location = r'/home/appuser/venv/lib/python3.9/site-packages/selenium/webdriver/firefox.exe'
# driver = webdriver.Firefox(
#     options=firefoxOptions,
#     executable_path="/home/appuser/venv/bin/geckodriver",
# )
# driver.get('http://google.com/')
# memo----------------------------------------------

# memo----------------------------------------------
# streamllit example1) https://discuss.streamlit.io/t/selenium-web-scraping-on-streamlit-cloud/21820/5
# from selenium import webdriver
# from selenium.webdriver import FirefoxOptions
# options = FirefoxOptions()
# options.add_argument("--headless")
# browser = webdriver.Firefox(options=options)
#
# browser.get('http://example.com')
# st.write(browser.page_source)
# memo----------------------------------------------

# memo----------------------------------------------
# streamllit example2) https://discuss.streamlit.io/t/selenium-web-scraping-on-streamlit-cloud/21820/5
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

URL = ""
TIMEOUT = 20

st.title("Test Selenium")

firefoxOptions = Options()
firefoxOptions.add_argument("--headless")
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(
    options=firefoxOptions,
    service=service,
)
driver.get(URL)
# memo----------------------------------------------
