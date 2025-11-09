from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    bootstrap_servers: str = Field(default=os.getenv("BOOTSTRAP_SERVERS", "localhost:9092"))
    schema_registry_url: str = Field(default=os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081"))
    compression: str = Field(default=os.getenv("PRODUCER_COMPRESSION", "gzip"))
    topic: str = Field(default=os.getenv("TOPIC_DEVICE_METRIC", "device_metrics_v1"))
    # Rate control
    rate_per_sec: int = int(os.getenv("PRODUCER_RATE_PER_SEC", "2000"))
    burst: int = int(os.getenv("PRODUCER_BURST", "5000"))
    linger_ms: int = int(os.getenv("PRODUCER_LINGER_MS", "5"))
    max_in_flight: int = int(os.getenv("PRODUCER_MAX_IN_FLIGHT", "100000"))
    # Batching
    batch_size: int = int(os.getenv("PRODUCER_BATCH_SIZE", "16384"))
    # Keys
    key_strategy: str = os.getenv("KEY_STRATEGY", "device_id")

SETTINGS = Settings()
