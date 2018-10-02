# 这里封装一个web api接口方便爬虫随时调用

from flask import Flask, g  # g是flask的全局变量
from db import RedisClient

# TODO python公开接口的方式，此处还需学习一个
__all__ = ['app']

app = Flask(__name__)


def get_conn():
    if not hasattr(g, "redis"):
        g.redis = RedisClient()
    return g.redis


@app.route('/')
def index():
    return '<h2>Welcome to Proxy pool system</h2>'


@app.route('/random')
def get_proxy():
    conn = get_conn()
    return conn.random()


@app.route('/all_validated')
def get_all_validated():
    conn = get_conn()
    return str(conn.all_validated())


@app.route('/count_validated')
def count_validated():
    conn = get_conn()
    return str(conn.count_validated())


@app.route('/count')
def get_counts():
    conn = get_conn()
    return str(conn.count())


if __name__ == '__main__':
    app.run()
