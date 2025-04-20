import threading

import json
from bs4 import BeautifulSoup

from src.config.settings import Settings
from src.core.frontier import Frontier
from src.core.fetcher import Fetcher
from src.core.corpus import Corpus
from src.core.extractor import extract_outlinks
from src.infra.logger import get_logger
from src.core.seeds_loader import get_seeds_from_file

from src.utils.get_safe_thread_count import get_safe_thread_count


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

        seeds = get_seeds_from_file(settings.seed_file)
        for seed in seeds:
            self.frontier.add(seed)

    def run(self):
        '''
        Inicia o processo de coleta criando múltiplas threads.

        Cada thread executa a função `worker`, responsável por extrair,
        processar e armazenar páginas da web. Aguarda até que todas as threads finalizem.
        '''

        thread_count = get_safe_thread_count(default=5)

        threads = []
        for _ in range(thread_count):  # Número de threads paralelas
            thread = threading.Thread(target=self.worker)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

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
