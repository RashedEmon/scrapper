import asyncio
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.reactor import install_reactor

install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

from scrapper.spiders.airbnb.airbnb_properties import AirbnbSpider



process = CrawlerProcess()
process.crawl(AirbnbSpider)
process.start()