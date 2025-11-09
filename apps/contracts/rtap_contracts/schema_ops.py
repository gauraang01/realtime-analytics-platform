from pathlib import Path
import json
from typing import Any, Dict, Tuple

from fastavro import parse_schema, validate
from jsonschema import validate as js_validate, Draft202012Validator, exceptions as js_exceptions

AVRO_PATH = Path(__file__).resolve().parent.parent / "schemas" / "avro" / "device_metric.v1.avsc"
JSON_PATH = Path(__file__).resolve().parent.parent / "schemas" / "json" / "device_metric.v1.json"

def load_schemas() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    avro_schema = json.loads(AVRO_PATH.read_text())
    json_schema = json.loads(JSON_PATH.read_text())
    return avro_schema, json_schema

def validate_local(sample: Dict[str, Any]) -> None:
    avro_schema, json_schema = load_schemas()
    parsed = parse_schema(avro_schema)
    if not validate(sample, parsed):
        raise ValueError("Sample failed Avro validation")
    Draft202012Validator(json_schema).validate(sample)
