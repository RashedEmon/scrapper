import scrapy
from scrapy import spiders
import re
from datetime import datetime
import json
from typing import Dict
from scrapper.database.operations import CommonDBOperation
from scrapper.database.models import GolfCourse, TeeTime
from scrapper.database.pydantic_models import PydanticGolfCourse, PydanticTeeDetails

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

    # extract all available cities
    def process_all_destination(self, res):
        data = res.json()
        url = "https://www.golfnow.com/destinations/"

        for country_group in data.get('data').get('countries'):
            for country in country_group.get("countriesGroup"):
                for state in country.get('states'):
                    for city in state.get('cities'):
                        yield scrapy.Request(method="GET", url=url+city.get('slug'), callback=self.extract_golf_courses,
                        meta={
                            "data": {
                                "city": city.get('name'),
                                "state": state.get("name"),
                                "country": country.get('name'),
                            }
                        },
                        )

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
            meta={"data": {**res.meta.get("data"), "latitude": data.get("latitude"), "longitude": data.get("longitude"), "radius": data.get("radius")}}, 
            headers=headers,
            body=json.dumps(payload).encode()
        )

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
        data = res.meta.get("data")
        course_info_list = self.process_course_list(res.css("ul.course-info-list li::text").getall())

        tee_details = []
        if res.css('#course-details-chart'):
            for tab_id in res.css('#course-details-chart > .course-tees-list>li>a::attr(id)').getall():
                tee_type = res.css(f'#course-details-chart > .course-tees-list>li>a[id="{tab_id}"]::text').get()
                table = res.css(f'#course-details-chart div#tab-{tab_id} table')
                tee_details.append(
                    {
                        tee_type: self.html_table_to_dict(table=table)
                    }
                )

        golf_course = {
            "course_id": data.get("facility_id"),
            "course_name": data.get("facility_name"),
            "city": data.get("city"),
            "state": data.get("state"),
            "country": data.get("country"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "address": self.build_address(res.meta.get('data', {}).get('address', {})),
            "postal_code": data.get("address", {}).get("postalCode"),
            "course_rating": str.strip(res.css('span.course-rating meta[itemprop="ratingValue"]::attr(content)').get('')) or None,
            "number_of_holes": str.strip(res.css("p.course-stats>span.course-statistics-holes::text").get('')) or None,
            "par": str.strip(res.css("p.course-stats>span.course-statistics-par::text").get('')) or None,
            "yardage": str.strip(res.css("p.course-stats>span.course-statistics-length::text").get('')) or None,
            "slope_rating": str.strip(res.css("p.course-stats>span.course-statistics-rating::text").get('')) or None,
            "year_built": course_info_list.get('year_built'),
            "greens": course_info_list.get('greens'),
            "architect": course_info_list.get('architect(s)'),
            "description": res.css("div.description>p::text").get(),
            "images": str.join(",", res.css('ul#facility-images li img::attr(src)').getall()),
            "tee_details": json.dumps({"tee_details": tee_details}) if tee_details else None,
            "policies": json.dumps({"policies": res.css('#policies-info > div > h3:contains("Policies")+ul li::text').getall()}),
            "rental_services": json.dumps({"rental_services": res.css('#policies-info > div > h3:contains("Rentals/Services")+ul li::text').getall()}),
            "practice_instructions" : json.dumps({"practice_instructions": res.css('#policies-info > div > h3:contains("Practice/Instruction")+ul li::text').getall()})
        }

        valid_golf_course = PydanticGolfCourse(**golf_course)
        CommonDBOperation().insert_or_ignore(model_class=GolfCourse,data_dict=valid_golf_course.model_dump())


        latitude=res.meta.get("data", {}).get("latitude")
        longitude=res.meta.get("data", {}).get("longitude")
        radius=res.meta.get("data", {}).get("radius")

        url = "https://www.golfnow.com/api/tee-times/tee-time-results"

        payload = {
            "Radius": radius,
            "Latitude": latitude,
            "Longitude": longitude,
            "PageSize": 1000,
            "PageNumber": 0,
            "SearchType": 1,
            "SortBy": "Date",
            "SortDirection": 0,
            "Date": datetime.now().strftime("%b %d %Y"),
            "HotDealsOnly": "false",
            "BestDealsOnly": False,
            "PriceMin": "0",
            "PriceMax": "10000",
            "Players": "0",
            "Holes": "3",
            "RateType": "all",
            "TimeMin": "10",
            "TimeMax": "42",
            "FacilityId": data.get("facility_id"),
            "SortByRollup": "Date.MinDate",
            "View": "Grouping",
            "ExcludeFeaturedFacilities": False,
            "TeeTimeCount": 15,
            "PromotedCampaignsOnly": "false"
        }

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type" : "application/json; charset=UTF-8"
        }

        yield scrapy.Request(
            method="POST",
            url=url,
            headers=headers,
            body=json.dumps(payload).encode(),
            callback=self.parse_tee_times
        )

    
    def parse_tee_times(self, res):

        url = "https://www.golfnow.com"

        for tee_time in res.json().get("ttResults").get("teeTimes"):
            extracted_data = {
                "course_id": tee_time.get("facilityId"),
                "tee_time_id": tee_time.get("defaultTeeTimeRateId"),
                "tee_datetime": tee_time.get("time"),
                "display_rate": tee_time.get("displayRate"),
                "currency": tee_time.get("currencyCode"),
                "display_fee_rate": tee_time.get("displayFeeRates"),
                "max_transaction_fee": tee_time.get("maxPriceTransactionFee"),
                "hole_count": tee_time.get("teeTimeRates", [{}])[0].get("holeCount"),
                "rate_name": tee_time.get("teeTimeRates", [{}])[0].get("rateName")
            }

            detail_url = tee_time.get("detailUrl")
            yield scrapy.Request(url=url+detail_url, callback=self.parse_tee_times_details, meta={"data": extracted_data})

    def parse_tee_times_details(self, res):
        tee_details = {}
        table = res.css("#course-details-chart")
        if table:
            tee_details = {"tee_details":self.html_table_to_dict(table)}

        tee_details = {
            **res.meta.get("data"),
            "tee_details": tee_details,
        }

        valid_tee_details = PydanticTeeDetails(**tee_details)
        CommonDBOperation().insert_or_ignore(model_class=TeeTime, data_dict=valid_tee_details.model_dump())
        

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
    
    def build_address(self, address):
        address_string = ""
        if address:
            address_parts = [address['line1'], address['line2'], address['city'], address['stateProvinceCode'], address['postalCode'], address['country']]
            address_string = ', '.join(part for part in address_parts if part)

        return address_string
    
    def html_table_to_dict(self, table):
        headers = table.css('thead tr th::text').getall()
        rows = []
        for row in table.css('tbody tr'):
            temp_dict = {}
            for idx, item in enumerate(row.css('td::text').getall()):
                temp_dict[headers[idx]] = item

            rows.append(temp_dict)
        
        return rows
