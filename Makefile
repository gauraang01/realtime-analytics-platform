COMPOSE := docker compose -f infra/compose/docker-compose.yml --env-file .env

# Load .env into make's environment
ifneq (,$(wildcard .env))
include .env
export $(shell sed 's/=.*//' .env)
endif

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



.PHONY: topics deps-topics deps-producer produce-run consume-test

deps-topics:
	uv pip install -r apps/topics/requirements.txt

deps-producer:
	uv pip install -r apps/producer/requirements.txt

topics: deps-topics
	uv run python apps/topics/manage_topics.py

# Async producer (aio-kafka)
produce-run: deps-producer
	BOOTSTRAP_SERVERS=$(BOOTSTRAP_SERVERS) SCHEMA_REGISTRY_URL=$(SCHEMA_REGISTRY_URL) \
	PYTHONPATH=apps/producer uv run python -m producer.main

# Optional quick consumer (kcat inside Docker) to see traffic
consume-test:
	docker run --rm -it --platform linux/amd64 --network rtap-net edenhill/kcat:1.7.1 \
		kcat -b redpanda:29092 -t ${TOPIC_DEVICE_METRIC} -C -o end -q -e

consume-tail:
	docker run --rm -it --platform linux/amd64 --network rtap-net edenhill/kcat:1.7.1 \
		kcat -b redpanda:29092 -t $(TOPIC_DEVICE_METRIC) -C -o beginning


print-topic:
	@echo "Topic = '${TOPIC_DEVICE_METRIC}'"
