from kafka import KafkaProducer
from typing import Dict, Any
import os
import json

class KafkaUtils:
    """A class with helpful methods to interact with Apache Kafka"""
    
    @staticmethod
    def get_kafka_bootstrap_server() -> str:
        """
        Gets the kafka server this API will send messages to.
        
        :return: The bootstrap server in the format 'hostname:port'
        :rtype: str
        """
        
        hostname = os.getenv("EPA_KAFKA_BROKER_HOSTNAME")
        port = os.getenv("EPA_KAFKA_BROKER_PORT")
        
        if not hostname or not port:
            raise ValueError("Environment variables for Kafka not set")
            
        return f"{hostname}:{port}"
        
    @staticmethod
    def get_kafka_post_topic() -> str:
        """
        Gets the kafka topic name for new posts
        
        :return: The kafka topic name
        :rtype: str
        """
        output = os.getenv("EPA_KAFKA_POST_TOPIC_NAME")
        if not output:
            raise ValueError("Environment variables for Kafka not set. EPA_KAFKA_POST_TOPIC_NAME not set")
            
        return output

        
    @staticmethod
    def connect_to_kafka_as_producer() -> KafkaProducer:
        """
        Connects to the Kafka as Kafka producer using the underlying envinroment variables.
        
        :return: A new kafka producer object
        :rtype: kafka.KafkaProducer
        """
        server = KafkaUtils.get_kafka_bootstrap_server()
        return KafkaProducer(
            bootstrap_servers=server,
            allow_auto_create_topics=False,
            retries=3)
        
    @staticmethod
    def send_message(producer: KafkaProducer, message: Dict[Any, Any]):
        """
        Sends a message to the Kafka queue.
        
        :param producer: A producer connected to a Kafka instance
        :type prodcuer: kafka.KafkaProducer
        :param message: The message to send
        :type message: Dict[Any, Any]
        """
        
        
        producer.send(
            KafkaUtils.get_kafka_post_topic(),
            json.dumps(message).encode("utf-8")
        )