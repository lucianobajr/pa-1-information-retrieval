import time
import json
import queue
import requests
import threading

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from src.config.settings import Settings

from src.infra.logger import get_logger
from src.infra.frontier import get_seeds_from_file, verify_is_valid_url


class CrawlerService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__, debug=settings.debug)
        self.frontier = queue.Queue()
        self.visited = set()
        self.lock = threading.Lock()
        self.domain_last_access = {}
        self.page_count = 0
        self.max_pages = settings.page_limit
        self.debug = settings.debug

        seeds = get_seeds_from_file(seed_file=settings.seed_file)
        for seed in seeds:
            self.frontier.put(seed)
            self.visited.add(seed)

    def run(self):
        threads = []
        for _ in range(5):  # Número de threads pode ser ajustado
            thread = threading.Thread(target=self.worker)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def worker(self):
        while not self.frontier.empty():
            if self.page_count >= self.max_pages:
                return

            url = self.frontier.get()

            try:
                self.fetch_and_process(url)
            except Exception as e:
                self.logger.error(f"Erro ao processar {url}: {e}")

            self.frontier.task_done()

    def fetch_and_process(self, url: str):
        domain = urlparse(url).netloc

        with self.lock:
            last_access = self.domain_last_access.get(domain)
            now = time.time()
            if last_access and now - last_access < 0.1:
                wait_time = 0.1 - (now - last_access)
                time.sleep(wait_time)
            self.domain_last_access[domain] = time.time()

        headers = {'User-Agent': 'WebCrawler-PA1'}
        response = requests.get(url, headers=headers, timeout=5)

        if 'text/html' not in response.headers.get('Content-Type', ''):
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string.strip() if soup.title else ""
        text = ' '.join(soup.get_text().split()[:20])
        timestamp = int(time.time())

        with self.lock:
            self.page_count += 1

        if self.debug:
            record = {
                "URL": url,
                "Title": title,
                "Text": text,
                "Timestamp": timestamp
            }
            print(json.dumps(record, ensure_ascii=False))

        # Descobrir novos links
        for link_tag in soup.find_all('a', href=True):
            new_url = urljoin(url, link_tag['href'])
            new_url = new_url.split('#')[0]  # Remove fragmentos

            if verify_is_valid_url(new_url):
                with self.lock:
                    if new_url not in self.visited and self.page_count < self.max_pages:
                        self.visited.add(new_url)
                        self.frontier.put(new_url)
