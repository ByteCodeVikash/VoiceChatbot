import os
import time
import subprocess
import tempfile
import wave
import numpy as np
from datetime import datetime
from typing import Tuple

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False

import speech_recognition as sr

class FastSpeechModule:
    def __init__(self, model_size="small", sample_rate=44100):
        self.model_size = model_size
        self.sample_rate = sample_rate
        self.whisper_model = None
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        self.recognizer.energy_threshold = 200
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0
        self.recognizer.operation_timeout = None
        
        self.available = self._initialize_system()
    
    def _initialize_system(self):
        try:
            self._fix_audio_system()
            
            if not self._initialize_microphone():
                print("❌ Microphone unavailable")
                return False
            
            self._load_faster_whisper()
            return True
        except Exception as e:
            print(f"Speech system initialization failed: {e}")
            return False
    
    def _fix_audio_system(self):
        try:
            asoundrc_content = '''pcm.!default {
    type pulse
}
ctl.!default {
    type pulse
}'''
            asoundrc_path = os.path.expanduser("~/.asoundrc")
            with open(asoundrc_path, 'w') as f:
                f.write(asoundrc_content)
            
            subprocess.run(['pulseaudio', '--kill'], capture_output=True)
            time.sleep(2)
            subprocess.run(['pulseaudio', '--start'], capture_output=True)
            time.sleep(3)
            
            print("✅ Audio system configured for 44100 Hz")
        except:
            pass
    
    def _initialize_microphone(self):
        try:
            if SOUNDDEVICE_AVAILABLE:
                try:
                    devices = sd.query_devices()
                    for i, device in enumerate(devices):
                        if device['max_input_channels'] > 0 and 'default' not in device['name'].lower():
                            try:
                                sd.check_input_settings(device=i, samplerate=self.sample_rate)
                                print(f"✅ Using device: {device['name']}")
                                sd.default.device[0] = i
                                return True
                            except:
                                continue
                except:
                    pass
            
            try:
                self.microphone = sr.Microphone(device_index=None)
                with self.microphone as source:
                    print("Adjusting for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=2.0)
                print("✅ Speech Recognition microphone initialized")
                return True
            except Exception as e:
                print(f"Default mic failed: {e}")
            
            devices = sr.Microphone.list_microphone_names()
            for i, device in enumerate(devices):
                if 'pulse' in device.lower() or 'default' in device.lower():
                    try:
                        self.microphone = sr.Microphone(device_index=i)
                        with self.microphone as source:
                            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                        print(f"✅ Using device: {device}")
                        return True
                    except:
                        continue
            
            self.microphone = sr.Microphone()
            print("⚠️ Using basic microphone")
            return True
            
        except Exception as e:
            print(f"❌ Microphone initialization failed: {e}")
            return False
    
    def _load_faster_whisper(self):
        if not FASTER_WHISPER_AVAILABLE:
            print("⚠️ faster-whisper not available, using speech_recognition")
            return
        
        try:
            self.whisper_model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8"
            )
            print("✅ faster-whisper model loaded")
        except Exception as e:
            print(f"⚠️ faster-whisper loading failed: {e}")
            self.whisper_model = None
    
    def _record_audio_sounddevice(self, duration=8):
        if not SOUNDDEVICE_AVAILABLE:
            return None
        
        try:
            print("🎤 Recording... (speak now)")
            
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                blocking=False
            )
            
            print("Recording started, speak clearly...")
            sd.wait()
            
            max_amplitude = np.max(np.abs(recording))
            print(f"Max amplitude: {max_amplitude:.4f}")
            
            if max_amplitude < 0.005:
                print("⚠️ Very low audio signal detected")
                return None
            
            audio_int16 = (recording * 32767).astype(np.int16)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                with wave.open(tmp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(self.sample_rate)
                    wav_file.writeframes(audio_int16.tobytes())
                
                return tmp_file.name
                
        except Exception as e:
            print(f"❌ sounddevice recording failed: {e}")
            return None
    
    def _transcribe_faster_whisper(self, audio_file, language="hi"):
        if not self.whisper_model:
            return None, 0.0
        
        try:
            segments, info = self.whisper_model.transcribe(
                audio_file,
                language=language,
                vad_filter=True,
                vad_parameters={
                    "min_silence_duration_ms": 500,
                    "threshold": 0.15
                }
            )
            
            text_segments = []
            for segment in segments:
                if segment.text.strip():
                    text_segments.append(segment.text.strip())
            
            full_text = " ".join(text_segments).strip()
            
            if full_text and len(full_text) > 2:
                confidence = getattr(info, 'language_probability', 0.8)
                return full_text, confidence
            
            return None, 0.0
            
        except Exception as e:
            print(f"❌ faster-whisper transcription failed: {e}")
            return None, 0.0
    
    def _listen_with_google_sr(self, language="hi-IN", timeout=10):
        if not self.microphone:
            return None, 0.0
        
        try:
            print("🎤 Listening with Google SR... (speak after beep)")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=15
                )
            
            text = self.recognizer.recognize_google(audio, language=language)
            if text and len(text.strip()) > 0:
                print(f"✅ Google SR: '{text}'")
                return text.strip(), 0.8
            
            return None, 0.0
            
        except sr.WaitTimeoutError:
            print("⏰ Google SR timeout - no speech detected")
        except sr.UnknownValueError:
            print("🤷 Google SR: Could not understand speech")
        except sr.RequestError as e:
            print(f"❌ Google SR service error: {e}")
        except Exception as e:
            print(f"❌ Google SR error: {e}")
        
        return None, 0.0
    
    def listen(self, timeout=10, language="english"):
        if not self.available:
            return "", 0.0
        
        lang_map = {
            "english": ("en-US", "en"),
            "hindi": ("hi-IN", "hi"),
            "hinglish": ("hi-IN", "hi")
        }
        
        sr_lang, whisper_lang = lang_map.get(language.lower(), ("hi-IN", "hi"))
        listen_timeout = max(timeout, 8)
        
        print(f"🎤 Listening in {language}... (timeout: {listen_timeout}s)")
        
        text, confidence = self._listen_with_google_sr(sr_lang, listen_timeout)
        if text and len(text.strip()) > 2:
            return text, confidence
        
        if SOUNDDEVICE_AVAILABLE and self.whisper_model:
            print("🔄 Trying faster-whisper as fallback...")
            audio_file = self._record_audio_sounddevice(listen_timeout)
            if audio_file:
                try:
                    text, confidence = self._transcribe_faster_whisper(audio_file, whisper_lang)
                    os.unlink(audio_file)
                    
                    if text and len(text.strip()) > 2:
                        print(f"✅ faster-whisper: '{text}'")
                        return text, confidence
                except:
                    if os.path.exists(audio_file):
                        os.unlink(audio_file)
        
        print("⚠️ No speech detected by any method")
        return "", 0.0
    
    def get_text_input(self):
        try:
            print("\n" + "="*50)
            print("🎤 Voice input failed - using text input")
            print("="*50)
            
            user_input = input(f"[{datetime.now().strftime('%H:%M:%S')}] ✍️ Type: ")
            
            if user_input.lower() in ["exit", "quit", "bye", "band karo", "khatam"]:
                return "exit"
            
            if user_input.strip():
                return user_input.strip()
                
        except KeyboardInterrupt:
            return "exit"
        except Exception as e:
            print(f"Input error: {e}")
        
        return None
    
    def test_microphone(self):
        if not self.available:
            print("❌ Speech module not available")
            return False
        
        print("🎤 Testing microphone...")
        print("📢 Please say 'HELLO TESTING' loudly and clearly")
        
        try:
            text, confidence = self.listen(timeout=8, language="english")
            if text:
                print(f"✅ Test successful: '{text}' (confidence: {confidence:.2f})")
                return True
            else:
                print("❌ Test failed - no speech detected")
                print("💡 Try speaking louder or check microphone permissions")
                return False
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False