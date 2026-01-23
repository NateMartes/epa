# Init script for Kakfa broker container

#!/bin/bash

./etc/kafka/docker/run &
PID=$!

echo "Waiting for Kafka..."
while ! nc -z 0.0.0.0 9092; do
  sleep 1
done

echo "Creating needed topics..."
/opt/kafka/bin/kafka-topics.sh --create --topic post-ingestor-consumer --bootstrap-server epa_kakfa_broker:9092
/opt/kafka/bin/kafka-topics.sh --create --topic cache-loader-consumer --bootstrap-server epa_kakfa_broker:9092
/opt/kafka/bin/kafka-topics.sh --create --topic notify-service-consumer --bootstrap-server epa_kakfa_broker:9092

echo "Done."
wait $PID 