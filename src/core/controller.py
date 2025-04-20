import threading

from bs4 import BeautifulSoup
import json

from src.config.settings import Settings
from src.core.frontier import Frontier
from src.core.fetcher import Fetcher
from src.core.corpus import Corpus
from src.core.extractor import extract_outlinks
from src.infra.logger import get_logger
from src.core.seeds_loader import get_seeds_from_file


class Controller:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__, debug=settings.debug)
        self.frontier = Frontier()
        self.fetcher = Fetcher()
        self.corpus = Corpus()
        self.max_pages = settings.page_limit
        self.page_count = 0
        self.lock = threading.Lock()

        seeds = get_seeds_from_file(settings.seed_file)
        for seed in seeds:
            self.frontier.add(seed)

    def run(self):
        threads = []
        for _ in range(5):  # Número de threads paralelas
            thread = threading.Thread(target=self.worker)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def worker(self):
        while not self.frontier.is_empty():
            with self.lock:
                if self.page_count >= self.max_pages:
                    return

            url = self.frontier.pop()
            if not url:
                return

            try:
                page = self.fetcher.fetch(url)

                if page.status_code != 200:
                    self.logger.warning(
                        f"[{page.status_code}] Ignorado: {url}")
                    continue

                if not self.corpus.save(page.url, page.html):
                    self.logger.debug(f"Duplicado (hash): {url}")
                    continue

                if self.settings.debug:

                    soup = BeautifulSoup(page.html, 'html.parser')
                    title = soup.title.string.strip() if soup.title else ""
                    text = ' '.join(soup.get_text().split()[:20])
                    record = {
                        "URL": page.url,
                        "Title": title,
                        "Text": text,
                        "Timestamp": int(page.timestamp)
                    }
                    print(json.dumps(record, ensure_ascii=False))

                outlinks = extract_outlinks(page.html, page.url)
                with self.lock:
                    self.page_count += 1

                self.logger.info(f"[{self.page_count}] Página coletada: {url}")

                for link in outlinks:
                    self.frontier.add(link)

            except Exception as e:
                self.logger.error(f"Erro ao processar {url}: {e}")
