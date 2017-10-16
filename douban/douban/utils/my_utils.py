#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@file: my_utils.py
@time: 17/10/16  下午8:35
@desc: 
"""
try:
    import cPickle as pickle
except ImportError, e:
    import pickle


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
