import scrapy


class ScreeningInfoSpider(scrapy.Spider):
    name = "screening_info"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.settings.set("DOWNLOAD_DELAY", 0, priority="spider")
        spider.settings.set("ROBOTSTXT_OBEY", False, priority="spider")
        if "path" in kwargs:
            spider.settings.set(
                "FEEDS", {"-info.".join(kwargs["path"].split(".")): {"format": "jsonlines"}}, priority="spider"
            )
        return spider

    async def start(self):
        for movie in self.movies:
            yield scrapy.Request(url=movie["info"]["url"], dont_filter=True, callback=self.parse, cb_kwargs={"movie": movie})

    def parse(self, response, movie=None):
        src = movie["info"]["src"]
        if src == "biorex":
            dates = response.css(
                "div.movie-showtimes-list__day::text").getall()
            date = [dates[0]]
            if len(dates) > 1 and "Tänään" in dates[0]:
                date = ["Jatkuvasti"]
            theater = "BioRex Tripla/Redi"
        elif src == "regina":
            date = response.css(
                "div.title-container span.title::text").getall()
            theater = "Kino Regina"
        elif src == "yle":
            date = [movie["info"]["date"]]
            theater = "Yle Areena"
        elif src == "kinot":
            date = list(response.json().keys())
            theater = list({show["theater_title"]
                           for date, shows in response.json().items() for show in shows})

        yield {"og_title": movie["og_title"], "title": movie["title"], "date": date, "theater": theater, "info": movie["info"], "letterboxd_info": movie["letterboxd_info"], "id_src": movie["id_src"]}
