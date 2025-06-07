# app.py - MAIN RAILWAY SERVER
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import asyncio
import os
from pathlib import Path

# Import your existing code
from voice_assistant import EnhancedVoiceAssistant
from config import CONFIG

app = FastAPI(title="Government Schemes Voice Assistant")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global assistant instance
assistant = None

@app.on_event("startup")
async def startup_event():
    global assistant
    print("🚀 Starting Railway Voice Assistant...")
    assistant = EnhancedVoiceAssistant()
    print("✅ Assistant initialized")

# app.py - Update the get_homepage function
@app.get("/")
async def get_homepage():
    """Serve the Gemini-style interface"""
    return FileResponse('static/index.html')

# Add static files mount
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print(f"🔌 Client connected: {websocket.client}")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive()
            
            if "text" in data:
                # Text message
                message = json.loads(data["text"])
                if message["type"] == "text":
                    query = message["message"]
                    
                    # Process with your existing logic
                    response = await process_query(query)
                    
                    # Send response
                    await websocket.send_text(json.dumps({
                        "type": "response",
                        "message": response
                    }))
            
            elif "bytes" in data:
                # Audio data (for future voice implementation)
                audio_data = data["bytes"]
                # TODO: Implement voice processing
                pass
                
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        print("🔌 Client disconnected")

async def process_query(query: str) -> str:
    """Process user query using existing assistant logic"""
    try:
        global assistant
        
        if not assistant:
            return "Assistant not ready. Please refresh the page."
        
        # Use your existing search logic
        schemes = assistant.find_relevant_schemes(query, top_n=3)
        response = assistant.format_scheme_response(schemes, query, "english")
        
        return response
        
    except Exception as e:
        print(f"❌ Query processing error: {e}")
        return "Sorry, I encountered an error processing your request."

@app.get("/health")
async def health_check():
    """Health check for Railway"""
    return {"status": "healthy", "service": "government-schemes-assistant"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)