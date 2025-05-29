import os
import time
import subprocess
import tempfile
import numpy as np
from typing import Tuple

# Try importing speech_recognition with different approaches
sr = None
try:
    import speech_recognition as sr
    print("✅ SpeechRecognition imported successfully")
except ImportError as e:
    print(f"❌ SpeechRecognition import failed: {e}")
    sr = None
except Exception as e:
    print(f"❌ SpeechRecognition error: {e}")
    sr = None

# Try importing torch and transformers
try:
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    transformers_available = True
except ImportError:
    torch = None
    transformers_available = False

class SpeechRecognitionModule:
    def __init__(self, model_size: str = "small"):
        self.model_size = model_size
        self.whisper_pipe = None
        self.recognizer = None
        self.microphone = None
        self.sample_rate = 16000
        self.sr_available = sr is not None
        
        print(f"SpeechRecognition available: {self.sr_available}")
        
        if self.sr_available:
            try:
                self.recognizer = sr.Recognizer()
                print("✅ Speech Recognizer created")
            except Exception as e:
                print(f"❌ Failed to create recognizer: {e}")
                self.sr_available = False
        
        self.available = self._initialize_system()
        
    def _initialize_system(self):
        """Initialize complete speech recognition system"""
        try:
            if not self.sr_available:
                print("❌ SpeechRecognition not available - using text-only mode")
                return False
                
            # Check audio system
            self._check_audio_system()
            
            # Initialize microphone
            if not self._initialize_microphone():
                print("❌ Microphone unavailable - text-only mode")
                return False
            
            # Load Whisper model (optional)
            if transformers_available:
                self._load_whisper_model()
            else:
                print("⚠️ Transformers not available - using Google SR only")
            
            return True
        except Exception as e:
            print(f"Speech recognition initialization failed: {e}")
            return False
    
    def _check_audio_system(self):
        """Check and configure audio system"""
        print("🔧 Checking audio system...")
        
        try:
            result = subprocess.run(['pulseaudio', '--check'], capture_output=True)
            if result.returncode != 0:
                print("Starting PulseAudio...")
                subprocess.run(['pulseaudio', '--start'], capture_output=True)
                time.sleep(2)
        except:
            pass
        
        try:
            subprocess.run(['pactl', 'info'], capture_output=True, check=True)
            print("✅ PulseAudio is working")
            return True
        except:
            print("⚠️ PulseAudio issues detected")
            return False
    
    def _initialize_microphone(self):
        """Initialize microphone with multiple fallback strategies"""
        if not self.sr_available or not sr:
            return False
            
        print("🎤 Initializing microphone...")
        
        try:
            # Check if Microphone class exists
            if not hasattr(sr, 'Microphone'):
                print("❌ sr.Microphone not found")
                return False
                
            # Strategy 1: Try default device
            try:
                self.microphone = sr.Microphone(device_index=None)
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("✅ Default microphone initialized")
                return True
            except Exception as e:
                print(f"Default mic failed: {e}")
            
            # Strategy 2: Try to list devices first
            try:
                devices = sr.Microphone.list_microphone_names()
                print(f"Available devices: {len(devices)} found")
                
                # Try specific devices
                for i, device in enumerate(devices):
                    if 'pulse' in device.lower() or 'default' in device.lower():
                        try:
                            self.microphone = sr.Microphone(device_index=i)
                            with self.microphone as source:
                                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                            print(f"✅ Using device: {device}")
                            return True
                        except Exception as e:
                            print(f"Device {device} failed: {e}")
                            continue
            except Exception as e:
                print(f"Device listing failed: {e}")
            
            # Strategy 3: Force use without testing
            try:
                self.microphone = sr.Microphone()
                print("⚠️ Using basic microphone (untested)")
                return True
            except Exception as e:
                print(f"Basic microphone failed: {e}")
            
            return False
            
        except Exception as e:
            print(f"❌ Microphone initialization failed: {e}")
            return False
    
    def _load_whisper_model(self, model_id="openai/whisper-tiny"):
        """Load Whisper model with better error handling"""
        if not transformers_available:
            return False
            
        try:
            print("Loading Whisper model...")
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id, 
                torch_dtype=torch_dtype, 
                low_cpu_mem_usage=True, 
                use_safetensors=True
            )
            model.to(device)
            processor = AutoProcessor.from_pretrained(model_id)
            
            self.whisper_pipe = pipeline(
                "automatic-speech-recognition",
                model=model,
                tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor,
                torch_dtype=torch_dtype,
                device=device,
            )
            print("✅ Whisper model loaded!")
            return True
        except Exception as e:
            print(f"⚠️ Whisper loading failed: {e}")
            return False
    
    def _listen_with_google_sr(self, language="hi-IN"):
        """Use Google Speech Recognition"""
        if not self.sr_available or not sr or self.microphone is None:
            return None, 0.0
            
        try:
            print("🎤 Listening with Google SR...")
            
            # Check if recognizer has required methods
            if not hasattr(self.recognizer, 'listen') or not hasattr(self.recognizer, 'recognize_google'):
                print("❌ Recognizer methods not available")
                return None, 0.0
                
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=8)
            
            text = self.recognizer.recognize_google(audio, language=language)
            if text:
                print(f"Google SR heard: {text}")
                return text.strip(), 0.8
                
        except Exception as e:
            if "WaitTimeoutError" in str(type(e)):
                print("⏰ Timeout - no speech detected")
            elif "UnknownValueError" in str(type(e)):
                print("🤷 Could not understand speech")
            else:
                print(f"❌ Speech recognition error: {e}")
        
        return None, 0.0
    
    def _listen_with_whisper(self, language="hi-IN"):
        """Use Whisper for speech recognition"""
        if not self.sr_available or not sr or self.microphone is None or self.whisper_pipe is None:
            return None, 0.0
            
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=8)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio.get_wav_data())
                temp_path = tmp_file.name
            
            lang_map = {"hi-IN": "hindi", "en-US": "english"}
            result = self.whisper_pipe(temp_path, generate_kwargs={"language": lang_map.get(language, "hindi")})
            text = result["text"].strip()
            
            os.unlink(temp_path)
            
            if text:
                print(f"Whisper heard: {text}")
                return text, 0.9
                
        except Exception as e:
            print(f"Whisper failed: {e}")
        
        return None, 0.0
    
    def listen(self, timeout: int = 10, language: str = "english") -> Tuple[str, float]:
        """Main listen function with fallback strategies"""
        if not self.available or not self.sr_available or not self.microphone:
            print("❌ Speech recognition not available")
            return "", 0.0
        
        # Map language to recognition format
        lang_map = {
            "english": "en-US",
            "hindi": "hi-IN", 
            "hinglish": "hi-IN"
        }
        rec_lang = lang_map.get(language.lower(), "hi-IN")
        
        print(f"🎤 Listening in {language}... (speak now)")
        
        # Strategy 1: Try Google Speech Recognition first (more reliable)
        text, confidence = self._listen_with_google_sr(rec_lang)
        if text:
            return text, confidence
        
        # Strategy 2: Try Whisper if available
        if self.whisper_pipe:
            text, confidence = self._listen_with_whisper(rec_lang)
            if text:
                return text, confidence
        
        print("⚠️ No speech detected or recognized")
        return "", 0.0
    
    def _get_language_code(self, language):
        """Get language code for speech recognition"""
        language_mapping = {
            "english": "en-US",
            "hindi": "hi-IN",
            "hinglish": "hi-IN"
        }
        return language_mapping.get(language.lower(), "hi-IN")

# Debug function to test imports
def debug_speech_recognition():
    """Debug function to test speech recognition imports"""
    print("🔍 Debugging Speech Recognition...")
    
    try:
        import speech_recognition as sr_test
        print(f"✅ speech_recognition imported: {sr_test.__version__ if hasattr(sr_test, '__version__') else 'version unknown'}")
        print(f"✅ Available classes: {[attr for attr in dir(sr_test) if not attr.startswith('_')]}")
        
        if hasattr(sr_test, 'Recognizer'):
            recognizer = sr_test.Recognizer()
            print("✅ Recognizer created successfully")
        else:
            print("❌ Recognizer class not found")
            
        if hasattr(sr_test, 'Microphone'):
            print("✅ Microphone class found")
        else:
            print("❌ Microphone class not found")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    debug_speech_recognition()