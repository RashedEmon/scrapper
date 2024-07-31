# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import re
import random

import sqlalchemy as alchemy
from scrapy import signals
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import IgnoreRequest, CloseSpider

from scrapper.database.operations import CommonDBOperation, RetriesCompeleted
from scrapper.database.airbnb.models import RequestTracker

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


class LogRequestMiddleware:
    
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        middleware.crawler = crawler
        return middleware

    async def process_request(self, request, spider):
        if request.url not in ["https://www.airbnb.com/sitemap-master-index.xml.gz"] and not str(request.url).startswith("https://www.airbnb.com/api"):
            query_filter = [
                alchemy.and_(
                        RequestTracker.url == request.url,
                        RequestTracker.status_code == 200,
                    )
            ]
            try:
                exist = await self.db.is_exist_async(
                    model_name=RequestTracker,
                    columns=[RequestTracker.url],
                    query_filter=query_filter
                )
            except RetriesCompeleted as err:
                raise CloseSpider(reason="database disconnected")
                
            if exist:
                raise IgnoreRequest

    async def process_response(self, request, response, spider):
        if not str(request.url).startswith("https://www.airbnb.com/api"):
            try:
                await self.db.insert_or_update_async(
                    model_class=RequestTracker,
                    data_dict={
                        "url": response.url,
                        "status_code": response.status,
                        "method": request.method
                    }
                )
            except RetriesCompeleted as err:
                raise CloseSpider(reason="database disconnected")
            
        return response

    def spider_opened(self, spider):
        self.db = CommonDBOperation()
    
    async def spider_closed(self, spider):
        await self.db.db_manager.dispose()
