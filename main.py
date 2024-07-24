# main.py
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import os
import uuid
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from datetime import datetime

load_dotenv()

app = FastAPI()

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9093').split(',')
KAFKA_TOPICS = set(os.getenv('KAFKA_TOPICS', '').split(','))
KAFKA_MONITORING_TOPIC = os.getenv('KAFKA_MONITORING_TOPIC', 'monitoring')
SERVICE_NAME = os.getenv('SERVICE_NAME', 'event-producer-api')

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(KafkaError)
)
def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

producer = get_kafka_producer()

class Event(BaseModel):
    topic: str
    data: dict

def create_monitoring_event(event_id: str, topic: str, status: str, details: str = None):
    return {
        "id": str(uuid.uuid4()),
        "event_id": event_id,
        "topic": topic,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "source": SERVICE_NAME,
        "details": details
    }

@app.post("/events/")
async def create_event(event: Event, request: Request):
    if event.topic not in KAFKA_TOPICS:
        raise HTTPException(status_code=400, detail=f"Topic '{event.topic}' does not exist")
    
    event_id = str(uuid.uuid4())
    event_with_id = {
        "id": event_id,
        "topic": event.topic,
        "data": event.data.model_dump(),
        "timestamp": datetime.utcnow().isoformat(),  # Convert to ISO format string
        "source_ip": request.client.host
    }
    
    try:
        # Send to the specified topic
        producer.send(event.topic, value=event_with_id)
        
        # Create and send monitoring event for successful production
        monitoring_event = create_monitoring_event(
            event_id=event_id,
            topic=event.topic,
            status="produced",
            details=f"Event successfully produced to topic {event.topic}"
        )
        producer.send(KAFKA_MONITORING_TOPIC, value=monitoring_event)
        
        return {"message": "Event created", "event_id": event_id}
    except KafkaError as e:
        # Create and send monitoring event for failed production
        monitoring_event = create_monitoring_event(
            event_id=event_id,
            topic=event.topic,
            status="failed",
            details=f"Failed to produce event to topic {event.topic}. Error: {str(e)}"
        )
        try:
            producer.send(KAFKA_MONITORING_TOPIC, value=monitoring_event)
        except:
            pass  # If sending to monitoring topic fails, we don't want to mask the original error
        
        raise HTTPException(status_code=500, detail=f"Failed to send event to Kafka: {str(e)}")

@app.get("/topics/")
async def get_topics():
    return {"topics": list(KAFKA_TOPICS)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)