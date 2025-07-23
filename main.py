from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrapy.utils.reactor import install_reactor
import jsonlines
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import os
from newsletter.newsletter import populate_html
from newsletter.send_email import send_email

install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")

load_dotenv()
user = os.getenv("LETTERBOXD_USER")
if not user:
    raise ValueError("Missing LETTERBOXD_USER environment variable")

settings = get_project_settings()
date = datetime.now().strftime("%Y%m%d-%H%M%S")
log_path = Path("logs") / (date + ".jsonl")
settings.set("FEEDS", {str(log_path): {"format": "jsonlines"}})

configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})
runner = CrawlerRunner(settings)

from twisted.internet import reactor, defer  # nopep8


@defer.inlineCallbacks
def crawl():
    yield runner.crawl("kinot")
    yield runner.crawl("biorex")
    yield runner.crawl("regina")
    yield runner.crawl("yle")
    yield runner.crawl("watchlist", user=user)
    yield runner.crawl("likes", user=user)

    with jsonlines.open(log_path) as reader:
        yield runner.crawl("movie_database", movies=list(reader), path=str(log_path))

    with jsonlines.open("-db.".join(str(log_path).split("."))) as reader:
        movie_list = list(reader)

    watchlist = {m["id"]: m for m in movie_list if m["id"]
                 and m["info"]["src"] in ["watchlist", "likes"]}
    screening_list = [m for m in movie_list if m["id"]
                      and m["info"]["src"] not in ["watchlist", "likes"]]

    matching_movies = []
    for movie in screening_list:
        if movie["id"] in watchlist.keys():
            movie["letterboxd_info"] = watchlist[movie["id"]
                                                 ]["info"]
            matching_movies.append(movie)

    print("Crawling info for:")
    print(matching_movies)

    yield runner.crawl("screening_info", movies=matching_movies, path=str(log_path))

    reactor.stop()


crawl()
reactor.run()

with jsonlines.open("-info.".join(str(log_path).split("."))) as reader:
    info_list = list(reader)

output = populate_html(info_list)

output_path = Path("newsletter/output")
output_path.mkdir(parents=True, exist_ok=True)
with open(output_path / (date + ".html"), "w", encoding="utf-8") as f:
    f.write(output)

print("Created email HTML: " + str(output_path / (date + ".html")))

subject = "Helsingin elokuvauutiskirje"
sender = os.getenv("SENDER_EMAIL")
recipient = os.getenv("RECIPIENT_EMAIL")
password = os.getenv("SENDER_PASSWORD")
send_email(subject, output, sender, [
           recipient], password)
