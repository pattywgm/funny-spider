#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@file: mongo_monitor.py
@time: 17/10/16  下午5:14
@desc: 监控MongoDB中各个collection的入库情况,连续7天未发生入库行为引发报警机制
"""
import sys
import json
from datetime import datetime, timedelta
import ConfigParser
import pymongo

from send_mail import send_email


class MongoMonitor(object):
    def __init__(self):
        # client = pymongo.MongoClient("mongodb://root:^aTFYU23Aqwe^@10.10.212.209")
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.last_date = (datetime.today() - timedelta(days=6)).isoformat()[:10] + 'T00:00:00'
        self.errors = dict()

    def check_insert_stat(self, db_name, filtered):
        """
        检查各个collection的入库情况
        :return:
        """
        db = self.client[db_name]
        colls = db.collection_names()
        colls = set(colls).difference(set(filtered))
        db_error = list()
        for coll in colls:
            db[coll].distinct('meta_updated')
            result = db[coll].count({'meta_updated': {'$gte': self.last_date}})
            if result == 0:
                # slack alarm
                db_error.append(coll)
        self.errors.update({db_name: db_error})

    def __del__(self):
        self.client.close()


if __name__ == "__main__":
    cfg_file = sys.argv[1]
    conf = ConfigParser.ConfigParser()
    conf.read(cfg_file)
    monitor = MongoMonitor()
    for db in ['perimit', 'permit', 'cpdaily', 'jediDB', 'price']:
        filtered = list()
        if conf.has_section(db):
            filtered = conf.items(db)[0][1].replace('[', '').replace(']', '').replace(' ', '').split(',')
        monitor.check_insert_stat(db, filtered)
    send_email(json.dumps(monitor.errors)+"\r\n 表名与数据源关系参照: http://gitlab.****")
