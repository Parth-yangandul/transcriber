# Audio Transcription Web Application

## Requirements
- sounddevice
- numpy
- faster-whisper
- flask
- python-socketio

## Installation

### With pip (local development)
```bash
pip install sounddevice numpy faster-whisper flask
python web_ui.py
```

### With Docker (recommended)
```bash
# Build the Docker image
docker build -t transcriber-app .

# Run the container
docker run -p 5000:5000 --device /dev/snd transcriber-app
```

### With Docker Compose (easiest)
```bash
# Start the application
docker-compose up

# Stop the application
docker-compose down
```

## Usage
1. Open http://localhost:5000 in your browser
2. Click the record button to start recording
3. Speak into your microphone
4. The recording will auto-stop after 3 seconds of silence
5. Click the record button again to manually stop recording
6. View the transcription results in real-time

## Docker Notes
- The application requires access to host audio devices
- On Linux, use `--device /dev/snd` flag
- On macOS/Windows, Docker audio access may require additional configuration
- For production, consider using a more robust audio setup and a proper web server