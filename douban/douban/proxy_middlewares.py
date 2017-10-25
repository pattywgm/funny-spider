#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@file: proxy_middlewares.py
@time: 17/10/24  下午6:18
@desc: ip代理
"""
import random

from utils.my_utils import get_redis_conn


class CustomProxyMiddleWare(object):
    def __init__(self):
        r = get_redis_conn()
        self.ips = r.hkeys('useful_proxy')

    def process_request(self, request, spider):
        request.meta["proxy"] = "http://" + random.choice(self.ips)
