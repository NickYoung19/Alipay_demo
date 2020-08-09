# -*- coding: utf-8 -*-
# @Author      : Nick
# @File        : order_monitor.py  v1.0
# @Contact     : PENGYANG19@163.COM
# @CreateTime  : 2020-08-09 14:30:11
# Copyright (C) 2020 Nick Ltd. All rights reserved.
import json
import time

import requests
from utils.common import Redis

# 创建Redis对象并连接redis数据库
redis = Redis().connection()
# 创建pub_sub对象，该对象订阅一个频道并侦听新消息：
pub_sub = redis.pubsub()


# 定义触发事件
def event_handler(msg):
    # {'type': 'pmessage', 'pattern': '__keyevent@0__:expired', 'channel': '__keyevent@0__:expired', 'data': 'nick_1'}
    print('捕获到订阅消息：', msg)
    data = msg.get('data')  # 获取键，创建订单设置SETEX key seconds value
    data_list = data.split('_')
    if data_list[0] == 'nick':  # 在创建订单，写入redis key时加上prefix前缀：nick_
        order_id = data_list[-1]
        print(f'过期的订单id：{order_id}')
        url = 'http://192.168.0.106:8008/payment/cancel_order/'
        result = requests.post(url=url, json=dict(order_id=order_id))
        data = json.loads(result.content.decode("UTF-8"))
        print("事件执行返回状态：", data)


# 订阅redis键空间通知，__keyevent@0__:expired 的 0 表示数据库index，表示只触发本数据库的过期事件
pub_sub.psubscribe(**{'__keyevent@0__:expired': event_handler})


def main():
    # 主方法，死循环，不停的接收订阅的通知
    while True:
        message = pub_sub.get_message()
        if message:
            # {'type': 'psubscribe', 'pattern': None, 'channel': '__keyevent@0__:expired', 'data': 1}
            print(f"订阅的消息: {message}")
            print('正在监听过期订单。。。。。。')
            time.sleep(0.5)
        else:
            time.sleep(0.5)


if __name__ == '__main__':
    main()
