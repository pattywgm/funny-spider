#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@file: run_redis.py
@time: 17/10/23  下午6:18
@desc: 分布式运行
"""

from utils.my_utils import load_obj, get_redis_conn

r = get_redis_conn()
urls = load_obj('./records/celebrities_urls.pkl')
r.lpush("celebrities:start_urls", 'https://movie.douban.com/celebrity/1319032/')
