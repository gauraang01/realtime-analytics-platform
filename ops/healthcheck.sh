#!/usr/bin/env bash
set -euo pipefail

# Use service names via docker compose (robust to container IDs)
DC="docker compose -f infra/compose/docker-compose.yml --env-file .env"

echo "===> Checking Redpanda (Kafka broker)..."
$DC exec -T redpanda rpk cluster info --brokers=redpanda:${KAFKA_BROKER_PORT:-9092} >/dev/null
echo "OK"

echo "===> Checking Schema Registry..."
curl -sf "http://localhost:${SCHEMA_REGISTRY_PORT:-8081}/subjects" >/dev/null && echo "OK"

echo "===> Checking Spark Master UI..."
curl -sf "http://localhost:${SPARK_MASTER_UI_PORT:-8080}" >/dev/null && echo "OK"

echo "===> Checking ClickHouse..."
curl -sf "http://localhost:${CLICKHOUSE_HTTP_PORT:-8123}" >/dev/null && echo "OK"

echo "===> Checking Grafana..."
curl -sf "http://localhost:${GRAFANA_PORT:-3000}/api/health" >/dev/null && echo "OK"

echo "All health checks passed."
