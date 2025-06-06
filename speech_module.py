import os
import time
from datetime import datetime
from typing import Tuple
import speech_recognition as sr

class FastSpeechModule:
    def __init__(self, model_size="small", sample_rate=44100):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.available = self._initialize_microphone()
        
        # Adjust settings for better performance
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
    
    def _initialize_microphone(self):
        try:
            # Try to initialize basic microphone
            self.microphone = sr.Microphone()
            with self.microphone as source:
                print("🎤 Adjusting microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Microphone ready (with fallback to text)")
            return True
        except Exception as e:
            print(f"⚠️ Microphone setup failed: {e}")
            print("📝 Text-only mode enabled")
            return False
    
    def listen(self, timeout=10, language="english"):
        # Always use text input for reliability
        print(f"🎤 Voice input (timeout: {timeout}s) or press Enter for text...")
        
        if self.available:
            try:
                lang_map = {"english": "en-US", "hindi": "hi-IN", "hinglish": "hi-IN"}
                sr_lang = lang_map.get(language.lower(), "hi-IN")
                
                print("🎤 Listening... (speak now or wait for text input)")
                with self.microphone as source:
                    try:
                        audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=8)
                        text = self.recognizer.recognize_google(audio, language=sr_lang)
                        if text and len(text.strip()) > 2:
                            print(f"✅ Voice heard: '{text}'")
                            return text.strip(), 0.8
                    except sr.WaitTimeoutError:
                        print("⏰ Voice timeout, switching to text input...")
                    except sr.UnknownValueError:
                        print("🤷 Voice unclear, switching to text input...")
                    except Exception as e:
                        print(f"🔇 Voice error: {e}")
            except Exception:
                print("🔇 Voice input failed, using text...")
        
        # Always fallback to text input
        return self.get_text_input(), 1.0
    
    def get_text_input(self):
        try:
            print("\n" + "="*40)
            print("📝 TEXT INPUT MODE")
            print("="*40)
            
            # Show example inputs based on context
            examples = [
                "Example inputs:",
                "• 'farmer scheme' (for agriculture schemes)",
                "• 'मुझे किसान योजना चाहिए' (Hindi)",
                "• 'kisan yojana batao' (Hinglish)",
                "• 'exit' to quit"
            ]
            
            for example in examples:
                print(f"💡 {example}")
            
            print()
            user_input = input(f"[{datetime.now().strftime('%H:%M:%S')}] ✍️ Type your message: ")
            
            if user_input.lower().strip() in ["exit", "quit", "bye", "band karo", "khatam", "exit.", "quit."]:
                return "exit"
            
            if user_input.strip():
                print(f"📝 You typed: '{user_input.strip()}'")
                return user_input.strip()
            else:
                print("⚠️ Empty input, please try again")
                return ""
                
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            return "exit"
        except Exception as e:
            print(f"❌ Input error: {e}")
            return ""
    
    def test_microphone(self):
        if not self.available:
            print("❌ Microphone not available - text-only mode")
            return False
        
        print("🎤 Testing microphone... Say 'hello test'")
        try:
            text, confidence = self.listen(timeout=5, language="english")
            if text and text != "exit" and "test" in text.lower():
                print(f"✅ Microphone test successful: '{text}'")
                return True
            elif text and text != "exit":
                print(f"✅ Microphone working: '{text}' (different than expected)")
                return True
            else:
                print("❌ Microphone test failed - using text-only mode")
                return False
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            return False