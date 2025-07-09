import scrapy
from html import unescape


class KinotSpider(scrapy.Spider):
    name = "kinot"
    start_urls = [
        "https://www.kinot.fi/wp-json/kinot-shows/v1/movies",
    ]

    def parse(self, response):
        for movie in response.json():
            url = "https://www.kinot.fi/wp-json/kinot-movies/v1/shows?movie_slug=" + \
                movie["movie_slug"]
            human_url = "https://www.kinot.fi/elokuva/" + movie["movie_slug"]
            yield {"title": unescape(movie["movie_title"]), "info": {"human_url": human_url, "url": url, "src": "kinot"}}
