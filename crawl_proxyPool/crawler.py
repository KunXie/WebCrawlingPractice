# 获取模块，此模块用于抓取各网站上的免费高匿代理

from settings import fetch_html
from bs4 import BeautifulSoup


# ⚠️知识点！️类本身就是一个对象，它是一个type的实例，既metaclass元类, 通过它来自定义继承此metaclass的初始化条件, 这里要好好思考
class ProxyMetaclass(type):
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for key, value in attrs.items():
            if 'crawl_' in key:
                attrs['__CrawlFunc__'].append(key)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class Crawler(object, metaclass=ProxyMetaclass):
    def get_proxies(self, callback):
        """
        调用从各网站抓取代理的函数，返回成功抓取代理的list
        :param callback: 抓取代理的函数名称
        :return: 一个含有代理proxy的列表
        """
        proxies = []
        for proxy in eval("self.{}()".format(callback)):
            print("Successfully fetch proxy:", proxy)
            proxies.append(proxy)
        return proxies

    # 下面都是从各网站抓取代理的函数，应定期检测这些网站是否可用，相应函数是否需要调整, TODO 这里还可以优化，代理网站有直接提供接口
    def crawl_ip3366(self):
        """
        目标网站http://www.ip3366.net, 抓取国内外高匿名代理，免费代理24小时更新一次
        :return:
        """
        # 只获取高匿代理
        for style in [1, 3]:
            for page in range(1, 8):
                url = "http://www.ip3366.net/free/?stype={0}&page={1}".format(style, page)
                html = fetch_html(url)
                if html is None:
                    print("can't crawl proxy from this url:", url)
                    continue
                soup = BeautifulSoup(html, 'lxml')
                for item in soup.find_all('tr'):
                    # 排除为[]的情况
                    if item.find_all("td"):
                        ip = item.find_all("td")[0].text
                        port = item.find_all("td")[1].text
                        yield ":".join([ip, port])

    def crawl_kuaidaili(self):
        """
        目标网站: https://www.kuaidaili.com, 抓取国内高匿代理，前十页就好了，后面的代理都太老了, 每一个小时更新一次
        :return:
        """
        for page in range(1, 11):
            url = "https://www.kuaidaili.com/free/inha/{}/".format(page)
            html = fetch_html(url)
            if html is None:
                print("can't crawl proxy from this url:", url)
                continue
            soup = BeautifulSoup(html, 'lxml')
            for m, n in zip(soup.find_all('td', attrs={"data-title": "IP"}),
                           soup.find_all('td', attrs={"data-title": "PORT"})):
                yield ":".join([m.text, n.text])

    def crawl_66ip(self):
        """
        目标网站: http://www.66ip.cn, 抓取国内高匿代理，前十页就好了，后面的代理都太老了, 每一个小时更新一次
        :return:
        """
        for page in range(1, 11):
            url = "http://www.66ip.cn/{}.html".format(page)
            html = fetch_html(url)
            if html is None:
                print("can't crawl proxy from this url:", url)
                continue
            soup = BeautifulSoup(html, 'lxml')
            items = soup.find_all('tr')
            # 这里要剔出前面两个无用元素
            items.pop(0)
            items.pop(0)
            for item in items:
                yield ":".join([item.find_all('td')[0].text, item.find_all('td')[1].text])


    # , 先写三个后面再加 TODO
    # def crawl_xicidaili(self):
    #     """
    #     这个西刺代理好棒，居然直接提供API
    #     :return:
    #     """




