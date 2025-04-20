from urllib.parse import urljoin
from typing import List
from bs4 import BeautifulSoup

def extract_outlinks(html: str, base_url: str) -> List[str]:
    '''
    Extrai todos os links (outlinks) de uma página HTML.

    Resolve os links relativos em relação à URL base, remove fragmentos (como #ancora)
    e retorna uma lista de URLs completas.
    '''
    
    soup = BeautifulSoup(html, 'html.parser')
    outlinks = []
    for tag in soup.find_all('a', href=True):
        href = tag.get('href')
        new_url = urljoin(base_url, href).split('#')[0]
        outlinks.append(new_url)
    return outlinks