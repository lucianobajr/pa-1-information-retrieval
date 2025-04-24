import os
from io import BytesIO
from multiprocessing import Process, Queue
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders


def warc_writer_worker(queue: Queue, directory="corpus/warcs"):
    """
    Processo separado para salvar arquivos WARC de forma paralela ao crawler principal.
    Gera um arquivo a cada N páginas coletadas.
    """
    os.makedirs(directory, exist_ok=True)

    file_index = 1
    page_count = 0
    writer = None
    output = None
    max_html_pages = 10  # lembrar de ajustar para 1000 na produção

    def open_new_file():
        nonlocal file_index, writer, output, page_count
        if output:
            output.close()
        filename = f"pages-{file_index:03d}.warc.gz"
        filepath = os.path.join(directory, filename)
        output = open(filepath, "wb")
        writer = WARCWriter(output, gzip=True)
        file_index += 1
        page_count = 0

    while True:
        item = queue.get()

        if item == "__STOP__":
            break

        url, html = item

        # Rotaciona ANTES da escrita se necessário
        if writer is None or page_count >= max_html_pages:
            open_new_file()

        headers = StatusAndHeaders(
            "200 OK",
            [("Content-Type", "text/html; charset=utf-8")],
            protocol="HTTP/1.0"
        )

        record = writer.create_warc_record(
            uri=url,
            record_type="response",
            payload=BytesIO(html.encode("utf-8")),
            http_headers=headers
        )
        writer.write_record(record)
        page_count += 1

    if output:
        output.close()


def start_warc_writer(queue: Queue) -> Process:
    process = Process(target=warc_writer_worker, args=(queue,))
    process.start()
    return process
