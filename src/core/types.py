class PrioritizedURL:
    def __init__(self, priority: int, url: str):
        self.priority = priority
        self.url = url

    def __lt__(self, other):
        return self.priority < other.priority


class Page:
    def __init__(self, url: str, html: str, status_code: int, timestamp: float, final_url: str = None):
        self.url = url
        self.html = html
        self.status_code = status_code
        self.timestamp = timestamp
        self.final_url = final_url
