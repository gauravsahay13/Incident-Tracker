from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

conn = sqlite3.connect("incidents.db", check_same_thread=False)
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

class Incident(BaseModel):
    title: str
    description: str
    priority: str

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
    return cursor.fetchall()

@app.put("/incidents/{incident_id}")
def update_incident(incident_id: int, status: str):
    cursor.execute("UPDATE incidents SET status=? WHERE id=?", (status, incident_id))
    conn.commit()
    return {"message": f"Incident {incident_id} updated to status '{status}'"}

@app.delete("/incidents/{incident_id}")
def delete_incident(incident_id: int):
    cursor.execute("DELETE FROM incidents WHERE id=?", (incident_id,))
    conn.commit()
    return {"message": f"Incident {incident_id} deleted"}