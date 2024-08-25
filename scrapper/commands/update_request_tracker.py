import io
import asyncio

import gzip
import requests
from lxml import etree
import tqdm

from abc import ABC, abstractmethod
from scrapper.config import PROJECT_ROOT
from scrapper.database.operations import CommonDBOperation
from scrapper.database.airbnb.db_operations import DBOperations
from scrapper.database.airbnb.models import PropertyUrls, RequestTracker, AirbnbUrls


class CronBase(ABC):

    @abstractmethod
    async def init(self) -> None:
        pass

class PopulateMissingUrls(CronBase):

    def __init__(self) -> None:
        file_path = f"{PROJECT_ROOT}/spiders_logs/missed_urls.txt"
        self.file = open(file_path, "w")
        self.common_db_ops = CommonDBOperation()
        self.airbnb_db_ops = DBOperations()

    async def init(self):
        res = await self.common_db_ops.db_manager.create_tables()
        if res:
            print("table created successfully")
        else:
            print("table creation failed")
            return
        
        result = await self.airbnb_db_ops.get_incomplete_xmls_from_request_tracker()
        if result is not None:
            print("got incomplete xmls successfully")

        for url, _ in tqdm.tqdm(result):
            if url not in ("https://www.airbnb.com/sitemap-master-index.xml.gz", None):
                await self.download_xml(url)

    async def download_xml(self, url):
        res = requests.get(url=url)
        if res.status_code !=  200:
            self.file.writelines([url])
            return
        
        with gzip.GzipFile(fileobj=io.BytesIO(res.content)) as f:
            sitemap_content = f.read()

        root = etree.fromstring(sitemap_content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        for loc in root.findall('.//ns:loc', namespace):
            await self.common_db_ops.insert_or_ignore_async(model_class=PropertyUrls, data_dict={"url": loc.text, "referer": url})
        
        print("inserted successfuly for ", url)


class RunQuery(CronBase):
    def __init__(self) -> None:
        self.airbnb_db_ops = DBOperations()
        self.common_db_ops = CommonDBOperation()
    
    async def init(self):
        is_created = await self.common_db_ops.db_manager.create_tables()
        if is_created:
            print("Table created")
        else:
            print('table creation failed')
            return
        
        total_urls = await self.airbnb_db_ops.get_missing_urls_count(
            property_urls=PropertyUrls, 
            request_tracker=RequestTracker
        )
        
        limit = 500
        offset = 0
        for _ in tqdm.tqdm(range(0, total_urls, limit)):
            res = await self.airbnb_db_ops.get_missing_urls(
                property_urls=PropertyUrls, 
                request_tracker=RequestTracker,
                limit=limit,
                offset=offset
            )
            
            offset += limit
            result = await self.airbnb_db_ops.bulk_insert_data(Model=AirbnbUrls, data_list=res)
            await asyncio.sleep(0.5)
            print(result, "inserted")
