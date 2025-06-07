import asyncio
import json
import logging
import os
import base64
import io
from datetime import datetime
from typing import Dict, Any, List
import traceback

# FastAPI and WebSocket
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

# Audio processing
import speech_recognition as sr
from gtts import gTTS
import tempfile

# Your existing components (modified for streaming)
from database_backup import SchemeDatabase
from synonym_dict import enhance_search_query
from config import CONFIG

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Real-time Voice Assistant")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class RealTimeVoiceAssistant:
    def __init__(self):
        self.current_language = "english"
        self.user_contexts = {}  # Store multiple user contexts
        
        # Initialize database
        try:
            self.scheme_db = SchemeDatabase(
                db_path=CONFIG["sqlite_db_path"],
                csv_path=CONFIG["schemes_csv_path"]
            )
            logger.info("✅ Database initialized")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            self.scheme_db = None
        
        # Speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.5
        
        logger.info("🤖 Real-time Voice Assistant initialized")
    
    def get_user_context(self, client_id: str) -> Dict:
        """Get or create user context"""
        if client_id not in self.user_contexts:
            self.user_contexts[client_id] = {
                "name": "User",
                "language": "english",
                "occupation": None,
                "location": None,
                "conversation_state": "greeting",
                "last_activity": datetime.now()
            }
        return self.user_contexts[client_id]
    
    async def process_audio_chunk(self, client_id: str, audio_data: bytes) -> Dict:
        """Process audio chunk and return response"""
        try:
            context = self.get_user_context(client_id)
            
            # Convert audio to text
            text = await self.speech_to_text(audio_data)
            
            if not text or len(text.strip()) < 2:
                return {
                    "type": "error",
                    "message": "Could not understand audio. Please try again."
                }
            
            logger.info(f"🎤 User said: '{text}'")
            
            # Process based on conversation state
            response_text = await self.process_user_input(client_id, text)
            
            # Convert response to audio
            audio_response = await self.text_to_speech(response_text, context["language"])
            
            return {
                "type": "response",
                "text": response_text,
                "audio": audio_response,
                "user_input": text
            }
            
        except Exception as e:
            logger.error(f"❌ Audio processing error: {e}")
            traceback.print_exc()
            return {
                "type": "error",
                "message": f"Processing error: {str(e)}"
            }
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        """Convert audio bytes to text"""
        try:
            # Create audio data from bytes
            audio_file = io.BytesIO(audio_data)
            
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio, language="hi-IN")
                return text.strip()
                
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            return ""
        except Exception as e:
            logger.error(f"STT error: {e}")
            return ""
    
    async def text_to_speech(self, text: str, language: str = "english") -> str:
        """Convert text to speech and return base64 encoded audio"""
        try:
            if not text or len(text.strip()) < 2:
                return ""
            
            # Language mapping
            lang_code = "hi" if language == "hindi" else "en"
            
            # Create TTS
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                
                # Read audio file and encode as base64
                with open(tmp_file.name, 'rb') as audio_file:
                    audio_data = audio_file.read()
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                # Cleanup
                os.unlink(tmp_file.name)
                
                return audio_base64
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return ""
    
    async def process_user_input(self, client_id: str, text: str) -> str:
        """Process user input based on conversation state"""
        context = self.get_user_context(client_id)
        text_lower = text.lower().strip()
        
        try:
            # Language detection
            if any(word in text_lower for word in ["hindi", "हिंदी", "1"]):
                context["language"] = "hindi"
                context["conversation_state"] = "name_collection"
                return "नमस्कार! आपका नाम क्या है?"
            
            elif any(word in text_lower for word in ["english", "अंग्रेजी", "2"]):
                context["language"] = "english"
                context["conversation_state"] = "name_collection"
                return "Hello! What's your name?"
            
            elif any(word in text_lower for word in ["hinglish", "हिंग्लिश", "3"]):
                context["language"] = "hinglish"
                context["conversation_state"] = "name_collection"
                return "Namaste! Aapka naam kya hai?"
            
            # Name collection
            if context["conversation_state"] == "name_collection":
                context["name"] = text.strip()
                context["conversation_state"] = "occupation_collection"
                
                responses = {
                    "hindi": f"धन्यवाद {context['name']}! आपका व्यवसाय क्या है?",
                    "english": f"Thank you {context['name']}! What's your occupation?",
                    "hinglish": f"Thank you {context['name']}! Aapka occupation kya hai?"
                }
                return responses.get(context["language"], responses["english"])
            
            # Occupation collection
            if context["conversation_state"] == "occupation_collection":
                occupation, location = self.parse_occupation_location(text)
                context["occupation"] = occupation
                context["location"] = location
                context["conversation_state"] = "scheme_queries"
                
                responses = {
                    "hindi": "समझ गया! अब आप सरकारी योजनाओं के बारे में पूछ सकते हैं।",
                    "english": "Got it! Now you can ask about government schemes.",
                    "hinglish": "Samjh gaya! Ab aap government schemes ke baare mein pooch sakte hain।"
                }
                return responses.get(context["language"], responses["english"])
            
            # Scheme queries
            if context["conversation_state"] == "scheme_queries":
                return await self.search_and_respond(client_id, text)
            
            # Default greeting
            if context["conversation_state"] == "greeting":
                context["conversation_state"] = "language_selection"
                return "Welcome! Please select language: Hindi, English, or Hinglish"
            
            return "I didn't understand. Please try again."
            
        except Exception as e:
            logger.error(f"Input processing error: {e}")
            return "Sorry, there was an error processing your request."
    
    def parse_occupation_location(self, text: str) -> tuple:
        """Parse occupation and location from text"""
        text_lower = text.lower()
        
        # Simple occupation detection
        occupations = {
            "farmer": ["farmer", "kisan", "किसान", "agriculture", "farming"],
            "fisherman": ["fisherman", "मछुआरा", "fishing", "marine"],
            "women": ["women", "महिला", "female", "woman"],
            "business": ["business", "व्यवसाय", "entrepreneur"],
            "student": ["student", "विद्यार्थी", "education"]
        }
        
        detected_occupation = "farmer"  # Default
        for occupation, keywords in occupations.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_occupation = occupation
                break
        
        # Simple location detection
        locations = ["gujarat", "गुजरात", "andhra", "आंध्र", "kerala", "केरल"]
        detected_location = None
        for location in locations:
            if location in text_lower:
                detected_location = location
                break
        
        return detected_occupation, detected_location
    
    async def search_and_respond(self, client_id: str, query: str) -> str:
        """Search schemes and generate response"""
        try:
            if not self.scheme_db:
                return "Database not available. Please try again later."
            
            context = self.get_user_context(client_id)
            
            # Search schemes
            schemes = self.scheme_db.search_by_context(
                query=query,
                occupation=context.get("occupation"),
                location=context.get("location"),
                top_k=3
            )
            
            if not schemes:
                responses = {
                    "hindi": "कोई संबंधित योजना नहीं मिली। कृपया अधिक विवरण दें।",
                    "english": "No relevant schemes found. Please provide more details.",
                    "hinglish": "Koi relevant scheme nahi mili। Please aur details dijiye।"
                }
                return responses.get(context["language"], responses["english"])
            
            # Format response
            scheme = schemes[0]
            name = scheme.get("Name", "Government Scheme")
            details = scheme.get("Details", "")
            
            # Create concise response for voice
            if len(details) > 150:
                details = details[:150] + "..."
            
            response = f"{name}. {details}"
            
            # Add language-specific formatting
            if context["language"] == "hindi":
                response = f"आपके लिए यह योजना है: {response}"
            elif context["language"] == "hinglish":
                response = f"Aapke liye yeh scheme hai: {response}"
            else:
                response = f"Here's a scheme for you: {response}"
            
            return response
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return "Sorry, there was an error searching for schemes."

# Initialize assistant
assistant = RealTimeVoiceAssistant()

@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    """Serve the main page"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: index.html not found in static folder</h1>")

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time voice communication"""
    await websocket.accept()
    client_id = f"client_{datetime.now().timestamp()}"
    
    logger.info(f"🔗 New client connected: {client_id}")
    
    try:
        # Send welcome message
        welcome_response = await assistant.text_to_speech(
            "Welcome to Government Schemes Voice Assistant! Please select your language.",
            "english"
        )
        
        await websocket.send_text(json.dumps({
            "type": "welcome",
            "text": "Welcome! Please select language: Hindi, English, or Hinglish",
            "audio": welcome_response
        }))
        
        # Main communication loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "audio":
                    # Process audio data
                    audio_data = base64.b64decode(message.get("data", ""))
                    response = await assistant.process_audio_chunk(client_id, audio_data)
                    await websocket.send_text(json.dumps(response))
                
                elif message.get("type") == "text":
                    # Process text input
                    text = message.get("text", "")
                    response_text = await assistant.process_user_input(client_id, text)
                    
                    context = assistant.get_user_context(client_id)
                    audio_response = await assistant.text_to_speech(response_text, context["language"])
                    
                    await websocket.send_text(json.dumps({
                        "type": "response",
                        "text": response_text,
                        "audio": audio_response,
                        "user_input": text
                    }))
                
                elif message.get("type") == "ping":
                    # Keep-alive ping
                    await websocket.send_text(json.dumps({"type": "pong"}))
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            
            except Exception as e:
                logger.error(f"Message processing error: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Error processing message"
                }))
    
    except WebSocketDisconnect:
        logger.info(f"🔌 Client disconnected: {client_id}")
        # Cleanup user context
        if client_id in assistant.user_contexts:
            del assistant.user_contexts[client_id]
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 Starting Real-time Voice Assistant Server...")
    print(f"🌐 Server will run on port: {port}")
    print("🎤 Real-time voice conversation enabled!")
    print("📱 Access via: http://localhost:8000")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )