import io
import os
import re
import math
import json
import gzip
import time
import base64
from urllib.parse import quote

import jmespath
import requests
from lxml import etree
from datetime import datetime, timedelta
from typing import Dict, List

import scrapy
from scrapy import spiders

from scrapper.config import PROJECT_ROOT
from scrapper.database.airbnb.pydantic_models import Property, Review, Host


class AirbnbSpider(scrapy.Spider):
    name="airbnb_property"
    allowed_domain = ["www.airbnb.com"]
    start_urls = ["https://www.airbnb.com/sitemap-master-index.xml.gz"]

    custom_settings = {
            "ITEM_PIPELINES": {
                "scrapper.pipelines.MultiModelValidationPipeline": 300,
            },
            "DOWNLOADER_MIDDLEWARES": {
                "scrapper.middlewares.LogRequestMiddleware": 510,
                'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 505,
                "scrapper.middlewares.RandomProxyMiddleware": 500,
            },
        }

    # @classmethod
    # def update_settings(cls, settings):
    #     super().update_settings(settings)
        # job_dir = f"{PROJECT_ROOT}/spiders_logs/{cls.name}_job_dir"
        # os.makedirs(job_dir)
        # settings.set(name="JOBDIR", value=job_dir, priority="spider")

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
    
        airbnb_x_api_key = self.get_airbnb_api_key(response)

        property_id = response.url.split('/')[-1]

        details_dict = {}
        try:
            details_dict = json.loads(response.css("#data-deferred-state-0::text").get())
        except Exception as err:
            print("parse_property_details => got error while parsing json from script tag.", str(err))

        if not details_dict:
            return None
        
        url = "https://www.airbnb.com/api/v3/PdpAvailabilityCalendar/8f08e03c7bd16fcad3c92a3592c19a8b559a0d0855a84028d1163d4733ed9ade"

        params = {
            "operationName": "PdpAvailabilityCalendar",
            "locale": "en",
            "currency": "USD",
            "variables": {
                "request": {
                    "count": 12,
                    "listingId": f"{property_id}",
                    "month": datetime.now().month,
                    "year": datetime.now().year
                }
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "8f08e03c7bd16fcad3c92a3592c19a8b559a0d0855a84028d1163d4733ed9ade"
                }
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'X-Airbnb-API-Key': airbnb_x_api_key,
        }

        query_string = self.prepare_query_string(params=params)
        full_url = f"{url}?{query_string}"

        yield scrapy.Request(method="GET", url=full_url, headers=headers, callback=self.available_date_extractor, cb_kwargs={
            "airbnb_x_api_key": airbnb_x_api_key,
            "property_id": property_id,
            "details_dict": details_dict
        })

    
    def get_airbnb_api_key(self, response):
        # get airbnb api key
        data_injector = json.loads(response.css("#data-injector-instances::text").get())
        airbnb_x_api_key = jmespath.search(data=data_injector, expression='"root > core-guest-spa"[]."layout-init".api_config.key | [0]')
        data_injector = {}
        return airbnb_x_api_key
        

    def get_reviews(self, property_id, check_in, check_out, airbnb_x_api_key):
        url = "https://www.airbnb.com/api/v3/StaysPdpReviewsQuery/dec1c8061483e78373602047450322fd474e79ba9afa8d3dbbc27f504030f91d"
        
        def prepare_params(limit: int, offset: int):
            return {
                "operationName": "StaysPdpReviewsQuery",
                "locale": "en",
                "currency": "USD",
                "variables": json.dumps({
                    "id": base64.b64encode(f"StayListing:{property_id}".encode()).decode('utf-8'),
                    "pdpReviewsRequest": {
                        "fieldSelector": "for_p3_translation_only",
                        "forPreview": False,
                        "limit": limit,
                        "offset": f"{offset}",
                        "showingTranslationButton": False,
                        "sortingPreference": "MOST_RECENT",
                        "checkinDate": f"{check_in}",
                        "checkoutDate": f"{check_out}",
                        "numberOfAdults": "1",
                        "numberOfChildren": "0",
                        "numberOfInfants": "0",
                        "numberOfPets": "0"
                    }
                }),
                "extensions": json.dumps({
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "dec1c8061483e78373602047450322fd474e79ba9afa8d3dbbc27f504030f91d"
                    }
                })
            }

        headers = {
            'X-Airbnb-API-Key': f'{airbnb_x_api_key}',
        }

        reviews_count = 0

        query_string = self.prepare_query_string(params=prepare_params(limit=1, offset=0))

        full_url = f"{url}?{query_string}"

        response = requests.request(method="GET", url=full_url, headers=headers)
        if response.status_code == 200:
            reviews_count = jmespath.search(expression="data.presentation.stayProductDetailPage.reviews.metadata.reviewsCount", data=response.json())

        if reviews_count and str.isnumeric(f'{reviews_count}'):
            reviews_count = int(reviews_count)

            limit = 24
            offset = 0
            for _ in range(math.ceil(reviews_count/limit)):
                query_string = self.prepare_query_string(params=prepare_params(limit=limit, offset=offset))
                full_url = f"{url}?{query_string}"
                yield scrapy.Request(method="GET", url=full_url, headers=headers, callback=self.parse_reviews, cb_kwargs={
                    "property_id": property_id
                })
                offset += limit

    
    def parse_reviews(self, response, property_id):
        reviews_dict_list = jmespath.search(
            expression='data.presentation.stayProductDetailPage.reviews.reviews[].{"review_id": id, "comments": comments, "reviewer_name": reviewer.firstName, "profile_image_url": reviewer.pictureUrl, "review_date": createdAt, "reviewer_location": localizedReviewerLocation, "rating": rating, "language": language}',
            data=response.json()
        )

        for review in reviews_dict_list:
            review.update(property_id=property_id)
            yield Review.model_construct(**review)


    def available_date_extractor(self, response, airbnb_x_api_key, property_id, details_dict):
        available_date_selector = 'data.merlin.pdpAvailabilityCalendar.calendarMonths[].days[?availableForCheckin == `true` || availableForCheckout==`true`].{"date": calendarDate, "available": available, "check_in": availableForCheckin, "check_out":availableForCheckout, "max_night": maxNights, "min_night": minNights} | []'
        available_dates = jmespath.search(expression=available_date_selector, data=response.json())
        
        price = None
        
        valid_stay = None

        if available_dates:
            valid_stay = self.find_valid_stay(available_dates)
            
            if valid_stay:
                price = self.find_property_price(airbnb_x_api_key=airbnb_x_api_key,property_id=property_id,check_in=valid_stay.get("check_in"),check_out=valid_stay.get("check_out"))
                if price and isinstance(price, str):
                    price = str.strip(price, "$").replace(',', '')
        

        # Host specific selector
        host_name_seclector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.name | [0]"
        host_id_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.userId | [0]"
        profile_image_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.profilePictureUrl | [0]"
        is_super_host_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.isSuperhost | [0]"
        is_verified_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.isVerified | [0]"
        host_rating_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.stats | [0][?type=='RATING'].value | [0]"
        host_review_count_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.stats | [0][?type=='REVIEW_COUNT'].value | [0]"
        host_years_hosting_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='MEET_YOUR_HOST'].section.cardData.stats | [0][?type=='YEARS_HOSTING'].value | [0]"
        host_details_selector = 'niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType==`MEET_YOUR_HOST`].section.{"host_details": hostDetails} | [0]'
        host_about_selector = 'niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType==`MEET_YOUR_HOST`].section.about | [0]'

        def get_host_id():
            _host_id = None
            try:
                encoded_host_id = jmespath.search(expression=host_id_selector, data=details_dict)
                if encoded_host_id:
                    _host_id = base64.b64decode(encoded_host_id.encode('utf-8')).decode('utf-8').split(":")[-1]
            except Exception as err:
                print(err)
            return _host_id

        host_items = {
            "host_id": get_host_id(),
            "host_name": jmespath.search(expression=host_name_seclector, data=details_dict),
            "number_of_reviews": jmespath.search(expression=host_review_count_selector, data=details_dict),
            "rating": jmespath.search(expression=host_rating_selector, data=details_dict),
            "years_hosting": jmespath.search(expression=host_years_hosting_selector, data=details_dict),
            "profile_image": jmespath.search(expression=profile_image_selector, data=details_dict),
            "is_super_host": jmespath.search(expression=is_super_host_selector, data=details_dict),
            "is_verified": jmespath.search(expression=is_verified_selector, data=details_dict),
            "host_details": jmespath.search(expression=host_details_selector, data=details_dict),
            "about": jmespath.search(expression=host_about_selector, data=details_dict),
        }

        yield Host.model_construct(**host_items)

        # Property specific selector
        property_name_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='TITLE_DEFAULT'].section.title | [0]"
        property_desctiption_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='PDP_DESCRIPTION_MODAL'].section | [0].items[].html[].htmlText"
        property_facilities_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sbuiData.sectionConfiguration.root.sections[?sectionId=='OVERVIEW_DEFAULT_V2'].sectionData[] | [0].overviewItems[].title"
        property_review_count_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sbuiData.sectionConfiguration.root.sections[?sectionId=='OVERVIEW_DEFAULT_V2'].sectionData[] | [0].reviewData.reviewCount"
        property_rating_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sbuiData.sectionConfiguration.root.sections[?sectionId=='OVERVIEW_DEFAULT_V2'].sectionData[] | [0].reviewData.ratingText"
        property_detailed_review_selector = 'niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType==`REVIEWS_DEFAULT`].section | [0].ratings[].{"label": label, "rating": localizedRating}'
        room_arrangement_selector = 'niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType==`SLEEPING_ARRANGEMENT_DEFAULT`].section[].arrangementDetails[]'
        latitude_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='LOCATION_PDP'].section[].lat | [0]"
        longitude_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='LOCATION_PDP'].section[].lng | [0]"
        image_url_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='PHOTO_TOUR_SCROLLABLE'].section[].mediaItems[][].baseUrl"
        policies_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType=='POLICIES_DEFAULT'].section"
        amenities_selector = 'niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType==`AMENITIES_DEFAULT`].section | [0].seeAllAmenitiesGroups[].{"title": title, "amenities": amenities[].{"available": available, "title": title, "subtitle": subtitle}}'
        nearby_location_selector = 'niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType==`SEO_LINKS_DEFAULT`].section.nearbyCities[].{"title": title, "subtitle": subtitle}'
        localtion_selector = "niobeMinimalClientData[0][1].data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType==`SEO_LINKS_DEFAULT`].section.breadcrumbs[].title | [1:]"

        location = jmespath.search(expression=localtion_selector, data=details_dict)

        property_dict = {
            "property_id": property_id,
            "property_name": jmespath.search(expression=property_name_selector, data=details_dict),
            "property_desctiption": jmespath.search(expression=property_desctiption_selector, data=details_dict),
            "facilities": jmespath.search(expression=property_facilities_selector, data=details_dict),
            "number_of_reviews": jmespath.search(expression=property_review_count_selector, data=details_dict),
            "property_rating": jmespath.search(expression=property_rating_selector, data=details_dict),
            "detailed_review": jmespath.search(expression=property_detailed_review_selector, data=details_dict),
            "room_arrangement": jmespath.search(expression=room_arrangement_selector, data=details_dict),
            "latitude": jmespath.search(expression=latitude_selector, data=details_dict),
            "longitude": jmespath.search(expression=longitude_selector, data=details_dict),
            "images": jmespath.search(expression=image_url_selector, data=details_dict),
            "policies": jmespath.search(expression=policies_selector, data=details_dict),
            "amenities": jmespath.search(expression=amenities_selector, data=details_dict),
            "currency_code": "USD",
            "price": price,
            "host_id": get_host_id(),
            "nearby_location": jmespath.search(expression=nearby_location_selector, data=details_dict),
            "country": location[0] if len(location) >= 1 else None,
            "state": location[1] if len(location) >= 2 else None,
            "city": location[-1] if len(location) >= 3 else None
        }

        yield Property.model_construct(**property_dict)

        yield from self.get_reviews(
            property_id=property_id,
            check_in=valid_stay.get("check_in") if valid_stay else datetime.now().strftime("%Y-%m-%d"),
            check_out=valid_stay.get("check_out") if valid_stay else (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            airbnb_x_api_key=airbnb_x_api_key
        )

    def find_valid_stay(self, data):
        """
        Find fiest valid stay from the given list.
        First it will find a valid(where check_in='True') check_in date and extract min and max nights.
        Then Find valid check_out date depends on the extracted min nights, max nights and check_out='True'.
        It find first valid check_in and check_out date pair.
        """
        for i, check_in_day in enumerate(data):
            if check_in_day['check_in']:
                check_in_date = datetime.strptime(check_in_day['date'], '%Y-%m-%d')
                min_nights = check_in_day['min_night']
                max_nights = check_in_day['max_night']

                for j in range(i + 1, len(data)):
                    check_out_day = data[j]
                    check_out_date = datetime.strptime(check_out_day['date'], '%Y-%m-%d')
                    nights = (check_out_date - check_in_date).days

                    if check_out_day['check_out'] and min_nights <= nights <= max_nights:
                        return {
                            'check_in': check_in_day['date'],
                            'check_out': check_out_day['date'],
                            'nights': nights
                        }
        return None
    

    def find_property_price(self, airbnb_x_api_key, property_id, check_in, check_out):
        url = "https://www.airbnb.com/api/v3/StaysPdpSections/80c7889b4b0027d99ffea830f6c0d4911a6e863a957cbe1044823f0fc746bf1f"

        params = {
            "operationName": "StaysPdpSections",
            "locale": "en",
            "currency": "USD",
            "variables": {
                "id": base64.b64encode(f"StayListing:{property_id}".encode()).decode('utf-8'),
                "pdpSectionsRequest": {
                    "adults": "1",
                    "amenityFilters": None,
                    "bypassTargetings": False,
                    "categoryTag": None,
                    "causeId": None,
                    "children": None,
                    "disasterId": None,
                    "discountedGuestFeeVersion": None,
                    "displayExtensions": None,
                    "federatedSearchId": None,
                    "forceBoostPriorityMessageType": None,
                    "infants": None,
                    "interactionType": None,
                    "layouts": ["SIDEBAR", "SINGLE_COLUMN"],
                    "pets": 0,
                    "pdpTypeOverride": None,
                    "photoId": None,
                    "preview": False,
                    "previousStateCheckIn": None,
                    "previousStateCheckOut": None,
                    "priceDropSource": None,
                    "privateBooking": False,
                    "promotionUuid": None,
                    "relaxedAmenityIds": None,
                    "searchId": None,
                    "selectedCancellationPolicyId": None,
                    "selectedRatePlanId": None,
                    "splitStays": None,
                    "staysBookingMigrationEnabled": False,
                    "translateUgc": None,
                    "useNewSectionWrapperApi": False,
                    "sectionIds": [
                        "BOOK_IT_CALENDAR_SHEET",
                        "CANCELLATION_POLICY_PICKER_MODAL",
                        "BOOK_IT_FLOATING_FOOTER",
                        "POLICIES_DEFAULT",
                        "EDUCATION_FOOTER_BANNER_MODAL",
                        "BOOK_IT_SIDEBAR",
                        "URGENCY_COMMITMENT_SIDEBAR",
                        "BOOK_IT_NAV",
                        "MESSAGE_BANNER",
                        "HIGHLIGHTS_DEFAULT",
                        "EDUCATION_FOOTER_BANNER",
                        "URGENCY_COMMITMENT"
                    ],
                    "checkIn": f"{check_in}",
                    "checkOut": f"{check_out}"
                }
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "80c7889b4b0027d99ffea830f6c0d4911a6e863a957cbe1044823f0fc746bf1f"
                }
            }
        }

        headers = {
            'X-Airbnb-API-Key': f'{airbnb_x_api_key}',
        }

        query_string = self.prepare_query_string(params=params)
        full_url = f"{url}?{query_string}"

        response = requests.request(method="GET", url=full_url, headers=headers)
        price_selector = "data.presentation.stayProductDetailPage.sections.sections[?sectionComponentType==`BOOK_IT_FLOATING_FOOTER`].section.structuredDisplayPrice.explanationData.priceDetails[0].items[0].priceString | [0]"
        price = jmespath.search(expression=price_selector, data=response.json())

        return price


    def prepare_query_string(self, params: dict):
        _list = []
        for key, value in params.items():
            if isinstance(value, (dict, list)):
                _list.append(f"{key}={quote(json.dumps(value))}")
            else:
                _list.append(f"{key}={value}")

        return '&'.join(_list)