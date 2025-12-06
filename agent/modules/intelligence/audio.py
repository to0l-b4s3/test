import pyaudio, wave, os, time, threading, queue, base64, json
from datetime import datetime

class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.record_thread = None
        self.audio_queue = queue.Queue()
        self.output_dir = os.path.join(os.environ['TEMP'], 'AetherAudio')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Audio parameters
        self.chunk = 1024
        self.sample_format = pyaudio.paInt16
        self.channels = 1
        self.fs = 44100
        self.duration = 10  # Default recording duration
        
    def record_audio(self, duration=10):
        """Record system audio."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"audio_{timestamp}.wav"
            filepath = os.path.join(self.output_dir, filename)
            
            p = pyaudio.PyAudio()
            
            # Open stream
            stream = p.open(
                format=self.sample_format,
                channels=self.channels,
                rate=self.fs,
                frames_per_buffer=self.chunk,
                input=True
            )
            
            frames = []
            
            # Record for specified duration
            for _ in range(0, int(self.fs / self.chunk * duration)):
                data = stream.read(self.chunk)
                frames.append(data)
            
            # Stop recording
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # Save to file
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(p.get_sample_size(self.sample_format))
                wf.setframerate(self.fs)
                wf.writeframes(b''.join(frames))
            
            return {
                'success': True,
                'filename': filename,
                'path': filepath,
                'duration': duration,
                'timestamp': timestamp,
                'size': os.path.getsize(filepath)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def start_continuous(self, duration=10):
        """Start continuous audio recording."""
        if self.recording:
            return "Audio recording already running"
        
        self.recording = True
        self.duration = duration
        self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.record_thread.start()
        
        return "Audio recording started"
    
    def _record_loop(self):
        """Continuous recording loop."""
        while self.recording:
            try:
                result = self.record_audio(self.duration)
                self.audio_queue.put(result)
                # Small delay before next recording
                time.sleep(2)
            except:
                pass
    
    def stop(self):
        """Stop audio recording."""
        self.recording = False
        return "Audio recording stopped"
    
    def get_recordings(self):
        """Get all recorded audio files."""
        recordings = []
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.wav'):
                filepath = os.path.join(self.output_dir, filename)
                recordings.append({
                    'filename': filename,
                    'path': filepath,
                    'size': os.path.getsize(filepath)
                })
        
        return recordings
