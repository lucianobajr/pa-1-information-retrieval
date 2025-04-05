from urllib.parse import urlparse
from typing import Set

def verify_is_valid_url(url: str) -> bool:
    """Verifica se a URL é válida e tem esquema e domínio."""
    try:
        parsed = urlparse(url=url)
        return all([parsed.scheme in {"http", "https"}, parsed.netloc])
    except Exception:
        return False


def get_seeds_from_file(seed_file: str) -> Set[str]:
    seeds = set()

    try:
        with open(seed_file, "r", encoding="utf-8") as file:
            for seed in file:
                seed = seed.strip()
                if not seed or seed.startswith("#"):
                    continue  # só recuperar urls

                if verify_is_valid_url(url=seed):
                    seeds.add(seed)

                else:
                    print("URL inválida ignorada!")
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Arquivo de seeds não encontrado: {seed_file}")
    except Exception as e:
        raise RuntimeError(f"Erro ao ler o arquivo de seeds: {e}")

    if not seeds:
        raise ValueError(
            "Nenhuma URL válida foi encontrada no arquivo de seeds.")

    return seeds
