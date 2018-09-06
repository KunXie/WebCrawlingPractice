# 写一个爬网络小说的脚本 我发现有不少的小说网站做了翻爬虫处理，如何破解反爬虫我还在研究中 :(
# return a txt file

# 单循环，运行巨慢

import requests
from requests import RequestException
from bs4 import BeautifulSoup


def request_url(url):
    try:
        res = requests.get(url)
        # res.encoding = 'utf-8'
        res.encoding = 'gb2312'
        return res
    except RequestException:
        print(RequestException)
        return None


def extract_chapter_content(chapter_url):
    res = request_url(chapter_url)
    if not res:
        return None

    try:
        soup = BeautifulSoup(res.text, 'html.parser')
        html_chapter = soup.select('div#book_text')
        return html_chapter[0].text
    except Exception as SoupException:
        print(SoupException)
        return None


def get_chapters(url):
    res = request_url(url)
    if not res:
        return None

    try:
        soup = BeautifulSoup(res.text, 'html.parser')
        html_list = soup.select('div.article_texttitleb')[0].select('a')
        # print(html_list)
        for item in html_list:
            print('loading {} ING....'.format(item.text))           # 进度反馈
            # 获取每页需要的信息
            yield item.text + '\n' + url + item['href'] + '\n' + str(extract_chapter_content(url + item['href']))

    except Exception as SoupException:
        print(SoupException)
        return None


def save_to_txt(novel_name, content):
    with open('{}.txt'.format(novel_name), 'a', encoding='utf-8') as f:
        f.write(content + '\n')
        f.close()


def get_novel_name(url):
    res = request_url(url)
    if not res:
        return None
    try:
        soup = BeautifulSoup(res.text, 'html.parser')
        novel_name = soup.select('h1')[0].text
        print("let's download the novel {}".format(novel_name))     # 进度反馈
        return novel_name
    except Exception as SoupException:
        print(SoupException)
        return None


def main():
    # 拿到目录页的 url
    url = 'https://www.boluoxs.com/biquge/35/35352/'
    novel_name = get_novel_name(url)
    for content in get_chapters(url):
        save_to_txt(novel_name, content)

    print('Having All Done. :)')                                    # 进度反馈


if __name__ == '__main__':
    main()
