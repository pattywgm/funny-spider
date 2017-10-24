#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@file: my_utils.py
@time: 17/10/16  下午8:35
@desc: 
"""
import random
import time

try:
    import cPickle as pickle
except ImportError, e:
    import pickle
import redis
from settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


def dump_obj(file_path, obj):
    """
    将对象持久化到本地
    :return:
    """
    with open(file_path, 'w') as f:
        pickle.dump(obj, f)


def load_obj(file_path):
    """
    加载持久化的对象
    :return:
    """
    with open(file_path, 'r') as f:
        return pickle.load(f)


def replace_dot(fileds):
    """
    替换'.',mongo不允许key值中含有'.', 如 E.T.In是非法的
    :param fileds:
    :return:
    """
    return [filed.replace('.', '\u002E') for filed in fileds]


def random_delay():
    """
    随机延时
    :return:
    """
    time.sleep(random.choice([1, 3, 5, 7]))


def get_redis_conn():
    """
    获取Redis连接对象
    :return:
    """
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, password=REDIS_PASSWORD)
