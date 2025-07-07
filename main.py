from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from pathlib import Path

settings = get_project_settings()
log_path = Path("logs") / "%(time)s.jsonl"
settings.set("FEEDS", {str(log_path): {"format": "jsonlines"}})

process = CrawlerProcess(settings)

process.crawl("kinot")
process.crawl("biorex")
process.crawl("regina")
process.crawl("yle")
process.crawl("watchlist")
process.crawl("likes")
process.start()
