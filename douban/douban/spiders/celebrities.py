#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@file: celebrities.py
@time: 17/10/20  下午3:02
@desc: 
"""

import random
import re
import time
from copy import deepcopy
from os.path import exists

import requests
import scrapy
from scrapy.http import HtmlResponse

from douban.items import CelebrityItem
from douban.settings import USER_AGENT_LIST
from douban.utils.my_utils import load_obj, random_delay

_META_VERSION = 'v1.0'
_CELEBRITIES = 'https://movie.douban.com/subject/{}/celebrities'
_IMG_URL = "https://movie.douban.com/celebrity/{}/photos/?type=C&start={}&sortby=like&size=a&subtype=a"
_AWARDS_URL = "https://movie.douban.com/celebrity/{}/awards/"
_WORKS_URL = "https://movie.douban.com/celebrity/{}/movies?sortby=time&format=pic&start={}"
_PARTNERS_URL = "https://movie.douban.com/celebrity/{}/partners?start={}"


class Celebrities(scrapy.Spider):
    name = 'celebrities'
    meta_version = _META_VERSION

    def __init__(self):
        """

        :param urls:
        :param done: 已经抓取完成的,用于断点续爬
        :return:
        """
        self.urls = load_obj('./records/celebrities_urls.pkl')
        self.done = list()
        if exists('./records/{}_done.pkl'.format(self.name)):
            self.done = load_obj('./records/{}_done.pkl'.format(self.name))
        self.new_done = deepcopy(self.done)

    def start_requests(self):
        req = list()
        for url in self.urls.itervalues():
            celebrity_code = re.findall('\d+', url)[0]
            if url not in self.done:
                req.append(scrapy.Request(url, callback=self.parse, meta={'celebrity_code': celebrity_code}))
        return req

    def parse(self, response):
        url = response.url
        self.logger.info('Crawl celebrity: {}'.format(url))
        item = CelebrityItem()
        item['url'] = url
        item['celebrity_code'] = response.meta['celebrity_code']
        # 名字,头像
        name = response.xpath('//div[@id="content"]/h1/text()').extract_first().strip()
        headline = response.xpath('//div[@id="headline"]')
        picture = headline.xpath('./div[@class="pic"]/a/@href').extract_first().strip()
        item['name'] = name
        item['picture'] = picture
        # 性别,星座,生卒日期,出生地,职业等基础信息
        tit = headline.xpath(".//li/span/text()").extract()
        values = [s.strip().split('\n')[-1] for s in headline.xpath(".//li/text()|.//li//a/text()").extract()]
        values = [v.strip() for v in values if len(v) > 0 and v != ':']
        infos = dict(zip(tit, values))
        item['base_infos'] = infos
        # 简介
        all_intro = response.xpath(
            '//div[@id="intro"]//span[@class="all hidden"]|//div[@id="intro"]//div[@class="bd"]').xpath(
                "string(.)").extract_first().strip()
        item['introduction'] = all_intro
        # yield scrapy.Request(_IMG_URL.format(item['celebrity_code'], 0), callback=self.parse_imgs,
        #                      headers={"User-Agent": random.choice(USER_AGENT_LIST)},
        #                      meta={'item': item, 'start': 0, 'imgs': list()})
        yield scrapy.Request(_AWARDS_URL.format(item['celebrity_code']), callback=self.parse_awards,
                             headers={"User-Agent": random.choice(USER_AGENT_LIST)},
                             meta={'item': item})

    def parse_imgs(self, response):
        """
        所有图片
        :param response:
        :return:
        """
        url = response.url
        self.logger.info('crawl {}'.format(url))
        item = response.meta['item']
        img_list = response.meta['imgs']
        start = response.meta['start']
        imgs = response.xpath('//div[@class="article"]/ul//img/@src')
        if len(imgs) > 0:
            img_list += imgs.extract()
            start += 40
            random_delay()
            yield scrapy.Request(_IMG_URL.format(item['celebrity_code'], start), callback=self.parse_imgs,
                                 headers={"User-Agent": random.choice(USER_AGENT_LIST)},
                                 meta={'item': item, 'start': start, 'imgs': img_list})
        else:
            item['images'] = img_list
            yield scrapy.Request(_AWARDS_URL.format(item['celebrity_code']), callback=self.parse_awards,
                                 headers={"User-Agent": random.choice(USER_AGENT_LIST)},
                                 meta={'item': item})

    def parse_awards(self, response):
        """
        获奖情况
        :param response:
        :return: {time:2004,name:第23届香港电影金像奖,award:演艺光辉永恒大奖,result:获奖}
        """
        url = response.url
        self.logger.info('crawl {}'.format(url))
        item = response.meta['item']
        award_list = list()
        for award_div in response.xpath('//div[@class="awards"]'):
            award_time = award_div.xpath(".//h2/text()").extract_first()
            for ul in award_div.xpath("./ul"):
                name = ul.xpath("./li[1]").xpath("string(.)").extract_first().strip()
                result_str = ul.xpath("./li[2]").xpath("string(.)").extract_first().strip()
                result = "获奖".decode("utf-8")
                if "提名".decode("utf-8") in result_str:
                    result = "提名".decode("utf-8")
                award = " ".join(ul.xpath('./li').xpath("string(.)").extract()[1:]).strip()
                award_list.append({"time": award_time,
                                   "name": name,
                                   "award": award,
                                   "result": result})
        item['awards'] = award_list
        yield scrapy.Request(_WORKS_URL.format(item['celebrity_code'], 0), callback=self.parse_works,
                             headers={"User-Agent": random.choice(USER_AGENT_LIST)},
                             meta={'item': item, 'start': 0, 'works': list()})

    def parse_works(self, response):
        """

        :param response:
        :return:
         {name:东邪西毒：终极版，
         URL：https://movie.douban.com/subject/3726072/，
         rate：8.7，
         datePublished：[{origin:中国大陆,date:2009-03-26},{origin:戛纳电影节, date:2008-05-18}]
        """
        url = response.url
        self.logger.info('crawl {}'.format(url))
        item = response.meta['item']
        start = response.meta['start']
        work_list = response.meta['works']
        work_lis = response.xpath('//div[@class="grid_view"]/ul/li')
        if len(work_lis) > 0:
            start += 10
            for work_li in work_lis:
                name = work_li.xpath(".//dt//img/@alt").extract_first()
                url = work_li.xpath(".//dt/a/@href").extract_first()
                rate = work_li.xpath('.//div[@class="star clearfix"]/span[2]/text()').extract_first()
                publish_date = self.get_publish_date(url)
                work_list.append({"name": name,
                                  "url": url,
                                  "rate": rate if rate is not None else '',
                                  "datePublished": publish_date})
            random_delay()
            yield scrapy.Request(_WORKS_URL.format(item['celebrity_code'], start), callback=self.parse_works,
                                 headers={"User-Agent": random.choice(USER_AGENT_LIST)},
                                 meta={'item': item, 'start': start, 'works': work_list})
        else:
            item['works'] = work_list
            yield scrapy.Request(_PARTNERS_URL.format(item['celebrity_code'], 0), callback=self.parse_partners,
                                 headers={"User-Agent": random.choice(USER_AGENT_LIST)},
                                 meta={'item': item, 'start': 0, 'partners': dict()})

    def parse_partners(self, response):
        """
        合作两次以上的艺人
        :param response:
        :return:
        """
        url = response.url
        self.logger.info('crawl {}'.format(url))
        item = response.meta['item']
        start = response.meta['start']
        partners = response.meta['partners']
        partner_divs = response.xpath('//div[@class="partners item"]')
        if len(partner_divs) > 0:
            start += 10
            p_names = partner_divs.xpath(".//h2/a/text()").extract()
            p_hrefs = partner_divs.xpath(".//h2/a/@href").extract()
            partners.update(dict(zip(p_names, p_hrefs)))
            random_delay()
            yield scrapy.Request(_PARTNERS_URL.format(item['celebrity_code'], start), callback=self.parse_partners,
                                 headers={"User-Agent": random.choice(USER_AGENT_LIST)},
                                 meta={'item': item, 'start': start, 'partners': partners})
        else:
            item['partners'] = partners
            # 此处可能存在对新的影人数据的抓取,seed从partners中来
            yield item

    def get_publish_date(self, url):
        """
        获取上映日期
        :param url:
        :return:
           [{origin:中国大陆,date:2009-03-26},{origin:戛纳电影节, date:2008-05-18}]
        """
        random_delay()
        req = requests.get(url, headers={"User-Agent": random.choice(USER_AGENT_LIST)})
        response = HtmlResponse(url, body=req.content, encoding="utf-8", request=req)
        selector = scrapy.Selector(response)
        publish_date = list()
        for content in selector.xpath('//span[@property="v:initialReleaseDate"]/@content').extract():
            date = content[:10]
            origin = content[11:-1]
            publish_date.append({"origin": origin, "date": date})
        return publish_date

    def get_info(self, headline, field):
        """
        获取对应字段的值
        :param headline:
        :param field:
        :return:
        """
        span = headline.xpath('.//span[contains(text(),"%s")]' % field)
        if len(span) > 0:
            val = self.parse_str(span.xpath('./parent::li/text()|./following-sibling::a/text()').extract())
            return val
        else:
            return None

    def parse_str(self, info):
        info_str = "".join(info).strip()
        return info_str[info_str.index(" ") + 1:].strip()
