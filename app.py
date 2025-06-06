import streamlit as st
import pandas as pd
import os
import time
import datetime
import logging
from typing import Dict, List, Any
import requests
import json

# Set page config
st.set_page_config(
    page_title="🎤 Voice Government Schemes Assistant",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide all default streamlit elements for clean voice interface
hide_default_format = """
<style>
#MainMenu {visibility: hidden; }
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}
.stDecoration {display:none;}

/* Voice interface styling */
.main-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    color: white;
}

.status-display {
    background: rgba(255,255,255,0.1);
    padding: 1.5rem;
    border-radius: 15px;
    margin: 1rem 0;
    border: 1px solid rgba(255,255,255,0.2);
    backdrop-filter: blur(10px);
}

.voice-controls {
    padding: 2rem;
    margin: 1rem 0;
}

.big-button {
    background: linear-gradient(45deg, #ff6b6b, #ee5a24);
    color: white;
    border: none;
    padding: 1.5rem 3rem;
    border-radius: 50px;
    font-size: 1.5rem;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
    margin: 0.5rem;
    min-width: 200px;
}

.big-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(255, 107, 107, 0.6);
}

.recording {
    animation: pulse 1.5s infinite;
    background: linear-gradient(45deg, #d63031, #e17055) !important;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.conversation-log {
    background: rgba(255,255,255,0.1);
    padding: 1rem;
    border-radius: 15px;
    margin: 1rem 0;
    text-align: left;
    max-height: 400px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    border: 1px solid rgba(255,255,255,0.2);
}

.step-indicator {
    background: linear-gradient(45deg, #74b9ff, #0984e3);
    padding: 1rem 2rem;
    border-radius: 25px;
    margin: 1rem 0;
    font-size: 1.2rem;
    font-weight: bold;
}

.error-message {
    background: linear-gradient(45deg, #d63031, #e17055);
    padding: 1rem;
    border-radius: 15px;
    margin: 1rem 0;
}

.success-message {
    background: linear-gradient(45deg, #00b894, #00cec9);
    padding: 1rem;
    border-radius: 15px;
    margin: 1rem 0;
}
</style>
"""

st.markdown(hide_default_format, unsafe_allow_html=True)

# JavaScript for voice recording
voice_js = """
<script>
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

window.startRecording = async function() {
    try {
        if (isRecording) return;
        
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = function(event) {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async function() {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            
            // Mock speech recognition for demo
            const transcript = await mockSpeechRecognition(audioBlob);
            
            // Send to Streamlit
            window.parent.postMessage({
                type: 'voice_input',
                text: transcript
            }, '*');
        };
        
        mediaRecorder.start();
        isRecording = true;
        
        // Update UI
        const btn = parent.document.querySelector('[data-testid="stButton"] button');
        if (btn && btn.textContent.includes('🎤 Start')) {
            btn.style.background = 'linear-gradient(45deg, #d63031, #e17055)';
            btn.textContent = '⏹️ Stop Recording';
            btn.classList.add('recording');
        }
        
        return true;
    } catch (err) {
        console.error('Microphone access denied:', err);
        alert('🎤 Please allow microphone access and try again.');
        return false;
    }
}

window.stopRecording = function() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        isRecording = false;
        
        // Update UI
        const btn = parent.document.querySelector('[data-testid="stButton"] button');
        if (btn) {
            btn.style.background = 'linear-gradient(45deg, #ff6b6b, #ee5a24)';
            btn.textContent = '🎤 Start Recording';
            btn.classList.remove('recording');
        }
    }
}

// Mock speech recognition (replace with real API)
async function mockSpeechRecognition(audioBlob) {
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock responses based on common queries
    const mockResponses = [
        "मुझे किसान योजना चाहिए",
        "farmer scheme batao",
        "women empowerment schemes",
        "fisherman yojana ke baare mein batao",
        "business loan scheme chahiye",
        "education scholarship",
        "kisan credit card",
        "हमें सरकारी योजना चाहिए"
    ];
    
    return mockResponses[Math.floor(Math.random() * mockResponses.length)];
}

// Listen for messages from Streamlit
window.addEventListener('message', function(event) {
    if (event.data.type === 'control_recording') {
        if (event.data.action === 'start') {
            startRecording();
        } else if (event.data.action === 'stop') {
            stopRecording();
        }
    }
});
</script>
"""

# Initialize session state - EXACT TERMINAL REPLICA
if 'conversation_state' not in st.session_state:
    st.session_state.conversation_state = 'language_selection'  # Exactly like terminal
if 'current_language' not in st.session_state:
    st.session_state.current_language = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'user_occupation' not in st.session_state:
    st.session_state.user_occupation = None
if 'user_location' not in st.session_state:
    st.session_state.user_location = None
if 'conversation_log' not in st.session_state:
    st.session_state.conversation_log = []
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'schemes_data' not in st.session_state:
    st.session_state.schemes_data = None
if 'conversation_count' not in st.session_state:
    st.session_state.conversation_count = 0

# Load CSV data (simplified)
@st.cache_data
def load_schemes_data():
    csv_path = "Government_schemes_final_english.csv"
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    else:
        # Demo data - exactly like terminal
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
                'Direct income support to farmers providing Rs 6000 per year in three installments',
                'Comprehensive development of fisheries sector with financial assistance for equipment',
                'Women empowerment through skill development and training programs at village level',
                'Micro finance scheme for small businesses providing collateral-free loans',
                'Scholarship schemes for students from economically weaker sections'
            ],
            'Benefits': [
                'Rs 6000 annual income support directly to bank account',
                'Subsidized boats, nets and fishing equipment up to Rs 3 lakh',
                'Free skill training and employment support for rural women',
                'Collateral-free loans up to Rs 10 lakh for business',
                'Educational scholarships and fee reimbursement'
            ],
            'Eligibility': [
                'Small and marginal farmers with land records',
                'Registered fishermen and fish farmers',
                'Women aged 18-65 from rural areas',
                'Non-defaulter individuals for business loans',
                'Students from economically weaker sections'
            ],
            'Document_Required': [
                'Aadhaar, Land records, Bank account details',
                'Fishing license, Aadhaar, Bank account',
                'Aadhaar, Age proof, Address proof',
                'Aadhaar, PAN, Business plan, Bank statement',
                'Income certificate, Aadhaar, Educational certificates'
            ],
            'Gender': ['All', 'All', 'Female', 'All', 'All'],
            'URL': ['pmkisan.gov.in', 'dof.gov.in', 'wcd.nic.in', 'mudra.org.in', 'scholarships.gov.in']
        })

# Load data
if st.session_state.schemes_data is None:
    st.session_state.schemes_data = load_schemes_data()

# Voice search function (simplified)
def search_schemes(query, occupation=None, location=None):
    """Simple voice-optimized search"""
    df = st.session_state.schemes_data
    
    # Voice query processing
    query_words = query.lower().split()
    
    # Create search mask
    search_text = (
        df['Name'].fillna('').astype(str) + ' ' +
        df['Department'].fillna('').astype(str) + ' ' +
        df['Details'].fillna('').astype(str) + ' ' +
        df['Benefits'].fillna('').astype(str)
    ).str.lower()
    
    mask = pd.Series([False] * len(df))
    
    # Search for keywords
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

# Generate response (voice-optimized)
def generate_voice_response(query, schemes, language):
    """Generate voice-appropriate response"""
    if not schemes:
        responses = {
            'english': f"I couldn't find specific schemes for '{query}'. Please try different keywords.",
            'hindi': f"'{query}' के लिए कोई विशेष योजना नहीं मिली। अलग keywords try करें।",
            'hinglish': f"'{query}' ke liye koi specific scheme nahi mili. Different keywords try kariye।"
        }
        return responses.get(language, responses['hinglish'])
    
    scheme = schemes[0]
    name = scheme['Name']
    benefits = scheme['Benefits'][:100]  # Keep short for voice
    
    responses = {
        'english': f"I found {len(schemes)} schemes. Main scheme is {name}. {benefits}",
        'hindi': f"मुझे {len(schemes)} योजनाएं मिलीं। मुख्य योजना है {name}। {benefits}",
        'hinglish': f"Mujhe {len(schemes)} schemes mili hain। Main scheme hai {name}। {benefits}"
    }
    
    return responses.get(language, responses['hinglish'])

# Text-to-speech function
def speak_text(text, language='hinglish'):
    """Convert text to speech URL"""
    try:
        # Use simple TTS service
        lang_code = 'hi' if language == 'hindi' else 'en'
        # For demo, return a placeholder URL
        # In production, integrate with Google TTS or similar
        tts_url = f"data:text/plain,Speaking: {text[:100]}..."
        return tts_url
    except:
        return ""

# Main app interface
def main():
    # Title
    st.markdown("""
    <div class="main-container">
        <h1>🎤 Voice Government Schemes Assistant</h1>
        <p style="font-size: 1.1rem; margin-bottom: 2rem;">
            Exact Terminal Experience - Voice Only Interface
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add JavaScript
    st.components.v1.html(voice_js, height=0)
    
    # State-based UI - EXACT TERMINAL FLOW
    if st.session_state.conversation_state == 'language_selection':
        show_language_selection()
    elif st.session_state.conversation_state == 'name_collection':
        show_name_collection()
    elif st.session_state.conversation_state == 'occupation_collection':
        show_occupation_collection()
    elif st.session_state.conversation_state == 'main_conversation':
        show_main_conversation()
    elif st.session_state.conversation_state == 'completed':
        show_completion()

def show_language_selection():
    """EXACT replica of terminal language selection"""
    st.markdown("""
    <div class="status-display">
        <h2>🌐 SELECT LANGUAGE / भाषा चुनें</h2>
        <p><strong>Step 1:</strong> Choose your preferred language</p>
        <div style="font-size: 1.1rem; margin: 1rem 0;">
            1️⃣ हिंदी (Hindi)<br>
            2️⃣ English<br>
            3️⃣ हिंग्लिश (Hinglish)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    show_voice_controls("Say your choice: Hindi, English, or Hinglish")
    
    # Language selection buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🇮🇳 हिंदी", key="lang_hindi", use_container_width=True):
            st.session_state.current_language = 'hindi'
            st.session_state.conversation_state = 'name_collection'
            st.session_state.conversation_log.append("✅ Selected: Hindi")
            st.rerun()
    
    with col2:
        if st.button("🇬🇧 English", key="lang_english", use_container_width=True):
            st.session_state.current_language = 'english'
            st.session_state.conversation_state = 'name_collection'
            st.session_state.conversation_log.append("✅ Selected: English")
            st.rerun()
    
    with col3:
        if st.button("🎭 Hinglish", key="lang_hinglish", use_container_width=True):
            st.session_state.current_language = 'hinglish'
            st.session_state.conversation_state = 'name_collection'
            st.session_state.conversation_log.append("✅ Selected: Hinglish")
            st.rerun()

def show_name_collection():
    """EXACT replica of terminal name collection"""
    prompts = {
        'hindi': "आपका नाम क्या है?",
        'english': "What's your name?",
        'hinglish': "Aapka naam kya hai?"
    }
    
    current_prompt = prompts[st.session_state.current_language]
    
    st.markdown(f"""
    <div class="status-display">
        <h2>👤 NAME COLLECTION</h2>
        <p><strong>Step 2:</strong> Please tell us your name</p>
        <div class="step-indicator">
            {current_prompt}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    show_voice_controls(current_prompt)
    
    # Manual input for demo
    col1, col2 = st.columns([3, 1])
    with col1:
        name_input = st.text_input("Or type your name:", key="name_input")
    with col2:
        if st.button("Submit", key="submit_name"):
            if name_input.strip():
                st.session_state.user_name = name_input.strip()
                st.session_state.conversation_state = 'occupation_collection'
                st.session_state.conversation_log.append(f"👤 Name: {name_input}")
                st.rerun()

def show_occupation_collection():
    """EXACT replica of terminal occupation collection"""
    prompts = {
        'hindi': "अपना व्यवसाय या स्थान बताएं (जैसे: मैं किसान हूँ, गुजरात से)",
        'english': "Tell me your occupation or location (e.g: I am farmer from Gujarat)",
        'hinglish': "Apna occupation ya location batayiye (jaise: main farmer hun, Gujarat se)"
    }
    
    current_prompt = prompts[st.session_state.current_language]
    
    st.markdown(f"""
    <div class="status-display">
        <h2>💼 OCCUPATION & LOCATION</h2>
        <p><strong>Step 3:</strong> Tell us about your occupation and location</p>
        <div class="step-indicator">
            {current_prompt}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    show_voice_controls(current_prompt)
    
    # Quick selection buttons
    st.markdown("**Quick Selection:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🌾 Farmer", key="occ_farmer"):
            st.session_state.user_occupation = 'farmer'
            process_occupation_selection()
    
    with col2:
        if st.button("🎣 Fisherman", key="occ_fisherman"):
            st.session_state.user_occupation = 'fisherman'
            process_occupation_selection()
    
    with col3:
        if st.button("👩 Women", key="occ_women"):
            st.session_state.user_occupation = 'women'
            process_occupation_selection()
    
    with col4:
        if st.button("💼 Business", key="occ_business"):
            st.session_state.user_occupation = 'business'
            process_occupation_selection()
    
    # Manual input
    col1, col2 = st.columns([3, 1])
    with col1:
        occupation_input = st.text_input("Or describe your occupation/location:", key="occupation_input")
    with col2:
        if st.button("Submit", key="submit_occupation"):
            if occupation_input.strip():
                # Simple parsing
                if any(word in occupation_input.lower() for word in ['farmer', 'kisan', 'खेती']):
                    st.session_state.user_occupation = 'farmer'
                elif any(word in occupation_input.lower() for word in ['fish', 'machhuara', 'मछली']):
                    st.session_state.user_occupation = 'fisherman'
                elif any(word in occupation_input.lower() for word in ['women', 'mahila', 'female']):
                    st.session_state.user_occupation = 'women'
                else:
                    st.session_state.user_occupation = 'general'
                
                process_occupation_selection()

def process_occupation_selection():
    """Process occupation selection and move to main conversation"""
    st.session_state.conversation_state = 'main_conversation'
    st.session_state.conversation_log.append(f"💼 Occupation: {st.session_state.user_occupation}")
    st.rerun()

def show_main_conversation():
    """EXACT replica of terminal main conversation"""
    query_prompts = {
        'hindi': "सरकारी योजनाओं के बारे में क्या जानना चाहते हैं?",
        'english': "What would you like to know about government schemes?",
        'hinglish': "Government schemes ke baare mein kya jaanna chahte hain?"
    }
    
    current_prompt = query_prompts[st.session_state.current_language]
    
    # Show user info - exactly like terminal
    st.markdown(f"""
    <div class="status-display">
        <h2>💬 CONVERSATION WITH {st.session_state.user_name.upper()}</h2>
        <p><strong>Language:</strong> {st.session_state.current_language.title()}</p>
        <p><strong>Occupation:</strong> {st.session_state.user_occupation or 'Not specified'}</p>
        <p><strong>Query Count:</strong> {st.session_state.conversation_count}/5</p>
        <hr>
        <div class="step-indicator">
            Query {st.session_state.conversation_count + 1}: {current_prompt}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.conversation_count < 5:
        show_voice_controls(current_prompt)
        
        # Quick query buttons
        st.markdown("**Quick Queries:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🌾 Farmer Schemes", key="query_farmer"):
                process_voice_query("farmer schemes")
        
        with col2:
            if st.button("👩 Women Schemes", key="query_women"):
                process_voice_query("women empowerment schemes")
        
        with col3:
            if st.button("💼 Business Loans", key="query_business"):
                process_voice_query("business loan schemes")
        
        # Manual query input
        col1, col2 = st.columns([3, 1])
        with col1:
            query_input = st.text_input("Or type your question:", key="query_input")
        with col2:
            if st.button("Ask", key="submit_query"):
                if query_input.strip():
                    process_voice_query(query_input.strip())
        
        # End conversation button
        if st.button("🔚 End Conversation", key="end_conversation"):
            st.session_state.conversation_state = 'completed'
            st.rerun()
    else:
        st.markdown("""
        <div class="success-message">
            <h3>✅ Maximum 5 queries completed!</h3>
            <p>Thank you for using the Voice Government Schemes Assistant.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔚 End Session", key="end_session"):
            st.session_state.conversation_state = 'completed'
            st.rerun()

def process_voice_query(query):
    """Process voice query - exactly like terminal"""
    st.session_state.conversation_count += 1
    
    # Log the query
    st.session_state.conversation_log.append(f"🗣️ Query {st.session_state.conversation_count}: {query}")
    
    # Search schemes
    schemes = search_schemes(query, st.session_state.user_occupation)
    
    # Generate response
    response = generate_voice_response(query, schemes, st.session_state.current_language)
    
    # Log the response
    st.session_state.conversation_log.append(f"🤖 Response: {response}")
    
    # Show found schemes
    if schemes:
        st.session_state.conversation_log.append(f"📋 Found {len(schemes)} schemes:")
        for i, scheme in enumerate(schemes, 1):
            st.session_state.conversation_log.append(f"  {i}. {scheme['Name']}")
    
    st.rerun()

def show_completion():
    """Show completion screen"""
    st.markdown(f"""
    <div class="success-message">
        <h2>🎉 Session Completed!</h2>
        <p>Thank you <strong>{st.session_state.user_name}</strong> for using our Voice Assistant.</p>
        <p>Language: {st.session_state.current_language.title()}</p>
        <p>Queries Processed: {st.session_state.conversation_count}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Start New Session", key="restart"):
        # Reset all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def show_voice_controls(prompt):
    """Show voice control interface"""
    st.markdown(f"""
    <div class="voice-controls">
        <p style="margin-bottom: 1rem;"><strong>🎤 Voice Prompt:</strong> {prompt}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎤 Start Recording", key=f"start_record_{st.session_state.conversation_state}", use_container_width=True):
            st.session_state.recording = True
            st.info("🔴 Recording... Speak now! (Click Stop when finished)")
    
    with col2:
        if st.button("⏹️ Stop Recording", key=f"stop_record_{st.session_state.conversation_state}", use_container_width=True):
            st.session_state.recording = False
            st.success("✅ Recording stopped. Processing...")

# Show conversation log (exactly like terminal)
if st.session_state.conversation_log:
    st.markdown("### 📊 Conversation Log")
    st.markdown("""
    <div class="conversation-log">
    """ + "<br>".join(st.session_state.conversation_log) + """
    </div>
    """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()