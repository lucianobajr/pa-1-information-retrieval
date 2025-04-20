class PrioritizedURL:
    '''
    Representa uma URL com uma prioridade associada, utilizada na fila de prioridades (frontier).

    A prioridade define a ordem de coleta das URLs, onde menores valores são processados antes.
    '''

    def __init__(self, priority: int, url: str):
        self.priority = priority
        self.url = url

    def __lt__(self, other):
        '''
        Define o critério de comparação para ordenação entre objetos PrioritizedURL.

        Permite uso em estruturas como `heapq` ou `PriorityQueue`.
        '''
        return self.priority < other.priority


class Page:
    '''
    Representa uma página coletada pelo crawler.

    Contém informações como URL original, HTML, código de status HTTP, timestamp da coleta
    e URL final (após redirecionamentos, se houver).
    '''

    def __init__(self, url: str, html: str, status_code: int, timestamp: float, final_url: str = None):  # pylint: disable=too-many-arguments
        self.url = url
        self.html = html
        self.status_code = status_code
        self.timestamp = timestamp
        self.final_url = final_url
