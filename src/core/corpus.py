import os
import hashlib

class Corpus:
    def __init__(self, directory="corpus"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
        self.hashes = set()

    def save(self, url: str, html: str):
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        if url_hash in self.hashes:
            return False
        self.hashes.add(url_hash)
        path = os.path.join(self.directory, f"{url_hash}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return True