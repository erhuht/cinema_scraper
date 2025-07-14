import scrapy
import config
import re


class MovieDatabaseSpider(scrapy.Spider):
    name = "movie_database"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.settings.set("DOWNLOAD_DELAY", 0, priority="spider")
        spider.settings.set("ROBOTSTXT_OBEY", False, priority="spider")
        if "path" in kwargs:
            spider.settings.set(
                "FEEDS", {"-db.".join(kwargs["path"].split(".")): {"format": "jsonlines"}}, priority="spider"
            )
        return spider

    async def start(self):
        for movie in self.movies:
            possible_movies = self.generate_possible_movies(movie)

            next_movie = possible_movies.pop(0)
            url = self.generate_omdb_url(next_movie)
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse_omdb, cb_kwargs={"movie": next_movie, "possible_movies": possible_movies})

    def generate_omdb_url(self, movie):
        if movie.get("year"):
            return f"http://www.omdbapi.com/?apikey={config.omdb_key}&t={movie["title"]}&y={movie["year"]}"
        else:
            return f"http://www.omdbapi.com/?apikey={config.omdb_key}&t={movie["title"]}"

    def generate_imdb_url(self, movie):
        if movie.get("year"):
            return f"https://www.imdb.com/find/?q={movie["title"]} {movie["year"]}&s=tt&exact=true"
        else:
            return f"https://www.imdb.com/find/?q={movie["title"]}&s=tt&exact=true"

    def generate_possible_movies(self, movie):
        # Try finding the movie without a prefix and colon or without parentheses
        possible_titles = [movie["title"]]
        if movie["title"].split(":")[-1] not in possible_titles:
            possible_titles.append(movie["title"].split(":")[-1].strip())

        for title in possible_titles:
            if "(" in title and ")" in title:
                title_no_paren = re.sub(r"\s*\([^)]*\)", "", title).strip()
                if title_no_paren and title_no_paren not in possible_titles:
                    possible_titles.append(title_no_paren)

        possible_movies = []

        for title in possible_titles:
            possible_movies.append(
                {"title": title, "info": movie["info"], "og_title": movie["title"]})
            if movie.get("year"):
                possible_movies.append(
                    {"title": title, "year": movie["year"], "info": movie["info"], "og_title": movie["title"]})

        return possible_movies

    def parse_omdb(self, response, movie={}, possible_movies=[]):
        if response.json().get("Response") == "True":
            yield {"title": response.json().get("Title"), "og_title": movie["og_title"], "id": response.json().get("imdbID"), "info": movie["info"], "id_src": "omdb"}
        else:
            url = self.generate_imdb_url(movie)
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse_imdb, cb_kwargs={"movie": movie, "possible_movies": possible_movies})

    def parse_imdb(self, response, movie={}, possible_movies=[]):
        if response.css("a.ipc-metadata-list-summary-item__t"):
            title = response.css(
                "a.ipc-metadata-list-summary-item__t::text").get()
            imdb_id = response.css(
                "a.ipc-metadata-list-summary-item__t::attr(href)").get().split("/")[2]
            yield {"title": title, "og_title": movie["og_title"], "id": imdb_id, "info": movie["info"], "id_src": "imdb"}
        else:
            if len(possible_movies) > 0:
                next_movie = possible_movies.pop(0)
                url = self.generate_omdb_url(next_movie)
                yield scrapy.Request(url=url, dont_filter=True, callback=self.parse_omdb, cb_kwargs={"movie": next_movie, "possible_movies": possible_movies})
            else:
                yield {"title": movie["og_title"], "info": movie["info"], "id": "", "id_src": "not_found"}
