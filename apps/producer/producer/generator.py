import random
from datetime import datetime, timezone
from typing import Dict, Any

def now_us() -> int:
    return int(datetime.now(tz=timezone.utc).timestamp() * 1_000_000)

def make_event(i: int) -> Dict[str, Any]:
    metric = random.choice(["cpu_util", "mem_util", "latency_ms", "errors"])
    val = round(random.uniform(0.0, 100.0), 3)
    if metric == "latency_ms":
        val = round(random.uniform(1.0, 2500.0), 3)
    if metric == "errors":
        val = float(random.randint(0, 50))
    return {
        "event_time": now_us(),
        "device_id": f"device-{i%1000:04d}",
        "metric": metric,
        "value": val,
        "tags": {"region": random.choice(["ap-south-1", "us-east-1", "eu-west-1"]), "app": "demo"},
        "trace_id": f"tr-{random.randint(10**5, 10**6-1)}",
        "ingest_ts": now_us(),
    }
