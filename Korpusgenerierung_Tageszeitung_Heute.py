from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time
import random
import argparse
import os

parser = argparse.ArgumentParser(description="Wählen Sie eine Rubrik aus folgenden Möglichkeiten: Politik, Wirtschaft, Welt, Ukraine")
parser.add_argument("category", metavar="category", type=str)

chromeOptions = Options()
chromeOptions.add_argument('--headless')
driver = webdriver.Chrome(options=chromeOptions)

def pause():
    time.sleep(random.randrange(2, 4))

driver.get(f"https://www.heute.at/nachrichten/{parser.parse_args().category.lower()}")
pause()
driver.maximize_window()
driver.find_element(By.XPATH, "//button[@id='onetrust-accept-btn-handler']").click()
pause()
article_links = [*dict.fromkeys([article.get_attribute("href") for article in driver.find_elements("xpath", "//a[starts-with(@href, '/s/')]")])]



counter = 0
for link in article_links:
    counter +=1
    os.makedirs(f"Korpus/{link[-9:]}")
    driver.get(link)
    author = " und ".join([element.text for element in driver.find_elements(by=By.CLASS_NAME, value="ctKcqi")])
    try:
        release_time_full = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                                    "body.__variable_8305d6.__variable_1a3fe4:nth-child(2) div.sc-beqWaB.gbORR:nth-child(2) main.sc-beqWaB.ccXOhg:nth-child(3) article.sc-beqWaB:nth-child(5) div.sc-beqWaB.jjfCPF section.sc-beqWaB.exrhwI div.sc-beqWaB.joufXr.page-section-center div.sc-beqWaB.isBDDt div.sc-beqWaB.hrVxim:nth-child(3) div.sc-beqWaB.hqoAQj div.sc-beqWaB.knGGGt div.sc-beqWaB.jbeNLg:nth-child(2) > time.sc-beqWaB.iaSGlr:nth-child(2)"))).text
    except TimeoutException:
        try:
            release_time_full = driver.find_element(by=By.CSS_SELECTOR,
                                                    value="body.__variable_8305d6.__variable_1a3fe4:nth-child(2) div.sc-beqWaB.gbORR:nth-child(2) main.sc-beqWaB.ccXOhg:nth-child(3) article.sc-beqWaB:nth-child(5) div.sc-beqWaB.jjfCPF section.sc-beqWaB.exrhwI div.sc-beqWaB.joufXr.page-section-center div.sc-beqWaB.isBDDt div.sc-beqWaB.hrVxim:nth-child(3) div.sc-beqWaB.hqoAQj div.sc-beqWaB.dXwla-D > time.sc-beqWaB.fmJrCd:nth-child(2)"
                                                    ).text
        except NoSuchElementException:
            release_time_full = "nicht angegeben, nicht angegeben"
    release_date, release_time = release_time_full.split(",")[0], release_time_full.split(",")[1].strip()
    headline = driver.find_element(by=By.CLASS_NAME, value="iTcspr").text
    subtitle = driver.find_element(by=By.CLASS_NAME, value="iOdRIJ").text
    text_elements = driver.find_elements(by=By.CLASS_NAME, value="jOAegM")
    full_text = " ".join([text_element.text for text_element in text_elements])

    with open(f"Korpus/{link[-9:]}/Metadaten.txt", "w", encoding="UTF-8") as file:
        file.write(f"Link: {link}\nRubrik: {parser.parse_args().category}\nVerfasser: {author}\nErscheinungsdatum: {release_date}\nUhrzeit: {release_time}\nSchlagzeile: {headline}\nUntertitlel: {subtitle}\n")

    with open(f"Korpus/{link[-9:]}/Volltext.txt", "w", encoding="UTF-8") as file:
        file.write(full_text)

    print(f"\033[37mArtikel {counter} von {len(article_links)} wurde gespeichert.\033[0m")
    print(headline, "\n")

    pause()

print("\033[32mKorpusgenerierung erfolgreich!\033[0m")

driver.quit()

