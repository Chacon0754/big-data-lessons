#!/usr/bin/env bash

set -euo pipefail

KAFKA_SERVICE="${KAFKA_SERVICE:-kafka}"
BOOTSTRAP_SERVER="${KAFKA_BOOTSTRAP_SERVERS:-kafka:19092}"

TOPICS=(
    "simpsons.characters"
    "pokemon.data"
    "randomuser.data"
)

for topic in "${TOPICS[@]}"; do
    docker compose exec -T "$KAFKA_SERVICE" \
        /opt/kafka/bin/kafka-topics.sh \
        --bootstrap-server "$BOOTSTRAP_SERVER" \
        --create \
        --if-not-exists \
        --topic "$topic" \
        --partitions 1 \
        --replication-factor 1

    echo "Topic ready: $topic"
done