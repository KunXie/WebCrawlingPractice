# 这个模块主要是存储模块，是整个proxy pool的核心

import redis
from random import choice
from error import PoolEmptyError
from settings import *


class RedisClient(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        redis类的实例初始化
        :param host:
        :param port:
        :param password:
        """
        # 获取redis数据库, 这里最后一个参数是什么意思？？ TODO
        self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)

    def add(self, proxy, score=INITIAL_SCORE):
        """
        往redis数据库中添加代理IP的方法
        :param proxy:
        :param score:
        :return:
        """
        # 再插入前要先判断collection中是不是已经存在
        if not self.db.zscore(REDIS_KEY, proxy):
            return self.db.zadd(REDIS_KEY, score, proxy)

    def score(self, proxy):
        """

        :return:
        """
        return self.db.zscore(REDIS_KEY, proxy)

    def random(self):
        """
        随机获取有效的代理, 从代理分数为最大值的标的中
        :return:
        """
        result = self.db.zrangebyscore(name=REDIS_KEY, min=MAX_SCORE, max=MAX_SCORE)
        if len(result) > 0:
            return choice(result)
        else:
            raise PoolEmptyError

    def decrease(self, proxy):
        """
        判断代理不可用时，则代理的当前分数减一, 当分数小于最低指时移除
        :param proxy:
        :return: 修改后的代理分数
        """
        score = self.db.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            # ⚠️这里的顺序和命令行的顺序不一样
            return self.db.zincrby(REDIS_KEY, proxy, -1)
        else:
            return self.db.zrem(REDIS_KEY, proxy)

    def exists(self, proxy):
        """
        判断这个代理是不是在数据库中存在
        :param proxy:
        :return:
        """
        return self.db.zscore(REDIS_KEY, proxy) is not None

    def max(self, proxy):
        """
        判断代理可用时，则直接将此代理的分数修改为最大值
        :param proxy:
        :return:
        """
        return self.db.zadd(REDIS_KEY, MAX_SCORE, proxy)

    def count(self):
        """
        显示数据库中所有代理的数量
        :param proxy:
        :return:
        """
        return self.db.zcard(REDIS_KEY)

    def count_validated(self):
        """
        显示数据库中所有满分代理的数量
        :param proxy:
        :return:
        """
        return len(self.all_validated())

    def all_validated(self):
        """
        显示数据库中所有满分代理的数量
        :param proxy:
        :return:
        """
        return self.db.zrangebyscore(name=REDIS_KEY, min=MAX_SCORE, max=MAX_SCORE)

    def all(self):
        """
        获取全部代理列表
        :return:
        """
        return self.db.zrangebyscore(REDIS_KEY, min=MIN_SCORE, max=MAX_SCORE)

    def remove_one(self, proxy):
        """
        删除代理
        :return: None
        """
        return self.db.zrem(REDIS_KEY, proxy)

    def remove_all(self):
        """
        删除数据中全部代理, 我自己加的
        :return: None
        """
        return self.db.zremrangebyscore(REDIS_KEY, min=MIN_SCORE, max=MAX_SCORE)


