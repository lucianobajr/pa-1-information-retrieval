# Diretório do ambiente virtual
VENV_DIR=venv

# Caminho para o arquivo de seeds
SEEDS=seeds.txt

# Número de páginas a coletar
LIMIT=1000

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
run:
	$(VENV_DIR)/bin/python $(MAIN) -s $(SEEDS) -n $(LIMIT)

# Executa com venv (modo debug)
debug:
	$(VENV_DIR)/bin/python $(MAIN) -s $(SEEDS) -n $(LIMIT) -d

# Executa localmente (sem venv)
run-local:
	python3 -B $(MAIN) -s $(SEEDS) -n $(LIMIT)

# Executa localmente (sem venv, modo debug)
debug-local:
	python3 -B $(MAIN) -s $(SEEDS) -n $(LIMIT) -d

# Remove o ambiente virtual e arquivos .pyc
clean:
	rm -rf $(VENV_DIR) __pycache__ **/__pycache__
	find . -name '*.pyc' -delete