from pydantic import BaseModel, Field
import os

class Settings(BaseModel):
    bootstrap_servers: str = Field(default=os.environ.get("BOOTSTRAP_SERVERS", "localhost:9092"))
    schema_registry_url: str = Field(default=os.environ.get("SCHEMA_REGISTRY_URL", "http://localhost:8081"))
    topic: str = Field(default=os.environ.get("TOPIC_DEVICE_METRIC", "device_metrics_v1"))
    subject_value: str = Field(default=os.environ.get("SUBJECT_DEVICE_METRIC", "device_metric-value"))
    acks: str = Field(default=os.environ.get("KAFKA_ACKS", "all"))

SETTINGS = Settings()
