#!/bin/bash

# Build and run Transcriber App with Docker

echo "Building transcriber app Docker image..."
docker build -t transcriber-app .

echo "Starting transcriber app container..."
# Check if running on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    docker run -p 5000:5000 --device /dev/snd --name transcriber-app transcriber-app
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Running on macOS - audio access may require additional Docker configuration"
    docker run -p 5000:5000 --name transcriber-app transcriber-app
else
    # Windows or other
    echo "Windows detected - audio access may require additional Docker configuration"
    docker run -p 5000:5000 --name transcriber-app transcriber-app
fi

echo "Transcriber app is running at http://localhost:5000"

# To stop the container later, run: docker stop transcriber-app