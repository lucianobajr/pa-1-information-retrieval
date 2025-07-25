# Diretório do ambiente virtual
VENV_DIR=pa1

# Caminho para o arquivo de seeds
SEEDS=./seeds/seeds-2024698420.txt

# Número de páginas a coletar
LIMIT=100000

# Nome do script principal
MAIN=main.py

# Caminho para requirements
REQ=requirements.txt

.PHONY: all run debug run-local debug-local venv install clean

# Cria o ambiente virtual
venv:
	python3 -m venv $(VENV_DIR)

# Instala dependências no ambiente virtual
install: venv
	$(VENV_DIR)/bin/pip install -r $(REQ)

# Executa com venv (modo normal)
run-venv:
	$(VENV_DIR)/bin/python $(MAIN) -s $(SEEDS) -n $(LIMIT)

# Executa com venv (modo debug)
debug-venv:
	$(VENV_DIR)/bin/python $(MAIN) -s $(SEEDS) -n $(LIMIT) -d

run:
	python3 -B $(MAIN) -s $(SEEDS) -n $(LIMIT)

# Executa localmente (sem venv, modo debug)
debug:
	python3 -B $(MAIN) -s $(SEEDS) -n $(LIMIT) -d

# Remove o ambiente virtual e arquivos .pyc
clean:
	rm -rf $(VENV_DIR) __pycache__ **/__pycache__
	find . -name '*.pyc' -delete