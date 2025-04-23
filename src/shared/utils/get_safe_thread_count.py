import os
import threading


def get_safe_thread_count(default: int = 6) -> int:
    '''
    Tenta retornar um número seguro de threads com base na CPU.
    Se falhar ao criar threads, retorna um valor padrão seguro.
    '''
    try:
        # Sugestão baseada no número de núcleos
        suggested = os.cpu_count() * 2 if os.cpu_count() else default

        # Teste rápido de viabilidade criando threads dummy
        threads = []
        for _ in range(suggested):
            thread = threading.Thread(target=lambda: None)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        return suggested
    except Exception as e:
        print(f"[AVISO] Não foi possível criar {suggested} threads: {e}")
        return default
