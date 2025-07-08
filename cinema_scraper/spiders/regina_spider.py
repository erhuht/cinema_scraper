import scrapy


class ReginaSpider(scrapy.Spider):
    name = "regina"
    start_urls = [
        "https://kinoregina.fi/ohjelmisto/elokuvat/",
    ]

    def parse(self, response):
        for movie in response.css("div.movie.pr.col-12.shows-coming"):
            yield {"title": movie.css("a.title::text").get().title(), "src": "regina"}
