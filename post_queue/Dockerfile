FROM apache/kafka:latest
ARG EPA_KAFKA_ADMIN_PASSWORD

USER root

COPY init.sh /init.sh
RUN chmod +x init.sh
COPY jaas.config /opt/kafka/config/jaas.conf

# insert password inline
RUN sed -i "s/user_admin=\"\";/user_admin=\"${EPA_KAFKA_ADMIN_PASSWORD}\";/g" /opt/kafka/config/jaas.conf

USER 1000

CMD ["./init.sh", "--broker", "epa-kafka-broker", "--port", "9092"]