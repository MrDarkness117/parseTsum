import logging
import traceback

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
driver.implicitly_wait(6)
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
pagination_class_selected = 'pagination__link pagination__link_full pagination__link_state_current ng-star-inserted'
last_page = '//div[@id="attrId"]/div/div[2]/span/a[@title="Последняя страница"]'
failed_pages = {'pages': []}

tables = {}
count = 0
row = 2
closed = False

scrolled = False

MAILING_ATTACHMENTS = ['{}'.format(filepath)]


def set_to_list(array):
    return [*array, ]


def open_brands():
    driver.get(url_brands)
    brands_list = []
    # driver.find_element(By.XPATH, '//span[contains(@class, "header__gender ng-star-inserted") and contains(text(), "{}")]'.format(categories[2])).click()
    for c in categories:
        if c == categories[0]:
            pass
        else:
            driver.execute_script('window.scrollBy(0, -20000)')
            WebDriverWait(driver, 60).until(EC.element_to_be_clickable(
                (By.XPATH, '//a[contains(@class, "style__link___DT6kW") and contains(text(), "{}")]'.format(c))))
            driver.find_element(By.XPATH,
                                '//span[contains(@class, "header__gender ng-star-inserted") and contains(text(), "{}")]'
                                .format(c)).click()
            # WebDriverWait(driver, 60).until(
            #     EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Бренды")]'))).click()
            time.sleep(2)
        try:
            driver.find_element(
                By.XPATH,
                '//div[@class="header__gender-switch header__gender-switch_desktop"]//span[contains(text(), "{}")]'
                    .format(c)).click()
            WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//a[@title="Бренды"]')))
            driver.find_element(By.XPATH, "//a[contains(text(), 'Бренды')]").click()
        except Exception as e:
            print('Category ' + c + ' already open')

        print("/"*40)
        scroll_brands()
        # for n in (driver.find_elements(By.XPATH, '//span[@class="brand-item__name ng-star-inserted"]')):
        for n in (driver.find_elements(By.XPATH, '//a[@data-test-id="brandLinkWrapper"]')):
            # brands_list.append(driver.find_element(
            #     By.XPATH, '//span[@class="brand-item__name ng-star-inserted"][{}]'.format(n)).text)
            print(n.text)
            brands_list.append(n.text)

    brands_list = set(brands_list)
    print(brands_list)
    available_brands = set(brands_list) & set(brands)
    search_brands = set.union(available_brands, search_values)
    print(set_to_list(search_brands))
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
    # time.sleep(1)
    print("Scrolling down to brand-list__full-show")
    # WebDriverWait(driver, 60).until(EC.visibility_of_element_located(
    #     (By.XPATH, '//span[@class="brand-list__full-show"]')
    # ))
    # AC.move_to_element(driver.find_element(By.XPATH, '//span[@class="brand-list__full-show"]')).perform()
    # try:
    #     driver.find_element(By.XPATH, '//span[@class="brand-list__full-show"]').click()
    # except Exception as e:
    #     print("Attempting to close popping iframe")
    #     iframe = driver.find_element(
    #         By.XPATH, '//iframe[contains(@id, "fl-")]')
    #     driver.switch_to.frame(iframe)
    #     driver.find_element(By.XPATH, '//button[@class="close"]').click()
    #     print("Popup closed.")
    #     driver.switch_to.default_content()
    #     driver.find_element(By.XPATH, '//span[@class="brand-list__full-show"]').click()
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
        # WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//button[@class="search-mobile__open-button"]')))
        try:
            search_form = driver.find_element(By.XPATH, '//div[@class="header__search-form"]')
            AC.move_to_element(search_form).click(search_form).perform()
            driver.find_element(By.XPATH, '//input[@class="field__input"]')
        except:
            print("Attempting to close popping iframe")
            iframe = driver.find_element(
                By.XPATH, '//iframe[contains(@id, "fl-")]')
            driver.switch_to.frame(iframe)
            driver.find_element(By.XPATH, '//button[@class="close"]').click()
            print("Popup closed.")
            driver.switch_to.default_content()
            AC.move_to_element(search_form).click(search_form).perform()
            driver.find_element(By.XPATH, '//input[@class="field__input"]').clear()
        print("Search for: " + b)
        driver.find_element(By.XPATH, '//input[@class="field__input"]').clear()
        driver.find_element(By.XPATH, '//input[@class="field__input"]').send_keys(b)
        driver.find_element(By.XPATH, '//input[@class="field__input"]').send_keys(Keys.ENTER)
        # time.sleep(2)
        try:
            write_data()
        except Exception as e:
            print("Failure in finding elements")


def change_page():
    try:
        # AC.move_to_element(driver.find_element(By.XPATH, show)).perform()  # May not be necessary?
        driver.find_element(By.XPATH, show).click()
        time.sleep(2)
    except Exception as e:
        exception(e)
        try:
            print("Attempting to close popping iframe")
            iframe = driver.find_element(
                (By.XPATH, '//iframe[contains(@id, "fl-")]'))
            driver.switch_to.frame(iframe)
            driver.find_element(By.XPATH, '//button[@class="close"]').click()
            driver.switch_to.default_content()
            driver.find_element(By.XPATH, show).click()
        except Exception as e:
            exception(e)
            print("Attempt failed")
            try:
                print("Attempting to close iframe")
                iframe = driver.find_element(By.XPATH, "fl-297767")
                driver.switch_to.frame(iframe)
                driver.find_element(By.XPATH, '//button[@class="close"]').click()
                driver.switch_to.default_content()
                driver.find_element(By.XPATH, show).click()
            except Exception as e:
                exception(e)
                print("Attempting to close lead form")
                try:
                    driver.execute_script("document.querySelector('.lead-form__close').click();")
                    driver.find_element(By.XPATH, show).click()
                except Exception as e:
                    exception(e)
                    print("Attempting to refresh the page")
                    driver.refresh()
                    time.sleep(1)
                    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, show)))
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    driver.find_element(By.XPATH, show).click()
        time.sleep(2)


def get_data():
    # driver.execute_script('window.scrollBy(0, -7000)')
    print('Get prices')
    elems_var = '//div[@class="product-list__products ng-star-inserted"]/div'
    WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, elems_var)))
    elems = driver.find_elements(By.XPATH, elems_var)
    WebDriverWait(driver, 60).until(EC.visibility_of_element_located((
        By.XPATH, '//div[@class="product-list__products ng-star-inserted"]/div//div[last()]'
    )))
    counter = 0
    print('[begin gather loop]')
    print(elems)
    for el in elems:
        counter += 1
        driver.execute_script("arguments[0].scrollIntoView();", el)
        # AC.move_to_element(el).perform()
        # driver.execute_script('window.scrollBy(0, {})'.format(counter * 20))
        price = 'Error'
        old_price = 0
        discount = 0
        try:
            title = str(el.find_element_by_xpath('//div[@class="product-list__products ng-star-inserted"]'
                                                 '/div[{}]/div/div/a/*[1]'.format(counter)).get_attribute('title'))
            # section_base = '//div[@class="product-list__products ng-star-inserted"]/div[{}]'.format(counter)

            # for bit in [
            #     '/div/div/a',
            #     '//span[@class="product__price-wrapper"]/span/span/span',
            #     '/div//a/p[@class="product__brand"]',
            # ]:
            #     WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, section_base + bit)))
            try:
                article = re.sub("[^0-9]", '', el.find_element_by_xpath(
                    '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                    '/div/div/a'.format(counter)).get_attribute('href'))[:7]
            except Exception as e:
                print("Failed to obtain article.")
                exception(e)
                continue

            try:
                WebDriverWait(driver, 0.2).until(EC.visibility_of_element_located(
                    (By.XPATH, '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                               '//span[@class="price"]'.format(counter))))
                price = re.sub("[^0-9]", '', el.find_element(By.XPATH,
                                                                 '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                                                                 '//span[@class="price"]/span'.format(
                                                                     counter)).text)
            except:
                try:
                    old_price = re.sub("[^0-9]", '', el.find_element(By.XPATH,
                                                                     '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                                                                     '//span[@class="price price_type_old"]/span'.format(
                                                                         counter)).text)
                    price = re.sub("[^0-9]", '', el.find_element(By.XPATH,
                                                                     '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                                                                     '//span[@class="price price_type_new"]/span'.format(
                                                                         counter)).text)
                except Exception as e:
                    print("Failed to obtain price.")
                    exception(e)
                    continue

            '''try:
                WebDriverWait(driver, 0.2).until(EC.visibility_of_element_located(
                    (By.XPATH, '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                                                                 '//span[@class="price price_type_old"]'.format(
                                                                     counter))))
                old_price = re.sub("[^0-9]", '', el.find_element(By.XPATH,
                                                                 '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                                                                 '//span[@class="price price_type_old"]'.format(
                                                                     counter)).text)
                discount = "{:.2f}".format(100 - round(int(price) / int(old_price) * 100)) + "%"
            except:
                print('No old price.')'''

            try:
                brand = el.find_element_by_xpath('//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                                                 '//p[@class="product__brand"]'.format(counter)).text
            except Exception as e:
                print("Failed to obtain brand.")
                traceback.print_exc()
                continue

            try:
                link = el.find_element_by_xpath('//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                                                '/div/div/a'.format(counter)).get_attribute('href')
            except Exception as e:
                print("Failed to obtain link.")
                exception(e)
                continue

            try:
                description = el.find_element_by_xpath('//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                                                       '//p[@class="product__description"]'.format(counter)).text
            except Exception as e:
                print("Failed to obtain description.")
                exception(e)
                continue

            article_brand = ' '.join(
                ' '.join(title.replace(description.lower() + ' ', '').replace(brand + ' ', "").replace("женские", "")
                    .replace("женское", "").replace("мужское", "").replace("женская", "").replace("мужская", "").replace("мужские", "")
                    .replace("детская", "").replace("детские", "").replace("детское", "").replace("мужской", "").replace("женский", "")
                    .replace("детский", "").split(' ')[5:]).replace("руб., арт. ", "")
                    .replace("| ", "").replace(" Фото 1", "").replace("Фото", "").replace("арт. ", "").replace("цвета ", "")
                    .replace("цене ", "").replace(price, "").replace('по ', "").replace("бежевого ", "").replace("черного ", "")
                    .replace("серого ", '').replace("белого ", "").replace("темно-синего ", "").replace("хаки ", "")
                    .replace("серебряного ", "").replace("синего ", "").replace("розового ", "").replace("золотого ","")
                    .replace("коричневого ", "").replace('стразами', '').replace("хлопковая", "")
                    .split(' '))
            try:
                if article_brand[0] == ' ': article_brand = article_brand[1:]
                # if article_brand[0] == '0' and article_brand[1] == ' ': article_brand = article_brand[2:]
            except IndexError:
                pass
            article_errors = [' ', '№1', "WILL BE", '']
            if article_brand in article_errors:
                print("{}: {}".format(brand, article_brand))
                article_brand = open_product_page_and_parse(link)
            # if article_brand[0] == '0' and article_brand[1] == ' ':
            #     article_brand = open_product_page_and_parse(link)
            if price not in title or (article_brand[0] == '0' and article_brand[1] == ' '):
                article_brand = open_product_page_and_parse(link)

            tables[article] = [price, discount, brand, article_brand, link]  # no old price
            global row
            sheet.write('A'+str(row), article)
            sheet.write('B'+str(row), price)
            sheet.write('C'+str(row), old_price)
            sheet.write('D'+str(row), discount)
            sheet.write('E'+str(row), brand)
            sheet.write('F'+str(row), article_brand)
            sheet.write('G'+str(row), link)
            row += 1

        except Exception as e:
            print("Exception detected while parsing: " + str(e))
            exception(e)
            global failed_pages
            failed_pages['pages'].append(re.sub('[^0-9]', '', str(driver.current_url)[-3:]).replace('=', ''))
    # print("Total: \n" + str(tables))
    print("Page {}".format(str(re.sub('[^0-9]', '', str(driver.current_url)[-3:]).replace('=', ''))))
    print('Prices obtained')


def open_product_page_and_parse(link):
    driver.switch_to.new_window('tab')
    window_handler = driver.window_handles
    default_window = window_handler[0]
    driver.get(link)
    article_brand_raw = driver.find_element(By.XPATH, '//li[contains(text(), "Артикул производителя")]').text
    article_brand = article_brand_raw.replace("Артикул производителя: ", '')
    driver.close()
    driver.switch_to.window(default_window)
    return article_brand


def write_data():
    try:
        while driver.find_element(By.XPATH, last_page).get_attribute('class') != pagination_class_selected:
            get_data()
            change_page()
    except:
        get_data()


def write_file(url, filename, params=0):
    try:
        if params == 0:
            """ ==== FULL ==== """
            driver.get(url)
            write_data()
            driver.quit()
        elif params == 1:
            """ ==== BRANDS ==== """
            open_brands()
            driver.quit()
        elif params == 2:
            """ ==== SEARCH ==== """
            search(search_values, change_url=True)
            driver.quit()
    except Exception as e:
        print("Error caught, terminating: " + str(e))
        exception(e)
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
        # mail = SMTP()
        # mail.connect(host='https://mail.noone.ru/', port=25)
        # mail.login(user='m.romantsov@noone.ru', password='Mihailo117!')
        # # mail.sendmail()
        # mail.quit()
    except Exception as e:
        print("Send mail error")
        exception(e)


def run():

    write_file(url_brands, 'C:\\Users\\admin\\Documents\\outputs\\TSUM_brands_full', params=1)
    # write_file(url_brands, 'C:\\Users\\admin\\Documents\\outputs\\TSUM_brands_full', params=2)

    print("End: " + str(datetime.datetime.now()))


if __name__ == '__main__':
    run()
