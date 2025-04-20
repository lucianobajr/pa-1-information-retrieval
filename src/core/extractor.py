from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List

def extract_outlinks(html: str, base_url: str) -> List[str]:
    soup = BeautifulSoup(html, 'html.parser')
    outlinks = []
    for tag in soup.find_all('a', href=True):
        href = tag.get('href')
        new_url = urljoin(base_url, href).split('#')[0]
        outlinks.append(new_url)
    return outlinks