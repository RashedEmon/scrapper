# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json

from pydantic import ValidationError
from scrapy.exceptions import DropItem

from scrapper.config import PROJECT_ROOT
from scrapper.database.operations import CommonDBOperation
from scrapper.database.airbnb.pydantic_models import Property, Review, Host
from scrapper.database.airbnb.models import PropertyModel, ReviewsModel, HostsModel

class MultiModelValidationPipeline:

    def open_spider(self, spider):
        self.buffer_size = 5
        self.review_list = []
        self.property_list = []
        self.host_list = []

        self.db = CommonDBOperation()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        if isinstance(item, Property):
            return self.process_property(item)
        elif isinstance(item, Review):
            return self.process_review(item)
        elif isinstance(item, Host):
            return self.process_host(item)
        else:
            raise DropItem(f"Unknown item type: {type(item)}")

    def process_property(self, item: Property):
        try:
            validated_item = Property(**item.model_dump())

            self.property_list.append(validated_item.model_dump())
            if len(self.property_list) >= self.buffer_size:
                self.db.upsert_rows(
                    model=PropertyModel,
                    data=self.property_list,
                    unique_columns=['property_id']
                )
        except ValidationError as e:
            raise DropItem(f"Invalid product: {e}")

    def process_review(self, item: Review):
        try:
            validated_item = Review(**item.model_dump())

            self.review_list.append(validated_item.model_dump())
            if len(self.review_list) >= self.buffer_size:
                self.db.upsert_rows(
                    model=ReviewsModel,
                    data=self.review_list,
                    unique_columns=['review_id']
                )
        except ValidationError as e:
            raise DropItem(f"Invalid review: {e}")
    
    def process_host(self, item: Host):
        try:
            validated_item = Host(**item.model_dump())
            
            self.host_list.append(validated_item.model_dump())
            if len(self.host_list) >= self.buffer_size:
                self.db.upsert_rows(
                    model=HostsModel,
                    data=self.host_list,
                    unique_columns=['host_id']
                )
        except ValidationError as e:
            raise DropItem(f"Invalid review: {e}")