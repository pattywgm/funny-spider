# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime

import pymongo
from items import AwardsItem, MovieItem
time_now = datetime.strftime(datetime.now(), '%Y%m%d')


class MongoDBObj(object):
    def __init__(self):
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.client["douban"]

    def insert(self, table, data):
        self.db[table].insert_one(data)

    def __del__(self):
        self.client.close()


class DoubanPipeline(object):
    def __init__(self):
        self.mongo_db = MongoDBObj()

    def process_item(self, item, spider):
        if isinstance(item, MovieItem):
            self.mongo_db.insert('movies', dict(item))
        if isinstance(item, AwardsItem):
            self.mongo_db.insert('movie_awards', dict(item))
        return item
