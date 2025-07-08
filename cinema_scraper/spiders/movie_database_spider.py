import scrapy
import config


class MovieDatabaseSpider(scrapy.Spider):
    name = "movie_database"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.settings.set("DOWNLOAD_DELAY", 0, priority="spider")
        if "path" in kwargs:
            spider.settings.set(
                "FEEDS", {"-db.".join(kwargs["path"].split(".")): {"format": "jsonlines"}}, priority="spider"
            )
        return spider

    async def start(self):
        self.count = 0
        # Limit the number of API requests
        # for movie in self.movies:
        for i in range(20):
            movie = self.movies[i]
            if movie.get("year"):
                yield scrapy.Request(url=f"http://www.omdbapi.com/?apikey={config.omdb_key}={movie["title"]}&y={movie["year"]}", callback=self.parse)
            else:
                yield scrapy.Request(url=f"http://www.omdbapi.com/?apikey={config.omdb_key}={movie["title"]}", callback=self.parse)

    def parse(self, response):
        if response.json().get("Response") == "True":
            self.count += 1
            self.logger.info(f"Found {self.count}/{len(self.movies)}")
            yield {"title": response.json().get("Title"), "id": response.json().get("imdbID"), "src": "movie_database"}
