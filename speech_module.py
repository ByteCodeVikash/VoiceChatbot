import os
import time
import subprocess
from datetime import datetime
import tempfile
import numpy as np
from typing import Tuple

# Proper import of actual speech_recognition library
import speech_recognition as sr
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

class SpeechModule:
    def __init__(self, model_size: str = "small"):
        self.model_size = model_size
        self.whisper_pipe = None
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.sample_rate = 16000
        
        # Better recognition settings
        self.recognizer.energy_threshold = 300  # Lower for better sensitivity
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Wait longer for complete sentences
        self.recognizer.operation_timeout = None  # No timeout during processing
        
        self.available = self._initialize_system()
        
    def _initialize_system(self):
        """Initialize complete speech recognition system"""
        try:
            # Check audio system
            self._check_audio_system()
            
            # Initialize microphone
            if not self._initialize_microphone():
                print("❌ Microphone unavailable - text-only mode")
                return False
            
            # Load Whisper model (optional)
            self._load_whisper_model()
            
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
        print("🎤 Initializing microphone...")
        
        try:
            # Strategy 1: Try default device
            try:
                self.microphone = sr.Microphone(device_index=None)
                with self.microphone as source:
                    print("Adjusting for ambient noise... (speak after this)")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                print("✅ Default microphone initialized")
                return True
            except Exception as e:
                print(f"Default mic failed: {e}")
            
            # Strategy 2: Try specific devices
            devices = sr.Microphone.list_microphone_names()
            print(f"Available devices: {len(devices)} found")
            
            for i, device in enumerate(devices):
                if 'pulse' in device.lower() or 'default' in device.lower():
                    try:
                        self.microphone = sr.Microphone(device_index=i)
                        with self.microphone as source:
                            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                        print(f"✅ Using device: {device}")
                        return True
                    except Exception as e:
                        print(f"Device {device} failed: {e}")
                        continue
            
            # Strategy 3: Force use without testing
            self.microphone = sr.Microphone()
            print("⚠️ Using basic microphone (untested)")
            return True
            
        except Exception as e:
            print(f"❌ Microphone initialization failed: {e}")
            return False
    
    def _load_whisper_model(self, model_id="openai/whisper-tiny"):
        """Load Whisper model with better error handling"""
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
    
    def _listen_with_google_sr(self, language="hi-IN", timeout=8):
        """Use Google Speech Recognition with improved settings"""
        if self.microphone is None:
            return None, 0.0
            
        try:
            print("🎤 Listening with Google SR... (speak clearly)")
            with self.microphone as source:
                # Quick ambient noise adjustment
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen with longer phrase time for complete sentences
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,  # Wait longer for user to start speaking
                    phrase_time_limit=10  # Allow longer phrases
                )
            
            # Try recognition with better error handling
            text = self.recognizer.recognize_google(audio, language=language)
            if text and len(text.strip()) > 0:
                print(f"✅ Google SR heard: '{text}'")
                return text.strip(), 0.8
            else:
                print("🤷 Empty response from Google SR")
                return None, 0.0
                
        except sr.WaitTimeoutError:
            print("⏰ Timeout - no speech detected")
        except sr.UnknownValueError:
            print("🤷 Could not understand speech - please speak more clearly")
        except sr.RequestError as e:
            print(f"❌ Google SR service error: {e}")
        except Exception as e:
            print(f"❌ Speech recognition error: {e}")
        
        return None, 0.0
    
    def _listen_with_whisper(self, language="hi-IN", timeout=8):
        """Use Whisper for speech recognition with improved settings"""
        if self.microphone is None or self.whisper_pipe is None:
            return None, 0.0
            
        try:
            print("🎤 Listening with Whisper... (speak clearly)")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=10
                )
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio.get_wav_data())
                temp_path = tmp_file.name
            
            try:
                lang_map = {"hi-IN": "hindi", "en-US": "english"}
                target_lang = lang_map.get(language, "hindi")
                
                result = self.whisper_pipe(
                    temp_path, 
                    generate_kwargs={"language": target_lang}
                )
                text = result["text"].strip()
                
                if text and len(text) > 1:
                    print(f"✅ Whisper heard: '{text}'")
                    return text, 0.9
                else:
                    print("🤷 Empty response from Whisper")
                    return None, 0.0
                    
            finally:
                # Always cleanup temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                
        except sr.WaitTimeoutError:
            print("⏰ Whisper timeout - no speech detected")
        except Exception as e:
            print(f"❌ Whisper failed: {e}")
        
        return None, 0.0
    
    def listen(self, timeout: int = 10, language: str = "english") -> Tuple[str, float]:
        """Main listen function with improved timeout handling"""
        if not self.available or not self.microphone:
            return "", 0.0
        
        # Map language to recognition format
        lang_map = {
            "english": "en-US",
            "hindi": "hi-IN", 
            "hinglish": "hi-IN"
        }
        rec_lang = lang_map.get(language.lower(), "hi-IN")
        
        # Use longer timeout for better user experience
        listen_timeout = max(timeout, 8)  # Minimum 8 seconds
        
        print(f"🎤 Listening in {language}... (speak clearly and completely)")
        print("💡 Tip: Speak after the beep sound, wait 1 second, then speak your full sentence")
        
        # Strategy 1: Try Google Speech Recognition first (more reliable)
        text, confidence = self._listen_with_google_sr(rec_lang, listen_timeout)
        if text and len(text.strip()) > 2:  # Minimum 3 characters
            return text, confidence
        
        # Strategy 2: Try Whisper if Google SR failed
        if self.whisper_pipe:
            print("🔄 Trying Whisper as fallback...")
            text, confidence = self._listen_with_whisper(rec_lang, listen_timeout)
            if text and len(text.strip()) > 2:
                return text, confidence
        
        print("⚠️ No clear speech detected by either method")
        return "", 0.0
    
    def get_text_input(self):
        """Get text input from user with better prompts"""
        try:
            print("\n" + "="*50)
            print("🎤 Voice input failed - switching to text input")
            print("="*50)
            
            user_input = input(f"[{datetime.now().strftime('%H:%M:%S')}] ✍️ Type your message: ")
            
            if user_input.lower() in ["exit", "quit", "bye", "band karo", "khatam"]:
                return "exit"
                
            if user_input.strip():
                print(f"[{datetime.now().strftime('%H:%M:%S')}] User (Text): {user_input}")
                return user_input.strip()
                
        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            return "exit"
        except Exception as e:
            print(f"Input error: {e}")
            
        return None
    
    def test_microphone(self):
        """Test microphone functionality"""
        if not self.available:
            print("❌ Speech module not available")
            return False
            
        print("🎤 Testing microphone... Say 'hello' when ready")
        
        try:
            text, confidence = self.listen(timeout=5, language="english")
            if text:
                print(f"✅ Microphone test successful: '{text}' (confidence: {confidence:.2f})")
                return True
            else:
                print("❌ Microphone test failed - no speech detected")
                return False
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            return False

# Test function
if __name__ == "__main__":
    print("🎤 Testing Speech Module")
    speech = SpeechModule()
    
    if speech.available:
        speech.test_microphone()
    else:
        print("❌ Speech module initialization failed")