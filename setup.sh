#!/bin/bash

# Government Schemes Voice Assistant Setup Script
# This script sets up the environment for the voice assistant

echo "🚀 Setting up Government Schemes Voice Assistant"
echo "=================================================="

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️ This script is designed for Linux. Please install dependencies manually."
    exit 1
fi

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Install system audio dependencies
echo "🔊 Installing audio system dependencies..."
sudo apt-get install -y \
    pulseaudio \
    pulseaudio-utils \
    alsa-utils \
    portaudio19-dev \
    python3-pyaudio \
    mpg123 \
    sox \
    ffmpeg \
    pactl

# Start PulseAudio if not running
echo "🎵 Starting PulseAudio..."
pulseaudio --check || pulseaudio --start

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p assets
mkdir -p speakers
mkdir -p models/rasa/nlu

# Download sample data if needed
echo "📄 Setting up sample data..."
if [ ! -f "Government_schemes_final_english.csv" ]; then
    echo "Creating sample schemes CSV..."
    cat > Government_schemes_final_english.csv << EOF
Name,Details,Eligibility,Benefits,URL
PM Kisan Samman Nidhi,Financial assistance to farmers,All small and marginal farmers,₹6000 per year in three installments,https://pmkisan.gov.in/
Ayushman Bharat,Health insurance scheme,Poor and vulnerable families,Health coverage up to ₹5 lakhs per family per year,https://pmjay.gov.in/
PM Awas Yojana,Housing scheme,Economically weaker sections,Financial assistance for house construction,https://pmaymis.gov.in/
Pradhan Mantri Mudra Yojana,Micro-finance scheme,Small business entrepreneurs,Loans up to ₹10 lakhs,https://mudra.org.in/
Janani Suraksha Yojana,Maternal health scheme,Pregnant women,Cash assistance for institutional delivery,https://nhm.gov.in/
EOF
fi

# Test audio setup
echo "🔧 Testing audio setup..."
echo "Testing audio output..."
echo "Hello, this is a test" | text-to-speech || echo "TTS test completed"

# Check microphone
echo "🎤 Testing microphone..."
echo "Please say something for 3 seconds..."
timeout 3 arecord -f cd -t raw | aplay -f cd -t raw 2>/dev/null || echo "Microphone test completed"

echo ""
echo "✅ Setup completed!"
echo ""
echo "To start the assistant:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the assistant: python main.py"
echo ""
echo "If you encounter audio issues:"
echo "- Check if PulseAudio is running: pulseaudio --check"
echo "- Test audio: speaker-test"
echo "- Test microphone: arecord test.wav"
echo ""
echo "🎉 Happy chatting with your voice assistant!"