import urllib.robotparser
from urllib.parse import urlparse

class RobotsCache:
    def __init__(self):
        self.cache = {}

    def get_parser(self, domain: str):
        if domain not in self.cache:
            parser = urllib.robotparser.RobotFileParser()
            parser.set_url(f"http://{domain}/robots.txt")
            try:
                parser.read()
            except Exception as e:
                print(f"Erro ao ler robots.txt de {domain}: {e}")
                parser = None
            self.cache[domain] = parser
        return self.cache[domain]

    def can_fetch(self, url: str, user_agent: str) -> bool:
        domain = urlparse(url).netloc
        parser = self.get_parser(domain)
        if not parser:
            return True
        return parser.can_fetch(user_agent, url)

    def get_crawl_delay(self, domain: str, user_agent: str) -> float:
        parser = self.get_parser(domain)
        if parser:
            delay = parser.crawl_delay(user_agent)
            return delay if delay is not None else 0.1
        return 0.1