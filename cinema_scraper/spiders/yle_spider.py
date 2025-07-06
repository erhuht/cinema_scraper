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
        yield scrapy.Request(url=response.json()["data"][0]["url"]["full"], callback=self.parse_article)

    def parse_article(self, response):
        for movie in response.css("h2.ydd-heading-large"):
            yield {"title": movie.css("h2::text").get(), "src": "yle"}
