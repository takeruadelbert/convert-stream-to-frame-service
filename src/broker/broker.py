import json
import os

from kafka import KafkaProducer

bootstrap_server = "{}:{}".format(os.getenv("KAFKA_HOST"), os.getenv("KAFKA_PORT"))


class Broker:
    def __init__(self, logger):
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_server,
                                      value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        self.logger = logger

    def produce(self, **kwargs):
        try:
            topic = kwargs.get("topic")
            payload = kwargs.get("payload")
            self.producer.send(topic, payload)
            self.logger.info('payload sent')
        except Exception as ex:
            self.logger.error('Error when sending payload to queue : {}'.format(ex))
