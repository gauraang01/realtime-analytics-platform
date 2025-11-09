from rtap_contracts.schema_ops import validate_local

def test_valid_sample():
    sample = {
        "event_time": 1_700_000_000_000_000,
        "device_id": "device-001",
        "metric": "cpu_util",
        "value": 12.34,
        "tags": {"region": "ap-south-1"},
        "trace_id": "tr-123456",
        "ingest_ts": 1_700_000_000_000_111
    }
    validate_local(sample)  # should not raise

def test_invalid_metric_symbol():
    invalid = {
        "event_time": 1_700_000_000_000_000,
        "device_id": "device-001",
        "metric": "disk_free",  # not in enum
        "value": 12.34
    }
    raised = False
    try:
        validate_local(invalid)
    except Exception:
        raised = True
    assert raised, "invalid enum symbol should fail"
