from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from os import path
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
driver.maximize_window()
driver.implicitly_wait(0.5)

url_brands = "https://www.rendez-vous.ru/catalog/brands/"

brands = [
    "Aldo Brue", "AGL", "BANU", "Bally", 'Bresciani', 'Brimarts', 'Carlo Visintini', 'Casadei', 'Casheart,',
    'Cerruti 1881', 'Cesare Casadei', 'Coccinelle', 'DKNY', 'Doria Maria', 'Doucal\'s', 'F_WD', 'Fabi', 'Fabrizio Lesi',
    'Ferre Milano', 'Flower Mountain', 'Franceschetti', 'Frasconi', 'Fratelli Rossetti', 'Fratelli Rossetti One',
    'Gianni Chiarini', 'Goose Tech', 'GUM', 'HIDE&JACK', 'Ice Play', 'Iceberg', 'In The Box', 'Inuikii',
    'John Galliano', 'John Richmond', 'Kalliste', 'Kat Maconie', 'Kate Spade', 'Lancaster', 'Landi', 'Le Silla',
    'Lemon Jelly', "L'Impermeabile", 'Marsell', 'Merola Gloves', 'Moose Knuckles', 'Moreschi', 'Moschino', 'Panchic',
    'Pantanetti', 'Parajumpers', 'Pasotti', 'Pertini', 'Pierre Cardin', 'Pollini', 'Portolano', 'Premiata',
    'Principe Di Bologna', 'RBRSL', "Reptile's House", 'Roberto Cavalli', 'Rocco P', 'Sergio Rossi', 'SPRAYGROUND',
    'Stemar', 'Stuart Weitzman', 'V SEASON', "VIC MATIE'", "Vic Matie", 'Voile Blanche', 'What For', 'Wolford', '3JUIN',
    'Premiata will be', 'Sprayground', 'Domrebel', 'GIUSEPPE ZANOTTI DESIGN', 'Giuseppe Zanotti Design',
    'GIUSEPPE ZANOTTI', 'Giuseppe Zanotti'
]

search_values = ['Wolford', 'RBRSL', "Rocco P", "DKNY", 'Flower Mountain', 'HIDE&JACK', 'Inuikii', 'Lancaster']

categories = [
    "Женское",
    'Мужское',
    "Детское"
]

iframe_ids = ['fl-545545']

show = "//li[@class='next']/a"
pagination_class_selected = 'page selected'
last_page = '//ul[@id="pagination_bottom"]/li[@class="last"]'
search_btn = '//*[@id="search-toggle"]'
search_bar = '//*[@id="Search_q"]'
failed_pages = {'pages': []}

output = xlsxwriter.Workbook('C:\\Users\\admin\\Documents\\outputs\\Rendez-vous {}.xlsx'.format(str(datetime.date.today())))
sheet = output.add_worksheet('Rendez-vous')
sheet.write('A1', 'Артикул')
sheet.write('B1', 'Цена')
sheet.write('C1', 'Старая цена')
sheet.write('D1', 'Скидка')
sheet.write('E1', 'Бренд')
sheet.write('F1', 'Артикул производителя')
sheet.write('G1', 'Ссылка')

tables = {}
count = 0
row = 2
closed = False

scrolled = False


def open_brands():
    driver.get(url_brands)

    for el in brands:
        global scrolled
        scrolled = False
        scroll_brands(el)


def open_brand(el):
    driver.find_element(By.XPATH, '//div[@class="js-quick-search-source brand-popover"]'
                                 '//a[contains(text(), "{}")]'.format(el.upper())).click()
    write_data()


def scroll_brands(el):
    driver.get(url_brands)
    driver.execute_script('window.scrollBy(0, -7000)')
    try:
        actions = ActionChains(driver)
        actions.move_to_element(driver.find_element_by_xpath('//div[@class="js-quick-search-source brand-popover"]'
                                                             '//a[contains(text(), "{}")]'.format(el.upper()))).perform()
        open_brand(el)
    except Exception as e:
        print(el.upper() + " not found in the list, skipping.")
        print(e)
    global scrolled
    scrolled = True


def search():
    driver.get(url_brands)
    for b in search_values:
        # WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//button[@class="search-mobile__open-button"]')))
        driver.find_element(By.XPATH, search_btn).click()
        driver.find_element(By.XPATH, search_bar).click()
        driver.find_element(By.XPATH, search_bar).clear()
        driver.find_element(By.XPATH, search_bar).send_keys(b)
        driver.find_element(By.XPATH, search_bar).send_keys(Keys.ENTER)
        time.sleep(2)
        try:
            write_data()
        except Exception as e:
            print("Failure in finding elements")


def change_page():
    try:
        # driver.execute_script('window.scrollBy(0, -800)')
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, show)))
        change_page = driver.find_element(By.XPATH, show)
        actions = ActionChains(driver)
        actions.move_to_element(change_page).perform()
        change_page.click()
        time.sleep(2)
    except Exception as e:
        for iframe in iframe_ids:
            try:
                print("Attempting to close iframe")
                frame = driver.find_element(By.XPATH, iframe)
                driver.switch_to.frame(frame)
                driver.find_element_by_xpath('//div[@class="widget__close"]').click()
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


def get_data():
    # driver.execute_script('window.scrollBy(0, -7000)')
    print('Get prices')
    elems_var = '//ul[@class="list-items list-view-1 js-list-items"]/li'
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, elems_var)))
    elems = driver.find_elements(By.XPATH, elems_var)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((
        By.XPATH, '//ul[@class="list-items list-view-1 js-list-items"]/li[last()]'
    )))
    counter = 0
    print('[begin gather loop]')
    print(elems)
    for el in elems:
        counter += 1
        driver.execute_script('window.scrollBy(0, {})'.format(counter * 20))
        try:
            title, price, brand, link, price_old = [None] * 5  # assign None to 5 variables
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,
                '//ul[@class="list-items list-view-1 js-list-items"]/li[{}]'.format(counter))))
            productinfo = json.loads(str(el.find_element_by_xpath(
                '//ul[@class="list-items list-view-1 js-list-items"]/li[{}]'
                    .format(counter)).get_attribute('data-productinfo')).replace('\'', '"'))
            try:
                title = productinfo['name'].replace(productinfo['brand'] + ' ', '')
            except:
                print('Failed to obtain price')
            # id = productinfo['id']
            try:
                price = float(productinfo['price'])
            except:
                print('Failed to obtain price')
            try:
                brand = productinfo['brand']
            except:
                print("Failed to obtain brand")
            try:
                link = str(el.find_element(
                    By.XPATH,
                    '//ul[@class="list-items list-view-1 js-list-items"]/li[{}]//a[@class="item-link"]'.format(counter))
                           .get_attribute('href'))
            except:
                print("Failed to obtain link")

            try:
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located)
                price_old = el.find_element(By.XPATH, '//ul[@class="list-items list-view-1 js-list-items"]'
                                                     '/li[{}]//span[@class="item-price-old"]/span'.format(counter)).get_attribute(
                    'content')
            except Exception as e:
                print("No discount for element {}".format(counter))
                print(e)

            tables[title] = [price, price_old, brand, link]
            global row
            sheet.write('A' + str(row), title)
            sheet.write('B' + str(row), price)
            sheet.write('C' + str(row), price_old)
            sheet.write('D' + str(row), brand)
            sheet.write('E' + str(row), link)
            row += 1
        except Exception as e:
            print("Exception detected while parsing: ")
            print(e)
            global failed_pages
            failed_pages['pages'].append(re.sub('[^0-9]', '', str(driver.current_url)[-3:]).replace('=', ''))
    print("Page {}".format(str(re.sub('[^0-9]', '', str(driver.current_url)[-3:]).replace('=', ''))))
    print('Prices obtained')


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
            search()
            driver.quit()
        output.close()
    except Exception as e:
        print("Error caught, terminating: " + str(e))
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


def run():
    write_file(url_brands, 'C:\\Users\\admin\\Documents\\outputs\\rendez-vous_brands_full', params=1)
    write_file(url_brands, 'C:\\Users\\admin\\Documents\\outputs\\rendez-vous_brands_full', params=2)

    print("End: " + str(datetime.datetime.now()))


if __name__ == '__main__':
    run()
