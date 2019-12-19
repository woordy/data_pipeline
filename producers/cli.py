from . import KafkaStreaming


def main(args=None):
    kafka_producer = KafkaStreaming()
    kafka_producer.produce()
