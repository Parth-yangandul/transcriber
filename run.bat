@echo off
echo Building transcriber app Docker image...
docker build -t transcriber-app .

echo Starting transcriber app container...
echo Windows detected - audio access may require additional Docker configuration
docker run -p 5000:5000 --name transcriber-app transcriber-app

echo Transcriber app is running at http://localhost:5000

rem To stop the container later, run: docker stop transcriber-app