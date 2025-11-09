from io import BytesIO
import httpx
import struct
import json
from pathlib import Path
from typing import Any, Dict
from fastavro import schemaless_writer

AVRO_PATH = Path(__file__).resolve().parent.parent.parent / "contracts" / "schemas" / "avro" / "device_metric.v1.avsc"
MAGIC_BYTE = b"\x00"

def load_avro() -> Dict[str, Any]:
    return json.loads(AVRO_PATH.read_text())

async def get_or_register_schema_id(sr_url: str, subject: str, schema: Dict[str, Any]) -> int:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{sr_url}/subjects/{subject}/versions/latest")
        if r.status_code == 200:
            return r.json()["id"]

        r2 = await client.post(
            f"{sr_url}/subjects/{subject}/versions",
            json={"schema": json.dumps(schema)},
        )
        r2.raise_for_status()
        return r2.json()["id"]

def encode_confluent_avro(schema_id: int, schema: Dict[str, Any], record: Dict[str, Any]) -> bytes:
    # Confluent framing header
    header = MAGIC_BYTE + struct.pack(">I", schema_id)

    # Use a BytesIO writer for Avro body
    buf = BytesIO()
    schemaless_writer(buf, schema, record)

    return header + buf.getvalue()
