#!/usr/bin/env python3
"""
Fix remaining dependency installation issues.
"""
import sys
import subprocess
import os

def run_as_admin():
    """Try to run script as administrator on Windows."""
    if sys.platform == 'win32':
        try:
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
                return True
            else:
                print("[!] Requesting administrator privileges...")
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                return False
        except:
            pass
    return True

def install_packages():
    packages = [
        ('pycryptodome', 'pip install pycryptodome'),
        ('dnspython', 'pip install dnspython'),
        ('pywin32', 'pip install pywin32'),
    ]
    
    for pkg, cmd in packages:
        print(f"\n[*] Installing {pkg}...")
        try:
            # Try direct import first
            __import__(pkg)
            print(f"[✓] {pkg} already installed")
            continue
        except ImportError:
            pass
        
        # Try to install
        for attempt in range(3):
            try:
                result = subprocess.run(
                    f'{sys.executable} -m {cmd}',
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode == 0 or "already satisfied" in result.stdout:
                    print(f"[✓] {pkg} installed successfully")
                    break
                else:
                    print(f"[!] Attempt {attempt+1} failed: {result.stderr[:100]}")
                    
                    # Special handling for pywin32
                    if pkg == 'pywin32' and attempt == 0:
                        print("[!] Trying pypiwin32 alternative...")
                        subprocess.run(f'{sys.executable} -m pip install pypiwin32', shell=True)
            except Exception as e:
                print(f"[!] Error: {e}")
    
    # Run pywin32 post-install if needed
    try:
        import win32api
        print("[✓] pywin32 imported successfully")
    except ImportError:
        print("[!] pywin32 may need post-installation")
        print("[!] Run: python pywin32_postinstall.py -install")
        print("[!] Find it in: PythonXX\\Scripts\\")

if __name__ == '__main__':
    print("="*60)
    print("FIXING REMAINING DEPENDENCIES")
    print("="*60)
    
    if not run_as_admin():
        print("[*] Restarting with admin privileges...")
        sys.exit(0)
    
    install_packages()
    
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    # Test imports
    imports_to_test = [
        ('Crypto.Cipher.AES', 'pycryptodome'),
        ('dns.resolver', 'dnspython'),
        ('win32api', 'pywin32'),
    ]
    
    all_ok = True
    for import_path, pkg_name in imports_to_test:
        try:
            __import__(import_path.split('.')[0])
            print(f"[✓] {pkg_name:15} ✓")
        except ImportError as e:
            print(f"[✗] {pkg_name:15} ✗ ({e})")
            all_ok = False
    
    if all_ok:
        print("\n[SUCCESS] All critical dependencies installed!")
        print("\nNow try: python server/aether_server.py")
    else:
        print("\n[WARNING] Some dependencies still missing.")
        print("You may need to:")
        print("  1. Run Command Prompt as Administrator")
        print("  2. Execute: pip install pycryptodome dnspython pywin32")
        print("  3. Run pywin32_postinstall.py -install")