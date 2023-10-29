from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import openpyxl
from time import time


main_url = 'https://b2b.sanwell.biz/main'
chrome_options = Options()


def time_logger(func):
    '''time-logger'''
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        log = end_time-start_time
        print(f' Done  at {log} seconds')
        return result
    return wrapper


@time_logger
def main(url):
    ''' This func get our url, open it with selenium
    skip authentication, then go to categories, subcategories, price
    parse all products and prices. In the end return json'''
    result = []
    items = {}
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1920, 1080)
    driver.get(url)
    demo_link = driver.find_element(By.XPATH, '//a[@href="/demo"]')
    demo_link.click()
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    divs = soup.find_all('div', class_="item clearfix")
    categories = {}
    for div in divs:
        links = div.find('a')
        href = links.get('href')
        categoria = div.text.strip()
        categories.update({categoria: href})
    for caty, category in categories.items():
        pattern = 'https://b2b.sanwell.biz'
        new_url = pattern+category
        driver.get(new_url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        pagies_with_price = {}
        pt30 = soup.find_all('td', class_="p-t-30")
        for td in pt30:
            lnk = td.find('a')
            hreff = lnk.get('href')
            group = lnk.get('alt')
            pagies_with_price.update({group: hreff})
        tds = soup.find_all('td', class_="text-center p-l-15 bage-box")
        for td in tds:
            lnk = td.find('a')
            hreff = lnk.get('href')
            group = lnk.get('alt')
            pagies_with_price.update({group:hreff})
        del pagies_with_price[None]
        for key, page in pagies_with_price.items():
            path = pattern+page
            uri = None
            while True:
                if uri:
                    driver.get(pattern+uri)
                else:
                    driver.get(path)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                tr = soup.find_all('tr')
                try:
                    for i in tr[1:21]:
                        a = i.find('a')
                        price = i.find('em')
                        p = str(price)
                        p = p.replace('</em>', '')
                        p =p.replace('<em>', '')
                        res = a.text
                        if price!=None:
                            if res in items:
                                pass
                            else:
                                items.update({res: p})
                                row = [caty, key, res, p]
                                print(row)
                                result.append(row)
                except AttributeError as erorr:
                    print(erorr)
                try:
                    next_ = soup.find('li', class_='next').find('a')
                    uri = next_.get('href')
                    print(uri)
                    disabled = soup.find('li', class_='next disabled')
                    if not next_:
                        break
                    if disabled:
                        break
                except:
                    break
    with open('json', 'w') as fh:
        json.dump({'result': result}, fh)
    driver.quit()


@time_logger
def from_json_to_xls():
    '''Simple func to convert json-file to xlsx object'''
    with open('json', 'r') as fd:
        js = json.load(fd)
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["Category", "Subcaotegory", "Name", "Price"])
    rows = js['result']
    for row in rows:
        sheet.append(row)
    workbook.save('Sanwell.xlsx')


if __name__ == '__main__':
    main(main_url)
    from_json_to_xls()
