from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pydantic import BaseModel
from typing import List
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DB_NAME = os.getenv('DATABASE_PATH', '/app/data/monitoring.db')

class Event(BaseModel):
    id: str
    event_id: str
    topic: str
    status: str
    timestamp: str
    source: str
    details: str = None


@app.get("/")
async def root():
    return {"message": "Hello from the Monitoring Dashboard"}


@app.get("/events", response_model=List[Event])
async def get_events():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM monitoring_events ORDER BY timestamp DESC")
    events = [Event(**dict(zip([column[0] for column in cursor.description], row))) for row in cursor.fetchall()]
    conn.close()
    return events

@app.get("/event/{event_id}", response_model=List[Event])
async def get_event(event_id: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM monitoring_events WHERE event_id = ? ORDER BY timestamp", (event_id,))
    events = [Event(**dict(zip([column[0] for column in cursor.description], row))) for row in cursor.fetchall()]
    conn.close()
    if not events:
        raise HTTPException(status_code=404, detail="Event not found")
    return events

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7070)