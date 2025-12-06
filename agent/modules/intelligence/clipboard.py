import ctypes, threading, queue, time, json, os
from datetime import datetime

class ClipboardMonitor:
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.clipboard_queue = queue.Queue()
        self.last_clipboard = None
        self.clipboard_log = os.path.join(os.environ['TEMP'], 'AetherClipboard.json')
        
    def get_clipboard_text(self):
        """Get text from Windows clipboard."""
        try:
            # Open clipboard
            if not ctypes.windll.user32.OpenClipboard(None):
                return None
            
            # Get handle to clipboard data
            try:
                # CF_UNICODETEXT = 13
                h = ctypes.windll.user32.GetClipboardData(13)
                if not h:
                    return None
                
                # Cast to string pointer
                text = ctypes.c_wchar_p(h).value
                return text
            finally:
                ctypes.windll.user32.CloseClipboard()
        except:
            return None
    
    def set_clipboard_text(self, text):
        """Set text to Windows clipboard."""
        try:
            # Allocate memory
            size = len(text) * 2 + 2
            hglob = ctypes.windll.kernel32.GlobalAlloc(0x0002, size)
            
            if not hglob:
                return False
            
            # Lock memory
            lpstr = ctypes.windll.kernel32.GlobalLock(hglob)
            
            # Copy text
            ctypes.memmove(lpstr, text.encode('utf-16le'), size)
            
            # Unlock
            ctypes.windll.kernel32.GlobalUnlock(hglob)
            
            # Set to clipboard
            if not ctypes.windll.user32.OpenClipboard(None):
                return False
            
            try:
                ctypes.windll.user32.EmptyClipboard()
                ctypes.windll.user32.SetClipboardData(13, hglob)
                return True
            finally:
                ctypes.windll.user32.CloseClipboard()
        except:
            return False
    
    def start_monitoring(self):
        """Start monitoring clipboard for changes."""
        if self.monitoring:
            return "Clipboard monitor already running"
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        return "Clipboard monitoring started"
    
    def _monitor_loop(self):
        """Continuous monitoring loop."""
        while self.monitoring:
            try:
                current = self.get_clipboard_text()
                
                # Check if clipboard changed
                if current and current != self.last_clipboard:
                    self.last_clipboard = current
                    
                    event = {
                        'timestamp': datetime.now().isoformat(),
                        'content': current[:200],  # Limit logged content
                        'length': len(current),
                        'type': self._detect_type(current)
                    }
                    
                    self.clipboard_queue.put(event)
                    self._log_clipboard(event)
                
                time.sleep(1)  # Check every second
            except:
                pass
    
    def _detect_type(self, text):
        """Detect clipboard content type."""
        if text.startswith('http://') or text.startswith('https://'):
            return 'url'
        elif '@' in text and '.' in text:
            return 'email'
        elif text.replace(' ', '').replace('-', '').isdigit():
            return 'number'
        else:
            return 'text'
    
    def _log_clipboard(self, event):
        """Log clipboard change."""
        try:
            clipboard_history = []
            
            if os.path.exists(self.clipboard_log):
                with open(self.clipboard_log, 'r') as f:
                    clipboard_history = json.load(f)
            
            clipboard_history.append(event)
            
            # Keep last 1000 entries
            if len(clipboard_history) > 1000:
                clipboard_history = clipboard_history[-1000:]
            
            with open(self.clipboard_log, 'w') as f:
                json.dump(clipboard_history, f, indent=2)
        except:
            pass
    
    def stop(self):
        """Stop clipboard monitoring."""
        self.monitoring = False
        return "Clipboard monitoring stopped"
    
    def get_clipboard_history(self):
        """Get clipboard history."""
        try:
            if os.path.exists(self.clipboard_log):
                with open(self.clipboard_log, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        return []
