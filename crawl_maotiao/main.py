import asyncio
import os
from hashlib import md5
from multiprocessing.pool import Pool
import requests
from bs4 import BeautifulSoup
import re
from config import *


def get_album_url_list(page_url):
    try:
        res = requests.get(page_url, headers=HEADERS, timeout=15)
        res.encoding = 'gb2312'
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            items = soup.find(name="dl", attrs={"class": "list-left public-box"}).find_all(name="a",
                                                                                          attrs={"target": "_blank"})
            album_url_list = []
            for item in items:
                album_url_list.append(item.attrs.get('href'))
            return album_url_list
        return None
    except Exception as e:
        print("can't get album url from this page due to ", e)
        return None


def compose_album_page_url(album_info_dict):
    """
    通过传递的dict 参数来合成这个album 的页码url list
    :param dic_data:
    :return:
    """
    album_page_url_list = [album_info_dict.get('album_url')]
    total_page = int(album_info_dict.get('total_page'))
    for i in range(2, total_page + 1):
        url_apart_list = album_info_dict.get('album_url').split('/')
        last_part_list = url_apart_list[-1].split('.')
        last_part_list[0] = last_part_list[0] + '_{}'.format(i)
        url_apart_list[-1] = '.'.join(last_part_list)
        new_url = '/'.join(url_apart_list)
        album_page_url_list.append(new_url)
    album_info_dict.pop('album_url')
    album_info_dict["album_page_url_list"] = album_page_url_list
    return album_info_dict


async def get_album_info_dict(album_url):
    try:
        res = requests.get(album_url, headers=HEADERS, timeout=15)
        res.encoding = 'gb2312'
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            string = soup.find(name='span', attrs={'class': 'page-ch'}).text
            total_page = re.search('[1-9][0-9]', string).group(0)
            album_info_dict = {
                "album_title": soup.find('h5').text,
                "total_page": total_page,
                "album_url": album_url
            }
            return compose_album_page_url(album_info_dict)
        return None
    except Exception as e:
        print("can't get album url from this page due to ", e)
        return None


async def get_album_info_tasks(album_url_list):
    tasks = []

    for album_url in album_url_list:
        tasks.append(asyncio.ensure_future(get_album_info_dict(album_url)))

    return await asyncio.gather(*tasks)


def save_image(album_title, img_addres):
    file_path = SECTION_NAME + os.path.sep + album_title
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    try:
        response = requests.get(img_addres, headers=HEADERS, timeout=10)
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


async def download_img(album_title, album_page_url):
    try:
        res = requests.get(album_page_url, headers=HEADERS, timeout=15)
        res.encoding = 'gb2312'
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            img_address = soup.find(name='img').attrs['src']
            # 传入 album_title & img_address 然后下载
            save_image(album_title, img_address)
    except Exception as e:
        print("can't can download this img from {0} due to {1}".format(album_page_url, e))
        return None


async def download_tasks(album_info_dict):
    tasks = []
    for album_page_url in album_info_dict.get('album_page_url_list'):
        tasks.append(asyncio.ensure_future(download_img(album_info_dict.get('album_title'), album_page_url)))
    return await asyncio.gather(*tasks)


def main(section_page_url):
    album_url_list = get_album_url_list(section_page_url)
    # 排除 album_url_list == None 的现象
    if not album_url_list:
        print("no album url in this page")
        return None

    loop = asyncio.get_event_loop()
    try:
        # 循环 1,
        album_info_dict_list = loop.run_until_complete(get_album_info_tasks(album_url_list))
        print(album_info_dict_list)
        # 循环 2, 每一个专辑使用一个协程下载
        for album_info_dict in album_info_dict_list:
            if album_info_dict:
                loop.run_until_complete(download_tasks(album_info_dict))
                print('完成专辑：', album_info_dict.get('album_title'))
            else:
                print("no data in this album")
        loop.close()
    except RuntimeError as e:
        print(section_page_url)
        print("something went wrong due to", e)
        loop.close()


def url_list():
    urllist = [SECTION_URL]
    url = SECTION_URL.rstrip('/')

    for i in range(2, MAX_PAGE+1):
        url_apart = url.split('/')
        url_apart.append("index_{}.html".format(i))
        new_url = '/'.join(url_apart)
        urllist.append(new_url)
    return urllist


if __name__ == '__main__':
    urllist = url_list()
    pool = Pool(4)
    pool.map(main, urllist)
    pool.join()
    pool.close()
