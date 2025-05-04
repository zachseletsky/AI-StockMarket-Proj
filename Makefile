# Makefile for AI Stock Trader Project

# Variables
ENV_NAME=ai-stock-trader
PYTHON_VER=3.11
IMAGE_NAME=ai-stock-trader
DOCKER_COMPOSE_FILE=docker-compose.yml

# ==== Conda Targets ====

.PHONY: conda-create
conda-create:
	conda create -y -n $(ENV_NAME) python=$(PYTHON_VER)

.PHONY: conda-activate
conda-activate:
	@echo "Run: conda activate $(ENV_NAME)"

.PHONY: conda-install
conda-install:
	conda run -n $(ENV_NAME) && conda install --file environment.yml

.PHONY: conda-export
conda-export:
	conda run -n $(ENV_NAME) && conda env export --no-builds > environment.yml

.PHONY: conda-update
conda-update:
	conda env update --name $(ENV_NAME) --file environment.yml --prune

.PHONY: conda-remove
conda-remove:
	conda remove -y --name $(ENV_NAME) --all

# ==== Docker Targets ====

.PHONY: docker-build
docker-build:
	docker build -t $(IMAGE_NAME) .

.PHONY: docker-run
docker-run:
	docker run --rm -v $(CURDIR):/app $(IMAGE_NAME)

.PHONY: docker-bash
docker-bash:
	docker run -it --rm -v $(CURDIR):/app $(IMAGE_NAME) bash

.PHONY: docker-compose-up
docker-compose-up:
	docker-compose -f $(DOCKER_COMPOSE_FILE) up --build

.PHONY: docker-compose-down
docker-compose-down:
	docker-compose -f $(DOCKER_COMPOSE_FILE) down

# ==== Dev Utilities ====

.PHONY: test
test:
	conda run -n $(ENV_NAME) pytest tests/

.PHONY: lint
lint:
	conda run -n $(ENV_NAME) black app/

.PHONY: format
format: lint

.PHONY: shell
shell:
	conda run -n $(ENV_NAME) ipython

.PHONY: run
run:
	conda run -n $(ENV_NAME) python app/main.py


# Pre-Commit dev tools
.PHONY: install-hooks
install-hooks:
	pre-commit install

.PHONY: run-hooks
run-hooks:
	pre-commit run --all-files
