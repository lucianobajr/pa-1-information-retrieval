import heapq
from typing import Set, List
from src.core.types import PrioritizedURL
from src.core.normalizer import normalize_url


class Frontier:
    def __init__(self):
        self.queue: List[PrioritizedURL] = []
        self.seen: Set[str] = set()

    def add(self, url: str, priority: int = 0):
        norm_url = normalize_url(url)
        if norm_url not in self.seen:
            heapq.heappush(self.queue, PrioritizedURL(priority, norm_url))
            self.seen.add(norm_url)

    def pop(self) -> str:
        return heapq.heappop(self.queue).url if self.queue else None

    def is_empty(self) -> bool:
        return len(self.queue) == 0
