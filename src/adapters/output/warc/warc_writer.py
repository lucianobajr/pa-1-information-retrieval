import os
from io import BytesIO
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders


class WarcRotatingWriter:
    '''
    Gerenciador de escrita de arquivos WARC com rotação automática.

    Esta classe é responsável por armazenar páginas HTML em arquivos WARC (.warc.gz), gerando um novo arquivo a cada 'max_per_file' (1000) páginas.
    '''

    def __init__(self, directory: str = "corpus/warcs", max_per_file: int = 1000):
        self.directory = directory
        self.max_per_file = max_per_file
        os.makedirs(self.directory, exist_ok=True)

        self.file_index = 1
        self.page_count = 0
        self.output = None
        self.writer = None

        self._open_new_file()

    def _open_new_file(self):
        '''
        Cria um novo arquivo WARC e atualiza o escritor interno.

        Fecha o arquivo atual, se aberto, e inicia um novo arquivo rotacionado.
        '''

        if self.output:
            self.output.close()

        filename = f"pages-{self.file_index:03d}.warc.gz"
        filepath = os.path.join(self.directory, filename)
        
        self.output = open(filepath, "wb")
        self.writer = WARCWriter(self.output, gzip=True)

        self.file_index += 1
        self.page_count = 0

    def write(self, url: str, html: str):
        '''
        Escreve uma nova página HTML em um arquivo WARC.

        Se o número de páginas atingir o limite máximo (`max_per_file`), automaticamente rotaciona para um novo arquivo.
        '''

        if self.page_count >= self.max_per_file:
            self._open_new_file()

        headers = StatusAndHeaders(
            "200 OK",
            [("Content-Type", "text/html; charset=utf-8")],
            protocol="HTTP/1.0"
        )

        record = self.writer.create_warc_record(
            uri=url,
            record_type="response",
            payload=BytesIO(html.encode("utf-8")),
            http_headers=headers
        )

        self.writer.write_record(record)
        self.page_count += 1

    def close(self):
        '''
        Fecha o arquivo WARC atual, se houver um aberto.

        Deve ser chamado no final da operação para garantir integridade dos arquivos gerados.
        '''

        if self.output:
            self.output.close()
