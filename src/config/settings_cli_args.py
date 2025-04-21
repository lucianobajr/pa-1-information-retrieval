class Settings:
    """
    Define as configurações de execução do crawler.

    Atributos:
        seed_file (str): Caminho para o arquivo com URLs iniciais (opção -s <SEEDS>).
        page_limit (int): Número máximo de páginas a serem rastreadas (opção -n <LIMIT>).
        debug (bool): Indica se o modo de depuração está ativado (opcional).
    """

    def __init__(self, seed_file: str, page_limit: int, debug: bool = False):
        self.seed_file = seed_file
        self.page_limit = page_limit
        self.debug = debug
