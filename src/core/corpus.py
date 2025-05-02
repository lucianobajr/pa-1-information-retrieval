import os
import hashlib


class Corpus:
    '''
    Responsável por armazenar localmente as páginas HTML coletadas.

    Cada página é salva com um nome baseado no hash MD5 da sua URL, garantindo unicidade.
    Também mantém um conjunto de hashes para evitar salvar duplicatas durante a execução.
    '''

    def __init__(self, directory="corpus/html"):
        '''
        Inicializa o diretório onde as páginas serão salvas e um conjunto de hashes.
        '''
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self.hashes = set()

    def save(self, url: str, html: str):
        '''
        Salva uma página HTML no corpus, caso ainda não tenha sido armazenada.
        '''
        
        # cria um hash md5 a partir da URL
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        if url_hash in self.hashes:
            return False
        
        self.hashes.add(url_hash)
        
        path = os.path.join(self.directory, f"{url_hash}.html")
        with open(path, "w", encoding="utf-8") as file_handle:
            file_handle.write(html)
            
        return True
