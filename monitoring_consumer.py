import logging
from kafka import KafkaConsumer
import json
import sqlite3
from datetime import datetime
import socket
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9093')
KAFKA_MONITORING_TOPIC = os.getenv('KAFKA_MONITORING_TOPIC', 'monitoring')

# SQLite database configuration
DB_NAME = 'monitoring_events.db'
def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS monitoring_events (
        id TEXT PRIMARY KEY,
        event_id TEXT,
        topic TEXT,
        status TEXT,
        timestamp TEXT,
        source TEXT,
        details TEXT
    )
    ''')
    conn.commit()
    conn.close()

def insert_event(event):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO monitoring_events (id, event_id, topic, status, timestamp, source, details)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        event['id'],
        event['event_id'],
        event['topic'],
        event['status'],
        event['timestamp'],
        event['source'],
        event['details']
    ))
    conn.commit()
    conn.close()

def check_kafka_connection(bootstrap_servers):
    print(f"Attempting to connect to Kafka brokers: {bootstrap_servers}")
    for server in bootstrap_servers.split(','):
        host, port = server.split(':')
        try:
            sock = socket.create_connection((host, int(port)), timeout=5)
            sock.close()
            print(f"Successfully connected to {server}")
            return True
        except socket.error as e:
            print(f"Failed to connect to {server}: {e}")
    return False


def main():
    create_table()

    logger.info(f"Attempting to connect to Kafka at: {KAFKA_BOOTSTRAP_SERVERS}")

    try:
        consumer = KafkaConsumer(
            KAFKA_MONITORING_TOPIC,
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='monitoring-consumer-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            api_version=(0, 10, 1)  # Add this line
        )

        logger.info(f"Successfully created KafkaConsumer instance")
        logger.info(f"Starting Kafka consumer for topic: {KAFKA_MONITORING_TOPIC}")

        for message in consumer:
            event = message.value
            logger.info(f"Received event: {event}")
            insert_event(event)
            logger.info(f"Inserted event with ID: {event['id']} into the database")

    except Exception as e:
        logger.error(f"Error in Kafka consumer: {str(e)}", exc_info=True)

    finally:
        if 'consumer' in locals():
            consumer.close()
            logger.info("Kafka consumer closed")

if __name__ == "__main__":
    main()