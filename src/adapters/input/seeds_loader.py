
from typing import Set
from urllib.parse import urlparse
from src.shared.helpers.normalizer import normalize_url


def verify_is_valid_url(url: str) -> bool:
    '''
    Verifica se uma string é uma URL válida com esquema HTTP ou HTTPS.
    '''
    if not url:
        return False

    try:
        parsed = urlparse(url.strip())
        return all([parsed.scheme in {"http", "https"}, parsed.netloc])
    except Exception:
        return False


def get_seeds_from_file(seed_file: str) -> Set[str]:
    '''
    Lê o arquivo de seeds contendo URLs, uma por linha, e retorna um conjunto de URLs válidas e normalizadas.

    Ignora linhas vazias ou comentários (linhas que começam com "#").
    URLs inválidas são descartadas.
    '''
    seeds = set()

    try:
        with open(seed_file, "r", encoding="utf-8") as file:
            for seed in file:
                seed = seed.strip()
                if not seed or seed.startswith("#"):
                    continue

                if verify_is_valid_url(url=seed):
                    normalized = normalize_url(url=seed)
                    seeds.add(normalized)
                else:
                    print(f"[WARN] URL inválida ignorada: {seed}")
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Arquivo de seeds não encontrado: {seed_file}")
    except Exception as e:
        raise RuntimeError(f"Erro ao ler o arquivo de seeds: {e}")

    if not seeds:
        raise ValueError(
            "Nenhuma URL válida foi encontrada no arquivo de seeds.")

    return seeds
