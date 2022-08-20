import streamlit as st
import os, sys

@st.experimental_singleton
def installff():
  os.system('sbase install geckodriver')
  os.system('ln -s /home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')
  # os.system('ln -s /home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver')
  # sys.path.append('/home/appuser/venv/lib/python3.9/site-packages/selenium/webdriver/firefox.exe')
  sys.path.append('/home/appuser/venv/bin/geckodriver')

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

_ = installff()
firefoxOptions = Options()
firefoxOptions.add_argument("--headless")
driver = webdriver.Firefox(
    options=firefoxOptions,
    executable_path="/home/appuser/venv/bin/geckodriver",
)
driver.get('http://google.com/')

# memo----------------------------------------------
# from selenium import webdriver
# from selenium.webdriver import FirefoxOptions
# options = FirefoxOptions()
# options.add_argument("--headless")
# browser = webdriver.Firefox(options=options)
#
# browser.get('http://example.com')
# st.write(browser.page_source)
# memo----------------------------------------------
