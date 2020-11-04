import json
import os

from kafka import KafkaProducer

bootstrap_server = "{}:{}".format(os.getenv("KAFKA_HOST"), os.getenv("KAFKA_PORT"))


class Broker:
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_server,
                                      value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def produce(self, **kwargs):
        try:
            topic = os.getenv("KAFKA_TOPIC")
            payload = kwargs.get("payload")
            self.producer.send(topic, payload)
        except Exception as ex:
            print(ex)
