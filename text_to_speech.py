import os
import time
import subprocess
import tempfile
from datetime import datetime
from gtts import gTTS

class TextToSpeechModule:
    def __init__(self, model_name="gtts", voice_rate=0.9, voice_volume=1.0):
        self.model_name = model_name
        self.voice_rate = voice_rate
        self.voice_volume = voice_volume
        self.available = self._initialize_tts()
        
    def _initialize_tts(self):
        """Initialize TTS system"""
        try:
            # Test basic TTS functionality
            test_text = "Test"
            tts = gTTS(text=test_text, lang="en", slow=False)
            
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as tmp_file:
                tts.save(tmp_file.name)
                
            print("✅ TTS system initialized")
            return True
        except Exception as e:
            print(f"❌ TTS initialization failed: {e}")
            return False
    
    def _log_message(self, message, role="System"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {role}: {message}")
    
    def _speak_with_system_players(self, text, lang="hi"):
        """Try different system audio players"""
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                tts.save(tmp_file.name)
                audio_file = tmp_file.name
            
            # Try different players in order of preference
            players = [
                f"mpg123 -q {audio_file}",
                f"sox {audio_file} -d",
                f"paplay {audio_file}",
                f"aplay {audio_file}",
                f"ffplay -nodisp -autoexit -v quiet {audio_file}"
            ]
            
            success = False
            for player_cmd in players:
                try:
                    result = subprocess.run(player_cmd.split(), 
                                          capture_output=True, 
                                          timeout=10)
                    if result.returncode == 0:
                        success = True
                        break
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            os.unlink(audio_file)
            return success
            
        except Exception as e:
            self._log_message(f"TTS error: {e}", "System")
            return False
    
    def speak(self, text, language="english"):
        """Main speak function with language mapping"""
        if not self.available:
            print(f"🔊 {text}")
            time.sleep(1)
            return False
        
        # Clean text for speech
        clean_text = self._clean_text_for_speech(text)
        if not clean_text:
            return False
            
        # Map language to TTS language codes
        lang_map = {
            "english": "en",
            "hindi": "hi",
            "hinglish": "hi"
        }
        tts_lang = lang_map.get(language.lower(), "hi")
        
        self._log_message(clean_text, "Chatbot")
        
        # Try system players first
        if self._speak_with_system_players(clean_text, tts_lang):
            return True
        
        # Fallback: Just print the text
        print(f"\n🔊 {clean_text}\n")
        time.sleep(1)
        return False
    
    def _clean_text_for_speech(self, text):
        """Clean text for better TTS"""
        import re
        
        # Remove markdown formatting
        text = text.replace('**', '')
        text = text.replace('*', '')
        
        # Add pauses for better speech
        text = text.replace('।', '। ')
        text = text.replace('.', '. ')
        text = text.replace(',', ', ')
        text = text.replace('?', '? ')
        text = text.replace('!', '! ')
        
        # Limit sentence length for better TTS
        sentences = text.split('.')
        if len(sentences) > 3:
            mid = len(sentences) // 2
            text = '. '.join(sentences[:mid]) + '... ' + '. '.join(sentences[mid:])
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _play_error_message(self):
        """Play error message"""
        try:
            error_msg = "Sorry, there's a technical issue."
            self.speak(error_msg, "english")
        except Exception:
            print("🔊 Technical error occurred")
            time.sleep(1)