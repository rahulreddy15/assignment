import logging
from kafka import KafkaConsumer, KafkaProducer
import json
import time
import os
from uuid import uuid4
from datetime import datetime
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaEventConsumer:
    def __init__(self, input_topic, group_id_prefix='consumer-group'):
        self.KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9093')
        self.KAFKA_INPUT_TOPIC = input_topic
        self.KAFKA_MONITORING_TOPIC = os.getenv('KAFKA_MONITORING_TOPIC', 'monitoring')
        self.GROUP_ID = f"{group_id_prefix}-{input_topic}"

        self.consumer = self._create_consumer()
        self.producer = self._create_producer()

    def _create_consumer(self):
        return KafkaConsumer(
            self.KAFKA_INPUT_TOPIC,
            bootstrap_servers=[self.KAFKA_BOOTSTRAP_SERVERS],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=self.GROUP_ID,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            api_version=(0, 10, 1)
        )

    def _create_producer(self):
        return KafkaProducer(
            bootstrap_servers=[self.KAFKA_BOOTSTRAP_SERVERS],
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            api_version=(0, 10, 1)
        )

    def simulate_db_call(self):
        """Simulate a database call with a random delay."""
        delay = random.uniform(0.1, 2.0)
        time.sleep(delay)
        return True

    def process_event(self, event):
        """Process the event and simulate a database call."""
        logger.info(f"Processing event: {event}")
        success = self.simulate_db_call()
        return success

    def create_monitoring_event(self, original_event, status):
        """Create a new monitoring event based on the original event."""
        return {
            'id': str(uuid4()),
            'event_id': original_event['id'],
            'topic': self.KAFKA_INPUT_TOPIC,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'source': f'consumer-{self.KAFKA_INPUT_TOPIC}',
            'details': json.dumps({'original_event': original_event})
        }

    def run(self):
        logger.info(f"Starting Kafka consumer for topic: {self.KAFKA_INPUT_TOPIC}")

        try:
            for message in self.consumer:
                event = message.value
                logger.info(f"Received event: {event}")

                success = self.process_event(event)

                status = 'processed' if success else 'failed'
                monitoring_event = self.create_monitoring_event(event, status)

                self.producer.send(self.KAFKA_MONITORING_TOPIC, value=monitoring_event)
                logger.info(f"Sent monitoring event: {monitoring_event}")

        except Exception as e:
            logger.error(f"Error in Kafka consumer/producer: {str(e)}", exc_info=True)

        finally:
            self.consumer.close()
            self.producer.close()
            logger.info("Kafka consumer and producer closed")

def create_consumer(topic):
    return KafkaEventConsumer(topic)

if __name__ == "__main__":
    # Example usage
    topic = 'product_updates'
    consumer = create_consumer(topic)
    consumer.run()