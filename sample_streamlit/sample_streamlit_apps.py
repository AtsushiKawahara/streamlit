import streamlit as st
import os, sys

@st.experimental_singleton
def installff():
  os.system('sbase install geckodriver')
  os.system('ln -s /home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')
  print('pwd-------------------------------------------')
  print(os.system('pwd'))
  print(os.system('ls'))
  print('pwd-------------------------------------------')
  # os.system('ln -s /home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver')
  sys.path.append('/home/appuser/venv/lib/python3.9/site-packages/selenium/webdriver/firefox.exe')
  sys.path.append('/home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver')
  sys.path.append('/home/appuser/venv/bin/geckodriver')

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

_ = installff()
options = Options()
# options = FirefoxOptions()
options.binary = FirefoxBinary(r'/home/appuser/venv/lib/python3.9/site-packages/selenium/webdriver/firefox.exe')
options.add_argument("--headless")
# options.binary_location = r'/home/appuser/venv/lib/python3.9/site-packages/selenium/webdriver/firefox'
# options.binary_location = r'/home/appuser/venv/lib/python3.9/site-packages/selenium/webdriver/firefox'
driver = webdriver.Firefox(executable_path=r'/home/appuser/venv/bin/geckodriver', options=options)
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
