import scrapy
import datetime as dt


class FinnkinoSpider(scrapy.Spider):
    name = "finnkino"
    custom_settings = {"DOWNLOAD_HANDLERS": {
        "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    }, "DOWNLOAD_DELAY": 0}

    async def start(self):

        urls = [
            "https://www.finnkino.fi/xml/Events/?listType=NowInTheatres&area=1014&includeVideos=false",
            "https://www.finnkino.fi/xml/Events/?listType=ComingSoon&includeVideos=false"
        ]
        self.titles = []
        for url in urls:
            yield scrapy.Request(url=url, meta={"playwright": True}, callback=self.parse_movies)

    def parse_movies(self, response):
        for event in response.css("Event"):
            title = event.css("OriginalTitle::text").get()
            human_url = event.css("EventURL::text").get()
            url = f"/xml/Schedule/?area=1014&eventID={event.css("ID::text").get()}&nrOfDays=31"
            year = event.css("ProductionYear::text").get()

            if title not in self.titles:
                movie = {"title": title, "year": year, "info": {
                    "human_url": human_url, "url": "https://www.finnkino.fi"+url, "src": "finnkino"}}
                yield response.follow(url=url, meta={"playwright": True}, callback=self.parse_schedule, cb_kwargs={"movie": movie})
            self.titles.append(title)

    def parse_schedule(self, response, movie={}):
        # Screening info is looked up for every movie because of limitations with playwright

        dates = response.css("dttmShowStartUTC::text").getall()

        if dates:
            first_dt = dt.datetime.fromisoformat(dates[0])
            today = dt.datetime.fromisoformat(
                response.css("PubDate::text").get())
            if len(dates) > 1 and first_dt - today < dt.timedelta(days=1):
                date = ["Jatkuvasti"]
            else:
                date = [first_dt.strftime("%d.%m.")]
        else:
            date = ["Ei päivämäärää"]

        if len(dates) == 1:
            theater = "Finnkino " + response.css("Theatre::text").get()
        else:
            theater = "Finnkino"

        info = movie["info"]
        info["date"] = date
        info["theater"] = theater
        movie["info"] = info
        yield movie
