
from urllib.parse import urlencode
from multiprocessing import Pool
from selenium import webdriver
from bs4 import BeautifulSoup
from hashlib import md5
import requests
import json
import os


def parse_ajax(ajax_url):
    """
    :param ajax_url:
    :return: from ajax html, pick street snaps out, and return them in a list
    """
    headers = {
        "authority": "www.toutiao.com",
        "method": "GET",
        "accept-encoding": "gzip, deflate, br",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36"
    }
    res = requests.get(ajax_url, headers=headers)
    data = json.loads(res.text)
    street_naps_url_list = []
    for item in data['data']:
        if item.get('open_url'):
            street_naps_url_list.append("https://www.toutiao.com" + item.get('open_url'))
        else:
            print("not a street snap url......")
    return street_naps_url_list


def save_image(item):
    file_path = 'street_snaps' + os.path.sep + item.get('title')
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    try:
        response = requests.get(item.get('image'))
        if response.status_code == 200:
            img_path = file_path + os.path.sep + '{0}.{1}'.format(md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(img_path):
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                print('Downloaded image path is {}'.format(img_path))
            else:
                print('Already Downloaded {}'.format(img_path))
    except Exception as e:
        print('Failed to Save Image due to {}'.format(e))


def get_image(street_snaps_url):
    """
    :param street_snaps_url:
    :return: 返回这个街拍组图的每一张 image address
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=chrome_options)
    try:
        browser.get(street_snaps_url)

        soup = BeautifulSoup(browser.page_source, 'lxml')
        title = soup.find("title").text
        for item in soup.find_all("li", attrs={"class": "image-item"}):
            yield {
                "title": title,
                "image": item.find('img').attrs["data-src"]
            }
    except Exception as e:
        print("sth went went wrong during getting images due to {}.\nReload....".format(e))
        get_image(street_snaps_url)


def main(offset):
    params = {
        "offset": offset,
        "format": "json",
        "keyword": "街拍",
        "autoload": "true",
        "count": 20,
        "cur_tab": 1,
        "from": "search_tab"
    }
    url = "https://www.toutiao.com/search_content/?" + urlencode(params)
    for street_snaps_url in parse_ajax(url):
        for item in get_image(street_snaps_url):
            save_image(item)


OFFSET_START = 0
OFFSET_END = 0

if __name__ == "__main__":
    pool = Pool()
    offset_list = [x * 20 for x in range(OFFSET_START, OFFSET_END + 1)]
    pool.map(main, offset_list)
    pool.close()
    pool.join()