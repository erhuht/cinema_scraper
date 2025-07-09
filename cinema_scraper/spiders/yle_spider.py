import scrapy
import time
from pathlib import Path
import re


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
        movies = response.css("div.ydd-body-content").xpath("*")
        for i in range(len(movies)):
            if movies[i].css("h2.ydd-heading-large"):
                try:
                    text = movies[i+1].css("p::text").get()
                except IndexError:
                    text = ""
                years = re.findall(
                    r"(\b19\d{2}\b|\b20\d{2}\b)[^-]", text or "")
                if years:
                    year = years[-1]
                else:
                    year = 0
                title = movies[i].css("h2::text").get()
                try:
                    date = movies[i+2].css("strong::text").get()
                except IndexError:
                    date = ""
                yield {"title": title, "year": year, "info": {"url": response.url, "src": "yle", "date": date}}
