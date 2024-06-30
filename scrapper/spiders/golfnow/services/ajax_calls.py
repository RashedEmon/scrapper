from scrapy import Request
import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, Callable
from datetime import datetime

class GolfNowService:
    def __init__(self) -> None:
        pass

    # get spotlight course
    @staticmethod
    def get_top_pick_course():
        url = "https://www.golfnow.com/destinations/143-dallas-ft-worth"

        payload = {}
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Sec-Fetch-Site': 'none',
            'Accept-Encoding': 'gzip, deflate, br',
            'Sec-Fetch-Mode': 'navigate',
            'Host': 'www.golfnow.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Sec-Fetch-Dest': 'document',
            'Connection': 'keep-alive'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        soup = BeautifulSoup(response.text, 'html.parser')


        # Find the script tag containing the JSON
        script_tags = soup.find_all('script', string=re.compile('var upostal'))
        for script_tag in script_tags:
            
            if "var upostal = upostal" in script_tag.text:
                print("Script tag found:")
                
                # Extract the JSON string using a regular expression
                match = re.search(r'JSON\.parse\((.*?)\)', script_tag.string)
                
                if match:
                    json_string = match.group(1)
                    
                    # Remove single quotes around the JSON string
                    json_string = json_string.strip("'")
                    
                    # Parse the JSON string
                    try:
                        upostal_data = json.loads(json_string)
                        
                        # Now you can access the data
                        print("Latitude:", upostal_data['latitude'])
                        print("Longitude:", upostal_data['longitude'])
                    except json.JSONDecodeError as e:
                        print("Error decoding JSON:", e)
                        print("JSON string:", json_string)
                else:
                    print("JSON.parse() not found in the script tag")
            else:
                print("Script tag with 'var upostal' not found")


            url = "https://www.golfnow.com/api/tee-times/spotlight-course-result"

            payload = "{\"PageSize\":30,\"PageNumber\":0,\"Date\":\"Jun 25 2024\",\"SortBy\":\"Facilities.Distance\",\"SortByRollup\":\"Facilities.Distance\",\"SortDirection\":0,\"Latitude\":32.778038,\"Longitude\":-96.80054,\"Radius\":85,\"NextAvailableTeeTime\":true,\"ExcludePrivateFacilities\":true,\"Tags\":\"PMPT1\"}"
            headers = {
                'Content-Type': 'application/json; charset=UTF-8',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Sec-Fetch-Site': 'same-origin',
                'Accept-Language': 'en-GB,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Fetch-Mode': 'cors',
                'Host': 'www.golfnow.com',
                'Origin': 'https://www.golfnow.com',
                'Content-Length': '267',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
                'Referer': 'https://www.golfnow.com/destinations/143-dallas-ft-worth',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'X-Requested-With': 'XMLHttpRequest'
            }
            with open("compare.txt", 'w') as file:
                
                response = requests.request("POST", url, headers=headers, data=payload)
                file.write(response.text)
                file.write("#######################################")
                response = requests.request("POST", url, headers=headers, data=payload)
                file.write(response.text)
            breakpoint()

    @staticmethod
    def get_all_golf_courses(callback: Callable, meta, data: Dict):
        pass




if __name__ == '__main__':
    GolfNowService.get_top_pick_course()