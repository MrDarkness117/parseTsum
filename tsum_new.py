import logging
import traceback

import requests
import selenium.common.exceptions
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from logging import exception
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from os import path
from pathlib import Path
import os
import re
import json
import time
import datetime
import xlsxwriter

print("Start: " + str(datetime.datetime.now()))

options = Options()
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option('prefs', prefs)
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
# driver = webdriver.Chrome(options=options)
driver.set_window_position(-2000, 0)
driver.maximize_window()
driver.implicitly_wait(0.5)  # was 6 before
AC = ActionChains(driver)

file_name = 'ЦУМ {}'.format(str(datetime.datetime.now()))[:-7].replace(":", "-")
filepath = str(Path.home()) + '\\Documents\\outputs\\{}.xlsx'.format(file_name)
output = xlsxwriter.Workbook(filepath)
sheet = output.add_worksheet('ЦУМ')
sheet.write('A1', 'Артикул')
sheet.write('B1', 'Цена')
sheet.write('C1', 'Старая цена')
sheet.write('D1', 'Скидка')
sheet.write('E1', 'Бренд')
sheet.write('F1', 'Артикул производителя')
sheet.write('G1', 'Ссылка')

url_f = "https://www.tsum.ru/catalog/obuv-18405/?availability=2&page=1"
url_f_sumki = 'https://www.tsum.ru/catalog/sumki-18438/'
url_f_aksess = 'https://www.tsum.ru/catalog/aksessuary-2404/'
url_f_modded = "https://www.tsum.ru/catalog/obuv-18405/?availability=2&page=289"
url_f_f_wd = 'https://www.tsum.ru/catalog/obuv-18405/?brand=10468094&availability=2'
url_f_f_wd_av = 'https://www.tsum.ru/catalog/obuv-18405/?brand=10468094'
url_f_le_silla_av = 'https://www.tsum.ru/catalog/obuv-18405/?brand=448697'
url_m = "https://www.tsum.ru/catalog/obuv-18440/?availability=2&page=1"
url_m_sumki = 'https://www.tsum.ru/catalog/muzhskie_sumki-4051/'
url_m_aksess = 'https://www.tsum.ru/catalog/aksessuary-4031/'
url_m_modded = "https://www.tsum.ru/catalog/obuv-18440/?availability=2&page=203"
url_f_k = "https://www.tsum.ru/catalog/obuv_dlya_devochek-3442/"
url_m_k = "https://www.tsum.ru/catalog/obuv_dlya_malchikov-3425/"

url_brands = "https://www.tsum.ru/brands/"

brands = ["ANNA RACHELE", "Aldo Brue", "Alto Milano", "AGL", "Automobili Lamborghini", "BANU", 'Baldinini', "Bally", "Braccialini",
    "Barracuda", 'Bresciani', 'Brimarts', 'Bikkembergs', 'Carlo Visintini', 'Casadei', 'Casheart,', 'Cerruti 1881',
    'Cesare Casadei', 'Coccinelle', "D.A.T.E.", 'DKNY', "Diadora", 'Doria Maria', 'Doucal\'s', 'Doucals', "DSQUARED2", 'F_WD', 'Fabi',
    'Fabrizio Lesi', 'Ferre Milano', 'Flower Mountain', 'Franceschetti', 'Frasconi', 'Fratelli Rossetti',
    'Fratelli Rossetti One', 'Gianni Chiarini', "GHOUD", 'Goose Tech', 'GUM', 'HIDE&JACK', 'Ice Play', 'Iceberg', 'In The Box',
    'Inuikii', 'John Galliano', 'John Richmond', 'Kalliste', 'Kat Maconie', 'Kate Spade', 'Lancaster', 'Landi',
    'Le Silla', 'Lemon Jelly', "Limitato", "L'Impermeabile", 'Marsell', 'Merola Gloves', 'Moose Knuckles', 'Moreschi',
    'Moschino', "NEW BALANCE", "No One", 'Panchic', 'Pantanetti', 'Parajumpers', 'Pasotti', 'Pertini', 'Pierre Cardin', 'Pollini',
    'Portolano', 'Premiata', 'Principe Di Bologna', 'RBRSL', "Reptile's House", "Renzo Mercuri", 'Roberto Cavalli',
    'Rocco P', "Run Of", 'Sergio Rossi', 'SPRAYGROUND', 'Stemar', 'Stuart Weitzman', 'Quete', "Versace Jeans Couture", 'Vivienne Westwood', 'V SEASON',
    "VIC MATIE'", "Vic Matie", 'Voile Blanche', 'What For', 'Wolford', '3JUIN', 'Premiata will be', 'Sprayground',
    'Domrebel', 'GIUSEPPE ZANOTTI DESIGN', 'Giuseppe Zanotti Design', 'GIUSEPPE ZANOTTI', 'Giuseppe Zanotti', '№21', "N21"]

search_values = ['Wolford']

categories = [
    "Женское",
    'Мужское',
    "Детское"
]

present = '//*[@id="catalog"]/div[2]/div/div/div/div[1]/filter-desktop/div[5]/div/div/div/div/div[3]' \
          '/div/perfect-scrollbar/div/div[1]/div/div[1]/div/label'
show = "//div[@class='js-pagination-next pagination__button pagination__button_type_next']"
pagination_class_selected = 'styles_numberBtn__6378cbe9 styles_active__6378cbe9'
last_page = '//div[@id="attrId"]/div/div[2]/span/a[@title="Последняя страница"]'
next_page = '//div[@class="js-pagination-next pagination__button pagination__button_type_next"]'
# next_page_disabled = 'js-pagination-next pagination__button pagination__button_disabled pagination__button_type_next'
next_page_disabled = 'pagination__button_disabled'
failed_pages = {'pages': []}

item_links = []
tables = {}
count = 0
row = 2
closed = False

scrolled = False

MAILING_ATTACHMENTS = ['{}'.format(filepath)]
wait = WebDriverWait(driver, 3)


def set_to_list(array):
    return [*array, ]


def open_brands():
    driver.get(url_brands)
    # driver.find_element(By.XPATH, '')
    brands_list = []
    # driver.find_element(By.XPATH, '//span[contains(@class, "header__gender ng-star-inserted") and contains(text(), "{}")]'.format(categories[2])).click()
    for c in categories:
        if c == categories[0]:
            pass
        else:
            driver.execute_script('window.scrollBy(0, -20000)')
            try:
                print(f"Opening anchor {c}")
                WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, f'//a[contains(text(), "{c}")]'))).click()
                print("Done.")
            except Exception as e:  # selenium.common.exceptions.NoSuchElementException:
                print("No anchor")
                print(f"Opening span {c}")
                WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, f'//span[contains(text(), "{c}")]'))).click()
                print("Done.")
            # else:
            #     print('Category ' + c + ' already open')
            # WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, '//a[text()="Бренды"]'))).click()
            # time.sleep(2)

        print("/"*40)
        try:
            WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, '//span[@class="brand-list__full-show"]'))).click()
            scroll_brands()
            print("Collecting brands...")
            for n in (driver.find_elements(By.XPATH, '//span[@class="brand-item__name ng-star-inserted"]')):
                # print(n.text)
                brands_list.append(n.text)
            print("Done.")
        except Exception as e:
            print("Not the old version, skipping")
            scroll_brands()
            print("Collecting brands...")
            for n in (driver.find_elements(By.XPATH, '//a[@data-test-id="brandLinkWrapper"]')):
                # brands_list.append(driver.find_element(
                #     By.XPATH, '//span[@class="brand-item__name ng-star-inserted"][{}]'.format(n)).text)
                # print(n.text)
                brands_list.append(n.text)
            print("Done.")
        print("Next category.")

    brands_list = set(brands_list)
    print(brands_list)
    available_brands = set(brands_list) & set(brands)
    search_brands = set.union(available_brands, search_values)
    print(set_to_list(search_brands))
    print("Begin search.")
    search(set_to_list(search_brands))

        # try:
        #     search(search_brands)
        # except:
        #     print("Attempting to close popping iframe")
        #     iframe = driver.find_element(
        #         By.XPATH, '//iframe[contains(@id, "fl-")]')
        #     driver.switch_to.frame(iframe)
        #     driver.find_element_by_xpath('//button[@class="close"]').click()
        #     print("Popup closed.")
        #     driver.switch_to.default_content()
        #     search(search_brands)

        #TODO: DEPRECATED
        # for el in brands:
        #     global scrolled
        #     scrolled = False
        #     scroll_brands()
        #     try:
        #         try:
        #             driver.find_element_by_xpath('//span[contains(text(), "{}")]'.format(el)).click()
        #         except Exception as e:
        #             print("Attempting to close popping iframe")
        #             iframe = driver.find_element(
        #                 (By.XPATH, '//iframe[contains(@id, "fl-")]'))
        #             driver.switch_to.frame(iframe)
        #             driver.find_element_by_xpath('//button[@class="close"]').click()
        #             print("Popup closed.")
        #             driver.switch_to.default_content()
        #             driver.find_element_by_xpath('//span[contains(text(), "{}")]'.format(el)).click()
        #         write_data()
        #     except Exception as e:
        #         print(el + " not found in the list, skipping.")


def scroll_brands(change_url=False):
    if change_url:
        driver.get(url_brands)
    driver.execute_script('window.scrollBy(0, 7000)')
    print("Scrolling down to brand-list__full-show")
    time.sleep(2)
    driver.execute_script('window.scrollBy(0, 7000)')
    time.sleep(1)
    driver.execute_script('window.scrollBy(0, 7000)')
    time.sleep(1)
    driver.execute_script('window.scrollBy(0, 7000)')
    time.sleep(1)
    driver.execute_script('window.scrollBy(0, 7000)')
    time.sleep(1)
    driver.execute_script('window.scrollBy(0, 7000)')
    global scrolled
    scrolled = True


def search(values, change_url=False):
    if change_url:
        driver.get(url_brands)
    for b in values:
        print('Start search')
        search_tag = '//input[@placeholder="Поиск"]'
        try:
            search_form = wait.until(EC.visibility_of_element_located((By.XPATH, search_tag)))
            AC.move_to_element(search_form).click(search_form).perform()
            # driver.find_element(By.XPATH, search_tag) # TODO: Is this even needed?
        # except:
        #     print("Attempting to close popping iframe")
        #     iframe = driver.find_element(
        #         By.XPATH, '//iframe[contains(@id, "fl-")]')
        #     driver.switch_to.frame(iframe)
        #     driver.find_element(By.XPATH, '//button[@class="close"]').click()
        #     print("Popup closed.")
        #     driver.switch_to.default_content()
        #     AC.move_to_element(search_form).click(search_form).perform()
        #     driver.find_element(By.XPATH, search_tag).clear()
        except Exception as e:
            driver.refresh()
            search_form = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, search_tag)))
            AC.move_to_element(search_form).click(search_form).perform()
            # driver.find_element(By.XPATH, search_tag)  # TODO: Is this even needed?
        print("Search for: " + b)
        driver.find_element(By.XPATH, search_tag).clear()
        driver.find_element(By.XPATH, search_tag).send_keys(b)
        driver.find_element(By.XPATH, search_tag).send_keys(Keys.ENTER)
        # time.sleep(2)
        try:
            elems_var = '//div[@class="product-list__products ng-star-inserted"]/div[last()]'
            wait.until(EC.visibility_of_element_located((By.XPATH, elems_var)))
            write_data(0)
        except Exception as e:
            elems_var = '//div[@class="styles__productList___e1E5m"]/div[last()]'
            wait.until(EC.visibility_of_element_located((By.XPATH, elems_var)))
            write_data(1)
        except selenium.common.exceptions.NoSuchElementException or selenium.common.exceptions.TimeoutException:
            print("Failure in finding elements")


def change_page():
    try:
        AC.move_to_element(driver.find_element(By.XPATH, next_page)).click().perform()
        time.sleep(2)
    except Exception as e:
        print(e)
        AC.move_to_element(driver.find_element(By.XPATH, '//div[@class="styles_nextBtn__6378cbe9"]')).click().perform()
        print("Changed page")
        # exception(e)
        # try:
        #     print("Attempting to close popping iframe")
        #     iframe = driver.find_element(
        #         (By.XPATH, '//iframe[contains(@id, "fl-")]'))
        #     driver.switch_to.frame(iframe)
        #     driver.find_element(By.XPATH, '//button[@class="close"]').click()
        #     driver.switch_to.default_content()
        #     driver.find_element(By.XPATH, next_page).click()
        # except Exception as e:
        #     exception(e)
        #     print("Attempt failed")
        #     try:
        #         print("Attempting to close iframe")
        #         iframe = driver.find_element(By.XPATH, "fl-297767")
        #         driver.switch_to.frame(iframe)
        #         driver.find_element(By.XPATH, '//button[@class="close"]').click()
        #         driver.switch_to.default_content()
        #         driver.find_element(By.XPATH, next_page).click()
        #     except Exception as e:
        #         exception(e)
        #         print("Attempting to close lead form")
        #         try:
        #             driver.execute_script("document.querySelector('.lead-form__close').click();")
        #             driver.find_element(By.XPATH, next_page).click()
        #         except Exception as e:
        #             exception(e)
        #             print("Attempting to refresh the page")
        #             driver.refresh()
        #             time.sleep(1)
        #             WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, next_page)))
        #             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #             driver.find_element(By.XPATH, next_page).click()
        time.sleep(2)


def get_data(param):
    print('Get prices')
    if param == 0:
        elems_var = '//div[@class="product-list__products ng-star-inserted"]/div'
        elems = WebDriverWait(driver, 1).until(EC.visibility_of_all_elements_located((By.XPATH, elems_var)))
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located(
            (By.XPATH, '//div[@class="product-list__products ng-star-inserted"]/div[last()]')))
    elif param == 1:
        print('product-list__products not found')
        elems_var = '//div[@class="styles__productList___e1E5m"]/div'
        elems = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, elems_var)))
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
            (By.XPATH, '//div[@class="styles__productList___e1E5m"]/div[last()]')))

    counter = 0
    print('[begin gather loop]')
    print(elems)
    for el in elems:
        counter += 1
        driver.execute_script("arguments[0].scrollIntoView();", el)
        price = 'Error'
        old_price = 0
        discount = 0
        try:
            # driver.find_element((By.XPATH, '')).
            # link = el.find_element_by_xpath(f'//div[{counter}]/div//a[@class="style__photoContainer___vfhcO"]').get_attribute('href')
            link = el.find_element_by_xpath(f'../div[{counter}]/div/div/a[@class="product__image-wrapper"]').get_attribute('href')
            item_links.append(link)
        except Exception as e:
            try:
                link = el.find_element_by_xpath(f'//a[@class="style__photoContainer___vfhcO"]').get_attribute('href')  # //div[@class="styles__productList___e1E5m"]//div[{counter}]
                item_links.append(link)
            except Exception as e:
                print("Exception detected while parsing: " + str(e))
                exception(e)
                global failed_pages
                failed_pages['pages'].append(re.sub('[^0-9]', '', str(driver.current_url)[-3:]).replace('=', ''))
    # print("Total: \n" + str(tables))
    print("Page {}".format(str(re.sub('[^0-9]', '', str(driver.current_url)[-3:]).replace('=', ''))))
    print('Links obtained')


def open_product_page_and_parse(link):
    # driver.switch_to.new_window('tab')
    # window_handler = driver.window_handles
    # default_window = window_handler[0]
    # driver.get(link)
    parse_tag_article = "Артикул производителя: "
    # brand_path = 'div.item_specifications>h1>a'
    parse_article = "Артикул: "
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
    article_brand = "Не удалось спарсить"
    brand = "Не удалось спарсить"
    article = "Не удалось спарсить"
    resp = requests.get(link, headers=headers, timeout=(3.05, 27))
    soup = BeautifulSoup(resp.content, 'html.parser')
    try:
        brand = soup.find('div', 'item__info-wrapper').find('div', 'item__info').find('div', 'item__specifications') \
            .find('h1').find('a').text
        article_brand = soup.find_all(lambda tag: len(tag.find_all()) == 0 and parse_tag_article in tag.text)[0].text\
            .replace(parse_tag_article, '')
        article = soup.find_all(lambda tag: len(tag.find_all()) == 0 and parse_tag_article in tag.text)[0].text.replace(parse_article, '')
    except Exception as e:
        print("/"*30 + "Error!!" + "\\"*30)
        print(link)
        exception(e)
        print("Retrying.")
        try:
            resp = requests.get(link, headers=headers, timeout=None)
            time.sleep(6)
            soup = BeautifulSoup(resp.content, 'html.parser')
            brand = soup.find('div', 'item__info-wrapper').find('div', 'item__info').find('div', 'item__specifications') \
                .find('h1').find('a').text
            article_brand = soup.find_all(lambda tag: len(tag.find_all()) == 0 and parse_tag_article in tag.text)[0]\
                .text.replace(parse_tag_article, '')
            article = soup.find_all(lambda tag: len(tag.find_all()) == 0 and parse_tag_article in tag.text)[0]\
                .text.replace(parse_article, '')
            print("Success.")
        except Exception as e:
            exception(e)
            print("Fatal. Skipping.")
            return
    # article_brand_raw = driver.find_element(By.XPATH, '//li[contains(text(), "Артикул производителя")]').text
    # article_brand = article_brand_raw.replace("Артикул производителя: ", '')
    # brand = driver.find_element(By.XPATH, '//div[@class="item__specifications"]/h1/a').text
    # article_raw = driver.find_element(By.XPATH, '//li[contains(text(), "Артикул")][1]').text
    # article = article_raw.replace("Артикул: ", "")
    price = 0
    price_old = 0
    price_new = 0
    discount = 0
    try:
        # price = re.sub('[^0-9]', '', driver.find_element(By.XPATH, '//div[@class="price price_type_retail ng-star-inserted"]/span').text)
        price = re.sub('[^0-9]', '', soup.find('div', class_="price price_type_retail ng-star-inserted").find('span').text)
    except:
        price_old = re.sub('[^0-9]', '', soup.find('div', class_="price price_type_old ng-star-inserted").find('span').text)
        price_new = re.sub('[^0-9]', '', soup.find('div', class_="price price_type_new ng-star-inserted").find('span').text)[:-2]
        discount = re.sub('[^0-9]', '', soup.find('div', class_="price price_type_new ng-star-inserted").find('span').text)[-2:] + '%'
        # price_old = re.sub('[^0-9]', '', driver.find_element(By.XPATH, '//div[@class="price price_type_old ng-star-inserted"]/span').text)
        # price_new = re.sub('[^0-9]', '', driver.find_element(By.XPATH, '//div[@class="price price_type_new ng-star-inserted"]/span').text)[:-2]
        # discount = re.sub('[^0-9]', '', driver.find_element(By.XPATH, '//div[@class="price price_type_new ng-star-inserted"]/span').text)[-2:]

    if price != 0:
        price_new = price
    tables[article] = [price_old, price_new, discount, brand, article_brand, link]
    global row
    sheet.write('A' + str(row), article)
    sheet.write('B' + str(row), price_new)
    sheet.write('C' + str(row), price_old)
    sheet.write('D' + str(row), discount)
    sheet.write('E' + str(row), brand)
    sheet.write('F' + str(row), article_brand)
    sheet.write('G' + str(row), link)
    row += 1


def write_data(params):
    try:
        while next_page_disabled not in str(driver.find_element(By.XPATH, next_page).get_attribute('class')):
            try:
                get_data(params)
                change_page()
            except:
                continue
    except selenium.common.exceptions.NoSuchElementException:
        try:
            while "styles_disable__6378cbe9" not in str(driver.find_element(
                    By.XPATH, '//div[contains(@class, "styles_nextBtn__6378cbe9")]').get_attribute('class')):
                try:
                    get_data(params)
                    change_page()
                except:
                    continue
        except Exception as e:
            print("Encountered error in write_data - no change page available")
            # exception(e)
            try:
                elems_var = '//div[@class="product-list__products ng-star-inserted"]/div[last()]'
                wait.until(EC.visibility_of_element_located((By.XPATH, elems_var)))
                get_data(0)
            except:
                elems_var = '//div[@class="styles__productList___e1E5m"]/div[last()]'
                wait.until(EC.visibility_of_element_located((By.XPATH, elems_var)))
                get_data(1)


def open_urls():
    for link in item_links:
        open_product_page_and_parse(link)


def write_file(url, filename, params=0):
    try:
        if params == 0:  # FIXME: Старое, не работает
            """ ==== FULL ==== """
            driver.get(url)
            write_data()
            open_urls()
            driver.quit()
        elif params == 1:
            """ ==== BRANDS ==== """
            open_brands()
            open_urls()
            driver.quit()
        elif params == 2:
            """ ==== SEARCH ==== """
            search(search_values, change_url=True)  # FIXME: Старое, не работает
            driver.quit()
    except Exception as e:
        print("Error caught, terminating: " + str(e))
        exception(e)
        driver.quit()
        # output.close()
    print('Writing file...')
    if not path.exists('{}.json'.format(filename)):
        with open('{}.json'.format(filename), 'w') as t:
            json.dump({}, t)
            t.close()

    with open('{}.json'.format(filename), 'r+', encoding='utf-8') as t:
        info = json.load(t)
        t.seek(0)
        info.update(tables)
        json.dump(info, t, ensure_ascii=False, indent=4)
        t.truncate()
        print('...Completed writing')
        t.close()

    with open('{}_failed_pages.json'.format(filename), 'w', encoding='utf-8') as p:

        json.dump(failed_pages, p, ensure_ascii=False, indent=4)
        p.close()

    output.close()

    from lib import mailing
    try:
        mailing.send_mail('miromantsov@gmail.com',
                          ['a.stepanov@noone.ru', 'm.biryukova@noone.ru'],
                          "Выгрузка ЦУМ {}".format(str(datetime.date.today())),
                          "Создано автоматически",
                          MAILING_ATTACHMENTS,
                          'smtp.gmail.com',
                          587,
                          'miromantsov@gmail.com',
                          'mihailogoogle117'
                          )

    except Exception as e:
        print("Send mail error")
        exception(e)


def run():

    write_file(url_brands, 'C:\\Users\\admin\\Documents\\outputs\\TSUM_brands_full', params=1)
    # write_file(url_brands, 'C:\\Users\\admin\\Documents\\outputs\\TSUM_brands_full', params=2)

    print("End: " + str(datetime.datetime.now()))


if __name__ == '__main__':
    run()
