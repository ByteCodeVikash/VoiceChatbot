#!/bin/bash

echo "🔧 Complete Audio System Fix"
echo "=============================="

# Kill existing audio processes
echo "🔄 Resetting audio system..."
pulseaudio --kill 2>/dev/null || true
sudo killall pulseaudio 2>/dev/null || true

# Remove old config
rm -rf ~/.config/pulse 2>/dev/null || true
rm -rf ~/.pulse* 2>/dev/null || true

# Reinstall audio system
echo "📦 Reinstalling audio components..."
sudo apt-get remove --purge pulseaudio pulseaudio-utils -y
sudo apt-get autoremove -y
sudo apt-get install pulseaudio pulseaudio-utils pavucontrol -y

# Configure audio groups
echo "👥 Setting up audio permissions..."
sudo usermod -a -G audio $USER

# Create PulseAudio config
echo "⚙️ Creating audio configuration..."
mkdir -p ~/.config/pulse

cat > ~/.config/pulse/client.conf << 'EOF'
# Enable autospawn
autospawn = yes

# Set the default server
default-server = unix:/tmp/pulse-socket
EOF

cat > ~/.config/pulse/daemon.conf << 'EOF'
# Basic daemon configuration
resample-method = speex-float-1
default-sample-format = s16le
default-sample-rate = 44100
default-sample-channels = 2

# Disable flat volumes
flat-volumes = no

# Reduce latency
default-fragments = 2
default-fragment-size-msec = 5
EOF

# Start PulseAudio properly
echo "🔊 Starting PulseAudio..."
pulseaudio --start --log-target=syslog

# Wait for audio system to initialize
sleep 3

# Test audio devices
echo "🧪 Testing audio devices..."
python3 -c "
import pyaudio
import sys

try:
    p = pyaudio.PyAudio()
    
    print('Available audio devices:')
    device_count = p.get_device_count()
    
    input_devices = []
    output_devices = []
    
    for i in range(device_count):
        info = p.get_device_info_by_index(i)
        name = info['name']
        
        if info['maxInputChannels'] > 0:
            input_devices.append((i, name))
            print(f'  INPUT  {i}: {name}')
            
        if info['maxOutputChannels'] > 0:
            output_devices.append((i, name))
            print(f'  OUTPUT {i}: {name}')
    
    print(f'\\nFound {len(input_devices)} input devices')
    print(f'Found {len(output_devices)} output devices')
    
    # Test basic recording
    if input_devices:
        print('\\n🎤 Testing microphone access...')
        try:
            # Use first available input device
            device_index = input_devices[0][0]
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024
            )
            
            # Record a small sample
            data = stream.read(1024)
            stream.stop_stream()
            stream.close()
            
            print('✅ Microphone test successful!')
            
        except Exception as e:
            print(f'❌ Microphone test failed: {e}')
    
    p.terminate()
    
except Exception as e:
    print(f'❌ PyAudio error: {e}')
    sys.exit(1)
"

# Set default audio devices
echo "🎯 Setting default audio devices..."
# Get pulse devices and set defaults
PULSE_SOURCES=$(pactl list sources short | grep -v monitor | head -1 | cut -f1)
if [ ! -z "$PULSE_SOURCES" ]; then
    pactl set-default-source $PULSE_SOURCES
    echo "✅ Default input device set"
fi

PULSE_SINKS=$(pactl list sinks short | head -1 | cut -f1)
if [ ! -z "$PULSE_SINKS" ]; then
    pactl set-default-sink $PULSE_SINKS
    echo "✅ Default output device set"
fi

# Test speech recognition
echo "🗣️ Testing speech recognition..."
python3 -c "
import speech_recognition as sr
import pyaudio

print('Testing SpeechRecognition library...')
try:
    r = sr.Recognizer()
    
    # List microphones
    mics = sr.Microphone.list_microphone_names()
    print(f'Available microphones: {len(mics)}')
    
    for i, name in enumerate(mics[:3]):  # Show first 3
        print(f'  {i}: {name}')
    
    # Test with default microphone
    print('\\nTesting default microphone...')
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print('✅ Microphone initialization successful!')
        
except Exception as e:
    print(f'❌ SpeechRecognition test failed: {e}')
"

echo ""
echo "🎉 Audio fix complete!"
echo ""
echo "Please run these commands to activate:"
echo "1. Log out and log back in (or reboot)"
echo "2. Or run: newgrp audio"
echo "3. Then test: python3 voice_assistant.py"
echo ""
echo "If issues persist:"
echo "- Check microphone permissions in system settings"
echo "- Try: pavucontrol (audio control panel)"
echo "- Restart system: sudo reboot"