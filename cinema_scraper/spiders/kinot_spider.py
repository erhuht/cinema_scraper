import scrapy
from html import unescape


class KinotSpider(scrapy.Spider):
    name = "kinot"
    start_urls = [
        "https://www.kinot.fi/wp-json/kinot-shows/v1/movies",
    ]

    def parse(self, response):
        for movie in response.json():
            yield {"title": unescape(movie["movie_title"]), "src": "kinot"}
