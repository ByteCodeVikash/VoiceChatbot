#!/usr/bin/env python3
# debug_tts_issue.py - Debug TTS problems

from tts_module import CachedTTSModule
import time
import os

def test_tts_directly():
    """Test TTS module directly"""
    print("🧪 Testing TTS Module Directly")
    print("=" * 50)
    
    # Initialize TTS
    cache_dir = "assets/cache/"
    os.makedirs(cache_dir, exist_ok=True)
    
    tts = CachedTTSModule(
        model_name="xtts_v2",
        cache_dir=cache_dir
    )
    
    if not tts.available:
        print("❌ TTS not available")
        return False
    
    print("✅ TTS initialized")
    
    # Test simple texts
    test_cases = [
        ("What's your name?", "english"),
        ("Simple test message", "english"), 
        ("The Indian government offers several schemes", "english"),
        ("Beti Bachao Beti Padhao scheme", "english"),
        ("Long response: The Indian government offers several schemes to empower women, including Beti Bachao Beti Padhao for girl child education, Sukanya Samriddhi Yojana for financial security", "english")
    ]
    
    for i, (text, lang) in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {text[:50]}...")
        print(f"Language: {lang}")
        
        try:
            success = tts.speak(text, lang)
            print(f"Result: {'✅ Success' if success else '❌ Failed'}")
            time.sleep(1)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return True

def test_gtts_fallback():
    """Test simple gTTS fallback"""
    print("\n🧪 Testing Simple gTTS Fallback")
    print("=" * 50)
    
    try:
        from gtts import gTTS
        import tempfile
        import subprocess
        
        # Test texts
        test_texts = [
            "What's your name?",
            "The Indian government offers several schemes for women"
        ]
        
        for text in test_texts:
            print(f"\n🔍 Testing: {text}")
            
            try:
                # Create TTS
                tts = gTTS(text=text, lang="en", slow=False)
                
                # Save to temp file
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                    tts.save(tmp_file.name)
                    audio_file = tmp_file.name
                
                print(f"✅ Created audio file: {audio_file}")
                
                # Try to play
                players = ["mpg123", "ffplay", "paplay"]
                success = False
                
                for player in players:
                    try:
                        cmd = [player, "-q", audio_file] if player == "mpg123" else [player, audio_file]
                        result = subprocess.run(cmd, capture_output=True, timeout=10)
                        if result.returncode == 0:
                            print(f"✅ Played with {player}")
                            success = True
                            break
                    except:
                        continue
                
                if not success:
                    print("❌ No player worked")
                
                # Cleanup
                os.unlink(audio_file)
                
            except Exception as e:
                print(f"❌ gTTS error: {e}")
    
    except ImportError:
        print("❌ gTTS not available")

def create_simple_tts():
    """Create super simple TTS for testing"""
    print("\n🔧 Creating Simple TTS Solution")
    print("=" * 50)
    
    simple_tts_code = '''
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
    tts.speak("The Indian government offers several schemes for women including Beti Bachao Beti Padhao")
'''
    
    # Write simple TTS file
    with open("simple_tts.py", "w") as f:
        f.write(simple_tts_code)
    
    print("✅ Created simple_tts.py")
    print("💡 Run: python simple_tts.py to test")

if __name__ == "__main__":
    print("🔍 Debugging TTS Issues")
    print("=" * 60)
    
    # Test current TTS
    test_tts_directly()
    
    # Test fallback
    test_gtts_fallback()
    
    # Create simple solution
    create_simple_tts()
    
    print("\n🎯 Next Steps:")
    print("1. Run: python simple_tts.py")
    print("2. If that works, we'll replace the complex TTS")
    print("3. This should fix both name prompt and long responses")