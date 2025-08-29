import scrapy


class SherylSpider(scrapy.Spider):
    name = "sheryl"
    start_urls = [
        "https://sheryl.tokyo.fi/",
    ]

    def parse(self, response):
        output_movies = []
        for movie in response.css("div.kinola-event"):
            url = movie.css("a.kinola-event-title::attr(href)").get()
            info = {"human_url": url, "url": url, "src": "sheryl"}
            title = movie.css("a.kinola-event-title::text").get().strip()
            if title not in output_movies:
                yield {"title": title, "info": info}
                output_movies.append(title)
