import streamlit as st
import test
import pandas as pd
import warnings
import numpy as np
import time
from selenium import webdriver

numero = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
liste_trj = []
trj_final = 0

warnings.filterwarnings("ignore")


def test(testo):
    return testo


def go_to_float(cote, cote_float):
    for elem in cote:
        elem = elem.replace(',', '.')
        cote_float.append(float(elem))
    return cote_float


def parse_cote(cotes_initiales, cotes_finales, sport):
    cote_tempo = []

    for i in range(len(cotes_initiales)):
        try:
            if cotes_initiales[i] in numero:
                if (cotes_initiales[i + 1] == "," or cotes_initiales[i + 1] == ".") and cotes_initiales[i - 1] in numero:
                    cote_tempo.append(cotes_initiales[i - 1:i + 4])
                elif cotes_initiales[i + 1] == "," or cotes_initiales[i + 1] == ".":
                    cote_tempo.append(cotes_initiales[i:i + 4])
                elif "ul" in cotes_initiales[i - 3: i]:
                    cote_tempo.append(cotes_initiales[i:i + 2])
                elif "NUL" in cotes_initiales[i - 4:i]:
                    cote_tempo.append(cotes_initiales[i:i + 2])
        except:
            break

    if sport == "Rugby":
        for i in range(len(cote_tempo)):
            try:
                if cote_tempo[i][0:2] != cote_tempo[i+1][0:2]:
                    cotes_finales.append(cote_tempo[i])
            except:
                break
        cotes_finales.append(cote_tempo[-1])
        return cotes_finales
    else:
        cotes_finales = cote_tempo.copy()
        return cotes_finales


def delete_fake_odds(cotes_initiales):
    for i in range(len(cotes_initiales)):
        for j in range(len(cotes_initiales)):
            try:
                if cotes_initiales[i][j] == ' ':
                    del cotes_initiales[i]
                    break
            except:
                break
    return cotes_initiales

def parse_pokerstars_2_issues(cotes_initiales):
    cotes_finales = []

    for a in range(len(cotes_initiales)):
        if a%2 == 0:
            cotes_finales.append(cotes_initiales[a])

    return cotes_finales

def parse_joa_2_issues(cotes_initiales):
    cotes_finales = []
    cotes_tempo = []
    modulo = int(len(cotes_initiales)/4)

    for a in range(modulo):
        try:
            if len(cotes_initiales[a]) > 5:
                del cotes_initiales[a]
        except:
            break

    for a in range(modulo):
        try:
            cotes_tempo.append(cotes_initiales[0])
            cotes_tempo.append(cotes_initiales[1])
            del cotes_initiales[0:5]
        except:
            break

    for a in range(len(cotes_tempo)):
        if cotes_tempo[a] < 10.0:
            cotes_finales.append(cotes_tempo[a])

    return cotes_finales


def parse_joa_3_issues(cotes_initiales):
    cotes_finales = []
    modulo = int(len(cotes_initiales) / 6)
    for a in range(modulo):
        try:
            if len(cotes_initiales[a]) > 5:
                del cotes_initiales[a]
        except:
            break

    for a in range(modulo):
        try:
            cotes_finales.append(cotes_initiales[0])
            cotes_finales.append(cotes_initiales[1])
            cotes_finales.append(cotes_initiales[2])
            del cotes_initiales[0:6]
        except:
            break

    return cotes_finales


def trois_issues(cote_float, nb_rencontres):
    liste_trj = []
    for a in range(int(len(cote_float) / 3)):
        liste_trj.append(
            1 / ((1 / (float(cote_float[3 * a]))) + (1 / (float(cote_float[3 * a + 1]))) + (
                    1 / (float(cote_float[3 * a + 2])))) * 100)

    trj_final = "{:.2f}".format(
        round((sum(liste_trj[0:nb_rencontres]) / len(liste_trj[0:nb_rencontres])), 2))
    return trj_final


def deux_issues(cote_float, nb_rencontres):
    liste_trj = []
    for a in range(int(len(cote_float) / 2)):
        liste_trj.append(
            1 / ((1 / (float(cote_float[2 * a]))) + (1 / (float(cote_float[2 * a + 1])))) * 100)

    trj_final = "{:.2f}".format(
        round((sum(liste_trj[0:nb_rencontres]) / len(liste_trj[0:nb_rencontres])), 2))
    return trj_final


def scrap(urlpage, balise,sport):
    """GOOGLE_CHROME_BIN = "/app/.apt/usr/bin/google-chrome"
    CHROMEDRIVER_PATH = "/app/.chromedriver/bin/chromedriver"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = GOOGLE_CHROME_BIN
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)"""

    st.write("-------------------------------------")
    print(f"urlpage:{urlpage}")
    print(f"balise:{balise}")
    print(f"sport:{sport}")
    driver = webdriver.PhantomJS()
    st.write(urlpage)
    st.write(balise)
    driver.get(urlpage)
    data = []
    t = 0

    while len(data) == 0 and t < 15:
        time.sleep(1)
        results = driver.find_elements_by_xpath(balise)
        for result in results:
            product_name = result.text
            if product_name != "":
                data.append(product_name)
        t += 1

    driver.quit()
    try:
        cote_a_nettoyer = data[0]
        cote = []
        cote_float = []
        cotes_parse = parse_cote(cote_a_nettoyer, cote, sport)
        delete_fake_odds(cotes_parse)
        go_to_float(cotes_parse, cote_float)
    except:
        cote_float = [0]

    print(f"cote_float:{cote_float}")
    return cote_float

# Opérateurs
zebet = "Zebet"
winamax = "winamax"
vbet = "vbet"
unibet = "unibet"
poker_stars = "pokerstars"
pmu = "pmu"
parions_sports = "psel"
netbet = "netbet"
betclic = "betclic"
genybet = "genybet"
fp = "fp"
joa = "joa"

operateurs = [winamax, unibet, betclic, parions_sports, zebet, pmu, poker_stars, vbet, netbet, genybet, fp, joa]
name_foot = []
name_basket = []
name_tennis = []
name_rugby = []

urls_foot = pd.read_csv('https://raw.githubusercontent.com/KoxNoob/benchmark-auto/main/competitions_foot.csv', sep=';', encoding="utf-8", header=None)
for i in range(len(urls_foot)):
    name_foot.append(urls_foot.iloc[i, 0])

urls_basket = pd.read_csv('https://raw.githubusercontent.com/KoxNoob/benchmark-auto/main/competitions_basket.csv', sep=';', encoding="utf-8", header=None)
for i in range(len(urls_basket)):
    name_basket.append(urls_basket.iloc[i, 0])

urls_tennis = pd.read_csv('https://raw.githubusercontent.com/KoxNoob/benchmark-auto/main/competitions_tennis.csv', sep=';', encoding="utf-8", header=None)
for i in range(len(urls_tennis)):
    name_tennis.append(urls_tennis.iloc[i, 0])

urls_rugby = pd.read_csv('https://raw.githubusercontent.com/KoxNoob/benchmark-auto/main/competitions_rugby.csv', sep=';', encoding="utf-8", header=None)
for i in range(len(urls_rugby)):
    name_rugby.append(urls_rugby.iloc[i, 0])


sport = st.sidebar.radio('Sports', ("Football", "Basketball", "Tennis", "Rugby"))

# memo
# from selenium import webdriver
# URL = "https://www.unibet.fr/sport/football/europa-league/europa-league-matchs"
# driver = webdriver.phantomJS()
# driver.get(URL)
# memo

if sport == "Football":
    st.markdown(
        "<h3 style='text-align: center; color: grey; size = 0'>Benchmark Football</h3>",
        unsafe_allow_html=True)

    operateur_selectionne = st.multiselect('Quel opérateur ?', operateurs, default=operateurs)
    nb_rencontres = st.slider('Combien de rencontres à prendre en compte maximum ?', 0, 20, 2)
    options = st.multiselect('Quelle compétition ?', name_foot)
    lancement = st.button('Lancez le benchmark')

    if lancement:
        st.write("-scraping_start------------------------------------")
        bench_final = pd.DataFrame(index=[i for i in operateurs])
        for competition in options:
            st.write(f"-----------------competition:{competition}--------------------")
            ts_trj = []
            for j in range(len(urls_foot)):
                st.write(f"-----------------urls_foot:{urls_foot}--------------------")
                st.write(f"-----------------j:{j}--------------------")
                if urls_foot.iloc[j, 0] == competition:
                    st.write(f"-----------------urls_foot.iloc[j, 0]:{urls_foot.iloc[j, 0]}--------------------")
                    for ope in operateurs:
                        trj = 0
                        try:
                            for k in range(13):
                                if urls_foot.iloc[0, k] == ope and ope in operateur_selectionne:
                                    st.write(f"-----------------urls_foot.iloc[0, k]:{urls_foot.iloc[0, k]}--------------------")
                                    st.write(f"-----------------ope:{ope}--------------------")

                                    if ope == "unibet":
                                        st.write(f"000000000000000000000000-----------------test.scrape:start--------------------")
                                        st.write(f"-----------------urls_foot.iloc[j, k]:{urls_foot.iloc[j, k]}--------------------")
                                        st.write(f"-----------------sport:{sport}--------------------")
                                        st.write("dfjakldfjalksdjfkalsjfakl;fjadksl;jfakl;fjakl;fjklas;dfjkals;fjdksal;fjkals;fjkals;")
                                        st.write({test.scrap(urls_foot.iloc[j, k], "//*[@class=\"ui-mainview-block eventpath-wrapper\"]",sport)})
                                        trj = (test.trois_issues(test.scrap(urls_foot.iloc[j, k], "//*[@class=\"ui-mainview-block eventpath-wrapper\"]",sport), nb_rencontres))
                                        st.write(f"000000000000000000000000-----------------test.scrape:end--------------------")
                                    elif ope == "Zebet":
                                        trj = (test.trois_issues(test.scrap(urls_foot.iloc[j, k],
                                                                              "//*[@class=\"uk-accordion-content uk-padding-remove uk-active\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "winamax":
                                        trj = (test.trois_issues(test.scrap(urls_foot.iloc[j, k],
                                                                              "//*[@class=\"sc-fakplV bCGXIW\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "vbet":
                                        trj = (test.trois_issues(test.scrap(urls_foot.iloc[j, k],
                                                                              "//*[@class=\"   module ModuleSbEventsList \"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "psel":
                                        trj = (test.trois_issues(
                                            test.scrap(urls_foot.iloc[j, k], "//*[@class=\"wpsel-app-wrapper\"]",sport),
                                            nb_rencontres))
                                    elif ope == "pokerstars":
                                        trj = (test.trois_issues(
                                            test.scrap(urls_foot.iloc[j, k], "//*[@class=\"sportCompetitionsView\"]",sport),
                                            nb_rencontres))
                                    elif ope == "pmu":
                                        trj = (test.trois_issues(test.scrap(urls_foot.iloc[j, k],
                                                                              "//*[@class=\"entity entity-bean bean-event-list clearfix\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "netbet":
                                        trj = (test.trois_issues(
                                            test.scrap(urls_foot.iloc[j, k], "//*[@class=\"nb-middle-content uk-flex\"]",sport),
                                            nb_rencontres))
                                    elif ope == "genybet":
                                        trj = (test.trois_issues(test.scrap(urls_foot.iloc[j, k],
                                                                              "//*[@class=\"snc-middle-content-middle uk-width-1-1\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "fp":
                                        trj = (test.trois_issues(
                                            test.scrap(urls_foot.iloc[j, k], "//*[@class=\"item-content uk-active\"]",sport),
                                            nb_rencontres))
                                    elif ope == "betclic":
                                        trj = (test.trois_issues(
                                            test.scrap(urls_foot.iloc[j, k], "//*[@class=\"verticalScroller_wrapper\"]",sport),
                                            nb_rencontres))
                                    elif ope == "joa":
                                        trj = (test.trois_issues(test.parse_joa_3_issues(
                                            test.scrap(urls_foot.iloc[j, k], "//*[@class=\"bet-event-list\"]",sport)),
                                                                   nb_rencontres))


                        except:
                            pass
                        ts_trj.append(trj)

                    bench_tempo = pd.DataFrame(data=ts_trj, index=[i for i in operateurs])
                    bench_tempo = bench_tempo.astype(np.float64)
                    bench_final = bench_final.merge(bench_tempo, left_index=True, right_index=True)

        bench_final.columns = options
        bench_final = bench_final.apply(lambda x: x.replace(0.00, np.nan))

        for competition in bench_final.columns:
            bench_final.loc['Moyenne Compétition', competition] = round(
                (bench_final[competition]).sum() / (
                        len(bench_final[competition]) - bench_final[competition].isnull().sum()), 2)
        st.table(bench_final.style.format("{:.2f}"))


if sport == "Basketball":
    st.markdown(
        "<h3 style='text-align: center; color: grey; size = 0'>Benchmark Basketball</h3>",
        unsafe_allow_html=True)

    operateur_selectionne = st.multiselect('Quel opérateur ?', operateurs, default=operateurs)
    nb_rencontres = st.slider('Combien de rencontres à prendre en compte maximum ?', 0, 20, 2)
    options = st.multiselect('Quelle compétition ?', name_basket)
    lancement = st.button('Lancez le benchmark')


    if lancement:
        bench_final = pd.DataFrame(index=[i for i in operateurs])
        for competition in options:
            ts_trj = []
            for j in range(len(urls_basket)):
                if urls_basket.iloc[j, 0] == competition:
                    for ope in operateurs:
                        trj = 0
                        try:
                            for k in range(13):
                                if urls_basket.iloc[0, k] == ope and ope in operateur_selectionne:

                                    if ope == "unibet":
                                        trj = (test.deux_issues(test.scrap(urls_basket.iloc[j, k],
                                                                              "//*[@class=\"ui-mainview-block eventpath-wrapper\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "Zebet":
                                        trj = (test.deux_issues(test.scrap(urls_basket.iloc[j, k],
                                                                              "//*[@class=\"uk-accordion-content uk-padding-remove uk-active\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "winamax":
                                        trj = (test.deux_issues(test.scrap(urls_basket.iloc[j, k],
                                                                              "//*[@class=\"sc-djErbT ftrOoP\"]//*[@class=\"ReactVirtualized__Grid__innerScrollContainer\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "vbet":
                                        trj = (test.deux_issues(test.scrap(urls_basket.iloc[j, k],
                                                                              "//*[@class=\"   module ModuleSbEventsList \"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "psel":
                                        trj = (test.trois_issues(
                                            test.scrap(urls_basket.iloc[j, k], "//*[@class=\"wpsel-app-wrapper\"]",sport),
                                            nb_rencontres))
                                    elif ope == "pokerstars":
                                        trj = (test.deux_issues(
                                            test.scrap(urls_basket.iloc[j, k], "//*[@class=\"sportCompetitionsView\"]",sport),
                                            nb_rencontres))
                                    elif ope == "pmu":
                                        trj = (test.deux_issues(test.scrap(urls_basket.iloc[j, k],
                                                                              "//*[@class=\"entity entity-bean bean-event-list clearfix\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "netbet":
                                        trj = (test.deux_issues(
                                            test.scrap(urls_basket.iloc[j, k], "//*[@class=\"nb-middle-content uk-flex\"]",sport),
                                            nb_rencontres))
                                    elif ope == "genybet":
                                        trj = (test.deux_issues(test.scrap(urls_basket.iloc[j, k],
                                                                              "//*[@class=\"snc-middle-content-middle uk-width-1-1\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "fp":
                                        trj = (test.deux_issues(
                                            test.scrap(urls_basket.iloc[j, k], "//*[@class=\"item-content uk-active\"]",sport),
                                            nb_rencontres))
                                    elif ope == "betclic":
                                        trj = (test.deux_issues(
                                            test.scrap(urls_basket.iloc[j, k], "//*[@class=\"verticalScroller_wrapper\"]",sport),
                                            nb_rencontres))
                                    elif ope == "joa":
                                        trj = (test.deux_issues(test.parse_joa_2_issues(
                                            test.scrap(urls_basket.iloc[j, k], "//*[@class=\"bet-event-list\"]",sport)),
                                                                   nb_rencontres))


                        except:
                            pass
                        ts_trj.append(trj)

                    bench_tempo = pd.DataFrame(data=ts_trj, index=[i for i in operateurs])
                    bench_tempo = bench_tempo.astype(np.float64)
                    bench_final = bench_final.merge(bench_tempo, left_index=True, right_index=True)

        bench_final.columns = options
        bench_final = bench_final.apply(lambda x: x.replace(0.00, np.nan))

        for competition in bench_final.columns:
            bench_final.loc['Moyenne Compétition', competition] = round(
                (bench_final[competition]).sum() / (
                        len(bench_final[competition]) - bench_final[competition].isnull().sum()), 2)
        st.table(bench_final.style.format("{:.2f}"))


if sport == "Tennis":
    st.markdown(
        "<h3 style='text-align: center; color: grey; size = 0'>Benchmark Tennis</h3>",
        unsafe_allow_html=True)

    operateur_selectionne = st.multiselect('Quel opérateur ?', operateurs, default=operateurs)
    nb_rencontres = st.slider('Combien de rencontres à prendre en compte maximum ?', 0, 20, 2)
    options = st.multiselect('Quelle compétition ?', name_tennis)
    lancement = st.button('Lancez le benchmark')


    if lancement:
        bench_final = pd.DataFrame(index=[i for i in operateurs])
        for competition in options:
            ts_trj = []
            for j in range(len(urls_tennis)):
                if urls_tennis.iloc[j, 0] == competition:
                    for ope in operateurs:
                        trj = 0
                        try:
                            for k in range(13):
                                if urls_tennis.iloc[0, k] == ope and ope in operateur_selectionne:

                                    if ope == "unibet":
                                        trj = (test.deux_issues(test.scrap(urls_tennis.iloc[j, k],
                                                                              "//*[@class=\"ui-mainview-block eventpath-wrapper\"]", sport),
                                                                   nb_rencontres))
                                    elif ope == "Zebet":
                                        trj = (test.deux_issues(test.scrap(urls_tennis.iloc[j, k],
                                                                              "//*[@class=\"uk-accordion-content uk-padding-remove uk-active\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "winamax":
                                        trj = (test.deux_issues(test.scrap(urls_tennis.iloc[j, k],
                                                                              "//*[@class=\"sc-djErbT ftrOoP\"]//*[@class=\"ReactVirtualized__Grid__innerScrollContainer\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "vbet":
                                        trj = (test.deux_issues(test.scrap(urls_tennis.iloc[j, k],
                                                                              "//*[@class=\"   module ModuleSbEventsList \"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "psel":
                                        trj = (test.deux_issues(
                                            test.scrap(urls_tennis.iloc[j, k], "//*[@class=\"wpsel-app-wrapper\"]",sport),
                                            nb_rencontres))
                                    elif ope == "pokerstars":
                                        trj = (test.deux_issues(test.parse_pokerstars_2_issues(
                                            test.scrap(urls_tennis.iloc[j, k], "//*[@class=\"content-center\"]",sport)),
                                            nb_rencontres))
                                    elif ope == "pmu":
                                        trj = (test.deux_issues(test.scrap(urls_tennis.iloc[j, k],
                                                                              "//*[@class=\"entity entity-bean bean-event-list clearfix\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "netbet":
                                        trj = (test.deux_issues(
                                            test.scrap(urls_tennis.iloc[j, k], "//*[@class=\"nb-middle-content uk-flex\"]",sport),
                                            nb_rencontres))
                                    elif ope == "genybet":
                                        trj = (test.deux_issues(test.scrap(urls_tennis.iloc[j, k],
                                                                              "//*[@class=\"snc-middle-content-middle uk-width-1-1\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "fp":
                                        trj = (test.deux_issues(
                                            test.scrap(urls_tennis.iloc[j, k], "//*[@class=\"item-content uk-active\"]",sport),
                                            nb_rencontres))
                                    elif ope == "betclic":
                                        trj = (test.deux_issues(
                                            test.scrap(urls_tennis.iloc[j, k], "//*[@class=\"verticalScroller_wrapper\"]",sport),
                                            nb_rencontres))
                                    elif ope == "joa":
                                        trj = (test.deux_issues(test.parse_joa_2_issues(
                                            test.scrap(urls_tennis.iloc[j, k], "//*[@class=\"bet-event-list\"]",sport)),
                                                                   nb_rencontres))


                        except:
                            pass
                        ts_trj.append(trj)

                    bench_tempo = pd.DataFrame(data=ts_trj, index=[i for i in operateurs])
                    bench_tempo = bench_tempo.astype(np.float64)
                    bench_final = bench_final.merge(bench_tempo, left_index=True, right_index=True)

        bench_final.columns = options
        bench_final = bench_final.apply(lambda x: x.replace(0.00, np.nan))

        for competition in bench_final.columns:
            bench_final.loc['Moyenne Compétition', competition] = round(
                (bench_final[competition]).sum() / (
                        len(bench_final[competition]) - bench_final[competition].isnull().sum()), 2)
        st.table(bench_final.style.format("{:.2f}"))



if sport == "Rugby":
    st.markdown(
        "<h3 style='text-align: center; color: grey; size = 0'>Benchmark Rugby</h3>",
        unsafe_allow_html=True)

    operateur_selectionne = st.multiselect('Quel opérateur ?', operateurs, default=operateurs)
    nb_rencontres = st.slider('Combien de rencontres à prendre en compte maximum ?', 0, 20, 2)
    options = st.multiselect('Quelle compétition ?', name_rugby)
    lancement = st.button('Lancez le benchmark')

    if lancement:
        bench_final = pd.DataFrame(index=[i for i in operateurs])
        for competition in options:
            ts_trj = []
            for j in range(len(urls_rugby)):
                if urls_rugby.iloc[j, 0] == competition:
                    for ope in operateurs:
                        trj = 0
                        try:
                            for k in range(13):
                                if urls_rugby.iloc[0, k] == ope and ope in operateur_selectionne:

                                    if ope == "unibet":
                                        trj = (test.trois_issues(test.scrap(urls_rugby.iloc[j, k],
                                                                              "//*[@class=\"ui-mainview-block eventpath-wrapper\"]", sport),
                                                                   nb_rencontres))
                                    elif ope == "Zebet":
                                        trj = (test.trois_issues(test.scrap(urls_rugby.iloc[j, k],
                                                                              "//*[@class=\"uk-accordion-content uk-padding-remove uk-active\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "winamax":
                                        trj = (test.trois_issues(test.scrap(urls_rugby.iloc[j, k],
                                                                              "//*[@class=\"sc-djErbT ftrOoP\"]//*[@class=\"ReactVirtualized__Grid__innerScrollContainer\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "vbet":
                                        trj = (test.trois_issues(test.scrap(urls_rugby.iloc[j, k],
                                                                              "//*[@class=\"   module ModuleSbEventsList \"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "psel":
                                        trj = (test.trois_issues(
                                            test.scrap(urls_rugby.iloc[j, k], "//*[@class=\"wpsel-app-wrapper\"]",sport),
                                            nb_rencontres))
                                    elif ope == "pokerstars":
                                        trj = (test.trois_issues(
                                            test.scrap(urls_rugby.iloc[j, k], "//*[@class=\"sportCompetitionsView\"]",sport),
                                            nb_rencontres))
                                    elif ope == "pmu":
                                        trj = (test.trois_issues(test.scrap(urls_rugby.iloc[j, k],
                                                                              "//*[@class=\"entity entity-bean bean-event-list clearfix\"]",sport),
                                                                   nb_rencontres))
                                    elif ope == "netbet":
                                        trj = (test.trois_issues(
                                            test.scrap(urls_rugby.iloc[j, k], "//*[@class=\"nb-middle-content uk-flex\"]",sport),
                                            nb_rencontres))
                                    elif ope == "genybet":
                                        trj = (test.trois_issues(test.scrap(urls_rugby.iloc[j, k],
                                                                              "//*[@class=\"snc-middle-content-middle uk-width-1-1\"]", sport),
                                                                   nb_rencontres))
                                    elif ope == "fp":
                                        trj = (test.trois_issues(
                                            test.scrap(urls_rugby.iloc[j, k], "//*[@class=\"item-content uk-active\"]",sport),
                                            nb_rencontres))
                                    elif ope == "betclic":
                                        trj = (test.trois_issues(
                                            test.scrap(urls_rugby.iloc[j, k], "//*[@class=\"verticalScroller_wrapper\"]", sport),
                                            nb_rencontres))
                                    elif ope == "joa":
                                        trj = (test.trois_issues(test.parse_joa_3_issues(
                                            test.scrap(urls_rugby.iloc[j, k], "//*[@class=\"bet-event-list\"]", sport)),
                                                                   nb_rencontres))


                        except:
                            pass
                        ts_trj.append(trj)

                    bench_tempo = pd.DataFrame(data=ts_trj, index=[i for i in operateurs])
                    bench_tempo = bench_tempo.astype(np.float64)
                    bench_final = bench_final.merge(bench_tempo, left_index=True, right_index=True)

        bench_final.columns = options
        bench_final = bench_final.apply(lambda x: x.replace(0.00, np.nan))

        for competition in bench_final.columns:
            bench_final.loc['Moyenne Compétition', competition] = round(
                (bench_final[competition]).sum() / (
                        len(bench_final[competition]) - bench_final[competition].isnull().sum()), 2)
        st.table(bench_final.style.format("{:.2f}"))
