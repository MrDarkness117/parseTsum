from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from os import path
import re
import json
import time
import datetime

print("Start: " + str(datetime.datetime.now()))

options = Options()
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option('prefs', prefs)
# driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.implicitly_wait(6)

url_f =     "https://www.tsum.ru/catalog/obuv-18405/?availability=2&page=1"
url_f2 =    "https://www.tsum.ru/catalog/obuv-18405/?availability=2&page=101"
url_f3 =    "https://www.tsum.ru/catalog/obuv-18405/?availability=2&page=201"
url_f4 =    "https://www.tsum.ru/catalog/obuv-18405/?availability=2&page=301"
url_m =     "https://www.tsum.ru/catalog/obuv-18440/?availability=2&page=1"
url_f_k =   "https://www.tsum.ru/catalog/obuv_dlya_devochek-3442/"
url_m_k =   "https://www.tsum.ru/catalog/obuv_dlya_malchikov-3425/"

present = '//*[@id="catalog"]/div[2]/div/div/div/div[1]/filter-desktop/div[5]/div/div/div/div/div[3]' \
          '/div/perfect-scrollbar/div/div[1]/div/div[1]/div/label'
show = "//div[@title='Следующая страница']"
pagination_class_selected = 'pagination__link pagination__link_full pagination__link_state_current ng-star-inserted'
last_page = '//div[@id="attrId"]/div/div[2]/span/a[@title="Последняя страница"]'
failed_pages = {'pages': []}

tables = {}
count = 0


def change_page():
    try:
        driver.find_element_by_xpath(show).click()
        time.sleep(2)
    except Exception as e:
        try:
            print("Attempting to close iframe")
            iframe = driver.find_element_by_id("fl-297767")
            driver.switch_to.frame(iframe)
            driver.find_element_by_xpath('//button[@class="close"]').click()
            driver.switch_to.default_content()
            driver.find_element_by_xpath(show).click()
        except Exception as e:
            print(e)
            print("Attempting to close lead form")
            try:
                driver.execute_script("document.querySelector('.lead-form__close').click();")
                driver.find_element_by_xpath(show).click()
            except Exception as e:
                print(e)
                print("Attempting to refresh the page")
                driver.refresh()
                time.sleep(1)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, show)))
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                driver.find_element_by_xpath(show).click()
        time.sleep(2)


# def gather(counter, el):
#         article = re.sub("[^0-9]", '', el.find_element_by_xpath(
#             '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
#             '/div/div/a'.format(counter)).get_attribute('href'))[:7]
#         price = re.sub("[^0-9]", '', el.find_element_by_xpath(
#             '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
#             '//span[@class="product__price-wrapper"]/span/span/span'.format(counter)).text)
#         brand = el.find_element_by_xpath('//div[@class="product-list__products ng-star-inserted"]/div[{}]/div//'
#                                          'a/p[@class="product__brand"]'.format(counter)).text
#         link = el.find_element_by_xpath('//div[@class="product-list__products ng-star-inserted"]/div[{}]'
#                                         '/div/div/a'.format(counter)).get_attribute('href')
#
#         tables[article] = [price, brand, link]


def get_data():
    print('Get prices')
    elems_var = '//div[@class="product-list__products ng-star-inserted"]/div'
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, elems_var)))
    elems = driver.find_elements_by_xpath(elems_var)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((
        By.XPATH, '//div[@class="product-list__products ng-star-inserted"]/div//div[last()]'
    )))
    counter = 0
    print('[begin gather loop]')
    time.sleep(3)
    for el in elems:
        counter += 1
        try:
            section_base = '//div[@class="product-list__products ng-star-inserted"]/div[{}]'.format(counter)
            # print(section_base)
            for bit in [
                '/div/div/a',
                '//span[@class="product__price-wrapper"]/span/span/span',
                '/div//a/p[@class="product__brand"]',
            ]:
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, section_base + bit)))
            article = re.sub("[^0-9]", '', el.find_element_by_xpath(
                '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                '/div/div/a'.format(counter)).get_attribute('href'))[:7]
            price = re.sub("[^0-9]", '', el.find_element_by_xpath(
                '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                '//span[@class="product__price-wrapper"]/span/span/span'.format(counter)).text)
            brand = el.find_element_by_xpath('//div[@class="product-list__products ng-star-inserted"]/div[{}]/div//'
                                             'a/p[@class="product__brand"]'.format(counter)).text
            link = el.find_element_by_xpath('//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                                            '/div/div/a'.format(counter)).get_attribute('href')

            tables[article] = [price, brand, link]
        except Exception as e:
            print("Exception detected: " + str(e))
            global failed_pages
            failed_pages['pages'].append(re.sub('[^0-9]', '', str(driver.current_url)[-3:]).replace('=', ''))
            """if driver.current_url == 'https://www.tsum.ru/catalog/obuv-18405/?availability=2':
                driver.refresh()
                time.sleep(4)
                article = re.sub("[^0-9]", '', el.find_element_by_xpath(
                    '//div[@class="product-list__products ng-star-inserted"]/div[{}]/div//a[@class="product__info"]'.format(counter)).get_attribute('href'))[:7]
                price = re.sub("[^0-9]", '', el.find_element_by_xpath(
                    '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                    '//span[@class="product__price-wrapper"]/span/span/span'.format(counter)).text)
                brand = el.find_element_by_xpath('//div[@class="product-list__products ng-star-inserted"]/div[{}]/div//'
                                                 'a/p[@class="product__brand"]'.format(counter)).text
                link = el.find_element_by_xpath('//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                                                '/div/div//a[@class="product__info"]'.format(counter)).get_attribute('href')

                tables[article] = [price, brand, link]"""
            # print('Reloading page...')
            # driver.refresh()
            # time.sleep(3)
            # WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, el.find_element_by_xpath(
            # '//div[@class="product-list__products ng-star-inserted"]/div[1]'
            # '/div/div/a'))))
            # try:
            #     article = re.sub("[^0-9]", '', el.find_element_by_xpath(
            #         '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
            #         '/div/div/a'.format(counter)).get_attribute('href'))[:7]
            #     price = re.sub("[^0-9]", '', el.find_element_by_xpath(
            #         '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
            #         '//span[@class="product__price-wrapper"]/span/span/span'.format(counter)).text)
            #     brand = el.find_element_by_xpath('//div[@class="product-list__products ng-star-inserted"]/div[{}]/div//'
            #                                      'a/p[@class="product__brand"]'.format(counter)).text
            #     link = el.find_element_by_xpath('//div[@class="product-list__products ng-star-inserted"]/div[{}]'
            #                                     '/div/div/a'.format(counter)).get_attribute('href')
            #
            #     tables[article] = [price, brand, link]
            # except Exception as e:
            #     print("Exception detected: " + str(e))
            #     global failed_pages
            #     failed_pages['pages'].append(re.sub('[^0-9]', '', str(driver.current_url)[-3:]).replace('=', ''))


    # print("Total: \n" + str(tables))
    print("Page {}".format(str(re.sub('[^0-9]', '', str(driver.current_url)[-3:]).replace('=', ''))))
    print('Prices obtained')


def write_data(url):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, last_page)))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    while driver.find_element_by_xpath(last_page).get_attribute('class') != pagination_class_selected:
        get_data()
        change_page()
        # try:
        #     if int(re.sub('[^0-9]', '', str(driver.current_url)[-3:]).replace('=', '')) % 100 == 0:
        #         break
        # except Exception as e:
        #     print("No page number, skipping: " + str(e))
        time.sleep(2)
    print(tables)


def write_file(url, filename):
    try:
        write_data(url)
    except Exception as e:
        print("Error caught, terminating: " + str(e))
    print('Writing file...')
    if not path.exists('{}.json'.format(filename)):
        with open('{}.json'.format(filename), 'w') as t:
            json.dump({}, t)

    with open('{}.json'.format(filename), 'r+', encoding='utf-8') as t:
        info = json.load(t)
        t.seek(0)
        tables.update(info)
        json.dump(tables, t, ensure_ascii=False, indent=4)
        t.truncate()
        print('...Completed writing')
        t.close()

    with open('failed_pages.json', 'w', encoding='utf-8') as p:
        json.dump(failed_pages, p, ensure_ascii=False, indent=4)
        p.close()


# write_file(url_m, 'obuv_m')
write_file(url_f, 'obuv_f')
# write_file(url_f2, 'obuv_f')
# write_file(url_f3, 'obuv_f')
# write_file(url_f4, 'obuv_f')

print("End: " + str(datetime.datetime.now()))
