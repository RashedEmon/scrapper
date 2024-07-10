# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from pydantic import ValidationError
from scrapy.exceptions import DropItem

from scrapper.database.operations import CommonDBOperation
from scrapper.database.airbnb.pydantic_models import Property, Reviews, Host



class MultiModelValidationPipeline:

    def open_spider(self, spider):
        pass
        # self.db = CommonDBOperation()

    def close_spider(self, spider):
        pass
        # self.db.close()

    def process_item(self, item, spider):
        print(f"processing an item (type: {type(item)}")
        if isinstance(item, Property):
            return self.process_property(item)
        elif isinstance(item, Reviews):
            return self.process_review(item)
        elif isinstance(item, Host):
            return self.process_host(item)
        else:
            raise DropItem(f"Unknown item type: {type(item)}")

    def process_property(self, item: Property):
        try:
            validated_item = Property(**item.model_dump())
            return dict(validated_item)
        except ValidationError as e:
            raise DropItem(f"Invalid product: {e}")

    def process_review(self, item):
        try:
            validated_item = Reviews(**item.dict())
            return dict(validated_item)
        except ValidationError as e:
            raise DropItem(f"Invalid review: {e}")
    
    def process_host(self, item):
        try:
            validated_item = Host(**item.dict())
            return dict(validated_item)
        except ValidationError as e:
            raise DropItem(f"Invalid review: {e}")