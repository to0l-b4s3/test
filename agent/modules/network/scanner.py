import socket, struct, ctypes, os, sys, threading, queue, time, ipaddress, subprocess
from datetime import datetime
import scapy.all as scapy
from scapy.layers.l2 import ARP, Ether
from scapy.layers.inet import IP, ICMP, TCP, UDP
import netifaces, nmap, concurrent.futures
import json, hashlib, base64

class NetworkScanner:
    def __init__(self):
        self.results = {}
        self.scanning = False
        self.interface = self.get_default_interface()
        self.local_ip = self.get_local_ip()
        self.subnet = self.get_subnet()
        
    def get_default_interface(self):
        """Get default network interface."""
        try:
            gateways = netifaces.gateways()
            default_gateway = gateways['default'][netifaces.AF_INET]
            return default_gateway[1]
        except:
            # Fallback to first non-loopback interface
            for iface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    return iface
        return None
    
    def get_local_ip(self):
        """Get local IP address."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def get_subnet(self):
        """Get local subnet."""
        try:
            iface = self.interface
            if iface:
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    addr_info = addrs[netifaces.AF_INET][0]
                    ip = addr_info['addr']
                    netmask = addr_info['netmask']
                    
                    # Calculate subnet
                    network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                    return str(network)
        except:
            pass
        return f"{self.local_ip}/24"  # Default /24 subnet
    
    def scan(self, target=None, scan_type='quick'):
        """Perform network scan."""
        if not target:
            target = self.subnet
        
        scans = {
            'quick': self.quick_scan,
            'arp': self.arp_scan,
            'port': self.port_scan,
            'full': self.full_scan,
            'service': self.service_scan,
            'os': self.os_detection
        }
        
        if scan_type in scans:
            return scans[scan_type](target)
        else:
            return self.full_scan(target)
    
    def quick_scan(self, target):
        """Quick scan - ARP discovery + common ports."""
        results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'hosts': [],
            'ports': {}
        }
        
        # ARP scan for hosts
        hosts = self.arp_scan(target)
        if 'hosts' in hosts:
            results['hosts'] = hosts['hosts']
        
        # Scan common ports on first 3 hosts
        common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 3389, 8080]
        
        for host in results['hosts'][:3]:
            ip = host['ip']
            ports = self.scan_ports(ip, common_ports, timeout=1)
            results['ports'][ip] = ports
        
        return results
    
    def arp_scan(self, target):
        """ARP scan for host discovery."""
        results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'hosts': []
        }
        
        try:
            # Use scapy for ARP scanning
            arp_request = ARP(pdst=target)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast/arp_request
            
            answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
            
            for element in answered_list:
                host = {
                    'ip': element[1].psrc,
                    'mac': element[1].hwsrc,
                    'vendor': self.get_vendor_from_mac(element[1].hwsrc)
                }
                results['hosts'].append(host)
                
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def get_vendor_from_mac(self, mac):
        """Get vendor from MAC address (OUI lookup)."""
        try:
            # Simple OUI lookup - in reality, use a proper database
            oui = mac[:8].upper().replace(':', '')
            
            # Common OUIs
            vendors = {
                '000C29': 'VMware',
                '005056': 'VMware',
                '001C14': 'Dell',
                '001517': 'HP',
                '000D3A': 'Microsoft',
                '001A11': 'Apple',
                '3C970E': 'Microsoft',
                'B8CA3A': 'Dell',
                'F0DEF1': 'Cisco',
                '001E8C': 'NVIDIA'
            }
            
            for oui_prefix, vendor in vendors.items():
                if oui.startswith(oui_prefix):
                    return vendor
            
            return "Unknown"
        except:
            return "Unknown"
    
    def port_scan(self, target, ports='common', timeout=1):
        """Port scan target."""
        results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'open_ports': []
        }
        
        # Parse ports
        port_list = []
        
        if ports == 'common':
            port_list = list(range(1, 1025))  # Common ports
        elif ports == 'all':
            port_list = list(range(1, 65536))
        elif isinstance(ports, str) and '-' in ports:
            # Range like 1-1000
            start, end = map(int, ports.split('-'))
            port_list = list(range(start, end + 1))
        elif isinstance(ports, list):
            port_list = ports
        else:
            try:
                port_list = [int(ports)]
            except:
                port_list = list(range(1, 1025))
        
        # Use threading for faster scanning
        open_ports = []
        lock = threading.Lock()
        
        def check_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                
                result = sock.connect_ex((target, port))
                sock.close()
                
                if result == 0:
                    with lock:
                        open_ports.append(port)
            except:
                pass
        
        # Thread pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(check_port, port_list)
        
        # Get service info for open ports
        for port in open_ports:
            service = self.get_service_info(target, port)
            results['open_ports'].append({
                'port': port,
                'service': service.get('name', 'unknown'),
                'version': service.get('version', ''),
                'banner': service.get('banner', '')
            })
        
        return results
    
    def scan_ports(self, target, ports, timeout=1):
        """Scan specific ports."""
        return self.port_scan(target, ports, timeout)
    
    def get_service_info(self, target, port):
        """Get service information from banner."""
        service_info = {
            'port': port,
            'name': self.get_service_name(port),
            'version': '',
            'banner': ''
        }
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((target, port))
            
            # Try to get banner
            if port == 80 or port == 443:
                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
            elif port == 21:
                sock.send(b"\r\n")
            elif port == 22:
                sock.send(b"\r\n")
            elif port == 25:
                sock.send(b"EHLO example.com\r\n")
            elif port == 110:
                sock.send(b"\r\n")
            
            banner = sock.recv(1024)
            sock.close()
            
            if banner:
                service_info['banner'] = banner.decode('utf-8', errors='ignore').strip()
                
                # Try to extract version
                if 'Server:' in service_info['banner']:
                    for line in service_info['banner'].split('\n'):
                        if 'Server:' in line:
                            service_info['version'] = line.split('Server:')[1].strip()
                            break
        
        except:
            pass
        
        return service_info
    
    def get_service_name(self, port):
        """Get service name from port number."""
        common_services = {
            20: 'FTP Data', 21: 'FTP', 22: 'SSH', 23: 'Telnet',
            25: 'SMTP', 53: 'DNS', 67: 'DHCP Server', 68: 'DHCP Client',
            80: 'HTTP', 110: 'POP3', 123: 'NTP', 135: 'MS RPC',
            139: 'NetBIOS', 143: 'IMAP', 161: 'SNMP', 389: 'LDAP',
            443: 'HTTPS', 445: 'SMB', 465: 'SMTPS', 514: 'Syslog',
            587: 'SMTP Submission', 636: 'LDAPS', 993: 'IMAPS',
            995: 'POP3S', 1433: 'MSSQL', 1521: 'Oracle', 1723: 'PPTP',
            1883: 'MQTT', 1900: 'UPnP', 2082: 'cPanel', 2083: 'cPanel SSL',
            2086: 'WHM', 2087: 'WHM SSL', 2095: 'Webmail', 2096: 'Webmail SSL',
            2222: 'DirectAdmin', 2375: 'Docker', 2376: 'Docker SSL',
            3000: 'Node.js', 3306: 'MySQL', 3389: 'RDP', 3690: 'SVN',
            4443: 'HTTPS Alt', 4505: 'Salt', 4506: 'Salt', 4848: 'GlassFish',
            5432: 'PostgreSQL', 5900: 'VNC', 5984: 'CouchDB', 6379: 'Redis',
            6667: 'IRC', 8000: 'HTTP Alt', 8008: 'HTTP Alt', 8080: 'HTTP Proxy',
            8081: 'HTTP Alt', 8443: 'HTTPS Alt', 8888: 'HTTP Alt', 9000: 'SonarQube',
            9001: 'Tor', 9042: 'Cassandra', 9092: 'Kafka', 9200: 'Elasticsearch',
            9300: 'Elasticsearch', 11211: 'Memcached', 27017: 'MongoDB',
            27018: 'MongoDB', 28017: 'MongoDB HTTP'
        }
        
        return common_services.get(port, 'Unknown')
    
    def full_scan(self, target):
        """Full network scan - hosts, ports, services."""
        results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'scan_type': 'full',
            'hosts': {}
        }
        
        # Discover hosts
        hosts = self.arp_scan(target)
        if 'hosts' in hosts:
            for host in hosts['hosts']:
                ip = host['ip']
                results['hosts'][ip] = {
                    'mac': host['mac'],
                    'vendor': host['vendor'],
                    'ports': {},
                    'os': {},
                    'services': []
                }
                
                # Scan top 1000 ports
                ports = self.port_scan(ip, list(range(1, 1001)), timeout=0.5)
                if 'open_ports' in ports:
                    results['hosts'][ip]['ports'] = ports['open_ports']
                
                # Get OS fingerprint
                os_info = self.os_detection_single(ip)
                results['hosts'][ip]['os'] = os_info
        
        return results
    
    def service_scan(self, target):
        """Service detection scan using nmap."""
        results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'services': []
        }
        
        try:
            nm = nmap.PortScanner()
            
            # Scan with version detection
            nm.scan(hosts=target, arguments='-sV --version-intensity 5')
            
            for host in nm.all_hosts():
                for proto in nm[host].all_protocols():
                    ports = nm[host][proto].keys()
                    
                    for port in ports:
                        service = nm[host][proto][port]
                        
                        results['services'].append({
                            'host': host,
                            'port': port,
                            'protocol': proto,
                            'service': service.get('name', ''),
                            'version': service.get('version', ''),
                            'product': service.get('product', ''),
                            'extra': service.get('extrainfo', ''),
                            'cpe': service.get('cpe', '')
                        })
        
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def os_detection(self, target):
        """OS detection scan."""
        results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'os_results': []
        }
        
        try:
            nm = nmap.PortScanner()
            nm.scan(hosts=target, arguments='-O')
            
            for host in nm.all_hosts():
                if 'osmatch' in nm[host]:
                    for os_match in nm[host]['osmatch']:
                        results['os_results'].append({
                            'host': host,
                            'name': os_match['name'],
                            'accuracy': os_match['accuracy'],
                            'osclass': os_match.get('osclass', [])
                        })
        
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def os_detection_single(self, ip):
        """OS detection for single host."""
        try:
            # TCP/IP fingerprinting
            os_guesses = []
            
            # Check TTL
            ttl = self.get_ttl(ip)
            if ttl:
                if ttl <= 64:
                    os_guesses.append('Linux/Unix')
                elif ttl <= 128:
                    os_guesses.append('Windows')
                else:
                    os_guesses.append('Other')
            
            # Check TCP window size
            window = self.get_tcp_window(ip, 80)  # Try HTTP port
            if window:
                if window == 5840:
                    os_guesses.append('Linux (kernel 2.4/2.6)')
                elif window == 5720:
                    os_guesses.append('Google Linux')
                elif window == 65535:
                    os_guesses.append('FreeBSD')
            
            return {
                'ttl': ttl,
                'window': window,
                'guesses': list(set(os_guesses))
            }
            
        except:
            return {'ttl': None, 'window': None, 'guesses': []}
    
    def get_ttl(self, ip):
        """Get TTL via ICMP ping."""
        try:
            # Create raw socket for ICMP
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            sock.settimeout(2)
            
            # Create ICMP echo request
            packet_id = os.getpid() & 0xFFFF
            packet = self.create_icmp_packet(packet_id)
            
            sock.sendto(packet, (ip, 0))
            
            # Receive response
            response, addr = sock.recvfrom(1024)
            sock.close()
            
            # Extract TTL from IP header (9th byte)
            ttl = response[8]
            return ttl
            
        except:
            return None
    
    def create_icmp_packet(self, packet_id):
        """Create ICMP echo request packet."""
        header = struct.pack('!BBHHH', 8, 0, 0, packet_id, 1)  # Type 8 = echo request
        data = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'  # 26 bytes of data
        
        # Calculate checksum
        checksum = self.calculate_checksum(header + data)
        header = struct.pack('!BBHHH', 8, 0, checksum, packet_id, 1)
        
        return header + data
    
    def calculate_checksum(self, data):
        """Calculate Internet checksum."""
        if len(data) % 2:
            data += b'\x00'
        
        s = sum(struct.unpack('!%dH' % (len(data) // 2), data))
        s = (s >> 16) + (s & 0xffff)
        s += s >> 16
        
        return ~s & 0xffff
    
    def get_tcp_window(self, ip, port):
        """Get TCP window size."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            
            # Try to connect
            sock.connect((ip, port))
            
            # Get socket options
            window = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
            sock.close()
            
            return window
            
        except:
            return None
    
    def scan_network_shares(self, target=None):
        """Scan for network shares."""
        if not target:
            target = self.get_local_subnet().split('/')[0] + '/24'
        
        results = {
            'target': target,
            'timestamp': datetime.now().isoformat(),
            'shares': []
        }
        
        try:
            # Use net view command
            cmd = ['net', 'view', '/domain']
            output = subprocess.run(cmd, capture_output=True, text=True, shell=True).stdout
            
            # Parse output
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                if line and '\\' in line and not '--' in line:
                    results['shares'].append(line)
        
        except:
            pass
        
        return results
    
    def arp_spoof_detect(self):
        """Detect ARP spoofing on network."""
        try:
            # Get ARP table
            arp_table = self.get_arp_table()
            
            # Look for duplicates (possible spoofing)
            ip_to_mac = {}
            duplicates = []
            
            for entry in arp_table:
                ip = entry.get('ip')
                mac = entry.get('mac')
                
                if ip in ip_to_mac:
                    if ip_to_mac[ip] != mac:
                        duplicates.append({
                            'ip': ip,
                            'mac1': ip_to_mac[ip],
                            'mac2': mac
                        })
                else:
                    ip_to_mac[ip] = mac
            
            return {
                'arp_table': arp_table,
                'duplicates': duplicates,
                'possible_spoofing': len(duplicates) > 0
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_arp_table(self):
        """Get system ARP table."""
        arp_table = []
        
        try:
            # Parse arp -a output
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True, shell=True)
            
            lines = result.stdout.split('\n')
            for line in lines:
                if 'dynamic' in line.lower() or 'static' in line.lower():
                    parts = line.split()
                    if len(parts) >= 3:
                        ip = parts[0]
                        mac = parts[1]
                        if ip and mac and mac != 'ff-ff-ff-ff-ff-ff':
                            arp_table.append({
                                'ip': ip,
                                'mac': mac.replace('-', ':'),
                                'type': parts[2]
                            })
        
        except:
            pass
        
        return arp_table
    
    def dns_enumeration(self, domain):
        """Enumerate DNS records."""
        try:
            import dns.resolver
            
            records = {}
            
            # Common record types
            record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
            
            for record_type in record_types:
                try:
                    answers = dns.resolver.resolve(domain, record_type)
                    records[record_type] = [str(r) for r in answers]
                except:
                    records[record_type] = []
            
            # Try zone transfer
            try:
                ns_servers = records.get('NS', [])
                for ns in ns_servers[:2]:  # Try first 2 NS servers
                    try:
                        zone = dns.zone.from_xfr(dns.query.xfr(ns, domain))
                        records['zone_transfer'] = [str(node) for node in zone.nodes.keys()]
                    except:
                        pass
            except:
                pass
            
            return {
                'domain': domain,
                'records': records
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def scan_http_services(self, target):
        """Scan HTTP services for info."""
        results = []
        
        # Common HTTP ports
        http_ports = [80, 443, 8000, 8080, 8443, 8888]
        
        for port in http_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                
                result = sock.connect_ex((target, port))
                if result == 0:
                    # Port is open, get HTTP headers
                    if port == 443:
                        import ssl
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        
                        sock = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=target)
                        sock.settimeout(2)
                        sock.connect((target, port))
                    
                    sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                    response = sock.recv(4096).decode('utf-8', errors='ignore')
                    sock.close()
                    
                    # Parse headers
                    headers = {}
                    for line in response.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            headers[key.strip()] = value.strip()
                    
                    results.append({
                        'port': port,
                        'protocol': 'https' if port in [443, 8443] else 'http',
                        'headers': headers,
                        'response': response[:500]  # First 500 chars
                    })
            except:
                continue
        
        return results