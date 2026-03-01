FROM apache/kafka:latest

USER root

COPY init.sh /init.sh
RUN chmod +x init.sh

USER 1000

CMD ["./init.sh", "--broker", "epa-kafka-broker", "--port", "9092"]