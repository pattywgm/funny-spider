# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime

import pymongo

from items import AwardsItem, MovieItem, CelebrityItem
from utils.my_utils import dump_obj, load_obj

time_now = datetime.strftime(datetime.now(), '%Y%m%d')


class MongoDBObj(object):
    def __init__(self):
        self.client = pymongo.MongoClient('127.0.0.1', 27017)
        self.db = self.client["douban"]

    def insert(self, table, data):
        self.db[table].insert_one(data)

    def __del__(self):
        self.client.close()

    def get_celebrities_from_awards(self):
        persons = dict()
        for doc in self.db['movie_awards'].find():
            for w in doc['awards']:
                for aw in w['awards']:
                    for k, v in aw.iteritems():
                        if len(v) > 0:
                            for person in v:
                                persons.update(person)
        dump_obj('./records/celebrities_urls.pkl', persons)

    def get_celebrities_from_movie(self):
        persons = load_obj('./records/celebrities_urls.pkl')
        for doc in self.db['movies'].find({}, {'director': 1,
                                               'scriptwriter': 1,
                                               'actor': 1}):
            persons.update(doc['director'])
            persons.update(doc['scriptwriter'])
            persons.update(doc['actor'])
        dump_obj('./records/celebrities_urls.pkl', persons)


class DoubanPipeline(object):
    def __init__(self):
        self.mongo_db = MongoDBObj()

    def process_item(self, item, spider):
        if isinstance(item, MovieItem):
            self.mongo_db.insert('movies', dict(item))
        if isinstance(item, AwardsItem):
            self.mongo_db.insert('movie_awards', dict(item))
        if isinstance(item, CelebrityItem):
            self.mongo_db.insert('celebrities', dict(item))
        return item
