#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@file: movie_awards.py
@time: 17/10/19  下午10:35
@desc: 电影获奖数据抓取
        28items/每分钟 被ban
"""
import re
from copy import deepcopy
from os.path import exists

import scrapy

from douban.items import AwardsItem
from douban.utils.my_utils import load_obj, replace_dot

_META_VERSION = 'v1.0'
_AWARDS = 'https://movie.douban.com/subject/{}/awards/'


class MovieAwards(scrapy.Spider):
    name = 'movie_awards'
    meta_version = _META_VERSION

    def __init__(self):
        """

        :param urls:
        :param done: 已经抓取完成的,用于断点续爬
        :return:
        """
        self.urls = load_obj('./records/urls.pkl')
        self.done = list()
        if exists('./records/{}_done.pkl'.format(self.name)):
            self.done = load_obj('./records/{}_done.pkl'.format(self.name))
        self.new_done = deepcopy(self.done)

    def start_requests(self):
        req = list()
        for url in self.urls:
            movie_code = re.findall('\d+', url)[0]
            award_url = _AWARDS.format(movie_code)
            if award_url not in self.done:
                req.append(scrapy.Request(award_url, callback=self.parse, meta={'movie_code': movie_code}))
        return req

    def parse(self, response):
        url = response.url
        self.logger.info('Crawl {}'.format(url))
        item = AwardsItem()
        item['url'] = url
        item['movie_code'] = response.meta['movie_code']
        award_divs = response.xpath('//div[@class="awards"]')
        item['awards'] = [self.parse_award_detail(div) for div in award_divs]
        yield item

    def parse_award_detail(self, award_div):
        """
        解析获奖详细信息
        :param award_div:
        :return:
        """
        award_detail = dict()
        # 颁奖方及年份
        url = award_div.xpath('.//h2/a/@href').extract_first()
        name = award_div.xpath('.//h2/a/text()').extract_first()
        year = award_div.xpath('.//h2/span/text()').extract_first().replace('(', '').replace(')', '').strip()
        award_detail.update({'award_provider': {name: url}, 'year': year})
        # 具体奖项名及获奖者
        awards = list()
        for ul in award_div.xpath('.//ul[@class="award"]'):
            award_name = ul.xpath('./li[1]/text()').extract_first()
            award_persons = list()
            for person in ul.xpath('./li[position()>1]'):
                if person.xpath('./a').extract_first() is None:
                    break
                p_name = replace_dot(person.xpath('./a/text()').extract())
                p_url = person.xpath('./a/@href').extract()
                award_persons.append(dict(zip(p_name, p_url)))
            awards.append({award_name: award_persons})
        award_detail.update({'awards': awards})
        return award_detail
