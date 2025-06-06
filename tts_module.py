import os
import time
import hashlib
import subprocess
import tempfile
from datetime import datetime
from gtts import gTTS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CachedTTSModule:
    def __init__(self, model_name="xtts_v2", voice_rate=0.9, voice_volume=1.0, cache_dir="assets/cache/"):
        self.model_name = model_name
        self.voice_rate = voice_rate
        self.voice_volume = voice_volume
        self.cache_dir = cache_dir
        
        os.makedirs(cache_dir, exist_ok=True)
        
        self.coqui_available = self._test_coqui()
        self.available = True
        self._is_speaking = False
        
    def _test_coqui(self):
        try:
            import TTS
            return True
        except ImportError:
            return False
    
    def _get_cache_path(self, text, lang):
        text_hash = hashlib.md5(f"{text}_{lang}".encode()).hexdigest()
        return os.path.join(self.cache_dir, f"tts_{text_hash}.mp3")
    
    def _clean_text_for_tts(self, text):
        if not text:
            return ""
        
        text = str(text).strip()
        
        encoding_fixes = {
            "â‚¹": "₹", "â€": "", "â€™": "'", "â€œ": '"', "â€": '"',
            "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"'
        }
        
        for bad, good in encoding_fixes.items():
            text = text.replace(bad, good)
        
        text = text.replace('**', '').replace('*', '').replace('#', '')
        text = text.replace('`', '').replace('_', ' ')
        
        import re
        text = re.sub(r'http[s]?://\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)
        text = re.sub(r'Rs\.?\s*(\d+)', r'रुपये \1', text)
        text = re.sub(r'₹\s*(\d+)', r'रुपये \1', text)
        
        text = text.replace('।', '. ').replace('.', '. ')
        text = text.replace(',', ', ').replace('?', '? ').replace('!', '! ')
        
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[-]{2,}', '-', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) > 150:
            text = text[:150]
        
        return text
    
    def _create_tts_coqui(self, text, lang, cache_path):
        if not self.coqui_available:
            return False
        
        try:
            from TTS.api import TTS
            
            if lang == "hi":
                model_name = "tts_models/hi/male/fairseq"
            else:
                model_name = "tts_models/en/ljspeech/tacotron2-DDC"
            
            tts = TTS(model_name)
            tts.tts_to_file(text=text, file_path=cache_path)
            return os.path.exists(cache_path)
        except:
            return False
    
    def _create_tts_gtts(self, text, lang, cache_path):
        try:
            slow_speech = len(text) > 60
            tts = gTTS(text=text, lang=lang, slow=slow_speech)
            tts.save(cache_path)
            return os.path.exists(cache_path)
        except:
            return False
    
    def _play_audio_file(self, audio_file):
        players = [
            ["mpg123", "-q", audio_file],
            ["ffplay", "-nodisp", "-autoexit", "-v", "quiet", audio_file],
            ["paplay", audio_file]
        ]
        
        for player_cmd in players:
            try:
                env = os.environ.copy()
                env['PULSE_RUNTIME_PATH'] = f'/run/user/{os.getuid()}/pulse'
                
                result = subprocess.run(
                    player_cmd,
                    capture_output=True,
                    timeout=10,
                    env=env
                )
                
                if result.returncode == 0:
                    return True
            except:
                continue
        
        return False
    
    def speak(self, text, language="english"):
        if self._is_speaking:
            return False
        
        self._is_speaking = True
        
        try:
            clean_text = self._clean_text_for_tts(text)
            if not clean_text or len(clean_text.strip()) < 2:
                return False
            
            lang_map = {
                "english": "en",
                "hindi": "hi",
                "hinglish": "hi"
            }
            tts_lang = lang_map.get(language.lower(), "hi")
            
            cache_path = self._get_cache_path(clean_text, tts_lang)
            
            if not os.path.exists(cache_path):
                success = False
                
                if self.model_name == "xtts_v2" and self.coqui_available:
                    success = self._create_tts_coqui(clean_text, tts_lang, cache_path)
                
                if not success:
                    success = self._create_tts_gtts(clean_text, tts_lang, cache_path)
                
                if not success:
                    print(f"🔊 {clean_text}")
                    time.sleep(1)
                    return False
            
            preview = clean_text[:60] + "..." if len(clean_text) > 60 else clean_text
            print(f"🔊 {preview}")
            
            success = self._play_audio_file(cache_path)
            
            if not success:
                print(f"📄 {clean_text}")
                time.sleep(1)
            
            return success
            
        finally:
            self._is_speaking = False
    
    def speak_short(self, text, language="english"):
        return self.speak(text, language)
    
    def test_tts(self):
        test_texts = [
            ("Hello, this is a test.", "en"),
            ("नमस्कार, यह एक परीक्षण है।", "hi")
        ]
        
        print("🧪 Testing TTS...")
        for text, lang in test_texts:
            print(f"Testing: {text}")
            cache_path = self._get_cache_path(text, lang)
            
            if os.path.exists(cache_path):
                os.remove(cache_path)
            
            success = self._create_tts_gtts(text, lang, cache_path)
            if success:
                play_success = self._play_audio_file(cache_path)
                print(f"Result: {'✅ Success' if play_success else '❌ Playback Failed'}")
            else:
                print("❌ TTS Creation Failed")
            time.sleep(1)