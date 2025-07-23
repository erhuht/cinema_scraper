import scrapy
import json


class LikesSpider(scrapy.Spider):
    name = "likes"

    async def start(self):
        yield scrapy.Request(url=f"https://letterboxd.com/{self.user}/likes/films/page/1/", callback=self.parse)

    def parse(self, response):
        for movie in response.css("li.poster-container"):
            url = "https://letterboxd.com" + \
                movie.css("div.poster::attr(data-target-link)").get()
            # id = movie.css("div.poster::attr(data-film-id)").get()
            # yield {"title": movie.css("img::attr(alt)").get(), "info": {"human_url": url, "url": url, "src": "likes", "letterboxd_id": id}}
            yield scrapy.Request(url=url, callback=self.parse_movie)

        next_page = response.css("a.next::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_movie(self, response):
        title = response.css("h1.primaryname span::text").get()
        data = response.xpath(
            "//script[@type='application/ld+json']/text()").get()
        poster = json.loads(data.strip().split("\n")[1])["image"].split("?")[
            0].replace("230-0-345", "2000-0-3000")
        director = response.css("a.contributor span::text").get()
        info = {"human_url": response.url, "url": response.url,
                "poster": poster, "director": director, "src": "watchlist"}
        output = {"title": title, "info": info}
        try:
            id = response.xpath(
                "//a[@data-track-action='IMDb']/@href").get().split("/")[-2]
            output["id"] = id
        except AttributeError:
            pass

        yield output
