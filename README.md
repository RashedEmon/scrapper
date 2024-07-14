## Travelai Scrapper

### This project contains multiple spiders. Each spider is responsible to scrape data from webpage with predefined command.


## Installation

#### Dependencies
    python >= 3.10

### Clone git repository

```shell
git clone https://code.lefttravel.com/vrs/rnd/travel-scraper.git
cd project_root
```

### Create and activate virtual environment
```shell
python -m venv .travel_ai_scrapper
source .travel_ai_scrapper/bin/activate
```
#### Install requires libraries
```shell
pip install -r requirements.txt
```

#### List all available spider
```shell
scrapy list
```

#### Run a Spider
```shell
scrapy crawl spider
```