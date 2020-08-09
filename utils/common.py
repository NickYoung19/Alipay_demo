# -*- coding: utf-8 -*-
import json
import os

import redis


# 项目环境配置信息
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_INFO = {}
try:
    CONFIG_FILE = BASE_DIR + '/.env'
    CONFIG_INFO = open(CONFIG_FILE).read()
    CONFIG_INFO = json.loads(CONFIG_INFO)
except Exception as E:
    print(E)
    print("没有找到项目env文件...")


def get_domain(request):
    """获取域名"""
    # 这里的域名应该为当前项目的域名，使用request.scheme 获取协议类型，使用request.META['HTTP_HOST'] 获取当前项目的域名
    domain = request.scheme + "://" + request.META['HTTP_HOST']

    return domain


class Redis(object):
    def __init__(self):
        self.r = None
        self.host = CONFIG_INFO.get("REDIS_HOST")
        self.port = CONFIG_INFO.get("REDIS_PORT")
        self.password = CONFIG_INFO.get("REDIS_PASSWORD")
        self.db = CONFIG_INFO.get("REDIS_DB")

    def connection(self):
        """连接 redis"""
        # decode_responses 将获取到的字节码转为字符串；
        # socket_connect_timeout 设置连接超时时间为 1s；
        # socket_time 设置连接建立后的读写操作超时为 1s；
        self.r = redis.StrictRedis(host=self.host,
                                   port=self.port,
                                   password=self.password,
                                   db=self.db,
                                   decode_responses=True,
                                   socket_connect_timeout=1,
                                   socket_timeout=1)
        return self.r
