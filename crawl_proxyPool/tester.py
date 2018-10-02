import asyncio
import time

from db import RedisClient
from settings import *
import aiohttp


class Tester(object):
    def __init__(self):
        self.redis = RedisClient()

    # 这里使用异步的方式测试请求库
    async def test_single_proxy(self, proxy):
        # TODO 控制同时连接的数量, 这里为还不知道这句话有什么卵用
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://' + proxy
                print("Start test proxy: ", proxy)
                async with session.get(TEST_URL, proxy=real_proxy, timeout=15) as response:
                    if response.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)
                        print('proxy validated:', proxy)
                    else:
                        self.redis.decrease(proxy)
                        print('illegal status code of response:', proxy)
            except Exception as e:
                self.redis.decrease(proxy)
                print('fail to test proxy: {0} due to >> {1}'.format(proxy, e))

    def run(self):
        """
        开始测试每一个proxy
        :return:
        """
        print("start testing the database")
        try:
            proxies = self.redis.all()
            loop = asyncio.get_event_loop()
            for i in range(0, len(proxies), BATCH_TEST_SIZE):
                test_proxies = proxies[i: i+BATCH_TEST_SIZE]
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
                time.sleep(5)
        except Exception as e:
            print("Tester wents wrong: ", e.args)

