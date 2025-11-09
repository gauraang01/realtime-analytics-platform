import asyncio
import signal
from aiokafka import AIOKafkaProducer
from producer.settings import SETTINGS
from producer.avro_wire import load_avro, get_or_register_schema_id, encode_confluent_avro
from producer.generator import make_event

async def run():
    schema = load_avro()
    subject = "device_metric-value"
    schema_id = await get_or_register_schema_id(SETTINGS.schema_registry_url, subject, schema)

    producer = AIOKafkaProducer(
        bootstrap_servers=SETTINGS.bootstrap_servers,
        linger_ms=SETTINGS.linger_ms,
        acks="all",
        compression_type=SETTINGS.compression,
        max_request_size=1024*1024,
        # aiokafka buffers/backpressure internally; limit in-flight by batching rate below
    )
    await producer.start()
    print(f"✅ Producer up. topic={SETTINGS.topic} rate/s={SETTINGS.rate_per_sec} burst={SETTINGS.burst} schema_id={schema_id}")

    stop = asyncio.Event()

    def _graceful(*_):
        stop.set()
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _graceful)

    i = 0
    try:
        # simple token-bucket rate limiter
        interval = 1.0 / max(1, SETTINGS.rate_per_sec)
        while not stop.is_set():
            # small bursts
            for _ in range(min(SETTINGS.burst, SETTINGS.rate_per_sec)):
                ev = make_event(i)
                i += 1
                key = ev["device_id"].encode("utf-8")
                val = encode_confluent_avro(schema_id, schema, ev)
                await producer.send_and_wait(SETTINGS.topic, value=val, key=key)
                if stop.is_set():
                    break
                await asyncio.sleep(interval)
    finally:
        await producer.stop()
        print("🛑 Producer stopped.")

if __name__ == "__main__":
    try:
        import uvloop  # type: ignore
        uvloop.install()
    except Exception:
        pass
    asyncio.run(run())
