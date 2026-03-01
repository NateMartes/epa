#!/bin/bash
# Init script for Kakfa broker Docker Container
# usage: init [--is-started | -s] [--broker | -b] myhostname [--port | -p] myport --


OPTIONS=$(getopt -o sb:p: --long is-started,broker:,port: -n 'init' -- "$@")
eval set -- "$OPTIONS"

TOPIC="new_posts"
TARGET_GROUPS=("cache_loader_consumer_group" "post_ingestor_consumer_group" "notify_service_consumer_group")

is_running=0
broker=""
port=""
while true; do
    echo $1
    case "$1" in
        -s|--is-started)
            is_running=1
            shift 1
            ;;
        -b|--broker)
            broker=$2
            shift 2
            ;;
        -p|--port)
            port=$2
            shift 2
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "usage: init [--is-started | -s] [--broker | -b] myhostname [--port | -p] myport" >&2
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
/opt/kafka/bin/kafka-topics.sh --create --topic new_posts --bootstrap-server $broker:$port
echo "Done."

echo "Creating Kafka Consumer Groups..."
for GROUP in "${TARGET_GROUPS[@]}"; do
  echo "Starting consumer for group: $GROUP"
  /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $broker:$port --topic $TOPIC --group $GROUP &
done

echo "Done."

if [[ $is_running -eq 0 ]]; then
    wait $PID
fi