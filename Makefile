# ADK 2.0 example — common tasks.
# `make help` lists everything.

IMAGE  ?= adk-two-example:latest
PORT   ?= 8000
AGENT  ?= smart_brief

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

# ───────────────────────── Local (host Python) ──────────────────────────────
.PHONY: venv
venv: ## Create .venv and install ADK 2.0 (pre-release) + dev deps
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && \
		pip install --pre -r requirements.txt

.PHONY: env
env: ## Create .env from the template (edit it afterwards)
	@test -f .env || cp .env.example .env
	@echo "Edit .env and add your GOOGLE_API_KEY (or Vertex settings)."

.PHONY: web
web: ## Run the ADK dev UI locally at http://localhost:$(PORT)
	. .venv/bin/activate && adk web --port $(PORT) app

.PHONY: run
run: ## Run $(AGENT) once in the terminal (interactive)
	. .venv/bin/activate && adk run app/$(AGENT)

.PHONY: a2a
a2a: ## Run dev UI + A2A endpoints (smart_brief exposed at /a2a/smart_brief)
	. .venv/bin/activate && adk web --port $(PORT) --a2a app

.PHONY: api
api: ## Run only the ADK REST API server (no UI)
	. .venv/bin/activate && adk api_server --port $(PORT) app

.PHONY: a2a-card
a2a-card: ## Print smart_brief's served A2A agent card (server must be running)
	@curl -s http://localhost:$(PORT)/a2a/smart_brief/.well-known/agent-card.json | python3 -m json.tool

.PHONY: test
test: ## Run the offline structural tests
	. .venv/bin/activate && pytest -q

.PHONY: version
version: ## Print the installed ADK version (should be 2.x)
	. .venv/bin/activate && python -c "import google.adk as a; print(a.__version__)"

# ───────────────────────────── Docker ───────────────────────────────────────
.PHONY: build
build: ## Build the Docker image
	docker build -t $(IMAGE) .

.PHONY: up
up: ## Start via docker compose (reads .env, serves on :$(PORT))
	docker compose up --build

.PHONY: down
down: ## Stop docker compose
	docker compose down

.PHONY: docker-run
docker-run: ## Run the image directly without compose
	docker run --rm -p $(PORT):8000 --env-file .env $(IMAGE)

.PHONY: clean
clean: ## Remove venv, caches and the Docker image
	rm -rf .venv .pytest_cache **/__pycache__
	-docker rmi $(IMAGE)
