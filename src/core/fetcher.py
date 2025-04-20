import time
from urllib.parse import urlparse
import requests
from src.core.types import Page
from src.infra.robots import RobotsCache

class Fetcher:
    def __init__(self, user_agent="WebCrawler-PA1"):
        self.domain_last_access = {}
        self.robots_cache = RobotsCache()
        self.user_agent = user_agent

    def fetch(self, url: str) -> Page:
        parsed = urlparse(url)
        domain = parsed.netloc

        # politeness
        delay = self.robots_cache.get_crawl_delay(domain, self.user_agent)
        last = self.domain_last_access.get(domain, 0)
        now = time.time()
        wait = max(0, delay - (now - last))
        if wait > 0:
            time.sleep(wait)

        headers = {"User-Agent": self.user_agent}
        response = requests.get(url, headers=headers, timeout=10)

        self.domain_last_access[domain] = time.time()

        return Page(
            url=url,
            html=response.text,
            status_code=response.status_code,
            timestamp=time.time(),
            final_url=response.url
        )
