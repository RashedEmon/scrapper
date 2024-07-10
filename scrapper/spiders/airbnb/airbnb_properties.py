import io
import re
import json
import gzip
import jmespath
import requests
from lxml import etree
from datetime import datetime

import scrapy
from scrapy import spiders

from scrapper.config import PROJECT_ROOT
from scrapper.database.airbnb.pydantic_models import Property, Reviews, Host

key_selector_mapping = {
    "images": "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='PHOTO_TOUR_SCROLLABLE'].section[].mediaItems[][].baseUrl",
}


class AirbnbSpider(scrapy.Spider):
    name="airbnb_property"
    allowed_domain = ["www.airbnb.com"]
    start_urls = ["https://www.airbnb.com/sitemap-master-index.xml.gz"]

    custom_settings = {
        "ITEM_PIPELINES": {
            "scrapper.pipelines.MultiModelValidationPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {

        },
        # "DEPTH_PRIORITY": 1,
        # "CONCURRENT_REQUESTS": 1,
        # 'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleLifoDiskQueue',
        # 'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.LifoMemoryQueue',
    }

    def __init__(self, name: str | None = None, **kwargs: spiders.Any):
        super().__init__(name, **kwargs)
    
    def parse(self, response: spiders.Response, **kwargs: spiders.Any) -> spiders.Any:

        with gzip.GzipFile(fileobj=io.BytesIO(response.body)) as f:
            sitemap_content = f.read()
        
        root = etree.fromstring(sitemap_content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        pattern = re.compile(r'https://www\.airbnb\.com/sitemap-homes-urls-(\d+)\.xml\.gz')

        for sitemap in root.findall('ns:sitemap', namespace):
            loc = sitemap.find('ns:loc', namespace)
            if loc is not None and re.match(pattern, loc.text):
                loc.text
                yield scrapy.Request(url=loc.text, callback=self.pase_home_urls)
    

    def pase_home_urls(self, response):
        with gzip.GzipFile(fileobj=io.BytesIO(response.body)) as f:
            sitemap_content = f.read()

        
        root = etree.fromstring(sitemap_content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        urls = []
        for loc in root.findall('.//ns:loc', namespace):
            urls.append(loc.text)
            yield scrapy.Request(url=loc.text, callback=self.parse_property_details)
    
    def parse_property_details(self, response):

        try:
            details_dict = json.loads(response.css("#data-deferred-state-0::text").get())
        except Exception as err:
            print("parse_property_details => got error while parsing json from script tag.", str(err))
        
        # Property specific selector
        property_id = response.url.split('/')[-1]
        
        property_name_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='TITLE_DEFAULT'].section.title | [0]"
        property_name = jmespath.search(expression=property_name_selector, data=details_dict)

        property_desctiption_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='PDP_DESCRIPTION_MODAL'].section | [0].items[].html[].htmlText"
        property_desctiption = jmespath.search(expression=property_desctiption_selector, data=details_dict)

        property_facilities_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sbuiData.sectionConfiguration.root.sections[?sectionId=='OVERVIEW_DEFAULT_V2'].sectionData[] | [0].overviewItems[].title"
        property_facilities = jmespath.search(expression=property_facilities_selector, data=details_dict)

        property_review_count_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sbuiData.sectionConfiguration.root.sections[?sectionId=='OVERVIEW_DEFAULT_V2'].sectionData[] | [0].reviewData.reviewCount"
        property_review_count = jmespath.search(expression=property_review_count_selector, data=details_dict)

        property_rating_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sbuiData.sectionConfiguration.root.sections[?sectionId=='OVERVIEW_DEFAULT_V2'].sectionData[] | [0].reviewData.ratingText"
        property_rating = jmespath.search(expression=property_rating_selector, data=details_dict)

        property_detailed_review_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='REVIEWS_DEFAULT'].section | [0].ratings"
        property_detailed_review = jmespath.search(expression=property_detailed_review_selector, data=details_dict)

        room_arrangement_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='SLEEPING_ARRANGEMENT_DEFAULT'].section[].arrangementDetails[]"
        room_arrangement = jmespath.search(expression=room_arrangement_selector, data=details_dict)

        latitude_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='LOCATION_PDP'].section[].lat | [0]"
        latitude = jmespath.search(expression=latitude_selector, data=details_dict)

        longitude_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='LOCATION_PDP'].section[].lng | [0]"
        longitude = jmespath.search(expression=longitude_selector, data=details_dict)

        image_url_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='PHOTO_TOUR_SCROLLABLE'].section[].mediaItems[][].baseUrl"
        images = jmespath.search(expression=image_url_selector, data=details_dict)

        policies_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='POLICIES_DEFAULT'].section"
        policies = jmespath.search(expression=policies_selector, data=details_dict)

        amenities_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='AMENITIES_DEFAULT'].section | [0].seeAllAmenitiesGroups"
        amenities = jmespath.search(expression=amenities_selector, data=details_dict)

        # Host specific selector

        host_name_seclector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.name | [0]"
        host_name = jmespath.search(expression=host_name_seclector, data=details_dict)

        host_id_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.userId | [0]"
        host_id = jmespath.search(expression=host_id_selector, data=details_dict)

        profile_image_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.profilePictureUrl | [0]"
        profile_image = jmespath.search(expression=profile_image_selector, data=details_dict)

        is_super_host_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.isSuperhost | [0]"
        is_super_host = jmespath.search(expression=is_super_host_selector, data=details_dict)

        is_verified_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.isVerified | [0]"
        is_verified = jmespath.search(expression=is_verified_selector, data=details_dict)

        host_rating_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.stats | [0][?type=='RATING'].value | [0]"
        host_rating = jmespath.search(expression=host_rating_selector, data=details_dict)

        host_review_count_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.stats | [0][?type=='REVIEW_COUNT'].value | [0]"
        host_review_count = jmespath.search(expression=host_review_count_selector, data=details_dict)

        host_years_hosting_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.stats | [0][?type=='YEARS_HOSTING'].value | [0]"
        host_years_hosting = jmespath.search(expression=host_years_hosting_selector, data=details_dict)
        
        # get airbnb api key
        data_injector = json.loads(response.css("#data-injector-instances::text").get())
        airbnb_x_api_key = jmespath.search(data=data_injector, expression='"root > core-guest-spa"[]."layout-init".api_config.key | [0]')
        data_injector = {}

        # get available dates
        self.get_available_and_min_stay_dates(airbnb_x_api_key, property_id)
        


        breakpoint()


    def get_available_and_min_stay_dates(self, airbnb_x_api_key: str, property_id):

        url = "https://www.airbnb.com/api/v3/PdpAvailabilityCalendar/8f08e03c7bd16fcad3c92a3592c19a8b559a0d0855a84028d1163d4733ed9ade"

        params = {
            "operationName": "PdpAvailabilityCalendar",
            "locale": "en",
            "currency": "USD",
            "variables": json.dumps({
                "request": {
                    "count": 12,
                    "listingId": f"{property_id}",
                    "month": datetime.now().month,
                    "year": datetime.now().year
                }
            }),
            "extensions": json.dumps({
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "8f08e03c7bd16fcad3c92a3592c19a8b559a0d0855a84028d1163d4733ed9ade"
                }
            })
        }

        headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'X-Airbnb-API-Key': airbnb_x_api_key,
        }

        response = requests.request("GET", url, headers=headers, params=params)

        print(response.text)
        breakpoint()

        available_date_selector = 'data.merlin.pdpAvailabilityCalendar.calendarMonths[].days[?available == `true`].{"date": calendarDate, "available": available, "max_night": maxNights, "min_night": minNights} | []'
        available_dates = jmespath.search(expression=available_date_selector, data=response.json())
        

