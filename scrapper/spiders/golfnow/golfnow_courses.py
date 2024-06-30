import urllib.parse
import scrapy
from scrapy import spiders
import urllib
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
import json
from typing import Dict

class CourseSpider(scrapy.Spider):
    name="golfnow_courses"

    allowed_domain = ["www.golfnow.com"]
    start_urls = ["https://www.golfnow.com/destinations"]
    

    def __init__(self, name: str | None = None, **kwargs: spiders.Any):
        print("spider initializing..........")
        super().__init__(name, **kwargs)
    

    def parse(self, response: spiders.Response, **kwargs: spiders.Any) -> spiders.Any:
        if response.status == 200:
            yield scrapy.Request(url="https://www.golfnow.com/api/destinations/other", method="GET", callback=self.process_all_destination, headers={
                "Host": "www.golfnow.com",
                'Accept': 'application/json, text/javascript, */*; q=0.01'
            }
            )
        else:
            raise Exception(f"Got error while requesting starting url({response.request.url}) of {self.name}")
    
    #https://www.golfnow.com/destinations/destination_slug
    def get_course(self, response: spiders.Response):
        pass

    # extract all available cities
    def process_all_destination(self, res):
        data = res.json()
        url = "https://www.golfnow.com/destinations/"

        all_links = []

        for country_group in data.get('data').get('countries'):
            for country in country_group.get("countriesGroup"):
                for state in country.get('states'):
                    for city in state.get('cities'):
                        # all_links.append(url+city.get('slug'))
                        yield scrapy.Request(method="GET", url=url+city.get('slug'), callback=self.extract_golf_courses,headers={

                        }, 
                        meta={
                            "data": {
                                "city": city.get('name'),
                                "state": state.get("name"),
                                "country": country.get('name'),
                            }
                        })

    def extract_golf_courses(self, res):
        latlon_pattern = r'\s*var positionInfo = JSON\.parse\(\'\{\"Longitude\"\:([0-9-.]+),\"Latitude\"\:([0-9-.]+)'
        radius_pattern = r'\s*var radius = Number\(\'(\d+)\'\)\;'

        data = {}

        for script in res.css('script').getall():
            matches = re.search(latlon_pattern, script)
            if matches:
                data["longitude"] = matches.group(1)
                data["latitude"] = matches.group(2)
                matches = re.search(radius_pattern, script)
                if matches:
                    data["radius"] = matches.group(1)

        url = "https://www.golfnow.com/api/tee-times/tee-time-results"

        payload = {
            "PageSize": 1000,
            "PageNumber": 0,
            "Date": datetime.now().strftime("%b %d %Y"),
            "SortBy": "Facilities.Distance",
            "SortByRollup": "Facilities.Distance",
            "SortDirection": 0,
            "Latitude": data.get("latitude"),
            "Longitude": data.get("longitude"),
            "Radius": data.get("radius"),
            # "Tags": "PMPT1|PMPT2",
            "NextAvailableTeeTime": True,
            "ExcludePrivateFacilities": False,
            "View": "Courses-Near-Me"
        }

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type" : "application/json; charset=UTF-8"
        }
        yield scrapy.Request(
            method='POST', 
            url=url, 
            callback=self.extract_facilities, 
            meta={"data": {**res.meta.get("data"), "latitude": data.get("latitude"), "longitude": data.get("longitude")}}, 
            headers=headers,
            body=json.dumps(payload).encode()
        )
        # yield scrapy.Request(method='POST', url=url, callback=self.extract_facilities, meta={"data": res.meta.get("data")}, headers=headers, body=json.dumps(payload).encode())

    def extract_facilities(self, res):
        response: dict = res.json()
        url = "https://www.golfnow.com/courses/"
        data = {}
        if response.get('ttResults', {}).get('facilities'):
            for facility in response.get('ttResults', {}).get('facilities'):
                data["facility_id"] = facility.get("facilityId")
                data["facility_name"] = facility.get("facilityName")
                data["address"] = facility.get("address")
                course_details_slug = facility.get("courseDetailSeoFriendlyName")
                yield scrapy.Request(url=url+course_details_slug, method="GET", meta={"data": {**res.meta.get("data"), **data}}, callback=self.description_extractor)
    
    def description_extractor(self, res):
        holes = res.css("p.course-stats>span.course-statistics-holes::text").get()
        par = res.css("p.course-stats>span.course-statistics-par::text").get()
        length = res.css("p.course-stats>span.course-statistics-length::text").get()
        slope = res.css("p.course-stats>span.course-statistics-slope::text").get()
        slope_rating = res.css("p.course-stats>span.course-statistics-rating::text").get()
        course_info_list = self.process_course_list(res.css("ul.course-info-list li::text").getall())

        year_built = course_info_list.get('year_built')
        greens = course_info_list.get('greens')
        season = course_info_list.get('season')
        fairways = course_info_list.get('fairways')
        architects = course_info_list.get('architect(s)')

        description = res.css("div.description>p::text").get()

        images = res.css('ul#facility-images li img::attr(src)').getall()

        breakpoint()



    def process_course_list(self, data)-> Dict:
        converted_data = {}
        for item in data:
            key, value = item.split(': ')
            key = str.lower(key).strip().replace(' ', '_')
            try:
                value = int(value)
            except ValueError:
                pass
            converted_data[key] = value

        return converted_data

