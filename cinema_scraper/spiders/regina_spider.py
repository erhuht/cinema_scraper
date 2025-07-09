import scrapy


class ReginaSpider(scrapy.Spider):
    name = "regina"
    start_urls = [
        "https://kinoregina.fi/ohjelmisto/elokuvat/",
    ]

    def parse(self, response):
        for movie in response.css("div.movie.pr.col-12.shows-coming"):
            url = movie.css("a.title::attr(href)").get()
            info = {"human_url": url, "url": url, "src": "regina"}
            yield {"title": movie.css("a.title::text").get().title(), "info": info}
