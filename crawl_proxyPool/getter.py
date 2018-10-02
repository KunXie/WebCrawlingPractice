# 动态的调用crawl开头的方法，获取到代理之后将它存储在数据库中
# 存储模块和抓取模块的交互

from db import RedisClient
from crawler import Crawler
from settings import *
import sys


class Getter(object):
    def __init__(self):
        self.redis = RedisClient()
        self.crawler = Crawler()

    def is_over_threshold(self):
        """
        判断是否数据库中的代理达到了最大值
        :return:
        """
        if self.redis.count() >= POOL_UPPER_THRESHOLD:
            return True
        else:
            return False

    def run(self):
        """

        :return:
        """
        print("start fetching proxies......")
        if not self.is_over_threshold():
            for callback_label in range(self.crawler.__CrawlFuncCount__):
                callback = self.crawler.__CrawlFunc__[callback_label]
                # 获取代理
                proxies = self.crawler.get_proxies(callback)
                # 刷新输出, 目前不知道有什么作用
                sys.stdout.flush()
                for proxy in proxies:
                    self.redis.add(proxy)



