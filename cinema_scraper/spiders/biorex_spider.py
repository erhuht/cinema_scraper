import scrapy


class BioRexSpider(scrapy.Spider):
    name = "biorex"

    async def start(self):
        yield scrapy.Request(url="https://biorex.fi/en/movies/?cinema_id=13", callback=self.fetch_movies)

    def fetch_movies(self, response):
        url = "https://biorex.fi/wp-admin/admin-ajax.php?lang=en&f_cinemas=all"
        yield scrapy.FormRequest(
            url=url,
            formdata={
                "action": "br_movies_handler",
                "genre": "-1",
                "date": "-1",
                "format": "-1",
                "language": "-1",
                "activeAlternativeTheater": "all",
                "activeAlternativeTheaterTitle": "Helsinki all",
                "activeType": "movies"
            },
            callback=self.parse
        )


    def parse(self, response):
        response = response.replace(body=response.json()["posts"].encode("utf-8"))
        for movie in response.css("div.movie-card__title"):
            yield {"title": movie.css("h3::text").get(), "src": "biorex"}