
# memo----------------------------------------------
# import streamlit as st
# import os, sys
# @st.experimental_singleton
# def installff():
#   os.system('sbase install geckodriver')
#   os.system('ln -s /home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')
#   st.write(os.system('ls /home/appuser/venv/bin/geckodriver'))
#   # st.write(os.system('ls /home/appuser/venv/bin/geckodriver/geckodriver-v0.31.0-linux64.tar.gz'))
#   # os.system('ln -s /home/appuser/venv/lib/python3.9/site-packages/seleniumbase/drivers/geckodriver')
#   # sys.path.append('/home/appuser/venv/lib/python3.9/site-packages/selenium/webdriver/firefox.exe')
#   sys.path.append('/home/appuser/venv/bin/geckodriver')
#   sys.path.append('/home/appuser/venv/bin/geckodriver/geckodriver-v0.31.0-linux64.tar.gz')

# from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver import FirefoxOptions
# from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
# memo----------------------------------------------

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
# from selenium import webdriver
# from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from webdriver_manager.firefox import GeckoDriverManager
#
# URL = ""
# TIMEOUT = 20
#
# st.title("Test Selenium")
# st.write(os.system('ls /home/appuser/venv/bin/geckodriver'))
# st.write(os.system('ls /home/appuser/venv/bin/geckodriver/geckodriver-v0.31.0-linux64.tar.gz'))
#
# firefoxOptions = Options()
# firefoxOptions.add_argument("--headless")
# service = Service(GeckoDriverManager().install())
# driver = webdriver.Firefox(
#     options=firefoxOptions,
#     service=service,
#     executable_path='/home/appuser/venv/bin/geckodriver/geckodriver-v0.31.0-linux64.tar.gz/geckodriver.exe',
# )
# driver.get(URL)
# memo----------------------------------------------

# memo----------------------------------------------
# https://github.com/Franky1/Streamlit-Selenium/blob/main/streamlit_app.py

import glob
import os

import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

st.write(os.system("ls /home/appuser/venv/lib/python3.9/site-packages/selenium/webdriver/firefox"))
# st.write(os.system("find /home/appuser/venv/lib/python3.9/site-packages/selenium/webdriver/firefox"))
st.write(os.system("grep -r .exe /home/"))
# st.write(os.system("ls /home/appuser/venv/lib/python3.9/site-packages/selenium/webdriver"))

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-features=NetworkService")
options.add_argument("--window-size=1920x1080")
options.add_argument("--disable-features=VizDisplayCompositor")


def delete_selenium_log():
    if os.path.exists('selenium.log'):
        os.remove('selenium.log')


def show_selenium_log():
    if os.path.exists('selenium.log'):
        with open('selenium.log') as f:
            content = f.read()
            st.code(content)


# not required anymore:
# def get_chromedriver_path():
#     results = glob.glob('/**/chromedriver', recursive=True)  # workaround on streamlit sharing
#     return results[0]


def run_selenium():
    name = str()
    with webdriver.Chrome(options=options, service_log_path='selenium.log') as driver:
        url = "https://www.unibet.fr/sport/football/europa-league/europa-league-matchs"
        driver.get(url)
        xpath = '//*[@class="ui-mainview-block eventpath-wrapper"]'
        # Wait for the element to be rendered:
        element = WebDriverWait(driver, 10).until(lambda x: x.find_elements(by=By.XPATH, value=xpath))
        name = element[0].get_property('attributes')[0]['name']
    return name


if __name__ == "__main__":
    delete_selenium_log()
    st.set_page_config(page_title="Selenium Test", page_icon='✅',
        initial_sidebar_state='collapsed')
    st.title('🔨 Selenium Test for Streamlit Sharing')
    st.markdown("""
        This app is only a very simple test for **Selenium** running on **Streamlit Sharing** runtime. <br>
        The suggestion for this demo app came from a post on the Streamlit Community Forum.  <br>
        <https://discuss.streamlit.io/t/issue-with-selenium-on-a-streamlit-app/11563>  <br>
        In rare cases this app has deployment issues on Streamlit Cloud and the deployment fails, but usually it works.
        This is just a very very simple example and more a proof of concept.
        A link is called and waited for the existence of a specific class and read it. If there is no error message, the action was successful.
        Afterwards the log file of chromium is read and displayed.
        ---
        """, unsafe_allow_html=True)

    st.balloons()
    if st.button('Start Selenium run'):
        st.info('Selenium is running, please wait...')
        result = run_selenium()
        st.info(f'Result -> {result}')
        st.info('Successful finished. Selenium log file is shown below...')
        show_selenium_log()
