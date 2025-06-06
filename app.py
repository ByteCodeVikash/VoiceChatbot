# app.py - Perfect Voice Assistant with Gradio
import gradio as gr
import pandas as pd
import os
import time
import json
from typing import List, Dict, Tuple, Optional
import requests
from gtts import gTTS
import tempfile
import io
import speech_recognition as sr
from pydub import AudioSegment
import numpy as np

# Configuration
class VoiceConfig:
    def __init__(self):
        self.current_language = "hinglish"
        self.user_name = ""
        self.user_occupation = ""
        self.conversation_step = "start"
        self.query_count = 0
        self.max_queries = 5
        self.conversation_log = []
        
        # Load schemes data
        self.schemes_data = self.load_schemes_data()
    
    def load_schemes_data(self):
        """Load CSV data"""
        csv_path = "Government_schemes_final_english.csv"
        if os.path.exists(csv_path):
            return pd.read_csv(csv_path)
        else:
            # Demo data
            return pd.DataFrame({
                'Name': [
                    'PM-KISAN Samman Nidhi Yojana',
                    'Pradhan Mantri Matsya Sampada Yojana',
                    'Mahila Shakti Kendra Scheme',
                    'Pradhan Mantri Mudra Yojana',
                    'National Scholarship Portal'
                ],
                'Department': ['Agriculture', 'Fisheries', 'Women Development', 'MSME', 'Education'],
                'Details': [
                    'Direct income support to farmers providing Rs 6000 per year',
                    'Comprehensive development of fisheries sector with financial assistance',
                    'Women empowerment through skill development and training programs',
                    'Micro finance scheme for small businesses providing collateral-free loans',
                    'Educational scholarships for students from economically weaker sections'
                ],
                'Benefits': [
                    'Rs 6000 annual income support directly to bank account',
                    'Subsidized boats and equipment up to Rs 3 lakh',
                    'Free skill training and employment support',
                    'Collateral-free loans up to Rs 10 lakh',
                    'Educational scholarships and fee reimbursement'
                ],
                'Eligibility': [
                    'Small and marginal farmers with land records',
                    'Registered fishermen and fish farmers',
                    'Women aged 18-65 from rural areas',
                    'Non-defaulter individuals for business loans',
                    'Students from economically weaker sections'
                ]
            })

# Global config
config = VoiceConfig()

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
    def text_to_speech(self, text: str, language: str = "hi") -> str:
        """Convert text to speech and return audio file path"""
        try:
            # Language mapping
            lang_code = "hi" if language in ["hindi", "hinglish"] else "en"
            
            # Create TTS
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_file.name)
            
            return temp_file.name
            
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
    
    def speech_to_text(self, audio_path: str) -> str:
        """Convert speech to text"""
        try:
            # Load audio
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
            
            # Recognize speech
            text = self.recognizer.recognize_google(
                audio, 
                language="hi-IN"  # Support both Hindi and English
            )
            
            return text.strip()
            
        except sr.UnknownValueError:
            return "समझ नहीं आया, कृपया फिर से कहें"
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return "आवाज़ साफ नहीं है"
        except Exception as e:
            print(f"Audio processing error: {e}")
            return "ऑडियो प्रोसेसिंग में समस्या"
    
    def search_schemes(self, query: str, occupation: str = None) -> List[Dict]:
        """Search schemes based on voice query"""
        df = config.schemes_data
        
        # Process query
        query_words = query.lower().split()
        
        # Create search text
        search_text = (
            df['Name'].fillna('').astype(str) + ' ' +
            df['Department'].fillna('').astype(str) + ' ' +
            df['Details'].fillna('').astype(str) + ' ' +
            df['Benefits'].fillna('').astype(str)
        ).str.lower()
        
        # Search
        mask = pd.Series([False] * len(df))
        for word in query_words:
            if len(word) > 2:
                mask |= search_text.str.contains(word, na=False, regex=False)
        
        # Occupation filter
        if occupation:
            occ_keywords = {
                'farmer': ['farmer', 'agriculture', 'farming', 'kisan'],
                'fisherman': ['fish', 'marine', 'boat', 'matsya'],
                'women': ['women', 'woman', 'female', 'mahila'],
                'business': ['business', 'entrepreneur', 'mudra'],
                'student': ['education', 'scholarship', 'student']
            }
            
            if occupation in occ_keywords:
                occ_mask = pd.Series([False] * len(df))
                for keyword in occ_keywords[occupation]:
                    occ_mask |= search_text.str.contains(keyword, na=False, regex=False)
                mask &= occ_mask
        
        results = df[mask].head(3)
        return results.to_dict('records') if not results.empty else []

# Initialize assistant
assistant = VoiceAssistant()

def start_conversation() -> Tuple[str, str]:
    """Start the voice conversation"""
    global config
    
    # Reset config
    config.conversation_step = "language_selection"
    config.query_count = 0
    config.conversation_log = []
    
    # Welcome message
    welcome_text = "नमस्कार! Government Schemes Voice Assistant में आपका स्वागत है। कृपया अपनी भाषा चुनें - Hindi, English, या Hinglish?"
    
    # Generate audio
    audio_path = assistant.text_to_speech(welcome_text, "hi")
    
    return welcome_text, audio_path

def process_language_selection(audio_input) -> Tuple[str, str]:
    """Process language selection from voice"""
    global config
    
    if audio_input is None:
        return "कृपया आवाज़ में अपनी भाषा बताएं", None
    
    # Convert speech to text
    recognized_text = assistant.speech_to_text(audio_input)
    print(f"Language selection heard: {recognized_text}")
    
    # Process language choice
    text_lower = recognized_text.lower()
    
    if any(word in text_lower for word in ["english", "अंग्रेजी", "इंग्लिश"]):
        config.current_language = "english"
        response = "You selected English. Let's continue."
    elif any(word in text_lower for word in ["hindi", "हिंदी"]):
        config.current_language = "hindi"
        response = "आपने हिंदी चुनी है। आगे बढ़ते हैं।"
    else:
        config.current_language = "hinglish"
        response = "Aapne Hinglish select kiya है। Chaliye continue karte hain।"
    
    # Move to next step
    config.conversation_step = "name_collection"
    
    # Ask for name
    name_prompts = {
        "english": "What is your name?",
        "hindi": "आपका नाम क्या है?",
        "hinglish": "Aapka naam kya hai?"
    }
    
    full_response = response + " " + name_prompts[config.current_language]
    audio_path = assistant.text_to_speech(full_response, config.current_language)
    
    return full_response, audio_path

def process_name_collection(audio_input) -> Tuple[str, str]:
    """Process name collection from voice"""
    global config
    
    if audio_input is None:
        return "कृपया अपना नाम बताएं", None
    
    # Convert speech to text
    recognized_name = assistant.speech_to_text(audio_input)
    config.user_name = recognized_name
    
    print(f"Name collected: {recognized_name}")
    
    # Thank user and ask for occupation
    thank_you_templates = {
        "english": f"Thank you, {recognized_name}. Tell me your occupation or location for better scheme suggestions.",
        "hindi": f"धन्यवाद, {recognized_name}। अपना व्यवसाय या स्थान बताएं ताकि मैं बेहतर योजनाएं सुझा सकूं।",
        "hinglish": f"Thank you, {recognized_name}। Apna occupation ya location batayiye better schemes suggest karne ke liye।"
    }
    
    config.conversation_step = "occupation_collection"
    response = thank_you_templates[config.current_language]
    audio_path = assistant.text_to_speech(response, config.current_language)
    
    return response, audio_path

def process_occupation_collection(audio_input) -> Tuple[str, str]:
    """Process occupation collection from voice"""
    global config
    
    if audio_input is None:
        return "कृपया अपना व्यवसाय बताएं", None
    
    # Convert speech to text
    recognized_occupation = assistant.speech_to_text(audio_input)
    
    # Parse occupation
    text_lower = recognized_occupation.lower()
    if any(word in text_lower for word in ["farmer", "kisan", "किसान", "खेती"]):
        config.user_occupation = "farmer"
    elif any(word in text_lower for word in ["fish", "machhuara", "मछुआरा"]):
        config.user_occupation = "fisherman"
    elif any(word in text_lower for word in ["women", "mahila", "महिला"]):
        config.user_occupation = "women"
    elif any(word in text_lower for word in ["business", "व्यापार"]):
        config.user_occupation = "business"
    else:
        config.user_occupation = "general"
    
    print(f"Occupation: {config.user_occupation}")
    
    # Start main conversation
    query_prompts = {
        "english": "How can I help you with government schemes?",
        "hindi": "मैं सरकारी योजनाओं के बारे में आपकी कैसे सहायता कर सकता हूँ?",
        "hinglish": "Main government schemes ke baare mein aapki kaise help kar sakta hoon?"
    }
    
    config.conversation_step = "main_conversation"
    response = query_prompts[config.current_language]
    audio_path = assistant.text_to_speech(response, config.current_language)
    
    return response, audio_path

def process_main_query(audio_input) -> Tuple[str, str]:
    """Process main conversation queries"""
    global config
    
    if audio_input is None:
        return "कृपया अपना सवाल पूछें", None
    
    if config.query_count >= config.max_queries:
        # End conversation
        end_messages = {
            "english": f"Thank you for contacting us, {config.user_name}. Have a nice day!",
            "hindi": f"हमसे संपर्क करने के लिए धन्यवाद, {config.user_name}। आपका दिन शुभ हो!",
            "hinglish": f"Humse contact karne ke liye thank you, {config.user_name}। Aapka din shubh ho!"
        }
        
        config.conversation_step = "completed"
        response = end_messages[config.current_language]
        audio_path = assistant.text_to_speech(response, config.current_language)
        return response, audio_path
    
    # Convert speech to text
    query = assistant.speech_to_text(audio_input)
    config.query_count += 1
    
    print(f"Query {config.query_count}: {query}")
    
    # Search schemes
    schemes = assistant.search_schemes(query, config.user_occupation)
    
    # Generate response
    if schemes:
        scheme = schemes[0]
        response_templates = {
            "english": f"I found {len(schemes)} relevant schemes. The main scheme is {scheme['Name']}. {scheme['Benefits'][:100]}",
            "hindi": f"मुझे {len(schemes)} संबंधित योजनाएं मिलीं। मुख्य योजना है {scheme['Name']}। {scheme['Benefits'][:100]}",
            "hinglish": f"Mujhe {len(schemes)} relevant schemes mili। Main scheme hai {scheme['Name']}। {scheme['Benefits'][:100]}"
        }
    else:
        response_templates = {
            "english": "I couldn't find specific schemes for your query. Please try different keywords.",
            "hindi": "आपकी क्वेरी के लिए कोई विशेष योजना नहीं मिली। कृपया अलग keywords try करें।",
            "hinglish": "Aapki query ke liye koi specific scheme nahi mili। Different keywords try kariye।"
        }
    
    response = response_templates[config.current_language]
    
    # Add query continuation
    if config.query_count < config.max_queries:
        continue_prompts = {
            "english": " Any other questions?",
            "hindi": " कोई और सवाल?",
            "hinglish": " Aur koi question?"
        }
        response += continue_prompts[config.current_language]
    
    audio_path = assistant.text_to_speech(response, config.current_language)
    return response, audio_path

def handle_voice_input(audio_input) -> Tuple[str, str]:
    """Main voice input handler"""
    global config
    
    if config.conversation_step == "start":
        return start_conversation()
    elif config.conversation_step == "language_selection":
        return process_language_selection(audio_input)
    elif config.conversation_step == "name_collection":
        return process_name_collection(audio_input)
    elif config.conversation_step == "occupation_collection":
        return process_occupation_collection(audio_input)
    elif config.conversation_step == "main_conversation":
        return process_main_query(audio_input)
    elif config.conversation_step == "completed":
        return "Conversation completed. Please restart to begin again.", None
    else:
        return "Something went wrong. Please restart.", None

def reset_conversation():
    """Reset conversation state"""
    global config
    config.conversation_step = "start"
    config.query_count = 0
    config.user_name = ""
    config.user_occupation = ""
    config.conversation_log = []
    return "Conversation reset. Click 'Start Voice Assistant' to begin.", None

# Create Gradio Interface
def create_interface():
    """Create the Gradio voice interface"""
    
    with gr.Blocks(
        title="🎤 Voice Government Schemes Assistant",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .voice-container {
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem 0;
            backdrop-filter: blur(10px);
        }
        """
    ) as demo:
        
        gr.HTML("""
        <div style="text-align: center; padding: 2rem; color: white;">
            <h1>🎤 Voice Government Schemes Assistant</h1>
            <p style="font-size: 1.2rem;">Complete Voice-to-Voice Conversation Experience</p>
            <p>🗣️ Bot will speak first → 👂 You respond with voice → 🔄 Natural conversation</p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                # Voice input
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="🎤 Click to Record Your Response",
                    interactive=True
                )
                
                # Control buttons
                start_btn = gr.Button("🎤 Start Voice Assistant", variant="primary", size="lg")
                reset_btn = gr.Button("🔄 Reset Conversation", variant="secondary")
                
            with gr.Column(scale=1):
                # Bot response (text)
                response_text = gr.Textbox(
                    label="🤖 Assistant Response",
                    interactive=False,
                    lines=4
                )
                
                # Bot response (audio)
                response_audio = gr.Audio(
                    label="🔊 Assistant Voice",
                    interactive=False,
                    autoplay=True  # Important: Auto-play bot response
                )
                
                # Conversation status
                status_display = gr.HTML("""
                <div class="voice-container">
                    <h3>📊 Conversation Status</h3>
                    <p>🔵 Ready to start</p>
                    <ol>
                        <li>Language Selection</li>
                        <li>Name Collection</li>
                        <li>Occupation/Location</li>
                        <li>Voice Queries (5 max)</li>
                        <li>Session End</li>
                    </ol>
                </div>
                """)
        
        # Event handlers
        start_btn.click(
            fn=start_conversation,
            outputs=[response_text, response_audio]
        )
        
        audio_input.change(
            fn=handle_voice_input,
            inputs=[audio_input],
            outputs=[response_text, response_audio]
        )
        
        reset_btn.click(
            fn=reset_conversation,
            outputs=[response_text, response_audio]
        )
        
        gr.HTML("""
        <div style="text-align: center; padding: 1rem; color: white; opacity: 0.8;">
            <p>🎯 Perfect Voice Experience: Bot speaks first, you respond, natural conversation flow!</p>
        </div>
        """)
    
    return demo

# Launch the app
if __name__ == "__main__":
    # Create and launch interface
    demo = create_interface()
    
    # Launch with specific settings for voice
    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=True,  # Create public link
        inbrowser=True,  # Auto-open browser
        show_error=True
    )