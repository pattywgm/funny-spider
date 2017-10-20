# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import json

from scrapy import signals
from scrapy.mail import MailSender

from settings import MAIL_TO
from utils.my_utils import dump_obj


class DoubanSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        # crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(s.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(s.spider_error, signal=signals.spider_error)
        s.mail = MailSender.from_settings(crawler.settings)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def spider_error(self, failure, response, spider):
        """
        spider_error信息处理方法, 发送email报警
        :param failure:
        :param response:
        :param spider:
        :return:
        """
        content = {'project_name': spider.settings.attributes['BOT_NAME'].value,
                   'spider_name': spider.name,
                   'url': response.url,
                   'failure_report': {'args': failure.value.args,
                                      'message': failure.value.message},
                   'error_from': 'Spider error, probably occurred in item parse functions'}
        self.mail.send(MAIL_TO, 'Scrapy Error Alarm from wugm', json.dumps(content))

    def item_scraped(self, item, response, spider):
        spider.new_done.append(item['url'])

    def spider_closed(self, spider, reason):
        dump_obj('./records/{}_done.pkl'.format(spider.name), spider.new_done)
