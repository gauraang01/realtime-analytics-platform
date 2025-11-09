from typing import Dict
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from confluent_kafka.admin import AdminClient, NewTopic, ConfigResource

load_dotenv()

class Settings(BaseModel):
    bootstrap_servers: str = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
    topic: str = os.getenv("TOPIC_DEVICE_METRIC", "device_metrics_v1")
    partitions: int = int(os.getenv("TOPIC_PARTITIONS", "3"))
    replication: int = int(os.getenv("TOPIC_RF", "1"))
    retention_ms: str = os.getenv("TOPIC_RETENTION_MS", str(24 * 60 * 60 * 1000))  # 1 day
    segment_ms: str = os.getenv("TOPIC_SEGMENT_MS", str(15 * 60 * 1000))  # 15 min
    cleanup_policy: str = os.getenv("TOPIC_CLEANUP_POLICY", "delete")

S = Settings()

def ensure_topic(ac: AdminClient, name: str, cfg: Dict[str, str]):
    md = ac.list_topics(timeout=5)
    if name in md.topics and not md.topics[name].error:
        print(f"🟢 Topic '{name}' exists; updating config if needed...")
        cr = ConfigResource(restype="topic", name=name, set_config=cfg)
        fs = ac.incremental_alter_configs([cr])
        for f in fs.values():
            try:
                f.result()
            except Exception as e:
                print(f"  note: {e}")
        return

    print(f"🟡 Creating topic '{name}'...")
    nt = NewTopic(name, S.partitions, S.replication, config=cfg)  # ✅ FIXED
    fs = ac.create_topics([nt])
    fs[name].result()  # raise if error
    print(f"✅ Topic '{name}' created.")


def main():
    ac = AdminClient({"bootstrap.servers": S.bootstrap_servers})
    cfg = {
        "retention.ms": S.retention_ms,
        "segment.ms": S.segment_ms,
        "cleanup.policy": S.cleanup_policy,
        "min.insync.replicas": "1",
        "compression.type": "zstd",
    }
    ensure_topic(ac, S.topic, cfg)

if __name__ == "__main__":
    main()
