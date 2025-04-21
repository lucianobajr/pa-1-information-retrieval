from urllib.parse import urlparse
from url_normalize import url_normalize

def normalize_url(url: str) -> str:
    '''
    Aplica normalização com `url_normalize`, seguido de verificação se a URL continua válida.

    Retorna uma string vazia se a URL resultante for inválida.
    '''
    if not url or not isinstance(url, str):
        return ""

    try:
        normalized = url_normalize(url)
        parsed = urlparse(normalized)
        if not parsed.scheme or not parsed.netloc:
            return ""
        return normalized
    except Exception:
        return ""
