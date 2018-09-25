#!/usr/bin/env python3

from multiprocessing.pool import Pool
from bs4 import BeautifulSoup
from hashlib import md5
from config import *
import requests
import asyncio
import os
import re


def get_album_url_list(section_page_url):
    """
    函数的目的写在函数名里了
    :param section_page_url:
    :return: 返回的是这个页面所有album的url
    """
    try:
        res = requests.get(section_page_url, headers=HEADERS, timeout=TIMEOUT)
        res.encoding = 'gb2312'
        # 排除 Bad response
        if res.status_code != 200:
            print("这一页的回复不正常 Bad response:", section_page_url)
            return None
        # 分析语句
        soup = BeautifulSoup(res.text, 'lxml')
        items = soup.find_all(name="li", attrs={'class': 'picimg'})
        album_url_list = []
        for item in items:
            # 去除是None的情况
            if item:
                album_url_list.append(item.find('a').attrs['href'])
        # 排除 album_url_list == [] 的情况
        if album_url_list:
            return album_url_list
        else:
            return None
    except Exception as e:
        print("can't get album url from this page {0} due to {1}".format(section_page_url, e))
        return None


async def get_album_info_dict(album_url):
    """
    函数的目的写在函数名里了
    :param album_url: 每一个album的url
    :return: 返回一个dict, 里面装有album的名称和每一页的url
    """
    try:
        res = requests.get(album_url, headers=HEADERS, timeout=TIMEOUT)
        res.encoding = 'gb2312'
        # 排除 Bad response
        if res.status_code != 200:
            print("此专辑url:{} 非正常回复 ".format(album_url))
            return None

        soup = BeautifulSoup(res.text, 'lxml')
        album_title = soup.find('h1').text.strip()
        total_page = int(re.search('[0-9]{1,2}', soup.find('li').text).group(0))
        # 取得album每一页的url
        album_page_url_list = [album_url]
        for i in range(2, total_page + 1):
            url_list = album_url.split('/')
            last_part = url_list[-1]
            last_part_list = last_part.split('.')
            last_part_list[0] = last_part_list[0] + '_{}'.format(i)
            url_list[-1] = '.'.join(last_part_list)
            new_url = '/'.join(url_list)
            album_page_url_list.append(new_url)

        return {
            "album_title": album_title,
            "album_page_url_list": album_page_url_list
        }

    except Exception as e:
        print("can't get album info from {0} due to {1}".format(album_url, e))
        return None


async def get_album_info_tasks(album_url_list):
    """
    task函数都是用来处理协程任务的中介函数
    :param album_url_list:
    :return:
    """
    tasks = []

    for album_url in album_url_list:
        tasks.append(asyncio.ensure_future(get_album_info_dict(album_url)))

    return await asyncio.gather(*tasks)


def save_image(album_title, img_address):
    """
    通过传入的参数，在互联网中下载文件并保存
    :param album_title: 文件的标题
    :param img_address: 图片的地址
    :return:
    """
    file_path = SECTION_NAME + os.path.sep + album_title
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    try:
        response = requests.get(img_address, headers=HEADERS, timeout=TIMEOUT)
        if response.status_code == 200:
            img_path = file_path + os.path.sep + '{0}.{1}'.format(md5(response.content).hexdigest(), 'jpg')
            if not os.path.exists(img_path):
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                print('完成下载的文件 path is {}'.format(img_path))
            else:
                print('已经下载 {}'.format(img_path))
    except Exception as e:
        print('保存文件失败, 因为 {}'.format(e))


async def download_img(album_title, album_page_url):
    """
    这里的处理主要是将album_page_url转换成img_address 然后传入save_image
    :param album_title:
    :param album_page_url:
    :return:
    """
    try:
        res = requests.get(album_page_url, headers=HEADERS, timeout=TIMEOUT)
        res.encoding = 'gb2312'
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'lxml')
            img_address = soup.find(name='img').attrs['src']
            # 传入 album_title & img_address 然后下载
            save_image(album_title, img_address)
    except Exception as e:
        print("不能从 {0} 下载此文件, 因为 {1}".format(album_page_url, e))
        return None


async def download_tasks(album_info_dict):
    """
    task函数都是用来处理协程任务的中介函数
    :param album_info_dict:
    :return:
    """
    tasks = []

    for album_page_url in album_info_dict.get('album_page_url_list'):
        tasks.append(asyncio.ensure_future(download_img(album_info_dict.get('album_title'), album_page_url)))

    return await asyncio.gather(*tasks)


def main(section_page_url):
    """
    主程序, 主要逻辑都在这里:
    :param section_page_url: 接受的是section其中一页的URL
    :return:
    """
    # 第一步找出每一页当中的album, 返回一个album_url_list
    album_url_list = get_album_url_list(section_page_url)
    # 排除album_url_list是None的现象
    if not album_url_list:
        print("*********************************************************这一页提取不出album来:", section_page_url)
        return
    else:
        print('*********************************************************开启一个新的进程：', album_url_list[0])

    # 协程开始语句
    loop = asyncio.get_event_loop()
    try:
        # 第一层循环，进入album url，返回所需要的信息，dict{album_title, album_url_list}形式
        album_info_dict_list = loop.run_until_complete(get_album_info_tasks(album_url_list))
        # 第二层循环, 每一个专辑使用一个协程下载
        for album_info_dict in album_info_dict_list:
            if album_info_dict:
                try:
                    print("-----开始下载专辑:", album_info_dict.get('album_title'))                            # 查看进度
                    # 第三层循环，在每一个专辑的下载中再次使用协程
                    loop.run_until_complete(download_tasks(album_info_dict))
                    print('-----完成专辑：', album_info_dict.get('album_title'))                               # 查看进度
                except Exception as e:
                    # 在捕捉到异常之后，抛出，并且让程序继续
                    print("------这个专辑{0}的下载出了问题{1}".format(album_info_dict.get('album_title'), e))
                    continue
            else:
                print("-----这个专辑没有数据")                                                                  # 查看进度
    except RuntimeError as e:
        print("这一页{0}事件循环出了问题, 因为{1}:".format(section_page_url, e))
    finally:
        print("*********************************************************此进程关闭", album_url_list)
        return

    # !!!! 这里是一个教训 不要在进程中关闭loop，会影响其他进程的使用
    # finally:
    #     loop.close()


def param_list():
    """
    :return: 根据config的常数，自动产生section_page_url参数（list形式)，并返回
    """
    param = []
    for page_num in range(1, MAX_PAGE + 1):
        new_url = URL + 'list_{0}_{1}.html'.format(LIST_NUM, page_num)
        param.append(new_url)
    return param


# 整个脚本开始的地方，逻辑很简单，开启多进程，每一个进程中传入section_page_url, 然后运行至结束
if __name__ == '__main__':
    params = param_list()
    pool = Pool(4)
    pool.map(main, params)
    pool.close()
