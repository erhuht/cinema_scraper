import scrapy
import time
from pathlib import Path


class Yle(scrapy.Spider):
    name = "yle"
    start_urls = [
        time.strftime(
            "https://yle-fi-search.api.yle.fi/v1/search?app_id=hakuylefi_v2_prod&app_key=4c1422b466ee676e03c4ba9866c0921f&language=fi&limit=10&offset=0&query=teeman%%20%Y%%20elokuvat&type=article"),
    ]
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
    }

    def parse(self, response):
        response_list = response.json()["data"]
        url = ""
        season = 0
        for article in response_list:
            if article["headline"] == time.strftime("Teeman kevään %Y elokuvat") and season == 0:
                url = article["url"]["full"]
                season = 1
            elif article["headline"] == time.strftime("Teeman kesän %Y elokuvat") and season <= 1:
                url = article["url"]["full"]
                season = 2
            elif article["headline"] == time.strftime("Teeman syksyn %Y elokuvat") and season <= 2:
                url = article["url"]["full"]
                season = 3

        yield scrapy.Request(url=url, callback=self.parse_article)

    def parse_article(self, response):
        for movie in response.css("h2.ydd-heading-large"):
            yield {"title": movie.css("h2::text").get(), "src": "yle"}
