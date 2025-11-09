import time
import random
from typing import Dict, Any
import json
from datetime import datetime, timezone

from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

from rtap_contracts.settings import SETTINGS
from rtap_contracts.schema_ops import load_schemas, validate_local


def now_us() -> int:
    return int(datetime.now(tz=timezone.utc).timestamp() * 1_000_000)


def example_event(i: int) -> Dict[str, Any]:
    metric = random.choice(["cpu_util", "mem_util", "latency_ms", "errors"])
    base = {
        "event_time": now_us(),
        "device_id": f"device-{i%100:03d}",
        "metric": metric,
        "value": round(random.uniform(0.0, 100.0), 3),
        "tags": {"region": random.choice(["us-east-1", "ap-south-1", "eu-west-1"]), "app": "demo"},
        "trace_id": f"tr-{random.randint(100000, 999999)}",
        "ingest_ts": now_us(),
    }
    if metric == "latency_ms":
        base["value"] = round(random.uniform(1.0, 2500.0), 3)
    if metric == "errors":
        base["value"] = float(random.randint(0, 50))
    return base


def main(count: int = 5) -> None:

    # 1) Load & locally validate schema
    avro_schema, _ = load_schemas()
    samples = [example_event(i) for i in range(count)]
    for s in samples:
        validate_local(s)

    # 2) Schema Registry client + serializers
    sr = SchemaRegistryClient({"url": SETTINGS.schema_registry_url})

    value_serializer = AvroSerializer(
        schema_registry_client=sr,
        schema_str=json.dumps(avro_schema),
    )
    key_serializer = StringSerializer("utf_8")

    # 3) SerializingProducer with serializers in config
    producer = SerializingProducer({
        "bootstrap.servers": SETTINGS.bootstrap_servers,
        "enable.idempotence": True,
        "linger.ms": 5,
        "batch.num.messages": 10000,
        "acks": SETTINGS.acks,
        "compression.type": "zstd",
        # NEW: serializers here, not per-produce()
        "key.serializer": key_serializer,
        "value.serializer": value_serializer,
    })

    delivered = 0

    def _cb(err, msg):
        nonlocal delivered
        if err is None:
            delivered += 1
        else:
            print(f"❌ delivery error: {err}")

    # 4) Produce events
    for s in samples:
        key = s["device_id"]
        producer.produce(
            topic=SETTINGS.topic,
            key=key,
            value=s,
            on_delivery=_cb,
        )

    producer.flush(10)

    print(f"✅ Sent {delivered}/{count} messages to topic '{SETTINGS.topic}' using Avro v1.")


if __name__ == "__main__":
    main()
