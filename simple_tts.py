
# simple_tts.py - Ultra simple TTS
import os
import tempfile
from gtts import gTTS
import subprocess

class SimpleTTS:
    def __init__(self):
        self.available = True
    
    def speak(self, text, language="english"):
        """Simple speak function"""
        try:
            print(f"🔊 Speaking: {text}")
            
            # Create TTS
            lang_code = "en" if language == "english" else "hi"
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            # Save and play
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                tts.save(tmp_file.name)
                
                # Try players
                players = [
                    ["mpg123", "-q", tmp_file.name],
                    ["ffplay", "-nodisp", "-autoexit", "-v", "quiet", tmp_file.name],
                    ["paplay", tmp_file.name]
                ]
                
                for player_cmd in players:
                    try:
                        result = subprocess.run(player_cmd, capture_output=True, timeout=15)
                        if result.returncode == 0:
                            os.unlink(tmp_file.name)
                            return True
                    except:
                        continue
                
                os.unlink(tmp_file.name)
                return False
                
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return False

# Test it
if __name__ == "__main__":
    tts = SimpleTTS()
    tts.speak("What is your name?")
    tts.speak("The Indian government offers several schemes to empower women, including Beti Bachao Beti Padhao for girl child education, Sukanya Samriddhi Yojana for financial security, Ujjwala Yojana for housing, Pradhan Mantri Matru Vandana Yojana for maternity benefits...")
