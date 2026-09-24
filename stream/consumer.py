"""
Consumes raw telemetry from Kafka, hands it off for preprocessing + scoring.

Run locally (outside Docker) against the host-exposed Kafka port:
    python stream/consumer.py

TODO (David):
- Preprocessing: normalize/clean the HL7/FHIR-shaped payload fields
- Feed cleaned records into the ML model (see ml/train_isolation_forest.py)
- Publish the result (record + risk score) to TOPIC_TELEMETRY_SCORED
"""
import json
import os

from kafka import KafkaConsumer, KafkaProducer

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS_HOST", "localhost:29092")
TOPIC_IN = os.getenv("TOPIC_TELEMETRY_RAW", "iomt.telemetry.raw")
TOPIC_OUT = os.getenv("TOPIC_TELEMETRY_SCORED", "iomt.telemetry.scored")


def main():
    consumer = KafkaConsumer(
        TOPIC_IN,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id="stream-preprocessing",
    )
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    print(f"Listening on '{TOPIC_IN}', publishing to '{TOPIC_OUT}'...")

    for message in consumer:
        record = message.value

        # TODO: replace with real preprocessing
        cleaned = record

        # TODO: replace with real model inference (import from ml/)
        risk_score = 0  # placeholder

        cleaned["risk_score"] = risk_score
        producer.send(TOPIC_OUT, cleaned)
        print(f"Scored record: risk_score={risk_score}")


if __name__ == "__main__":
    main()