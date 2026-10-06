import json
import os
import random
import time
import uuid
from datetime import datetime, timezone

import requests
from confluent_kafka import Producer


KAFKA_SERVER = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "kafka:19092",
)

BATCH_COUNT = int(
    os.getenv("BATCH_COUNT", "3")
)

BATCH_INTERVAL_SECONDS = int(
    os.getenv("BATCH_INTERVAL_SECONDS", "5")
)

producer = Producer(
    {
        "bootstrap.servers": KAFKA_SERVER,
        "acks": "all",
    }
)


def get_json(url, params=None):
    response = requests.get(
        url,
        params=params,
        headers={
            "User-Agent": "kafka-data-pipeline/1.0"
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def fetch_simpsons_character():
    page = random.randint(1, 60)

    data = get_json(
        "https://thesimpsonsapi.com/api/characters",
        {"page": page},
    )

    character = random.choice(data["results"])

    return {
        "id": character["id"],
        "name": character["name"],
        "occupation": character.get("occupation"),
        "status": character.get("status"),
    }


def fetch_pokemon():
    pokemon_id = random.randint(1, 1025)

    pokemon = get_json(
        f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/"
    )

    return {
        "id": pokemon["id"],
        "name": pokemon["name"],
        "height": pokemon["height"],
        "weight": pokemon["weight"],
        "types": [
            item["type"]["name"]
            for item in pokemon["types"]
        ],
    }


def fetch_random_user():
    data = get_json(
        "https://randomuser.me/api/1.4/",
        {
            "results": 1,
            "noinfo": "true",
        },
    )

    user = data["results"][0]

    return {
        "id": user["login"]["uuid"],
        "first_name": user["name"]["first"],
        "last_name": user["name"]["last"],
        "email": user["email"],
        "country": user["location"]["country"],
    }


def delivery_report(error, message):
    if error:
        print(f"Delivery failed: {error}")
    else:
        print(
            f"Published topic={message.topic()} "
            f"partition={message.partition()} "
            f"offset={message.offset()}"
        )


def publish(topic, source, payload):
    event = {
        "event_id": str(uuid.uuid4()),
        "source": source,
        "produced_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "payload": payload,
    }

    producer.produce(
        topic=topic,
        key=event["event_id"],
        value=json.dumps(
            event,
            ensure_ascii=False,
        ),
        callback=delivery_report,
    )

    producer.poll(0)

    print(
        f"Queued source={source} topic={topic}"
    )


jobs = [
    (
        "simpsons.characters",
        "the_simpsons_api",
        fetch_simpsons_character,
    ),
    (
        "pokemon.data",
        "pokeapi",
        fetch_pokemon,
    ),
    (
        "randomuser.data",
        "random_user_api",
        fetch_random_user,
    ),
]


total_published = 0

for batch_number in range(1, BATCH_COUNT + 1):
    print(
        f"Starting batch={batch_number}/{BATCH_COUNT}"
    )

    batch_published = 0

    for topic, source, fetch_function in jobs:
        try:
            payload = fetch_function()

            publish(
                topic,
                source,
                payload,
            )

            batch_published += 1

        except Exception as error:
            print(
                f"Failed source={source}: {error}"
            )

    remaining = producer.flush(15)
    total_published += batch_published

    print(
        f"Batch completed batch={batch_number} "
        f"published={batch_published} expected=3"
    )

    if batch_published != 3 or remaining != 0:
        raise SystemExit(1)

    if batch_number < BATCH_COUNT:
        time.sleep(BATCH_INTERVAL_SECONDS)

print(
    f"Producer completed "
    f"total_published={total_published} "
    f"expected={BATCH_COUNT * 3}"
)