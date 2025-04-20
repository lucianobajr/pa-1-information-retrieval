from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    '''
    Normaliza uma URL para garantir consistência na comparação e armazenamento.

    A normalização inclui:
    - Conversão do esquema (http/https) e domínio para minúsculas.
    - Inclusão da porta apenas se ela for não padrão (≠ 80 para http, ≠ 443 para https).
    - Garantia de que o caminho não termine com uma barra (a menos que seja apenas "/").
    - Remoção de parâmetros, query string e fragmentos.
    
    Retorna a URL em formato canônico
    '''
    parsed = urlparse(url)

    scheme = parsed.scheme.lower()
    netloc = parsed.hostname.lower()
    if parsed.port:
        if (scheme == "http" and parsed.port != 80) or (scheme == "https" and parsed.port != 443):
            netloc += f":{parsed.port}"

    path = parsed.path or "/"
    path = path.rstrip("/")

    return urlunparse((scheme, netloc, path, '', '', ''))
