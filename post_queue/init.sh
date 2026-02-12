#!/bin/bash
# Init script for Kakfa broker container

TOPIC="new_posts"
BROKER="epa-kafka-broker:9092"
TARGET_GROUPS=("cache_loader_consumer_group" "post_ingestor_consumer_group" "notify_service_consumer_group")

./etc/kafka/docker/run &
PID=$!

echo "Waiting for Kafka..."
while ! nc -z 0.0.0.0 9092; do
  sleep 1
done

echo "Creating needed topic..."
/opt/kafka/bin/kafka-topics.sh --create --topic new_posts --bootstrap-server epa_kakfa_broker:9092
echo "Done."

echo "Creating Kafka Consumer Groups..."
for GROUP in "${TARGET_GROUPS[@]}"; do
  echo "Starting consumer for group: $GROUP"
  /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $BROKER --topic $TOPIC --group $GROUP &
done

echo "Done."
wait $PID 