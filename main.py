from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
import json
import time
import datetime
import xlsxwriter

print("Start: " + str(datetime.datetime.now()))

options = Options()
prefs = {"profile.managed_default_content_settings.images": 2}
# prefs = {"profile.managed_default_content_settings.images": 2, "profile.default_content_setting_values.notifications" : 2}
options.add_experimental_option('prefs', prefs)
# driver = webdriver.Chrome(ChromeDriverManager().install())
# driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.implicitly_wait(6)

url_f = "https://www.tsum.ru/catalog/obuv-18405/"
url_m = "https://www.tsum.ru/catalog/obuv-18440/"
url_f_k = "https://www.tsum.ru/catalog/obuv_dlya_devochek-3442/"
url_m_k = "https://www.tsum.ru/catalog/obuv_dlya_malchikov-3425/"

present = '//*[@id="catalog"]/div[2]/div/div/div/div[1]/filter-desktop/div[5]/div/div/div/div/div[3]/div/perfect-scrollbar/div/div[1]/div/div[1]/div/label'
show = "//div[@title='Следующая страница']"
pagination_class_selected = 'pagination__link pagination__link_full pagination__link_state_current ng-star-inserted'

tables = {}
count = 0

# workbook = xlsxwriter.Workbook('obuv_m.xlsx')
# worksheet = workbook.add_worksheet()

def write_data():
    time.sleep(1)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, present)))
    driver.find_element_by_xpath(present).click()
    time.sleep(1)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@id="attrId"]/div/div[2]/span/a[@title="Последняя страница"]')))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    while driver.find_element_by_xpath('//div[@id="attrId"]/div/div[2]/span/a[@title="Последняя страница"]').get_attribute('class') != pagination_class_selected:
        try:
            driver.find_element_by_xpath(show).click()
            time.sleep(2)
        except:
            try:
                print("Attempting to close iframe")
                iframe = driver.find_element_by_id("fl-297767")
                driver.switch_to.frame(iframe)
                driver.find_element_by_xpath('//button[@class="close"]').click()
                driver.switch_to.default_content()
                driver.find_element_by_xpath(show).click()
            except:
                print("Attempting to close lead form")
                try:
                    driver.execute_script("document.querySelector('.lead-form__close').click();")
                    driver.find_element_by_xpath(show).click()
                except Exception as e:
                    print("Attempting to refresh the page")
                    driver.refresh()
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, show)))
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    driver.find_element_by_xpath(show).click()
            time.sleep(2)

        print('Get prices')
        elems = driver.find_elements_by_xpath('//div[@class="product-list__products ng-star-inserted"]/div')
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((
            By.XPATH, '//div[@class="product-list__products ng-star-inserted"]/div//div[last()]'
        )))
        counter = 0
        for el in elems:
            counter += 1
            try:
                article = re.sub("[^0-9]", '', el.find_element_by_xpath(
                    '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                    '/div/div/a'.format(counter)).get_attribute('href'))[:7]
                price = re.sub("[^0-9]", '', el.find_element_by_xpath(
                    '//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                    '//span[@class="product__price-wrapper"]/span/span/span'.format(counter)).text)
                brand = el.find_element_by_xpath('//div[@class="product-list__products ng-star-inserted"]/div[1]/div//'
                                                 'a/p[@class="product__brand"]'.format(counter)).text
                link = el.find_element_by_xpath('//div[@class="product-list__products ng-star-inserted"]/div[{}]'
                                                '/div/div/a'.format(counter)).get_attribute('href')

                # worksheet.write('A{}'.format(counter), article)
                # worksheet.write('B{}'.format(counter), price)
                # worksheet.write('C{}'.format(counter), brand)
                # worksheet.write('D{}'.format(counter), link)

                tables[article] = [price, brand, link]
                # print(tables)
            except Exception as e:
                print("Exception detected: " + str(e))
                last_url = driver.current_url
                driver.close()
                driver.get(last_url)
                write_data()
        print("Total: \n" + str(tables))
        print('Prices obtained')
        time.sleep(1)


# for url in [url_f, url_m]:
driver.get(url_f)
try:
    write_data()
except Exception as e:
    print("Error caught, terminating: " + str(e))
print('Writing file...')
with open('obuv_f.json', 'w') as t:
    json.dump(tables, t, ensure_ascii=False, indent=4)
    print('...Completed writing')

# workbook.close()

print("End: " + str(datetime.datetime.now()))
