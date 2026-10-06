import json
import os
from datetime import datetime, timezone

from confluent_kafka import Consumer
from pymongo import MongoClient


KAFKA_SERVER = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "kafka:19092",
)

CONSUMER_GROUP = os.getenv(
    "KAFKA_CONSUMER_GROUP",
    "mongodb-writer",
)

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://mongodb:27017",
)

MONGO_DATABASE = os.getenv(
    "MONGO_DATABASE",
    "kafka_pipeline",
)

MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", "9"))

TOPICS = [
    "simpsons.characters",
    "pokemon.data",
    "randomuser.data",
]

COLLECTIONS = {
    "simpsons.characters": "simpsons_characters",
    "pokemon.data": "pokemon",
    "randomuser.data": "random_users",
}


consumer = Consumer(
    {
        "bootstrap.servers": KAFKA_SERVER,
        "group.id": CONSUMER_GROUP,
        "group.protocol": "consumer",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    }
)

mongo_client = MongoClient(MONGO_URI)
database = mongo_client[MONGO_DATABASE]

processed = 0
empty_polls = 0

try:
    mongo_client.admin.command("ping")
    print("Connected to MongoDB")

    consumer.subscribe(TOPICS)
    print(f"Subscribed to topics: {', '.join(TOPICS)}")

    while processed < MAX_MESSAGES and empty_polls < 10:
        message = consumer.poll(1.0)

        if message is None:
            empty_polls += 1
            continue

        if message.error():
            print(f"Kafka error: {message.error()}")
            continue

        empty_polls = 0

        event = json.loads(message.value().decode("utf-8"))
        collection_name = COLLECTIONS[message.topic()]

        document = {
            **event,
            "stored_at": datetime.now(timezone.utc).isoformat(),
            "kafka": {
                "topic": message.topic(),
                "partition": message.partition(),
                "offset": message.offset(),
            },
        }

        database[collection_name].replace_one(
            {"event_id": event["event_id"]},
            document,
            upsert=True,
        )

        consumer.commit(
            message=message,
            asynchronous=False,
        )

        processed += 1

        print(
            f"Stored topic={message.topic()} "
            f"collection={collection_name} "
            f"partition={message.partition()} "
            f"offset={message.offset()}"
        )

finally:
    consumer.close()
    mongo_client.close()

print(
    f"Consumer completed "
    f"processed={processed} "
    f"expected={MAX_MESSAGES}"
)

if processed != MAX_MESSAGES:
    raise SystemExit(1)