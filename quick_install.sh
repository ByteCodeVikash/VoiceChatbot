#!/bin/bash

echo "🚀 Quick Install - Missing Dependencies"
echo "====================================="

# Install missing dependencies one by one
echo "📦 Installing SpeechRecognition..."
pip3 install SpeechRecognition

echo "📦 Installing gTTS..."
pip3 install gTTS

echo "📦 Installing sounddevice..."
pip3 install sounddevice

echo "📦 Installing soundfile..."
pip3 install soundfile

echo "📦 Installing librosa..."
pip3 install librosa

echo "📦 Installing psutil..."
pip3 install psutil

echo "✅ All dependencies installed!"
echo ""
echo "Now run: python3 main.py"