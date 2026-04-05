#!/bin/bash
# Init script for Kakfa broker Docker Container
# usage: init [--is-started | -s] --


OPTIONS=$(getopt -o s --long is-started -n 'init' -- "$@")
eval set -- "$OPTIONS"

TOPIC="new_posts"
TARGET_GROUPS=("cache_loader_consumer_group" "post_ingestor_consumer_group" "notify_service_consumer_group")

is_running=0
while true; do
    echo $1
    case "$1" in
        -s|--is-started)
            is_running=1
            shift 1
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "usage: init [--is-started | -s] --" >&2
            exit 1
            ;;
    esac
done

if [[ $is_running -eq 0 ]]; then
    
    /etc/kafka/docker/run &
    PID=$!
    
    echo "Waiting for Kafka..."
    while ! nc -z 0.0.0.0 9092; do
        sleep 1
    done
fi

echo "Creating needed topic..."
/opt/kafka/bin/kafka-topics.sh --create --topic new_posts --bootstrap-server localhost:9092
echo "Done."

echo "Adding ACL rules..."
/opt/kafka/bin/kafka-acls.sh --bootstrap-server localhost:9092 \
  --add --operation Write --topic $TOPIC \
  --allow-principal User:post_producer

/opt/kafka/bin/kafka-acls.sh --bootstrap-server localhost:9092 \
  --add --operation Read --topic $TOPIC \
  --allow-principal User:post_consumer

/opt/kafka/bin/kafka-acls.sh --bootstrap-server localhost:9092 \
  --add --operation Describe --topic $TOPIC \
  --allow-principal User:post_producer \
  --allow-principal User:post_consumer

for GROUP in "${TARGET_GROUPS[@]}"; do
  /opt/kafka/bin/kafka-acls.sh --bootstrap-server localhost:9092 \
    --add --operation Read --operation Describe \
    --group "$GROUP" \
    --allow-principal User:post_consumer
done

echo "Done."
echo "Creating Kafka Consumer Groups..."
for GROUP in "${TARGET_GROUPS[@]}"; do
  /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 \
    --topic $TOPIC --group $GROUP &
done

if [[ $is_running -eq 0 ]]; then
    wait $PID
fi