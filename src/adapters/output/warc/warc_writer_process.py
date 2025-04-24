from multiprocessing import Process, Queue
from src.adapters.output.warc.warc_writer import WarcRotatingWriter


def warc_writer_worker(queue: Queue, directory: str = "corpus/warcs", max_html_pages: int = 1000):
    writer = WarcRotatingWriter(
        directory=directory, max_per_file=max_html_pages)

    while True:
        item = queue.get()

        if item == "__STOP__":
            break

        url, html = item
        writer.write(url, html)

    writer.close()


def start_warc_writer(queue: Queue, directory="corpus/warcs", max_html_pages=1000) -> Process:
    process = Process(
        target=warc_writer_worker,
        args=(queue, directory, max_html_pages)
    )
    process.start()
    return process
