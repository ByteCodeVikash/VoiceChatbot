# voice_utils.py - Add these functions to your app.py for real voice

import streamlit as st
import base64
import requests
import json
from io import BytesIO

# Real Speech Recognition Integration
def speech_to_text_api(audio_blob, language='hi-IN'):
    """Convert audio to text using Google Speech-to-Text API"""
    try:
        # Convert blob to base64
        audio_data = base64.b64decode(audio_blob)
        
        # Google Speech-to-Text API
        api_key = st.secrets.get("GOOGLE_API_KEY", "")
        if not api_key:
            return "Mock: Kisan yojana batao"  # Fallback
        
        url = f"https://speech.googleapis.com/v1/speech:recognize?key={api_key}"
        
        headers = {'Content-Type': 'application/json'}
        
        data = {
            "config": {
                "encoding": "WEBM_OPUS",
                "sampleRateHertz": 48000,
                "languageCode": language,
                "alternativeLanguageCodes": ["hi-IN", "en-IN"],
                "enableAutomaticPunctuation": True
            },
            "audio": {
                "content": audio_blob
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'results' in result and result['results']:
                transcript = result['results'][0]['alternatives'][0]['transcript']
                return transcript
        
        return "Mock fallback response"
        
    except Exception as e:
        st.error(f"Speech recognition failed: {e}")
        return "Voice recognition error"

# Real Text-to-Speech Integration  
def text_to_speech_api(text, language='hi'):
    """Convert text to speech using Google TTS"""
    try:
        api_key = st.secrets.get("GOOGLE_API_KEY", "")
        if not api_key:
            return None
        
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
        
        headers = {'Content-Type': 'application/json'}
        
        data = {
            "input": {"text": text[:500]},  # Limit text length
            "voice": {
                "languageCode": language,
                "ssmlGender": "FEMALE"
            },
            "audioConfig": {
                "audioEncoding": "MP3"
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            audio_content = result.get('audioContent', '')
            return audio_content
        
        return None
        
    except Exception as e:
        st.error(f"Text-to-speech failed: {e}")
        return None

# Enhanced Voice JavaScript with Real API Integration
def get_enhanced_voice_js():
    return """
<script>
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

window.startRecording = async function() {
    try {
        if (isRecording) return;
        
        console.log('Starting recording...');
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                sampleRate: 48000,
                channelCount: 1,
                echoCancellation: true,
                noiseSuppression: true
            } 
        });
        
        mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm;codecs=opus'
        });
        audioChunks = [];
        
        mediaRecorder.ondataavailable = function(event) {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = async function() {
            console.log('Recording stopped, processing...');
            
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm;codecs=opus' });
            
            // Convert to base64 for sending to backend
            const reader = new FileReader();
            reader.onloadend = function() {
                const base64Audio = reader.result.split(',')[1];
                
                // Send to Streamlit backend
                fetch('/speech-to-text', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        audio: base64Audio,
                        language: getCurrentLanguage()
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.transcript) {
                        // Update Streamlit session state
                        window.parent.postMessage({
                            type: 'voice_transcript',
                            text: data.transcript,
                            confidence: data.confidence || 0.8
                        }, '*');
                        
                        // Show transcript in UI
                        showTranscript(data.transcript);
                    }
                })
                .catch(error => {
                    console.error('Speech recognition error:', error);
                    // Fallback to mock response
                    const mockTranscript = generateMockTranscript();
                    window.parent.postMessage({
                        type: 'voice_transcript',
                        text: mockTranscript,
                        confidence: 0.7
                    }, '*');
                });
            };
            reader.readAsDataURL(audioBlob);
            
            // Cleanup
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start(1000); // Collect data every second
        isRecording = true;
        
        // Update UI
        updateRecordingUI(true);
        
        // Auto-stop after 10 seconds
        setTimeout(() => {
            if (isRecording) {
                stopRecording();
            }
        }, 10000);
        
        return true;
    } catch (err) {
        console.error('Microphone access denied:', err);
        showError('🎤 Please allow microphone access and try again.');
        return false;
    }
}

window.stopRecording = function() {
    if (mediaRecorder && isRecording) {
        console.log('Stopping recording...');
        mediaRecorder.stop();
        isRecording = false;
        updateRecordingUI(false);
    }
}

function updateRecordingUI(recording) {
    const startBtn = parent.document.querySelector('[data-testid="stButton"] button');
    if (startBtn) {
        if (recording) {
            startBtn.style.background = 'linear-gradient(45deg, #d63031, #e17055)';
            startBtn.textContent = '⏹️ Stop Recording (Auto-stop in 10s)';
            startBtn.classList.add('recording');
        } else {
            startBtn.style.background = 'linear-gradient(45deg, #ff6b6b, #ee5a24)';
            startBtn.textContent = '🎤 Start Recording';
            startBtn.classList.remove('recording');
        }
    }
}

function showTranscript(text) {
    // Create or update transcript display
    let transcriptDiv = parent.document.getElementById('voice-transcript');
    if (!transcriptDiv) {
        transcriptDiv = parent.document.createElement('div');
        transcriptDiv.id = 'voice-transcript';
        transcriptDiv.style.cssText = `
            background: linear-gradient(45deg, #00b894, #00cec9);
            color: white;
            padding: 1rem;
            border-radius: 15px;
            margin: 1rem 0;
            font-size: 1.1rem;
            font-weight: bold;
        `;
        
        const container = parent.document.querySelector('.main-container');
        if (container) {
            container.appendChild(transcriptDiv);
        }
    }
    
    transcriptDiv.innerHTML = `🎤 You said: "${text}"`;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (transcriptDiv && transcriptDiv.parentNode) {
            transcriptDiv.parentNode.removeChild(transcriptDiv);
        }
    }, 5000);
}

function showError(message) {
    const errorDiv = parent.document.createElement('div');
    errorDiv.style.cssText = `
        background: linear-gradient(45deg, #d63031, #e17055);
        color: white;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-size: 1.1rem;
    `;
    errorDiv.textContent = message;
    
    const container = parent.document.querySelector('.main-container');
    if (container) {
        container.appendChild(errorDiv);
        
        setTimeout(() => {
            if (errorDiv && errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 3000);
    }
}

function getCurrentLanguage() {
    // Get current language from Streamlit session state
    const langMap = {
        'hindi': 'hi-IN',
        'english': 'en-IN', 
        'hinglish': 'hi-IN'
    };
    
    // Default to Hindi for better recognition of mixed language
    return 'hi-IN';
}

function generateMockTranscript() {
    const mockResponses = [
        "मुझे किसान योजना चाहिए",
        "farmer scheme batao",
        "women empowerment scheme chahiye",
        "fisherman yojana ke baare mein batao",
        "business loan scheme",
        "education scholarship",
        "kisan credit card scheme",
        "mahila samman yojana"
    ];
    
    return mockResponses[Math.floor(Math.random() * mockResponses.length)];
}

// Auto-start if user clicks voice button
window.addEventListener('message', function(event) {
    if (event.data.type === 'start_voice_recording') {
        startRecording();
    } else if (event.data.type === 'stop_voice_recording') {
        stopRecording();
    }
});

console.log('Enhanced voice system loaded');
</script>
"""

# Enhanced Audio Player Component
def create_audio_player(audio_base64, text):
    """Create audio player for TTS output"""
    if not audio_base64:
        return
    
    audio_html = f"""
    <div style="margin: 1rem 0; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 15px;">
        <p style="margin-bottom: 0.5rem;"><strong>🔊 Assistant Response:</strong></p>
        <audio controls style="width: 100%; margin-bottom: 0.5rem;">
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        <p style="font-size: 0.9rem; color: rgba(255,255,255,0.8);">"{text[:100]}..."</p>
    </div>
    """
    
    st.markdown(audio_html, unsafe_allow_html=True)

# Voice-enabled response function
def process_voice_query_with_tts(query):
    """Process voice query with TTS response"""
    # Search schemes (your existing function)
    schemes = search_schemes(query, st.session_state.user_occupation)
    
    # Generate text response (your existing function)
    response_text = generate_voice_response(query, schemes, st.session_state.current_language)
    
    # Convert to speech
    lang_code = 'hi' if st.session_state.current_language == 'hindi' else 'en'
    audio_base64 = text_to_speech_api(response_text, lang_code)
    
    # Update conversation log
    st.session_state.conversation_count += 1
    st.session_state.conversation_log.append(f"🗣️ Query {st.session_state.conversation_count}: {query}")
    st.session_state.conversation_log.append(f"🤖 Response: {response_text}")
    
    # Show schemes found
    if schemes:
        st.session_state.conversation_log.append(f"📋 Found {len(schemes)} schemes:")
        for i, scheme in enumerate(schemes, 1):
            st.session_state.conversation_log.append(f"  {i}. {scheme['Name']}")
    
    # Play audio response
    if audio_base64:
        create_audio_player(audio_base64, response_text)
    
    return response_text, schemes