from urllib.parse import urlparse, urlunparse

def normalize_url(url: str) -> str:
    parsed = urlparse(url)

    scheme = parsed.scheme.lower()
    netloc = parsed.hostname.lower()
    if parsed.port:
        if (scheme == "http" and parsed.port != 80) or (scheme == "https" and parsed.port != 443):
            netloc += f":{parsed.port}"

    path = parsed.path or "/"
    path = path.rstrip("/")

    return urlunparse((scheme, netloc, path, '', '', ''))
