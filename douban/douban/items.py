# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    no = scrapy.Field()    # 排名
    name = scrapy.Field()  # 电影名
    main_picture = scrapy.Field()  #海报地址
    director = scrapy.Field()
    scriptwriter = scrapy.Field()
    actor = scrapy.Field()
    plot = scrapy.Field()
    made_in = scrapy.Field()
    language = scrapy.Field()
    another_names = scrapy.Field()
    release_date = scrapy.Field()
    runtime = scrapy.Field()
    imdb = scrapy.Field()
    rating_avg = scrapy.Field()
    related_info = scrapy.Field()
    recommendations = scrapy.Field()


class AwardsItem(scrapy.Item):
    movie_code = scrapy.Field()
    url = scrapy.Field()
    awards = scrapy.Field()

