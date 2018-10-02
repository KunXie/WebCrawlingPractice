# 定义「常量」和「通用函数」的地方

import requests

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PASSWORD = None
REDIS_KEY = 'proxies'   # 在redis中，collection的key名

# 代理分数:
# 100分为可用，检测一次不可用则减1分，低于50分则删除出数据库；检测一次可用则直接变成100分；未检测的新代理初始得分80分。
MAX_SCORE = 100
MIN_SCORE = 50
INITIAL_SCORE = 80

# 判断成功返回的status code，302是重定向redirect
VALID_STATUS_CODES = [200, 302]

# 代理池数量界限, 代理池最大ip数量
POOL_UPPER_THRESHOLD = 10000


TESTER_CYCLE = 5*60   # 检查周期，五分钟测试一次
GETTER_CYCLE = 60*60  # 获取周期, 一个小时获取一次就好了

TEST_URL = 'http://www.baidu.com'   # 测试IP的网站

# 代理池调用API的配置
API_HOST = '0.0.0.0'
API_PORT = 5555

# 各项开关
TESTER_ENABLED = True
GETTER_ENABLED = True
API_ENABLED = True

# 每一批的最大测试量
BATCH_TEST_SIZE = 10

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
}


def fetch_html(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code in VALID_STATUS_CODES:
            return response.text
        print("Bad response")
        return None
    except Exception as e:
        print("something wrong when fetching HTML due to ", e)
        return None

