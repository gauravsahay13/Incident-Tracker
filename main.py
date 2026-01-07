from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel, Field
from enum import Enum
import sqlite3

app = FastAPI()

conn = sqlite3.connect("incidents.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    priority TEXT,
    status TEXT DEFAULT 'Open'
)
""")
conn.commit()

class Priority(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"

class Incident(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str
    priority: Priority

@app.get("/")
def home():
    return {"message": "Welcome to Incident Tracker!"}

@app.post("/incidents/")
def create_incident(incident: Incident):
    cursor.execute("INSERT INTO incidents (title, description, priority) VALUES (?, ?, ?)",
                   (incident.title, incident.description, incident.priority))
    conn.commit()
    return {"message": "Incident created successfully"}

@app.get("/incidents/")
def list_incidents():
    cursor.execute("SELECT * FROM incidents")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@app.get("/incidents/{incident_id}")
def get_incident(incident_id: int):
    cursor.execute("SELECT * FROM incidents WHERE id=?", (incident_id,))
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")   
    
    return dict(row)

@app.put("/incidents/{incident_id}")
def update_incident(incident_id: int, status: str):
    cursor.execute("UPDATE incidents SET status=? WHERE id=?", (status, incident_id))
    conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"message": f"Incident {incident_id} updated to status '{status}'"}

@app.delete("/incidents/{incident_id}")
def delete_incident(incident_id: int):
    cursor.execute("DELETE FROM incidents WHERE id = ?", (incident_id,))
    conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {"message": f"Incident {incident_id} deleted"}
