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
