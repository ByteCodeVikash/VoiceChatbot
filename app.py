import streamlit as st
import pandas as pd
import os
import time
import datetime
import json
import base64
from typing import Dict, List

# Set page config for voice interface
st.set_page_config(
    page_title="🎤 Voice Government Assistant",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Gemini-like interface
st.markdown("""
<style>
/* Hide default Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

/* Gemini-style interface */
.chat-container {
    max-width: 700px;
    margin: 0 auto;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    border-radius: 25px;
    padding: 2rem;
    color: white;
    min-height: 80vh;
}

.voice-status {
    background: rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 1.5rem;
    margin: 1rem 0;
    text-align: center;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
}

.bot-speaking {
    background: linear-gradient(45deg, #667eea, #764ba2);
    padding: 1.5rem;
    border-radius: 20px;
    margin: 1rem 0;
    animation: speaking 2s infinite;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

@keyframes speaking {
    0%, 100% { transform: scale(1); opacity: 0.9; }
    50% { transform: scale(1.02); opacity: 1; }
}

.user-listening {
    background: linear-gradient(45deg, #ff6b6b, #ee5a24);
    padding: 1.5rem;
    border-radius: 20px;
    margin: 1rem 0;
    animation: listening 1.5s infinite;
    box-shadow: 0 8px 32px rgba(255, 107, 107, 0.3);
}

@keyframes listening {
    0%, 100% { box-shadow: 0 8px 32px rgba(255, 107, 107, 0.3); }
    50% { box-shadow: 0 12px 40px rgba(255, 107, 107, 0.6); }
}

.voice-controls {
    text-align: center;
    margin: 2rem 0;
}

.big-voice-btn {
    background: linear-gradient(45deg, #00b894, #00cec9);
    color: white;
    border: none;
    padding: 1.5rem 3rem;
    border-radius: 50px;
    font-size: 1.3rem;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 8px 25px rgba(0, 184, 148, 0.4);
    margin: 0.5rem;
    min-width: 250px;
}

.big-voice-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(0, 184, 148, 0.6);
}

.conversation-step {
    background: rgba(255,255,255,0.1);
    padding: 1rem 1.5rem;
    border-radius: 15px;
    margin: 0.5rem 0;
    border-left: 4px solid #74b9ff;
    font-family: 'Arial', sans-serif;
}

.step-completed {
    border-left-color: #00b894;
    background: rgba(0, 184, 148, 0.1);
}

.assistant-avatar {
    width: 60px;
    height: 60px;
    background: linear-gradient(45deg, #667eea, #764ba2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin: 0 auto 1rem auto;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
}

.status-ready { background: #00b894; }
.status-speaking { background: #667eea; animation: pulse 1s infinite; }
.status-listening { background: #ff6b6b; animation: pulse 1s infinite; }

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.audio-visualizer {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 3px;
    margin: 1rem 0;
}

.audio-bar {
    width: 4px;
    height: 20px;
    background: #74b9ff;
    border-radius: 2px;
    animation: audioWave 1.5s infinite ease-in-out;
}

.audio-bar:nth-child(2) { animation-delay: 0.1s; }
.audio-bar:nth-child(3) { animation-delay: 0.2s; }
.audio-bar:nth-child(4) { animation-delay: 0.3s; }
.audio-bar:nth-child(5) { animation-delay: 0.4s; }

@keyframes audioWave {
    0%, 100% { height: 20px; }
    50% { height: 40px; }
}
</style>
""", unsafe_allow_html=True)

# Advanced Voice JavaScript
voice_js = """
<script>
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let currentStep = 'start';
let synth = window.speechSynthesis;
let currentLanguage = 'hinglish';

// Text-to-Speech function
function speakText(text, language = 'hi-IN') {
    return new Promise((resolve) => {
        // Stop any current speech
        synth.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Set language
        if (language === 'hi-IN' || language === 'hinglish') {
            utterance.lang = 'hi-IN';
            utterance.rate = 0.9;
        } else {
            utterance.lang = 'en-IN';
            utterance.rate = 0.9;
        }
        
        utterance.volume = 1;
        utterance.pitch = 1;
        
        utterance.onend = function() {
            resolve();
        };
        
        utterance.onerror = function() {
            resolve();
        };
        
        synth.speak(utterance);
    });
}

// Speech Recognition
async function listenForSpeech(timeout = 10000) {
    return new Promise(async (resolve) => {
        try {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                resolve('Mock: Kisan yojana batao');
                return;
            }
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            
            recognition.lang = currentLanguage === 'english' ? 'en-IN' : 'hi-IN';
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;
            
            let timeoutId = setTimeout(() => {
                recognition.stop();
                resolve('timeout');
            }, timeout);
            
            recognition.onresult = function(event) {
                clearTimeout(timeoutId);
                const transcript = event.results[0][0].transcript;
                resolve(transcript);
            };
            
            recognition.onerror = function(event) {
                clearTimeout(timeoutId);
                console.error('Speech recognition error:', event.error);
                resolve('Mock: Default response');
            };
            
            recognition.start();
            
        } catch (error) {
            console.error('Speech recognition failed:', error);
            resolve('Mock: Default response');
        }
    });
}

// Update UI status
function updateStatus(status, message) {
    const statusDiv = parent.document.getElementById('voice-status');
    if (statusDiv) {
        let statusClass = 'status-ready';
        if (status === 'speaking') statusClass = 'status-speaking';
        if (status === 'listening') statusClass = 'status-listening';
        
        statusDiv.innerHTML = `
            <span class="status-indicator ${statusClass}"></span>
            ${message}
        `;
    }
}

// Main conversation flow
async function startConversation() {
    console.log('Starting voice conversation...');
    
    // Welcome message
    updateStatus('speaking', '🤖 Assistant is speaking...');
    await speakText('नमस्कार! Government Schemes Voice Assistant में आपका स्वागत है।', 'hi-IN');
    
    // Language selection
    await speakText('कृपया अपनी भाषा चुनें। Hindi के लिए हिंदी कहें, English के लिए इंग्लिश कहें, या Hinglish के लिए हिंग्लिश कहें।', 'hi-IN');
    
    updateStatus('listening', '🎤 Listening for language choice...');
    const languageChoice = await listenForSpeech(8000);
    
    // Process language
    let selectedLanguage = 'hinglish';
    if (languageChoice.toLowerCase().includes('english') || languageChoice.toLowerCase().includes('अंग्रेजी')) {
        selectedLanguage = 'english';
    } else if (languageChoice.toLowerCase().includes('hindi') || languageChoice.toLowerCase().includes('हिंदी')) {
        selectedLanguage = 'hindi';
    }
    
    currentLanguage = selectedLanguage;
    
    // Confirm language
    const langConfirmations = {
        'english': 'You selected English. Let us continue.',
        'hindi': 'आपने हिंदी चुनी है। आगे बढ़ते हैं।',
        'hinglish': 'Aapne Hinglish select kiya है। Chaliye continue karte hain।'
    };
    
    updateStatus('speaking', '🤖 Assistant is speaking...');
    await speakText(langConfirmations[selectedLanguage]);
    
    // Get name
    const namePrompts = {
        'english': 'What is your name?',
        'hindi': 'आपका नाम क्या है?',
        'hinglish': 'Aapka naam kya hai?'
    };
    
    await speakText(namePrompts[selectedLanguage]);
    updateStatus('listening', '🎤 Listening for your name...');
    const userName = await listenForSpeech(8000);
    
    // Thank user
    const thankYouMessages = {
        'english': `Thank you, ${userName}।`,
        'hindi': `धन्यवाद, ${userName}।`,
        'hinglish': `Thank you, ${userName}।`
    };
    
    updateStatus('speaking', '🤖 Assistant is speaking...');
    await speakText(thankYouMessages[selectedLanguage]);
    
    // Get occupation
    const occupationPrompts = {
        'english': 'Tell me your occupation or location for better scheme suggestions.',
        'hindi': 'अपना व्यवसाय या स्थान बताएं ताकि मैं बेहतर योजनाएं सुझा सकूं।',
        'hinglish': 'Apna occupation ya location batayiye better schemes suggest karne ke liye।'
    };
    
    await speakText(occupationPrompts[selectedLanguage]);
    updateStatus('listening', '🎤 Listening for occupation/location...');
    const occupation = await listenForSpeech(10000);
    
    // Start main conversation
    const conversationPrompts = {
        'english': 'How can I help you with government schemes?',
        'hindi': 'मैं सरकारी योजनाओं के बारे में आपकी कैसे सहायता कर सकता हूँ?',
        'hinglish': 'Main government schemes ke baare mein aapki kaise help kar sakta hoon?'
    };
    
    updateStatus('speaking', '🤖 Assistant is speaking...');
    await speakText(conversationPrompts[selectedLanguage]);
    
    // Send data to Streamlit
    window.parent.postMessage({
        type: 'conversation_complete',
        data: {
            language: selectedLanguage,
            name: userName,
            occupation: occupation,
            step: 'main_conversation'
        }
    }, '*');
    
    // Start query loop
    await handleQueries(selectedLanguage, userName);
}

async function handleQueries(language, userName) {
    let queryCount = 0;
    const maxQueries = 5;
    
    while (queryCount < maxQueries) {
        updateStatus('listening', `🎤 Query ${queryCount + 1}/${maxQueries} - Listening...`);
        
        const query = await listenForSpeech(15000);
        
        if (query === 'timeout' || query.toLowerCase().includes('exit') || query.toLowerCase().includes('bye')) {
            break;
        }
        
        queryCount++;
        
        // Send query to Streamlit for processing
        window.parent.postMessage({
            type: 'process_query',
            data: {
                query: query,
                language: language,
                queryCount: queryCount
            }
        }, '*');
        
        // Wait for response
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Mock response for now
        const responses = {
            'english': `I found relevant schemes for your query: ${query}. Would you like more details?`,
            'hindi': `आपकी क्वेरी के लिए संबंधित योजनाएं मिलीं: ${query}। क्या आप और जानकारी चाहते हैं?`,
            'hinglish': `Aapki query ke liye relevant schemes mili: ${query}। Kya aap aur details chahte hain?`
        };
        
        updateStatus('speaking', '🤖 Assistant is responding...');
        await speakText(responses[language]);
    }
    
    // End conversation
    const endMessages = {
        'english': `Thank you for contacting us, ${userName}। Have a nice day!`,
        'hindi': `हमसे संपर्क करने के लिए धन्यवाद, ${userName}। आपका दिन शुभ हो!`,
        'hinglish': `Humse contact karne ke liye thank you, ${userName}। Aapka din shubh ho!`
    };
    
    updateStatus('speaking', '🤖 Assistant is speaking...');
    await speakText(endMessages[language]);
    
    updateStatus('ready', '✅ Conversation completed. Click Start to begin again.');
}

// Initialize
window.startVoiceAssistant = startConversation;
console.log('Gemini-style voice assistant loaded');
</script>
"""

# Initialize session state
if 'conversation_active' not in st.session_state:
    st.session_state.conversation_active = False
if 'conversation_data' not in st.session_state:
    st.session_state.conversation_data = {}
if 'conversation_log' not in st.session_state:
    st.session_state.conversation_log = []

# Load schemes data
@st.cache_data
def load_schemes_data():
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
                'Pradhan Mantri Mudra Yojana'
            ],
            'Department': ['Agriculture', 'Fisheries', 'Women Development', 'MSME'],
            'Details': [
                'Direct income support to farmers',
                'Fisheries development with financial assistance',
                'Women empowerment programs',
                'Micro finance for small businesses'
            ],
            'Benefits': [
                'Rs 6000 annual income support',
                'Subsidized equipment up to Rs 3 lakh',
                'Free skill training',
                'Collateral-free loans'
            ]
        })

schemes_data = load_schemes_data()

def search_schemes_voice(query, occupation=None):
    """Voice-optimized scheme search"""
    df = schemes_data
    
    # Simple keyword matching
    search_text = (
        df['Name'].fillna('').astype(str) + ' ' +
        df['Department'].fillna('').astype(str) + ' ' +
        df['Details'].fillna('').astype(str)
    ).str.lower()
    
    query_words = query.lower().split()
    mask = pd.Series([False] * len(df))
    
    for word in query_words:
        if len(word) > 2:
            mask |= search_text.str.contains(word, na=False, regex=False)
    
    results = df[mask].head(3)
    return results.to_dict('records') if not results.empty else []

# Main Interface
def main():
    st.markdown("""
    <div class="chat-container">
        <div class="assistant-avatar">🤖</div>
        <h1 style="text-align: center; margin-bottom: 2rem;">Voice Government Assistant</h1>
        <p style="text-align: center; font-size: 1.1rem; margin-bottom: 2rem; opacity: 0.9;">
            Gemini-style voice interaction for government schemes
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Voice status indicator
    st.markdown("""
    <div class="voice-status" id="voice-status">
        <span class="status-indicator status-ready"></span>
        Ready to start conversation
    </div>
    """, unsafe_allow_html=True)
    
    # Main voice controls
    if not st.session_state.conversation_active:
        st.markdown("""
        <div class="voice-controls">
            <h3>🎤 Click to Start Voice Conversation</h3>
            <p>The assistant will guide you through:</p>
            <div style="text-align: left; margin: 1rem 0; max-width: 400px; margin-left: auto; margin-right: auto;">
                <div class="conversation-step">1️⃣ Language Selection</div>
                <div class="conversation-step">2️⃣ Name Collection</div>
                <div class="conversation-step">3️⃣ Occupation/Location</div>
                <div class="conversation-step">4️⃣ Voice Queries (5 max)</div>
                <div class="conversation-step">5️⃣ Session End</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎤 Start Voice Assistant", key="start_voice", help="Click to begin voice conversation"):
            st.session_state.conversation_active = True
            st.markdown("""
            <div class="bot-speaking">
                <div class="audio-visualizer">
                    <div class="audio-bar"></div>
                    <div class="audio-bar"></div>
                    <div class="audio-bar"></div>
                    <div class="audio-bar"></div>
                    <div class="audio-bar"></div>
                </div>
                <h3>🤖 Voice Assistant is starting...</h3>
                <p>Please allow microphone access when prompted</p>
            </div>
            
            <script>
            setTimeout(() => {
                if (window.startVoiceAssistant) {
                    window.startVoiceAssistant();
                }
            }, 1000);
            </script>
            """, unsafe_allow_html=True)
            st.rerun()
    
    else:
        # Show active conversation
        st.markdown("""
        <div class="user-listening">
            <div class="audio-visualizer">
                <div class="audio-bar"></div>
                <div class="audio-bar"></div>
                <div class="audio-bar"></div>
                <div class="audio-bar"></div>
                <div class="audio-bar"></div>
            </div>
            <h3>🎤 Voice Conversation Active</h3>
            <p>Speaking with the voice assistant...</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show conversation progress
        if st.session_state.conversation_data:
            data = st.session_state.conversation_data
            st.markdown(f"""
            <div class="voice-status">
                <h4>📊 Conversation Progress</h4>
                <div class="conversation-step step-completed">✅ Language: {data.get('language', 'Not set').title()}</div>
                <div class="conversation-step step-completed">✅ Name: {data.get('name', 'Not provided')}</div>
                <div class="conversation-step step-completed">✅ Occupation: {data.get('occupation', 'Not specified')}</div>
                <div class="conversation-step">🔄 Processing queries...</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Reset button
        if st.button("🔄 Reset Conversation", key="reset_voice"):
            st.session_state.conversation_active = False
            st.session_state.conversation_data = {}
            st.session_state.conversation_log = []
            st.rerun()
    
    # Add JavaScript
    st.components.v1.html(voice_js, height=0)
    
    # Show conversation log if available
    if st.session_state.conversation_log:
        st.markdown("### 📝 Conversation Log")
        for log_entry in st.session_state.conversation_log:
            st.markdown(f"<div class='conversation-step'>{log_entry}</div>", unsafe_allow_html=True)

# Handle messages from JavaScript
if 'last_message' not in st.session_state:
    st.session_state.last_message = None

# Check for new messages (simplified)
# In production, use st.components.v1 bidirectional communication

if __name__ == "__main__":
    main()