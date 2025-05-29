import os
import time
import subprocess
import tempfile
from datetime import datetime
from gtts import gTTS

class TTSModule:
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
        """Try different system audio players with improved handling"""
        try:
            # Create TTS with better settings
            tts = gTTS(text=text, lang=lang, slow=False)
            
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                tts.save(tmp_file.name)
                audio_file = tmp_file.name
            
            # Try different players in order of preference
            players = [
                f"mpg123 -q {audio_file}",
                f"ffplay -nodisp -autoexit -v quiet {audio_file}",
                f"sox {audio_file} -d",
                f"paplay {audio_file}",
                f"aplay {audio_file}"
            ]
            
            success = False
            for player_cmd in players:
                try:
                    # Use shorter timeout to avoid long waits
                    result = subprocess.run(
                        player_cmd.split(), 
                        capture_output=True, 
                        timeout=8  # Reduced from 10 to 8 seconds
                    )
                    if result.returncode == 0:
                        success = True
                        break
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
                except Exception as e:
                    print(f"Player failed: {e}")
                    continue
            
            # Always cleanup the file
            try:
                os.unlink(audio_file)
            except:
                pass
                
            return success
            
        except Exception as e:
            self._log_message(f"TTS error: {e}", "System")
            return False
    
    def speak(self, text, language="english"):
        """Main speak function with improved text processing"""
        if not self.available:
            print(f"🔊 {text}")
            time.sleep(1)
            return False
        
        # Clean and prepare text for speech
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
        
        self._log_message(f"Speaking: {clean_text[:100]}...", "Chatbot")
        
        # Split long text into shorter chunks for better TTS
        chunks = self._split_text_for_tts(clean_text)
        
        success = True
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
                
            print(f"🔊 Speaking part {i+1}/{len(chunks)}: {chunk[:50]}...")
            
            # Speak each chunk
            if not self._speak_with_system_players(chunk, tts_lang):
                print(f"🔊 {chunk}")
                time.sleep(2)  # Fallback delay
                success = False
            else:
                # Small pause between chunks
                if i < len(chunks) - 1:
                    time.sleep(0.5)
        
        return success
    
    def _split_text_for_tts(self, text, max_length=200):
        """Split long text into TTS-friendly chunks"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        sentences = text.split('।')  # Split on Hindi/Hinglish sentence separator
        
        if len(sentences) == 1:
            # No Hindi separators, try English
            sentences = text.split('.')
        
        current_chunk = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed max length, start new chunk
            if len(current_chunk) + len(sentence) > max_length and current_chunk:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += "। " + sentence
                else:
                    current_chunk = sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If still too long, force split
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= max_length:
                final_chunks.append(chunk)
            else:
                # Force split at word boundaries
                words = chunk.split()
                temp_chunk = ""
                for word in words:
                    if len(temp_chunk) + len(word) + 1 <= max_length:
                        temp_chunk += " " + word if temp_chunk else word
                    else:
                        if temp_chunk:
                            final_chunks.append(temp_chunk)
                        temp_chunk = word
                if temp_chunk:
                    final_chunks.append(temp_chunk)
        
        return final_chunks if final_chunks else [text[:max_length]]
    
    def _clean_text_for_speech(self, text):
        """Clean text for better TTS with aggressive cleaning"""
        import re
        
        # Remove markdown formatting
        text = text.replace('**', '')
        text = text.replace('*', '')
        text = text.replace('#', '')
        
        # Fix encoding issues
        text = text.replace("â‚¹", "₹")
        text = text.replace("â€", "")
        text = text.replace("â€™", "'")
        text = text.replace("â€œ", '"')
        text = text.replace("â€", '"')
        text = text.replace("â€¢", "•")
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[-]{2,}', '-', text)
        
        # Add proper pauses
        text = text.replace('।', '। ')
        text = text.replace('.', '. ')
        text = text.replace(',', ', ')
        text = text.replace('?', '? ')
        text = text.replace('!', '! ')
        text = text.replace(':', ': ')
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit total length for TTS
        if len(text) > 500:
            sentences = text.split('.')
            if len(sentences) > 3:
                text = '. '.join(sentences[:3]) + '.'
            else:
                text = text[:500] + "..."
        
        return text
    
    def _play_error_message(self):
        """Play error message"""
        try:
            error_msg = "Sorry, there's a technical issue."
            self.speak(error_msg, "english")
        except Exception:
            print("🔊 Technical error occurred")
            time.sleep(1)