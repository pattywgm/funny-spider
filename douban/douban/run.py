#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@file: run.py
@time: 17/10/16  下午9:16
@desc: 
"""
import sys

from scrapy.cmdline import execute

reload(sys)
sys.setdefaultencoding('utf-8')

# execute(("scrapy crawl top250_movies").split())

# execute(("scrapy crawl movie_awards").split())

execute(("scrapy crawl celebrities").split())
