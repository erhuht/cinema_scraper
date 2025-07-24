import scrapy
import json
from dotenv import load_dotenv
import os
import json


class Letterboxd(scrapy.Spider):
    name = "letterboxd"

    async def start(self):
        load_dotenv()
        custom_lists = json.loads(os.getenv("CUSTOM_LISTS"))

        sections = [{"name": "Watchlist", "url": f"https://letterboxd.com/{self.user}/watchlist/page/1/"},
                    {"name": "Tykätyt", "url": f"https://letterboxd.com/{self.user}/likes/films/page/1/"}]
        sections += custom_lists
        for section in sections:
            yield scrapy.Request(url=section["url"], callback=self.parse, cb_kwargs={"section": section["name"]})

    def parse(self, response, section=""):
        for movie in response.css("li.poster-container"):
            url = "https://letterboxd.com" + \
                movie.css("div.poster::attr(data-target-link)").get()
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse_movie, cb_kwargs={"section": section})

        next_page = response.css("a.next::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse, cb_kwargs={"section": section})

    def parse_movie(self, response, section=""):
        title = response.css("h1.primaryname span::text").get()
        data = response.xpath(
            "//script[@type='application/ld+json']/text()").get()
        poster = json.loads(data.strip().split("\n")[1])["image"].split("?")[
            0].replace("230-0-345", "2000-0-3000")
        director = response.css("a.contributor span::text").get()
        info = {"human_url": response.url, "url": response.url,
                "poster": poster, "director": director, "section": section, "src": "letterboxd"}
        output = {"title": title, "info": info}
        try:
            id = response.xpath(
                "//a[@data-track-action='IMDb']/@href").get().split("/")[-2]
            output["id"] = id
        except AttributeError:
            pass

        yield output
