#!/usr/bin/env python3
"""
Quick debug script to check SpeechRecognition installation
"""

def check_speech_recognition():
    print("🔍 Checking SpeechRecognition installation...")
    
    try:
        # Test basic import
        import speech_recognition
        print(f"✅ speech_recognition module imported")
        print(f"📍 Module location: {speech_recognition.__file__}")
        
        # Check version
        if hasattr(speech_recognition, '__version__'):
            print(f"📦 Version: {speech_recognition.__version__}")
        
        # List all attributes
        attrs = [attr for attr in dir(speech_recognition) if not attr.startswith('_')]
        print(f"📋 Available attributes: {attrs}")
        
        # Test Recognizer class
        if hasattr(speech_recognition, 'Recognizer'):
            recognizer = speech_recognition.Recognizer()
            print("✅ Recognizer class works")
        else:
            print("❌ Recognizer class not found")
            
        # Test Microphone class  
        if hasattr(speech_recognition, 'Microphone'):
            print("✅ Microphone class found")
            try:
                mic = speech_recognition.Microphone()
                print("✅ Microphone can be instantiated")
            except Exception as e:
                print(f"⚠️ Microphone instantiation failed: {e}")
        else:
            print("❌ Microphone class not found")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

def reinstall_speech_recognition():
    print("\n🔧 Reinstalling SpeechRecognition...")
    import subprocess
    import sys
    
    commands = [
        [sys.executable, "-m", "pip", "uninstall", "SpeechRecognition", "-y"],
        [sys.executable, "-m", "pip", "install", "SpeechRecognition==3.8.1"],
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(f"Command: {' '.join(cmd)}")
            print(f"Return code: {result.returncode}")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
        except Exception as e:
            print(f"Command failed: {e}")

if __name__ == "__main__":
    print("🤖 SpeechRecognition Debug Script")
    print("=" * 40)
    
    if not check_speech_recognition():
        print("\n❌ SpeechRecognition has issues")
        print("Trying to reinstall...")
        reinstall_speech_recognition()
        print("\nTesting again...")
        check_speech_recognition()
    else:
        print("\n✅ SpeechRecognition is working!")
        
    print("\n" + "=" * 40)
    print("Debug complete")