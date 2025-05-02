from multiprocessing import Process, Queue
from src.adapters.output.warc.warc_writer import WarcRotatingWriter


def warc_writer_worker(queue: Queue, directory: str = "corpus/warcs", max_html_pages: int = 1000):
    '''
    Função worker que roda em um processo separado para escrever páginas HTML em arquivos WARC.
    Args:
        queue (Queue): Fila de comunicação entre o processo principal e este processo de escrita.
        directory (str): Diretório onde os arquivos .warc.gz serão salvos.
        max_html_pages (int): Número máximo de páginas por arquivo WARC.
    '''
    
    writer = WarcRotatingWriter(
        directory=directory, max_per_file=max_html_pages)

    while True:
        item = queue.get()

        if item == "__STOP__":
            break

        url, html = item
        writer.write(url=url, html=html)

    writer.close()


def start_warc_writer(queue: Queue, directory="corpus/warcs", max_html_pages=1000) -> Process:
    '''
    Inicializa o processo separado para gravação de páginas HTML em arquivos WARC.
    '''
    process = Process(
        target=warc_writer_worker,
        args=(queue, directory, max_html_pages)
    )
    process.start()
    return process
