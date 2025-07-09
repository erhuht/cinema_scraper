import scrapy


class LikesSpider(scrapy.Spider):
    name = "likes"

    async def start(self):
        yield scrapy.Request(url=f"https://letterboxd.com/{self.user}/likes/films/page/1/", callback=self.parse)

    def parse(self, response):
        for movie in response.css("li.poster-container"):
            # alt is not ideal
            url = "https://letterboxd.com/" + \
                movie.css("div.poster::attr(data-target-link)").get()
            yield {"title": movie.css("img::attr(alt)").get(), "info": {"url": url, "src": "watchlist"}}

        next_page = response.css("a.next::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
