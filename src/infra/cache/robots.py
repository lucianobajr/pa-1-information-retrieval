from urllib.parse import urlparse

from protego import Protego
import requests

class RobotsCache:
    '''
    Classe responsável por armazenar e gerenciar os arquivos robots.txt já lidos,
    evitando múltiplas requisições para o mesmo domínio.
    '''

    def __init__(self):
        '''
        Inicializa o cache de parsers de arquivos robots.txt.
        '''

        self.cache = {}

    def get_parser(self, domain: str):
        '''
        Obtém (ou cria e armazena) o parser de robots.txt para um domínio.
        '''

        if domain not in self.cache:
            try:
                response = requests.get(f"http://{domain}/robots.txt", timeout=5)
                if response.status_code == 200:
                    self.cache[domain] = Protego.parse(response.text)
                else:
                    self.cache[domain] = None
            except Exception as e:
                print(f"Erro ao obter robots.txt de {domain}: {e}")
                self.cache[domain] = None
        return self.cache[domain]

    def can_fetch(self, url: str, user_agent: str) -> bool:
        '''
        Verifica se uma URL pode ser acessada por um user-agent, de acordo com o robots.txt.
        '''

        domain = urlparse(url).netloc
        parser = self.get_parser(domain)
        if not parser:
            return True
        return parser.can_fetch(user_agent, url)

    def get_crawl_delay(self, domain: str, user_agent: str) -> float:
        '''
        Retorna o tempo de espera (crawl-delay) definido no robots.txt para o user-agent.
        '''

        parser = self.get_parser(domain)
        if parser:
            delay = parser.crawl_delay(user_agent)
            return delay if delay is not None else 0.1
        
        # atraso de pelo menos 100 ms
        return 0.1
