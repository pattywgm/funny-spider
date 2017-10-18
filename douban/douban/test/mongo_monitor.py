#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@file: mongo_monitor.py
@time: 17/10/16  下午5:14
@desc: 监控MongoDB中各个collection的入库情况,连续7天未发生入库行为引发报警机制
"""
import json
from datetime import datetime, timedelta

import pymongo

from send_mail import send_email


class MongoMonitor(object):
    def __init__(self):
        # client = pymongo.MongoClient("mongodb://root:^aTFYU23Aqwe^@10.10.212.209")
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.last_date = (datetime.today() - timedelta(days=6)).isoformat()[:10] + 'T00:00:00'
        self.errors = dict()

    def check_insert_stat(self, db_name):
        """
        检查各个collection的入库情况
        :return:
        """
        db = self.client[db_name]
        colls = db.collection_names()
        db_error = list()
        for coll in colls:
            db[coll].distinct('meta_updated')
            result = db[coll].count({'meta_updated': {'$gte': self.last_date}})
            if result == 0:
                # slack alarm
                db_error.append("{}-{}".format(db_name, coll))
        self.errors.update({db_name: db_error})

    def __del__(self):
        self.client.close()

    def insert_many(self):
        with open('/Users/pattywgm/howbuy_profile_20171014full.json','r') as f:
            docs = list()
            db = self.client['price']
            coll = db['howbuy_profile']
            for line in f.readlines():
                data = json.loads(line.strip())
                docs.append(data)
                if len(docs) % 20 == 0:
                    coll.insert_many(docs)
                    docs = list()
            if len(docs) > 0:
                coll.insert_many(docs)



if __name__ == "__main__":
    monitor = MongoMonitor()
    monitor.insert_many()
#     for db in ['perimit', 'permit', 'cpdaily', 'jediDB', 'price']:
#         monitor.check_insert_stat(db)
    # send_email(json.dumps(monitor.errors))
