# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import asyncio
import queue
import threading

from pydantic import ValidationError
from scrapy.exceptions import DropItem

from scrapper.database.operations import CommonDBOperation
from scrapper.database.airbnb.pydantic_models import Property, Review, Host
from scrapper.database.airbnb.models import PropertyModel, ReviewsModel, HostsModel

class DatabaseWorker:
    def __init__(self):
        self.queue = queue.Queue()
        self.running = False

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        self.running = False
        self.queue.put(None)
        self.thread.join()

    def run(self):
        asyncio.run(self._run_async())

    async def _run_async(self):
        await self._init_db()
        while self.running:
            item = self.queue.get()
            if item is None:
                break
            await self._process_item(item)
        await self._close_db()

    async def _init_db(self):
        self.db = CommonDBOperation()
        await self.db.db_manager.create_tables()

    async def _process_item(self, item):
        if isinstance(item, Property):
            await self.db.insert_or_ignore_async(model_class=PropertyModel, data_dict=item.model_dump())
        elif isinstance(item, Review):
            await self.db.insert_or_ignore_async(model_class=ReviewsModel, data_dict=item.model_dump())
        elif isinstance(item, Host):
            await self.db.insert_or_ignore_async(model_class=HostsModel, data_dict=item.model_dump())

    async def _close_db(self):
        await self.db.db_manager.dispose()


class MultiModelValidationPipeline:
    def __init__(self):
        self.db_worker = None

    def open_spider(self, spider):
        self.db_worker = DatabaseWorker()
        self.db_worker.start()
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
    
    def close_spider(self, spider):
        self.db_worker.stop()
    
    def process_item(self, item, spider):
        if isinstance(item, Property):
            self.process_property(item)
        elif isinstance(item, Review):
            self.process_review(item)
        elif isinstance(item, Host):
            self.process_host(item)
        else:
            raise DropItem(f"Unknown item type: {type(item)}")

    
    def process_property(self, item: Property):
        try:
            item.amenities = json.dumps({"amenities": item.amenities}) if item.amenities else None
            item.room_arrangement = json.dumps({"room_arrangement": item.room_arrangement}) if item.room_arrangement else None
            item.detailed_review = json.dumps({"detailed_review": item.detailed_review}) if item.detailed_review else None
            item.images = json.dumps({"images": item.images}) if item.images else None
            item.facilities = json.dumps({"facilities": item.facilities}) if item.facilities else None
            item.policies = json.dumps({"policies": item.policies}) if item.policies else None

            self.db_worker.queue.put(Property(**item.model_dump()))
        except ValidationError as e:
            raise DropItem(f"Invalid product: {e}")

    def process_review(self, item: Review):
        try:
            self.db_worker.queue.put(Review(**item.model_dump()))
        except ValidationError as e:
            raise DropItem(f"Invalid review: {e}")
    
    def process_host(self, item: Host):
        try:
            item.host_details = json.dumps({"host_details": item.host_details}) if item.host_details else None
            self.db_worker.queue.put(Host(**item.model_dump()))
        except ValidationError as e:
            raise DropItem(f"Invalid review: {e}")