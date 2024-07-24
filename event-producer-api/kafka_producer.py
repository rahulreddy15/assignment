from kafka import KafkaProducer
from kafka.errors import KafkaError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import json
from datetime import datetime
from .config import KAFKA_BOOTSTRAP_SERVERS

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

def json_serializer(data):
    return json.dumps(data, cls=DateTimeEncoder).encode('utf-8')

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(KafkaError)
)
def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=json_serializer
    )

producer = get_kafka_producer()