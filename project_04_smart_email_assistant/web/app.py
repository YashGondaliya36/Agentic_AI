"""FastAPI Backend for Email Assistant Web UI"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# Add parent directory to path to import from agents/integrations
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

# Load .env from root (parent of parent)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# Initialize FastAPI
app = FastAPI(title="Smart Email Assistant", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates (relative to web directory)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Global state
email_queue = []
active_connections: List[WebSocket] = []


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render main dashboard"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/emails")
async def get_emails():
    """Fetch unread emails from Gmail"""
    try:
        from integrations.gmail_client import gmail_client
        emails = gmail_client.get_recent_emails(max_results=10)
        
        # Format for frontend
        formatted_emails = []
        for email in emails:
            formatted_emails.append({
                "id": email["id"],
                "from_name": email["from_name"],
                "from_email": email["from_email"],
                "subject": email["subject"],
                "body": email["body"][:200] + "..." if len(email["body"]) > 200 else email["body"],
                "full_body": email["body"],
                "date": email.get("date", datetime.now()).isoformat() if isinstance(email.get("date"), datetime) else str(email.get("date")),
                "labels": email.get("labels", [])
            })
        
        return {"success": True, "emails": formatted_emails, "count": len(formatted_emails)}
    
    except Exception as e:
        return {"success": False, "error": str(e), "emails": [], "count": 0}


@app.post("/api/classify/{email_id}")
async def classify_email(email_id: str):
    """Classify a specific email"""
    try:
        from integrations.gmail_client import gmail_client
        from agents.classifier import classifier_agent
        from graph.state import create_initial_state
        
        # Get email details
        emails = gmail_client.get_recent_emails(max_results=50)
        email = next((e for e in emails if e["id"] == email_id), None)
        
        if not email:
            return {"success": False, "error": "Email not found"}
        
        # Create state and classify
        state = create_initial_state(email)
        result = classifier_agent.classify(state)
        
        return {
            "success": True,
            "category": result.get("category"),
            "priority": result.get("priority"),
            "action_required": result.get("action_required")
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/generate-draft/{email_id}")
async def generate_draft(email_id: str):
    """Generate draft response for an email"""
    try:
        from integrations.gmail_client import gmail_client
        from agents.classifier import classifier_agent
        from agents.draft_writer import draft_writer_agent
        from graph.state import create_initial_state
        
        # Get email
        emails = gmail_client.get_recent_emails(max_results=50)
        email = next((e for e in emails if e["id"] == email_id), None)
        
        if not email:
            return {"success": False, "error": "Email not found"}
        
        # Classify and generate draft
        state = create_initial_state(email)
        state = classifier_agent.classify(state)
        state = draft_writer_agent.write_draft(state)
        
        return {
            "success": True,
            "draft": state.get("draft_response"),
            "category": state.get("category"),
            "priority": state.get("priority")
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/send-email")
async def send_email(data: dict):
    """Send an approved email"""
    try:
        from integrations.gmail_client import gmail_client
        
        email_id = data.get("email_id")
        to = data.get("to")
        subject = data.get("subject")
        body = data.get("body")
        
        if not all([to, subject, body]):
            return {"success": False, "error": "Missing required fields"}
        
        # Send email
        success = gmail_client.send_email(to=to, subject=subject, body=body)
        
        if success and email_id:
            # Mark original as read
            gmail_client.mark_as_read(email_id)
        
        return {"success": success, "message": "Email sent successfully!" if success else "Failed to send email"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/archive/{email_id}")
async def archive_email(email_id: str):
    """Archive (mark as read) an email"""
    try:
        from integrations.gmail_client import gmail_client
        success = gmail_client.mark_as_read(email_id)
        return {"success": success}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle WebSocket messages if needed
            await websocket.send_text(f"Echo: {data}")
    
    except WebSocketDisconnect:
        active_connections.remove(websocket)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Smart Email Assistant"}


if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting Smart Email Assistant Web Server...")
    print("📍 Open browser: http://localhost:8000\n")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
