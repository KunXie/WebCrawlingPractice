# 专门用来定义异常


class PoolEmptyError(Exception):
    # 此类的初始化
    def __init__(self):
        Exception.__init__(self)

    # 让实例输出str, 解释器
    def __str__(self):
        return "proxy is EMPTY!"
    __repr__ = __str__
