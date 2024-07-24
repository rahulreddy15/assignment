from fastapi import FastAPI, HTTPException, Request
from .models import Event
from .kafka_producer import producer
from .config import KAFKA_TOPICS, KAFKA_MONITORING_TOPIC, SERVICE_NAME
from kafka.errors import KafkaError
import uuid
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

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
        "timestamp": datetime.utcnow().isoformat(),
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
