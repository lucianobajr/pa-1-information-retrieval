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