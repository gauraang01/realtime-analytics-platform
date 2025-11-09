# Real-Time Analytics Pipeline (Kafka ➜ Spark ➜ ClickHouse ➜ Grafana)

Reproducible local stack to support:
- Kafka-compatible broker (Redpanda) + Schema Registry + Console
- Spark 3.5 (master + worker) for Structured Streaming
- ClickHouse 24.8 (LTS) for OLAP
- Grafana with ClickHouse datasource

## Quickstart

```bash
# 1) copy env and boot
cp .env.example .env
make up

# 2) check health
make ps
make logs
chmod +x ops/healthcheck.sh
./ops/healthcheck.sh

uv venv
make deps
make produce

curl -s http://localhost:8081/subjects | jq


# Ensure infra is up
make up

# 1) Create/ensure topic with desired config
make topics

# 2) Start async producer (Ctrl+C to stop)
make produce-run

