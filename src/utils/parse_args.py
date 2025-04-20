import argparse

def parse_args():
    '''
    Analisa os argumentos de linha de comando para configuração do crawler.

    Retorna: Um objeto contendo os valores dos argumentos
    '''
    parser = argparse.ArgumentParser(description="Web Crawler - PA1 - Luciano Belo")
    parser.add_argument("-s", "--seeds", required=True, help="Arquivo com as seed URLs (uma por linha)")
    parser.add_argument("-n", "--limit", required=True, type=int, help="Número de páginas a serem coletadas")
    parser.add_argument("-d", "--debug", action="store_true", help="Ativa modo debug")
    return parser.parse_args()