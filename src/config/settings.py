class Settings:
    def __init__(self, seed_file: str, page_limit: int, debug: bool = False):
        self.seed_file = seed_file
        self.page_limit = page_limit
        self.debug = debug
