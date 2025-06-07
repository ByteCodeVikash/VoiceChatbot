import os
import sys
import logging
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import tempfile
import base64
import io
import json
import traceback
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your existing modules
try:
    from voice_assistant import EnhancedVoiceAssistant
    from config import CONFIG, PHRASES
    print("✅ Successfully imported voice assistant modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all your files are in the same directory")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

# Global assistant instance
assistant = None
assistant_ready = False

def initialize_assistant():
    """Initialize the voice assistant"""
    global assistant, assistant_ready
    
    try:
        print("🤖 Initializing Enhanced Voice Assistant...")
        
        # Create assistant instance
        assistant = EnhancedVoiceAssistant()
        
        # Set default language
        assistant.current_language = "english"
        assistant.user_name = "User"
        assistant.name_collected = True
        
        # Test the assistant components
        if hasattr(assistant, 'scheme_db') and assistant.scheme_db:
            total_schemes = assistant.scheme_db.get_scheme_count()
            print(f"📊 Database loaded with {total_schemes} schemes")
        else:
            print("⚠️ Database not fully initialized")
        
        assistant_ready = True
        print("✅ Voice Assistant initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Assistant initialization failed: {e}")
        traceback.print_exc()
        assistant_ready = False
        return False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "assistant_ready": assistant_ready,
        "assistant_available": assistant is not None
    }

@app.route('/test')
def test():
    """Test endpoint"""
    return {
        "message": "Voice Assistant API is running!",
        "assistant_status": "Ready" if assistant_ready else "Not Ready"
    }

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'🔗 Client connected: {request.sid}')
    
    # Send welcome message
    emit('status', {
        'type': 'connection',
        'message': 'Connected to Government Schemes Voice Assistant!',
        'assistant_ready': assistant_ready
    })
    
    # Send welcome message from assistant
    if assistant_ready:
        welcome_msg = "Namaste! Main aapki government schemes mein madad kar sakta hun। Aap Hindi, English ya Hinglish mein baat kar sakte hain।"
        emit('bot_response', {
            'text': welcome_msg,
            'type': 'welcome',
            'timestamp': datetime.now().isoformat()
        })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'❌ Client disconnected: {request.sid}')

@socketio.on('set_language')
def handle_language_change(data):
    """Handle language change"""
    global assistant
    
    try:
        language = data.get('language', 'english')
        
        if assistant and assistant_ready:
            assistant.current_language = language
            
            # Send confirmation in selected language
            confirmations = {
                'hindi': 'आपकी भाषा हिंदी में बदल गई है।',
                'english': 'Language changed to English.',
                'hinglish': 'Language Hinglish mein change ho gayi hai।'
            }
            
            emit('bot_response', {
                'text': confirmations.get(language, confirmations['english']),
                'type': 'language_change'
            })
            
            print(f"🌐 Language changed to: {language}")
        
    except Exception as e:
        print(f"Error changing language: {e}")
        emit('error', {'message': f'Language change error: {str(e)}'})

@socketio.on('set_user_context')
def handle_user_context(data):
    """Handle user context (name, occupation, location)"""
    global assistant
    
    try:
        if assistant and assistant_ready:
            name = data.get('name', 'User')
            occupation = data.get('occupation', '')
            location = data.get('location', '')
            
            # Update assistant context
            assistant.user_name = name
            assistant.user_context.update({
                'name': name,
                'occupation': occupation if occupation else None,
                'location': location if location else None
            })
            
            # Parse occupation and location if provided as text
            if occupation:
                parsed_occ, parsed_loc = assistant.parse_user_occupation(occupation)
                if parsed_occ:
                    assistant.user_context['occupation'] = parsed_occ
                if parsed_loc and not location:
                    assistant.user_context['location'] = parsed_loc
            
            response_parts = [f"Dhanyawad {name}!"]
            
            if assistant.user_context.get('occupation'):
                response_parts.append(f"Aap {assistant.user_context['occupation']} hain।")
            
            if assistant.user_context.get('location'):
                response_parts.append(f"Location: {assistant.user_context['location']}।")
            
            response_parts.append("Main aapko relevant schemes suggest kar sakta hun।")
            
            emit('bot_response', {
                'text': ' '.join(response_parts),
                'type': 'context_update'
            })
            
            print(f"👤 User context updated: {assistant.user_context}")
        
    except Exception as e:
        print(f"Error updating user context: {e}")
        emit('error', {'message': f'Context update error: {str(e)}'})

@socketio.on('text_message')
def handle_text_message(data):
    """Handle text message from user"""
    global assistant
    
    if not assistant_ready or not assistant:
        emit('error', {'message': 'Assistant not ready. Please refresh the page.'})
        return
    
    try:
        query = data.get('message', '').strip()
        language = data.get('language', assistant.current_language if assistant else 'english')
        
        if not query:
            emit('error', {'message': 'Empty message received'})
            return
        
        print(f"🗣️ Processing query: '{query}' (Language: {language})")
        
        # Update assistant language
        assistant.current_language = language
        
        # Handle special commands
        if query.lower() in ['exit', 'quit', 'bye', 'band karo', 'khatam']:
            goodbye_messages = {
                'hindi': 'धन्यवाद! आपका दिन शुभ हो!',
                'english': 'Thank you! Have a great day!',
                'hinglish': 'Thank you! Aapka din shubh ho!'
            }
            
            emit('bot_response', {
                'text': goodbye_messages.get(language, goodbye_messages['english']),
                'type': 'goodbye'
            })
            return
        
        # Use your existing scheme search logic
        print(f"🔍 Searching schemes for: {query}")
        
        # Get user context
        occupation = assistant.user_context.get('occupation')
        location = assistant.user_context.get('location')
        
        print(f"👤 User context - Occupation: {occupation}, Location: {location}")
        
        # Find relevant schemes using your existing logic
        relevant_schemes = assistant.find_relevant_schemes(query, top_n=5)
        
        if relevant_schemes:
            print(f"✅ Found {len(relevant_schemes)} relevant schemes")
            
            # Log found schemes
            for i, scheme in enumerate(relevant_schemes[:3], 1):
                scheme_name = scheme.get('Name', 'Unknown')[:50]
                print(f"  {i}. {scheme_name}...")
            
            # Format response using your existing logic
            response = assistant.format_scheme_response(relevant_schemes, query, language)
            
            # Also send structured scheme data
            schemes_data = []
            for scheme in relevant_schemes[:3]:  # Top 3 schemes
                schemes_data.append({
                    'name': scheme.get('Name', 'Unknown'),
                    'department': scheme.get('Department', 'N/A'),
                    'benefits': scheme.get('Benefits', 'N/A')[:200],
                    'eligibility': scheme.get('Eligibility', 'N/A')[:200],
                    'score': scheme.get('Score', 0)
                })
            
            emit('bot_response', {
                'text': response,
                'type': 'scheme_response',
                'schemes': schemes_data,
                'query': query,
                'timestamp': datetime.now().isoformat()
            })
            
        else:
            print("❌ No schemes found")
            
            # No schemes found response
            no_scheme_messages = {
                'hindi': f"'{query}' के लिए कोई योजना नहीं मिली। कृपया अधिक विवरण दें या अलग तरीके से पूछें।",
                'english': f"No schemes found for '{query}'. Please provide more details or try asking differently.",
                'hinglish': f"'{query}' ke liye koi scheme nahi mili। Please aur details dijiye ya different way mein puchiye।"
            }
            
            emit('bot_response', {
                'text': no_scheme_messages.get(language, no_scheme_messages['english']),
                'type': 'no_results',
                'query': query
            })
    
    except Exception as e:
        error_msg = f"Processing error: {str(e)}"
        print(f"❌ Error processing message: {e}")
        traceback.print_exc()
        
        emit('error', {
            'message': error_msg,
            'type': 'processing_error'
        })

@socketio.on('get_assistant_status')
def handle_status_request():
    """Get assistant status"""
    status = {
        'ready': assistant_ready,
        'available': assistant is not None,
        'language': assistant.current_language if assistant else 'english',
        'user_context': assistant.user_context if assistant else {}
    }
    
    emit('assistant_status', status)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@socketio.on_error_default
def default_error_handler(e):
    print(f"SocketIO Error: {e}")
    emit('error', {'message': 'Connection error occurred'})

if __name__ == '__main__':
    print("🚀 Starting Government Schemes Voice Assistant Server...")
    
    # Initialize assistant
    init_success = initialize_assistant()
    
    if not init_success:
        print("⚠️ Assistant initialization failed, but server will still run")
    
    # Get port from environment (Railway sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🌐 Server starting on port {port}")
    print(f"🤖 Assistant ready: {assistant_ready}")
    
    # Run the app
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port, 
        debug=False,  # Set to False for production
        allow_unsafe_werkzeug=True
    )