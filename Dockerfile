# Railway automatically adds these, but you might need:
RUN apt-get update && apt-get install -y \
    ffmpeg \
    portaudio19-dev \
    python3-pyaudio \
    alsa-utils