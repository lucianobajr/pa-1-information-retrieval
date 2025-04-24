import os
import threading
import json
import socket
import time

from multiprocessing import Queue

from collections import defaultdict
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from src.config.settings_cli_args import Settings

from src.core.frontier import Frontier
from src.core.fetcher import Fetcher
from src.core.corpus import Corpus

from src.adapters.output.logger import get_logger
from src.adapters.output.warc.warc_writer_process import start_warc_writer
from src.adapters.input.seeds_loader import get_seeds_from_file

from src.shared.helpers.extractor import extract_outlinks
from src.shared.utils.get_safe_thread_count import get_safe_thread_count


class Controller:
    '''
    Classe principal responsável por orquestrar o processo de coleta do crawler.
    A coleta é encerrada ao atingir o número máximo de páginas definido (`page_limit`).
    '''

    def __init__(self, settings: Settings):
        '''
        Inicializa os componentes principais do crawler.
        '''
        self.settings = settings
        self.logger = get_logger(__name__, debug=settings.debug)
        self.frontier = Frontier()
        self.fetcher = Fetcher()
        self.corpus = Corpus()
        self.max_pages = settings.page_limit
        self.page_count = 0
        self.lock = threading.Lock()

        self.start_time = None
        self.graph = []
        self.nodes = {}
        self.domain_page_count = defaultdict(int)
        self.token_count_per_url = {}

        self.warc_queue = Queue()
        self.warc_process = start_warc_writer(self.warc_queue)

        seeds = get_seeds_from_file(settings.seed_file)
        for seed in seeds:
            self.frontier.add(seed)

    def run(self):
        '''
        Inicia o processo de coleta criando múltiplas threads.

        Cada thread executa a função `worker`, responsável por extrair,
        processar e armazenar páginas da web. Aguarda até que todas as threads finalizem.
        '''

        self.start_time = time.time()
        thread_count = get_safe_thread_count(default=6)

        threads = []

        # Parallelization Policy
        for _ in range(thread_count):  # Número de threads paralelas
            thread = threading.Thread(target=self.worker)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        if self.warc_process:
            self.warc_queue.put("__STOP__")
            self.warc_process.join()

        self.save_statistics(thread_count)

    def worker(self):
        '''
        Função executada por cada thread.

        Executa o ciclo principal de coleta:
            - Verifica se o limite de páginas foi atingido.
            - Recupera a próxima URL da frontier.
            - Faz o download da página.
            - Valida e salva a página no corpus.
            - Se estiver no modo debug, exibe resumo com título e primeiros termos.
            - Extrai os outlinks da página e os adiciona à frontier.

        O acesso a variáveis compartilhadas (`page_count`, `frontier`) é controlado por mutex (lock).
        '''
        while not self.frontier.is_empty():
            with self.lock:
                if self.page_count >= self.max_pages:
                    return

            url = self.frontier.pop()
            if not url:
                return

            try:
                page = self.fetcher.fetch(url)

                if not page:
                    self.logger.debug(
                        f"[Controller] Nenhuma página retornada para: {url}")
                    continue

                if page.status_code != 200:
                    self.logger.warning(
                        f"[{page.status_code}] Ignorado: {url}")
                    continue

                # Storage Policy
                self.storage_policy(
                    url=url, page_url=page.url, page_html=page.html)

                soup = BeautifulSoup(page.html, 'html.parser')

                title_tag = soup.title
                title = title_tag.string.strip() if title_tag and title_tag.string else ""

                text = soup.get_text(separator=' ', strip=True)
                tokens = text.split()

                record = {
                    "URL": page.url,
                    "Title": title,
                    "Text": ' '.join(tokens[:20]),
                    "Timestamp": int(page.timestamp)
                }
                parsed = urlparse(page.url)
                domain = parsed.netloc

                try:
                    ip = socket.gethostbyname(domain)
                except Exception:
                    ip = None

                self.nodes[page.url] = ip
                self.token_count_per_url[page.url] = len(tokens)

                if self.settings.debug:

                    print(json.dumps(record, ensure_ascii=False))

                with self.lock:
                    if self.page_count >= self.max_pages:
                        return

                    self.page_count += 1
                    self.domain_page_count[domain] += 1

                outlinks = extract_outlinks(page.html, page.url)

                self.logger.info(f"[{self.page_count}] Página coletada: {url}")

                for link in outlinks:
                    self.frontier.add(link)
                    self.graph.append({
                        "source": page.url,
                        "target": link
                    })

            except Exception as e:
                self.logger.error(f"Erro ao processar {url}: {e}")

    def storage_policy(self, url: str, page_url: str, page_html: str):

        if self.settings.storage_policy == "warc":
            self.warc_queue.put((page_url, page_html))

        if self.settings.storage_policy == "html_pages":
            if not self.corpus.save(page_url, page_html):
                self.logger.debug(f"Duplicado (hash): {url}")

    def save_statistics(self, thread_count: int):
        end_time = time.time()
        elapsed = end_time - self.start_time if self.start_time else 1
        stats_dir = "stats"

        os.makedirs(stats_dir, exist_ok=True)

        with open(f"{stats_dir}/graph.json", "w", encoding="utf-8") as file_json:
            json.dump({
                "nodes": [{"id": url, "ip": ip} for url, ip in self.nodes.items()],
                "edges": self.graph
            }, file_json, indent=2)

        with open(f"{stats_dir}/download_stats.json", "w", encoding="utf-8") as file_json:
            json.dump({
                "total_pages": self.page_count,
                "elapsed_time_sec": round(elapsed, 2),
                "pages_per_second": round(self.page_count / elapsed, 2),
                "threads": thread_count
            }, file_json, indent=2)

        with open(f"{stats_dir}/domain_distribution.json", "w", encoding="utf-8") as file_json:
            json.dump(self.domain_page_count, file_json, indent=2)

        with open(f"{stats_dir}/token_distribution.json", "w", encoding="utf-8") as file_json:
            json.dump(self.token_count_per_url, file_json, indent=2)

        print("\n📊 Estatísticas do Corpus:")
        print(f"- Total de páginas coletadas: {self.page_count}")
        print(f"- Total de domínios únicos: {len(self.domain_page_count)}")
        print("- Distribuição de páginas por domínio:")
        for domain, count in sorted(self.domain_page_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  • {domain}: {count} páginas")
        print("- Distribuição de tokens por página (top 10):")
        for url, count in sorted(self.token_count_per_url.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  • {url}: {count} tokens")
