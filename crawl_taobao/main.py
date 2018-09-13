# 搜索关键词 selenim 驱动浏览器
# 分析页码并翻页
# 分析提取商品内容PyQuery
# 存储到 mongodb
import pymongo

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
from bs4 import BeautifulSoup
from config import *

# 不打开浏览器
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options = chrome_options)
wait = WebDriverWait(browser, 10)


def get_products_info():
    html = browser.page_source
    try:
        soup = BeautifulSoup(html, 'lxml')
        data = soup.select('div.item.J_MouserOnverReq')
        for item in data:
            item = {
                'title': item.find(('div'), attrs={'class': 'row row-2 title'}).text.strip(),
                'price': item.find(('strong')).text,
                'shop': item.find(('div'),  attrs={'class': 'shop'}).text.strip(),
                'location': item.find(('div'),  attrs={'class': 'location'}).text.strip(),
                'img_url': item.find('img', attrs={'class': 'J_ItemPic img'}).attrs['data-src']

            }
            save_to_mongo(item)
    except Exception as e:
        print(e)
        print('something went wrong during extracting info')
        return None


def goto_page(page_num):
    """
    抓取索引页
    :param page_num: 页码
    """
    print('正在抓取第', page_num, '页')
    try:
        url = 'https://s.taobao.com/search?q=' + quote(KEYWORD)
        browser.get(url)
        # 转入特定页码
        if page_num > 1:
            input_ele = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.input.J_Input')))
            submit_ele = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.btn.J_Submit')))
            input_ele.clear()
            input_ele.send_keys(page_num)
            submit_ele.click()
        # 核对当前页码
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'li.item.active span.num'), str(page_num)))
        # 等待加载商品信息
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.items')))
        get_products_info()
    except Exception as e:
        print(e)
        print('something bad happended, reloaded..')
        goto_page(page_num)


def save_to_mongo(content):
    client = pymongo.MongoClient(MONGO_URL)
    db = client[MONGO_DB]
    try:
        if db[MONGO_COLLECTION].insert(content):
            print('save to mongo successfully')
    except Exception as e:
        print(e, 'sth goes wrong when saving to db')


def main():
    for page_num in range(1, MAX_PAGE + 1):
        goto_page(page_num)


if __name__ == '__main__':
    main()
