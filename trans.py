import sounddevice as sd
import numpy as np
import queue
import threading
import time
from faster_whisper import WhisperModel

class AudioTranscriber:
    def __init__(self):
        self.samplerate = 16000
        self.block_duration = 0.5
        self.chunk_duration = 2
        self.channels = 1
        self.silence_threshold = 0.01  # RMS energy threshold for silence detection
        self.silence_duration = 3.0  # Duration of silence before auto-stop (seconds)
        
        self.frames_per_block = int(self.samplerate * self.block_duration)
        self.frames_per_chunk = int(self.samplerate * self.chunk_duration)
        
        self.model = WhisperModel("tiny", device="cpu", compute_type="int8")
        
        self.audio_queue = queue.Queue()
        self.audio_buffer = []
        self.transcription_results = []
        self.is_recording = False
        self.last_audio_time = 0
        self.stream = None
        self.recorder_thread = None
        self.transcriber_thread = None

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print(status)
        if self.is_recording:
            self.audio_queue.put(indata.copy())

    def _calc_rms(self, audio_data):
        return np.sqrt(np.mean(audio_data**2))

    def _is_silence(self, audio_data):
        return self._calc_rms(audio_data) < self.silence_threshold

    def recorder(self):
        with sd.InputStream(samplerate=self.samplerate, 
                           channels=self.channels, 
                           callback=self.audio_callback, 
                           blocksize=self.frames_per_block):
            print("Listening...")
            while self.is_recording:
                sd.sleep(100)

    def transcribe_audio(self):
        while self.is_recording:
            try:
                block = self.audio_queue.get(timeout=0.1)
                self.audio_buffer.append(block)
                self.last_audio_time = time.time()

                total_frames = sum(len(b) for b in self.audio_buffer)
                if total_frames >= self.frames_per_chunk:
                    audio_data = np.concatenate(self.audio_buffer)[:self.frames_per_chunk]
                    self.audio_buffer = []

                    audio_data = audio_data.flatten().astype(np.float16)

                    # Check for silence
                    if self._is_silence(audio_data):
                        if time.time() - self.last_audio_time > self.silence_duration:
                            print("Silence detected, stopping recording...")
                            self.stop_recording()
                            break

                    segments, _ = self.model.transcribe(audio_data, language="en", beam_size=1)
                    for segment in segments:
                        self.transcription_results.append(segment.text)
                        print(f"{segment.text}")
            except queue.Empty:
                # Check for silence timeout even when no audio chunks
                if (self.audio_buffer and 
                    time.time() - self.last_audio_time > self.silence_duration):
                    print("Silence timeout, stopping recording...")
                    self.stop_recording()
                    break

    def start_recording(self):
        if self.is_recording:
            return "Recording already in progress"
        
        self.is_recording = True
        self.audio_buffer = []
        self.transcription_results = []
        self.last_audio_time = time.time()
        
        # Start recording thread
        self.recorder_thread = threading.Thread(target=self.recorder)
        self.recorder_thread.daemon = True
        self.recorder_thread.start()
        
        # Start transcription thread
        self.transcriber_thread = threading.Thread(target=self.transcribe_audio)
        self.transcriber_thread.daemon = True
        self.transcriber_thread.start()
        
        return "Recording started"

    def stop_recording(self):
        if not self.is_recording:
            return "No recording in progress"
        
        self.is_recording = False
        
        # Wait for threads to finish
        if self.recorder_thread and self.recorder_thread.is_alive():
            self.recorder_thread.join(timeout=1.0)
        if self.transcriber_thread and self.transcriber_thread.is_alive():
            self.transcriber_thread.join(timeout=1.0)
        
        # Process any remaining audio
        if self.audio_buffer:
            audio_data = np.concatenate(self.audio_buffer)
            audio_data = audio_data.flatten().astype(np.float16)
            
            segments, _ = self.model.transcribe(audio_data, language="en", beam_size=1)
            for segment in segments:
                self.transcription_results.append(segment.text)
                print(f"{segment.text}")
        
        return "Recording stopped"

    def get_transcription(self):
        return " ".join(self.transcription_results)

    def is_recording_active(self):
        return self.is_recording

# Global transcriber instance
transcriber = AudioTranscriber()