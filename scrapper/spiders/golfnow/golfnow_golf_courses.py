import os
import re
import json
import scrapy
from typing import Dict
from datetime import datetime

from scrapy import spiders

from scrapper.database.operations import CommonDBOperation
from scrapper.database.models import GolfCourse
from scrapper.database.pydantic_models import PydanticGolfCourse
from scrapper.config import PROJECT_ROOT

class CourseSpider(scrapy.Spider):
    name="golfnow_golf_courses"
    allowed_domain = ["www.golfnow.com"]
    start_urls = ["https://www.golfnow.com/course-directory"]

    def __init__(self, name: str | None = None, **kwargs: spiders.Any):
        print("spider initializing..........")
        self.db_operation = CommonDBOperation()
        self.domain = "https://www.golfnow.com"
        self.log_file = f"{PROJECT_ROOT}/spiders_logs/non_traverse_pages.txt"
        self.create_file(self.log_file)
        super().__init__(name, **kwargs)
    
    # Process page https://www.golfnow.com/course-directory
    def parse(self, response: spiders.Response, **kwargs: spiders.Any) -> spiders.Any:
        if not response.css("div.country-cube.rounded.white>h2>a::attr('href')").getall():
            self.keep_log(lines=[f"{response.url}, {response.status}"])
        
        for country in response.css("div.country-cube.rounded.white>h2>a::attr('href')").getall():
            yield scrapy.Request(url=self.domain+country, callback=self.process_all_destination)

    # Process page https://www.golfnow.com/course-directory/us
    def process_all_destination(self, res):
        country = res.css("#country-select option[selected]::text").get()

        if not res.css(f".us-destination-wrapper>div>a").getall():
            self.keep_log(lines=[f"{res.url}, {res.status}"])

        for state_anchor in res.css(f".us-destination-wrapper>div>a"):
            state_link = state_anchor.css("a::attr('href')").get()
            state_name = state_anchor.css("a::text").get()

            yield scrapy.Request(url=self.domain+state_link, callback=self.process_all_states, cb_kwargs={
                "country": country,
                "state": state_name
            })
    # Process page https://www.golfnow.com/course-directory/us/pa
    def process_all_states(self, res, country, state):
        if not res.css('section.city-courses>.row>div.columns>div.city-cube>h2>a').getall():
            self.keep_log(lines=[f"{res.url}, {res.status}"])

        for city in res.css('section.city-courses>.row>div.columns>div.city-cube>h2>a'):
            city_link = city.css("a::attr(href)").get()

            yield scrapy.Request(url=self.domain+city_link, callback=self.process_all_city, cb_kwargs={
                "country": country,
                "state": state,
            })
    
    # Process page https://www.golfnow.com/course-directory/us/pa/8902-harrisburg
    def process_all_city(self, res, country, state):
        url = f"{self.domain}/courses/"

        city = res.css("ol.course-directory-breadcrumbs li:last-child span[itemprop='name']::text").get()

        if not res.css(".city-courses>div.row>div.columns>div::attr(id)").getall():
            self.keep_log(lines=[f"{res.url}, {res.status}"])

        
        for course in res.css(".city-courses>div.row>div.columns>div::attr(id)").getall():
            course_id = course.split("-", 1)[-1]
            yield scrapy.Request(url=url+course_id, callback=self.process_golf_courses, cb_kwargs={
                "country": country,
                "state": state,
                "city": city,
                "course_id": course_id
            })

    def process_golf_courses(self, res, country, state, city, course_id):
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
            "course_id": course_id,
            "course_name": res.css("#course-quick-info h3[itemprop='name']::text").get(),
            "city": city,
            "state": state,
            "country": country,
            "latitude": res.css("gn-related-courses[latitude]::attr(latitude)").get(),
            "longitude": res.css("gn-related-courses[longitude]::attr(longitude)").get(),
            "address": ",".join(res.css("#course-quick-info address span::text").getall()),
            "postal_code": res.css("#course-quick-info address span[itemprop='postalCode']::text").get(),
            "course_rating": str.strip(res.css('span.course-rating meta[itemprop="ratingValue"]::attr(content)').get('')) or None,
            "number_of_holes": res.css("p.course-stats>span.course-statistics-holes").xpath('text()[normalize-space()]').get() or None,
            "par": res.css("p.course-stats>span.course-statistics-par").xpath('text()[normalize-space()]').get() or None,
            "yardage": self.get_first_numeric_word(res.css("p.course-stats>span.course-statistics-length").xpath('text()[normalize-space()]').get()) or None,
            "slope_rating": res.css("p.course-stats>span.course-statistics-rating").xpath('text()[normalize-space()]').get() or None,
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
        
        try:
            valid_golf_course = PydanticGolfCourse(**golf_course)
            self.db_operation.insert_or_ignore(model_class=GolfCourse,data_dict=valid_golf_course.model_dump())
        except Exception as err:
            lines = [f"{res.url}, {res.status}"]
            self.keep_log(lines=lines)

        
    def process_course_list(self, data)-> Dict:
        converted_data = {}
        try:
            for item in data:
                key, value = item.split(': ')
                key = str.lower(key).strip().replace(' ', '_')
                converted_data[key] = value
        except Exception as err:
            print(err)
        return converted_data
    
    def get_first_numeric_word(self, text):
        res = ""
        try:
            first_numeric_word = re.search(r'^\s*(\d+)\b', text)
            if first_numeric_word:
                res = first_numeric_word.group(1)
        except Exception as err:
            print(err)
        return res

    def html_table_to_dict(self, table):
        rows = []
        try:
            headers = table.css('thead tr th::text').getall()
            for row in table.css('tbody tr'):
                temp_dict = {}
                for idx, item in enumerate(row.css('td::text').getall()):
                    temp_dict[headers[idx]] = item

                rows.append(temp_dict)
        except Exception as err:
            print(err)
        return rows

    def create_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
        
        directory = os.path.dirname(file_path)
        
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w') as f:
            pass
    
    def keep_log(self, lines):

        with open(self.log_file, "w") as file:
            file.writelines(lines)