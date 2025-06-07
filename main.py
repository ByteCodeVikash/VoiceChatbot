import os
import sys
import subprocess
from voice_assistant import EnhancedVoiceAssistant

def check_dependencies():
    required_packages = {
        'gtts': 'gTTS',
        'speech_recognition': 'SpeechRecognition',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'requests': 'Requests',
        'rapidfuzz': 'RapidFuzz'
    }
    
    optional_packages = {
        'faster_whisper': 'faster-whisper',
        'sounddevice': 'sounddevice',
        'TTS': 'Coqui-TTS'
    }
    
    missing_packages = []
    
    for package, name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(name)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install with: pip install gtts SpeechRecognition pandas numpy requests rapidfuzz")
        return False
    
    print("✅ All required dependencies found")
    
    missing_optional = []
    for package, name in optional_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_optional.append(name)
    
    if missing_optional:
        print(f"⚠️ Optional packages missing: {', '.join(missing_optional)}")
        print("For better performance: pip install faster-whisper sounddevice TTS")
    
    return True

def check_ollama():
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            models = result.stdout
            if 'phi3:mini' in models:
                print("✅ Ollama and phi3:mini model ready")
                return True
            else:
                print("⚠️ phi3:mini model not found")
                print("Pull model: ollama pull phi3:mini")
                return False
        else:
            print("❌ Ollama not responding")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Ollama not installed or not running")
        print("Install: curl -fsSL https://ollama.com/install.sh | sh")
        print("Start: ollama serve")
        return False

def setup_database():
    from database_backup import SchemeDatabase
    from config import CONFIG
    
    csv_path = CONFIG["schemes_csv_path"]
    db_path = CONFIG["sqlite_db_path"]
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return False
    
    print("🗄️ Initializing SQLite database...")
    db = SchemeDatabase(db_path, csv_path)
    db.close()
    print("✅ Database ready")
    return True

def fix_audio_system():
    try:
        asoundrc_content = '''pcm.!default {
    type plug
    slave {
        pcm "hw:1,0"
        rate 44100
    }
}'''
        asoundrc_path = os.path.expanduser("~/.asoundrc")
        with open(asoundrc_path, 'w') as f:
            f.write(asoundrc_content)
        
        subprocess.run(['pulseaudio', '--kill'], capture_output=True)
        subprocess.run(['pulseaudio', '--start'], capture_output=True)
        
        print("✅ Audio system configured for 44100 Hz")
        return True
    except Exception as e:
        print(f"⚠️ Audio system setup failed: {e}")
        return False

def main():
    print("🤖 Enhanced Government Schemes Voice Assistant")
    print("=" * 60)
    
    if not check_dependencies():
        print("\nExiting due to missing dependencies...")
        return
    
    ollama_available = check_ollama()
    if not ollama_available:
        print("⚠️ Continuing without Ollama (reduced functionality)")
    
    if not setup_database():
        print("\nExiting due to database setup failure...")
        return
    
    fix_audio_system()
    
    try:
        assistant = EnhancedVoiceAssistant()
        assistant.run_conversation()
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()