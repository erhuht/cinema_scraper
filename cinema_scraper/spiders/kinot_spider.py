import scrapy


class KinotSpider(scrapy.Spider):
    name = "kinot"
    start_urls = [
            "https://www.kinot.fi/wp-json/kinot-shows/v1/movies",
        ]


    def parse(self, response):
        for movie in response.json():
            yield {"title": movie["movie_title"], "src": "kinot"}