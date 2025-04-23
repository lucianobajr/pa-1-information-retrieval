import os
import gzip
from io import BytesIO
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders

class WarcStorage:
    """
    Classe responsável por armazenar as páginas HTML no formato WARC.

    Armazena 1000 páginas por arquivo, rotacionando automaticamente.
    """

    def __init__(self, directory="warc"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        
        self.file_index = 1
        self.page_count = 0
        self.max_per_file = 1000
        self.writer = None
        self.output = None
        self._open_new_file()

    def _open_new_file(self):
        if self.output:
            self.output.close()

        filename = f"pages-{self.file_index:03d}.warc.gz"
        filepath = os.path.join(self.directory, filename)

        self.output = gzip.open(filepath, "wb")
        self.writer = WARCWriter(self.output, gzip=False)

        self.file_index += 1
        self.page_count = 0

    def save(self, url: str, html: str):
        """
        Salva a página HTML com o URL associado no arquivo WARC atual.
        """
        if self.page_count >= self.max_per_file:
            self._open_new_file()

        http_headers = StatusAndHeaders(
            '200 OK',
            [('Content-Type', "text/html")],
            protocol='HTTP/1.1'
        )
        
        payload = html.encode('utf-8')
        record = self.writer.create_warc_record(
            uri=url,
            record_type="response",
            payload=BytesIO(payload),
            http_headers=http_headers
        )
        self.writer.write_record(record)
        self.page_count += 1

    def close(self):
        if self.output:
            self.output.flush()
            self.output.close()
