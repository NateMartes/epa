FROM apache/kafka:latest
ARG EPA_KAFKA_ADMIN_PASSWORD
ARG EPA_KAFKA_PRODUCER_PASSWORD
ARG EPA_KAFKA_CONSUMER_PASSWORD

USER root

COPY init.sh /init.sh
RUN chmod +x init.sh
COPY jaas.config /opt/kafka/config/jaas.conf

# insert passwords inline
RUN sed -i "s/user_admin=\"\"/user_admin=\"${EPA_KAFKA_ADMIN_PASSWORD}\"/g" /opt/kafka/config/jaas.conf
RUN sed -i "s/user_post_producer=\"\"/user_post_producer=\"${EPA_KAFKA_PRODUCER_PASSWORD}\"/g" /opt/kafka/config/jaas.conf
RUN sed -i "s/user_post_consumer=\"\"/user_post_consumer=\"${EPA_KAFKA_CONSUMER_PASSWORD}\"/g" /opt/kafka/config/jaas.conf

USER 1000

CMD ["./init.sh"]