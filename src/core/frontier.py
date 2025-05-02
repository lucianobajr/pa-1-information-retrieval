import heapq
from typing import Set, List

from src.domain.types.prioritized_url import PrioritizedURL
from src.shared.helpers.normalizer import normalize_url


class Frontier:
    '''
    Implementa a fronteira do crawler como uma fila de prioridade (min-heap).

    Gerencia as URLs a serem visitadas, evitando repetições com um conjunto (`seen`)
    e priorizando URLs com base em sua prioridade associada.

    URLs são normalizadas antes de serem adicionadas para garantir unicidade.
    '''

    def __init__(self):
        self.queue: List[PrioritizedURL] = []
        self.seen: Set[str] = set()

    def add(self, url: str, priority: int = 0):
        '''
        Adiciona uma nova URL à fronteira, se ainda não foi visitada.
        '''
        normalized_url = normalize_url(url=url)

        # Revisitation Policy
        if normalized_url and normalized_url not in self.seen:
            heapq.heappush(self.queue, PrioritizedURL(
                priority=priority, url=normalized_url))
            self.seen.add(normalized_url)

    def pop(self) -> str:
        '''
        Remove e retorna a próxima URL da fila de prioridade.
        '''
        return heapq.heappop(self.queue).url if self.queue else None

    def is_empty(self) -> bool:
        '''
        Verifica se a fila de URLs está vazia.
        '''
        return len(self.queue) == 0
