from flask import Flask, render_template_string, request, jsonify
from trans import transcriber

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transcriber Web UI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .controls {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
        }
        .record-button {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background-color: #4CAF50;
            border: none;
            cursor: pointer;
            position: relative;
            transition: background-color 0.3s, transform 0.3s;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .record-button:hover {
            transform: scale(1.05);
        }
        .record-button.active {
            background-color: #f44336;
            animation: pulse 1.5s infinite;
        }
        .record-icon {
            width: 30px;
            height: 30px;
            background-color: white;
            border-radius: 50%;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            transition: border-radius 0.3s, width 0.3s, height 0.3s;
        }
        .record-button.active .record-icon {
            border-radius: 5px;
            width: 25px;
            height: 25px;
        }
        button:disabled {
            background-color: #cccccc !important;
            cursor: not-allowed;
            transform: none;
            animation: none;
        }
        #outputBox {
            width: 100%;
            height: 300px;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            font-family: monospace;
            font-size: 14px;
            background-color: #f9f9f9;
            overflow-y: auto;
            white-space: pre-wrap;
        }
        .status {
            text-align: center;
            margin-top: 15px;
            font-style: italic;
            color: #666;
        }
        .recording {
            color: #ff5722;
            font-weight: bold;
            animation: pulse 1.5s infinite;
        }
        .silent {
            color: #5bc0de;
            animation: pulse 2s infinite;
        }
        .error {
            color: #d9534f;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Transcriber Web UI</h1>
        <div class="controls">
            <button id="recordButton" class="record-button not-recording">
                <div class="record-icon"></div>
            </button>
        </div>
        <div id="outputBox"></div>
        <div class="status" id="status"></div>
    </div>

    <script>
        let isRecording = false;
        let updateInterval;
        let previousTranscription = "";
        
        document.getElementById('recordButton').addEventListener('click', async function() {
            if (isRecording) {
                await stopRecording();
            } else {
                await startRecording();
            }
        });
        
        async function startRecording() {
            const recordButton = document.getElementById('recordButton');
            const recordIcon = recordButton.querySelector('.record-icon');
            const outputBox = document.getElementById('outputBox');
            const status = document.getElementById('status');
            
            try {
                const response = await fetch('/start_recording', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    isRecording = true;
                    recordButton.classList.remove('not-recording');
                    recordButton.classList.add('active');
                    status.textContent = 'Recording... Will auto-stop after 3 seconds of silence';
                    status.className = 'status recording';
                    
                    // Start polling for updates
                    updateInterval = setInterval(updateTranscription, 500);
                } else {
                    status.textContent = `Error: ${data.error}`;
                    status.className = 'status error';
                }
            } catch (error) {
                status.textContent = `Network error: ${error.message}`;
                status.className = 'status error';
            }
        }
        
        async function stopRecording() {
            const recordButton = document.getElementById('recordButton');
            const recordIcon = recordButton.querySelector('.record-icon');
            const status = document.getElementById('status');
            
            try {
                const response = await fetch('/stop_recording', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    isRecording = false;
                    recordButton.classList.remove('active');
                    recordButton.classList.add('not-recording');
                    clearInterval(updateInterval);
                    status.textContent = 'Recording stopped';
                    status.className = 'status';
                    
                    // Get final transcription
                    await updateTranscription();
                } else {
                    status.textContent = `Error: ${data.error}`;
                    status.className = 'status error';
                }
            } catch (error) {
                status.textContent = `Network error: ${error.message}`;
                status.className = 'status error';
            }
        }
        
        async function updateTranscription() {
            try {
                const response = await fetch('/get_transcription', {
                    method: 'GET',
                });
                
                if (response.ok) {
                    const data = await response.json();
                    const outputBox = document.getElementById('outputBox');
                    
                    if (data.transcription && data.transcription !== previousTranscription) {
                        outputBox.textContent = data.transcription;
                        previousTranscription = data.transcription;
                    }
                    
                    if (data.is_recording === false) {
                        // Recording stopped automatically
                        clearInterval(updateInterval);
                        const recordButton = document.getElementById('recordButton');
                        recordButton.classList.remove('active');
                        recordButton.classList.add('not-recording');
                        isRecording = false;
                        document.getElementById('status').textContent = 'Auto-stopped due to silence';
                        document.getElementById('status').className = 'status';
                    }
                }
            } catch (error) {
                console.error('Error updating transcription:', error);
            }
        }
    </script>
</body>
</html>
    ''')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    try:
        result = transcriber.start_recording()
        return jsonify({'message': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    try:
        result = transcriber.stop_recording()
        return jsonify({'message': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_transcription', methods=['GET'])
def get_transcription():
    try:
        text = transcriber.get_transcription()
        is_recording = transcriber.is_recording_active()
        return jsonify({'transcription': text, 'is_recording': is_recording})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)