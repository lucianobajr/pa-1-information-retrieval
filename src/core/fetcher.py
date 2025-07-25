import time
from urllib.parse import urlparse

import requests
from requests.exceptions import RequestException

from src.domain.types.page import Page
from src.infra.cache.robots import RobotsCache
from src.adapters.output.logger import get_logger


class Fetcher:
    '''
    Responsável por realizar o download de páginas HTML a partir de URLs fornecidas.

    Aplica política de politeness com base no `robots.txt` do domínio,
    utilizando `crawl-delay` e evitando sobrecarga de servidores.

    Também armazena a URL final após redirecionamentos e registra o tempo de acesso.
    '''

    def __init__(self, user_agent="WebCrawler-PA1"):
        '''
        Inicializa o Fetcher com controle de politeness por domínio e cache de robots.txt.
        '''
        self.domain_last_access = {}
        self.robots_cache = RobotsCache()
        self.user_agent = user_agent
        self.logger = get_logger(__name__)

    def fetch(self, url: str) -> Page:
        '''
        Realiza o download de uma página da web respeitando as regras de crawl-delay.

        - Consulta o `robots.txt` para obter o tempo de espera mínimo entre requisições ao mesmo domínio.
        - Aguarda o tempo necessário, se houver.
        - Realiza a requisição HTTP GET com o cabeçalho `User-Agent`.
        - Retorna um objeto `Page` com as informações da resposta.
        '''

        # Faz o parsing da URL para extrair o domínio
        parsed = urlparse(url)
        domain = parsed.netloc

        # Se a URL não tiver domínio, considera inválida
        if not domain:
            self.logger.warning(f"[Fetcher] URL inválida ignorada: {url}")
            return None

        # Politeness Policy => Consulta o delay mínimo permitido entre requisições para o domínio (via robots.txt)
        delay = self.robots_cache.get_crawl_delay(
            domain=domain, user_agent=self.user_agent)

        # Recupera o timestamp do último acesso ao mesmo domínio
        last = self.domain_last_access.get(domain, 0)
        now = time.time()

        # Calculando o tempo que deve aguardar para respeitar o delay
        wait = max(0, delay - (now - last))
        if wait > 0:
            time.sleep(wait)

        headers = {"User-Agent": self.user_agent}
        try:
            response = requests.get(url, headers=headers, timeout=10)

            # Atualiza o tempo do último acesso para este domínio
            self.domain_last_access[domain] = time.time()

            content_type = response.headers.get("Content-Type", "").lower()

            # Selection Policy
            if "text/html" not in content_type:
                self.logger.debug(
                    f"[Fetcher] Ignorado (não HTML): {url} -> {content_type}")
                return None

            return Page(
                url=url,
                html=response.text,
                status_code=response.status_code,
                timestamp=time.time(),
                final_url=response.url
            )
        except RequestException as e:
            self.logger.warning(f"[Fetcher] Falha ao acessar {url}: {e}")
            return None
