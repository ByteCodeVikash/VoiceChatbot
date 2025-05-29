#!/bin/bash

echo "🎤 Installing PyAudio for Voice Input"
echo "===================================="

# Install system dependencies for PyAudio
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    libasound2-dev \
    portaudio19-dev \
    build-essential \
    python3-pyaudio

# Install PyAudio via pip
echo "📦 Installing PyAudio via pip..."
pip3 install pyaudio

# Test PyAudio installation
echo "🧪 Testing PyAudio..."
python3 -c "
try:
    import pyaudio
    print('✅ PyAudio installed successfully!')
    
    # Test audio devices
    p = pyaudio.PyAudio()
    print(f'📱 Audio devices found: {p.get_device_count()}')
    
    # List some devices
    for i in range(min(3, p.get_device_count())):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f'🎤 Input device {i}: {info[\"name\"]}')
    
    p.terminate()
except ImportError as e:
    print(f'❌ PyAudio installation failed: {e}')
except Exception as e:
    print(f'⚠️ PyAudio test error: {e}')
"

echo ""
echo "🎉 PyAudio installation complete!"
echo "Now run: python3 voice_assistant.py"