# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
# from typing import TYPE_CHECKING

from scrapy.http import Response
from scrapy.utils.httpobj import urlparse_cached

# if TYPE_CHECKING:
from scrapy.http.request import Request
from scrapy.settings import BaseSettings

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class CinemaScraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    async def process_start(self, start):
        # Called with an async iterator over the spider start() method or the
        # maching method of an earlier spider middleware.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class CinemaScraperDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class MoviePolicy:
    def __init__(self, settings: BaseSettings):
        self.ignore_schemes: list[str] = settings.getlist(
            "HTTPCACHE_IGNORE_SCHEMES")
        self.ignore_http_codes: list[int] = [
            int(x) for x in settings.getlist("HTTPCACHE_IGNORE_HTTP_CODES")
        ]

    def should_cache_request(self, request: Request) -> bool:
        if urlparse_cached(request).scheme in self.ignore_schemes:
            return False
        elif urlparse_cached(request).netloc in ["www.omdbapi.com", "www.imdb.com"]:
            return True
        else:
            return urlparse_cached(request).netloc == "letterboxd.com" and "film/" in urlparse_cached(request).path

    def should_cache_response(self, response: Response, request: Request) -> bool:
        if response.status in self.ignore_http_codes:
            return False
        elif urlparse_cached(request).netloc in ["www.omdbapi.com", "www.imdb.com"]:
            return True
        else:
            return urlparse_cached(request).netloc == "letterboxd.com" and "film/" in urlparse_cached(request).path

    def is_cached_response_fresh(
        self, cachedresponse: Response, request: Request
    ) -> bool:
        return True

    def is_cached_response_valid(
        self, cachedresponse: Response, response: Response, request: Request
    ) -> bool:
        return True
