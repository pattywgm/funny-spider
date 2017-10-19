#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@file: top250_movies.py
@time: 17/10/16  下午8:23
@desc: 豆瓣电影 Top 250 抓取
"""
import scrapy

from douban.items import MovieItem
from douban.utils.my_utils import replace_dot

_META_VERSION = 'v1.0'
_CELEBRITIES = 'https://movie.douban.com/subject/{}/celebrities'
_AWARDS = 'https://movie.douban.com/subject/{}/awards/'
_COMMENTS = 'https://movie.douban.com/subject/{}/comments?start={}&limit=20&sort=new_score&status=P'


class Top250MoviesSpider(scrapy.Spider):
    name = 'top250_movies'
    meta_version = _META_VERSION

    def start_requests(self):
        url = 'https://movie.douban.com/top250?start={}&filter='
        for i in range(0, 275, 25):
            yield scrapy.Request(url.format(i), callback=self.parse)

    def parse(self, response):
        self.logger.info('Crawl {}'.format(response.url))
        movie_links = response.xpath('//ol[@class="grid_view"]//a/@href').extract()
        for link in movie_links:
            yield scrapy.Request(link, callback=self.parse_item)

    def parse_item(self, response):
        """
        简介抓取
        :param response:
        :return:
        """
        url = response.url
        self.logger.info('Crawl {}'.format(url))
        item = MovieItem()
        item['url'] = url
        item['no'] = response.xpath('//span[@class="top250-no"]/text()').extract_first()
        item['name'] = response.xpath('//h1/span[1]/text()').extract_first()
        intro_div = response.xpath('//div[@class="subject clearfix"]')
        item['main_picture'] = intro_div.xpath('.//div[@id="mainpic"]/a/@href').extract_first()
        info_div = intro_div.xpath('.//div[@id="info"]')
        # 导演
        director_url = info_div.xpath('./span[1]//a/@href').extract()
        director_name = replace_dot(info_div.xpath('./span[1]//a/text()').extract())
        director_url = [response.urljoin(url) for url in director_url]
        item['director'] = dict(zip(director_name, director_url))
        # 编剧
        scriptwriter_url = info_div.xpath('./span[2]//a/@href').extract()
        scriptwriter_name = replace_dot(info_div.xpath('./span[2]//a/text()').extract())
        scriptwriter_url = [response.urljoin(url) for url in scriptwriter_url]
        item['scriptwriter'] = dict(zip(scriptwriter_name, scriptwriter_url))
        # 主演
        actor_url = info_div.xpath('./span[3]//a[not(@title)]/@href').extract()
        actor_name = replace_dot(info_div.xpath('./span[3]//a[not(@title)]/text()').extract())
        actor_url = [response.urljoin(url) for url in actor_url]
        item['actor'] = dict(zip(actor_name, actor_url))
        # 剧情
        item['plot'] = '/'.join(info_div.xpath('.//span[@property="v:genre"]/text()').extract())
        # 制片国家/地区, 语言, 又名
        texts = info_div.xpath('./text()').extract()
        texts = [t.strip() for t in texts if t.strip() not in ('', ' ', '/')]
        item['made_in'] = texts[0]
        item['language'] = texts[1]
        if len(texts) == 3:
            item['another_names'] = texts[2]
        # 上映日期
        item['release_date'] = '/'.join(info_div.xpath('.//span[@property="v:initialReleaseDate"]/@content').extract())
        # 片长
        item['runtime'] = info_div.xpath('.//span[@property="v:runtime"]/text()').extract_first()
        # IMDB链接
        item['imdb'] = response.urljoin(info_div.xpath('.//a[last()]/@href').extract_first())
        # 豆瓣评分
        average = response.xpath('//strong[@property="v:average"]/text()').extract_first()
        rating_people = {
            response.xpath('//span[@property="v:votes"]/text()').extract_first(): response.urljoin('collections')}
        star_titles = response.xpath('//div[@class="ratings-on-weight"]//span[@title]/text()').extract()
        star_titles = [t.strip() for t in star_titles if t is not None]
        star_weights = response.xpath('//div[@class="ratings-on-weight"]//span[@class="rating_per"]/text()').extract()
        item['rating_avg'] = {"average": average,
                              "rating_people": rating_people,
                              "star_weight": dict(zip(star_titles, star_weights))}
        # 剧情简介
        summary = ''.join(response.xpath('//div[@id="link-report"]//span[@property="v:summary"]').xpath(
            'string(.)').extract()).strip()
        all_info = ''.join(
            response.xpath('//div[@id="link-report"]//span[@class="all hidden"]').xpath('string(.)').extract()).strip()
        item['related_info'] = summary + ' ' + all_info
        # 喜欢该影片的人也喜欢
        recomm_names = replace_dot(response.xpath('//div[@id="recommendations"]//dd/a/text()').extract())
        recomm_urls = response.xpath('//div[@id="recommendations"]//dd/a/@href').extract()
        item['recommendations'] = dict(zip(recomm_names, recomm_urls))
        yield item
