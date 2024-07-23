import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9093').split(',')
KAFKA_TOPICS = set(os.getenv('KAFKA_TOPICS', '').split(','))
KAFKA_MONITORING_TOPIC = os.getenv('KAFKA_MONITORING_TOPIC', 'monitoring')
SERVICE_NAME = os.getenv('SERVICE_NAME', 'events-producer-api')