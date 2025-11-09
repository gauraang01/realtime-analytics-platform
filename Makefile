COMPOSE := docker compose -f infra/compose/docker-compose.yml --env-file .env

.PHONY: up down logs ps clean

up:
	@$(COMPOSE) up -d --remove-orphans
	@echo "Waiting for health..."
	@sleep 3
	@$(COMPOSE) ps

down:
	@$(COMPOSE) down

logs:
	@$(COMPOSE) logs -f

ps:
	@$(COMPOSE) ps

clean:
	@$(COMPOSE) down -v --remove-orphans
	@docker volume prune -f || true



.PHONY: deps test produce

deps:
	uv pip install -r apps/contracts/requirements.txt

test:
	PYTHONPATH=apps/contracts uv run -m pytest -q

produce:
	PYTHONPATH=apps/contracts uv run python -m rtap_contracts.register_and_probe
