#!/bin/bash

# Start consumer for product_updates topic
python kafka_event_consumer.py product_updates &

# Start consumer for country topic
python kafka_event_consumer.py country &

# Start consumer for product_discounts topic
python kafka_event_consumer.py product_discounts