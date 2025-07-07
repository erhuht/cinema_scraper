import scrapy


class WatchlistSpider(scrapy.Spider):
    name = "watchlist"

    async def start(self):
        yield scrapy.Request(url=f"https://letterboxd.com/{self.user}/watchlist/page/1/", callback=self.parse)

    def parse(self, response):
        for movie in response.css("li.poster-container"):
            # alt is not ideal
            yield {"title": movie.css("img::attr(alt)").get(), "src": "watchlist"}

        next_page = response.css("a.next::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
