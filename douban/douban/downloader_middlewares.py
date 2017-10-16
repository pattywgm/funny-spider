#!/usr/bin/env python
# encoding: utf-8

"""
@version: 1.0
@file: downloader_middlewares.py
@time: 17/10/16  下午8:28
@desc: 下载中间件,js动态渲染
"""
import random

from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from settings import USER_AGENT_LIST, PHANTOMJS_DRIVER


class PhantomjsInit(object):
    def __init__(self, proxy=None):
        # 设置User-Agent
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = random.choice(USER_AGENT_LIST)

        self.browser = webdriver.PhantomJS(executable_path=PHANTOMJS_DRIVER, desired_capabilities=dcap,
                                           service_args=proxy)


class DouBanDownloaderMiddleware(object):
    def __init__(self):
        self.browser = PhantomjsInit().browser
        self.browser.implicitly_wait(10)

    def process_request(self, request, spider):
        self.browser.get(request.url)
        body = self.browser.page_source
        return HtmlResponse(self.browser.current_url, body=body, encoding="utf-8", request=request)

    def __del__(self):
        self.browser.quit()
