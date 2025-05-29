import os
import sys
from voice_assistant import VoiceAssistant

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = {
        'gtts': 'gTTS',
        'speech_recognition': 'SpeechRecognition', 
        'torch': 'PyTorch',
        'transformers': 'Transformers',
        'pandas': 'Pandas',
        'numpy': 'NumPy'
    }
    
    missing_packages = []
    
    for package, name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(name)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("\nPlease install missing packages:")
        print("pip install gtts SpeechRecognition torch transformers pandas numpy")
        return False
    
    print("✅ All core dependencies found")
    return True

def main():
    """Main entry point"""
    print("🤖 Government Schemes Voice Assistant")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\nExiting due to missing dependencies...")
        return
    
    try:
        # Initialize and run voice assistant
        assistant = VoiceAssistant()
        assistant.run_conversation()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("Please check your setup and try again.")

if __name__ == "__main__":
    main()