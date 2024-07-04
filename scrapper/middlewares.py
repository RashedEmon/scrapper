# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import random

from scrapy import signals
from scrapy.utils.project import get_project_settings

class LogRequestHeadersMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        spider.logger.info(f"########################start request logger###########################")
        spider.logger.info(request.url)
        spider.logger.info(f"Request headers: {request.headers}")
        spider.logger.info(f"##########################end#########################")
        return None

    def process_response(self, request, response, spider):
        spider.logger.info(f"########################start response logger###########################")
        spider.logger.info(f"Response headers: {response.url}")
        spider.logger.info(f"Response headers: {response.status}")
        spider.logger.info(f"Response headers: {response.headers}")
        spider.logger.info(f"##########################end#########################")
        return response

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")


class RandomProxyMiddleware:
    def __init__(self):
        settings = get_project_settings()
        self.proxies = settings.get('PROXY_LIST')

    def process_request(self, request, spider):
        proxy = random.choice(self.proxies)
        request.meta['proxy'] = proxy
