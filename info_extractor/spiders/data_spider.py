import scrapy
from info_extractor.config import Config
from info_extractor.items import InfoExtractorItem
from info_extractor.utils import Utils
import json
import time

class DataSpider(scrapy.Spider):
    name = "dataspider"

    def __init__(self, *args, **kwargs):
        super(DataSpider, self).__init__(*args, **kwargs)
        file_path = f"data/static/xpaths/{Config.allowed_domain}.json"
        self.xpaths = Utils.load_json_data(file_path)

    def start_requests(self):
        entry_url = Config.start_url  
        yield scrapy.Request(url=entry_url, callback=self.parse_entry)

    
    def parse_entry(self, response):
        detail_links = response.xpath(self.xpaths['details_urls'])
        for link in detail_links:
            relative_url = link.attrib['href']
            full_url = response.urljoin(relative_url)
            print("full_url:", full_url)
            yield scrapy.Request(url=full_url, callback=self.parse_detail)
    def parse_detail(self, response):
        item = InfoExtractorItem()
        item['url'] = response.url
        print("url: ", response.url)
        title = response.xpath(self.xpaths['title']).get()
        item['title'] = title
        print("title:", title)
        yield item
