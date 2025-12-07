# AETHER C2 - Complete Documentation Index

## 🎯 Quick Navigation

### 🚀 Start Here (Choose One)
- **New User?** → Read `QUICK_START_REFERENCE.md` (5 min)
- **Want Auto Setup?** → Run `bash quickstart.sh` (Linux/Mac) or `python3 MASTER_SETUP.py`
- **Experienced?** → Jump to [Component Startup Guide](#component-startup-guide)
- **Need WhatsApp?** → See `WHATSAPP_BOT_INTEGRATION.md`

---

## 📚 Documentation Files

### Core Guides (Read in Order)

| File | Purpose | Read Time | Status |
|------|---------|-----------|--------|
| **QUICK_START_REFERENCE.md** | Quick reference card | 5 min | ✅ Essential |
| **COMPLETE_CONFIG_GUIDE.md** | All configuration options | 30 min | ✅ Critical |
| **COMPLETE_DEPLOYMENT_GUIDE.md** | Full deployment steps | 45 min | ✅ Complete |
| **WHATSAPP_BOT_INTEGRATION.md** | WhatsApp bot setup & commands | 20 min | ✅ Optional |
| **README.md** | Project overview | 10 min | ℹ️ Info |

### Setup & Automation Tools

| File | Purpose | Type | Execute |
|------|---------|------|---------|
| **MASTER_SETUP.py** | Interactive setup wizard | Python | `python3 MASTER_SETUP.py` |
| **quickstart.sh** | Auto setup script | Bash | `bash quickstart.sh` |
| **install_deps.py** | Dependency installer | Python | `python3 install_deps.py` |
| **quickfix.py** | Quick validation | Python | `python3 quickfix.py` |

### Configuration Templates

| File | Purpose | Edit? |
|------|---------|-------|
| **config.json** | Main server config | ✅ YES - Required |
| **server/comms/whatsapp_config.py** | WhatsApp settings | ✅ YES - If using WhatsApp |
| **WA-BOT-Base/aether-bridge.js** | Bot bridge config | ✅ YES - If using bot |
| **WA-BOT-Base/package.json** | Bot dependencies | ❌ Auto-managed |
| **requirements.txt** | Python packages | ❌ Auto-managed |

---

## 🔧 Configuration Roadmap

### Phase 1: Initial Setup (10 minutes)

```
START
  ↓
Run MASTER_SETUP.py OR quickstart.sh
  ↓
Answer configuration questions
  ↓
Dependencies installed automatically
  ↓
Configuration files created
  ↓
Verify with: python3 quickfix.py
  ↓
READY FOR STARTUP
```

### Phase 2: Manual Configuration (If Needed)

If automated setup doesn't work:

1. **Edit config.json**
   - Set C2 host/port
   - Set agent C2 host/port
   - Generate encryption key
   - Configure builder options

2. **Edit server/comms/whatsapp_config.py** (Optional)
   - Set WhatsApp password
   - Add authorized phone numbers
   - Configure bot URL

3. **Edit WA-BOT-Base/aether-bridge.js** (Optional)
   - Set AETHER server address
   - Set bot API key if needed

See `COMPLETE_CONFIG_GUIDE.md` for detailed instructions.

### Phase 3: Startup (5 minutes)

```
Terminal 1: python3 server/aether_server.py
Terminal 2: cd WA-BOT-Base && npm start (optional)
Terminal 3: Monitor with tail -f aether.log
```

See `COMPLETE_DEPLOYMENT_GUIDE.md` § Component Startup Guide

---

## 📋 Configuration Checklist

### Before First Run

Essential Settings:
- [ ] config.json exists and is valid JSON
- [ ] Encryption key is set (not default)
- [ ] Agent C2 host/port configured
- [ ] C2 server port available (not in use)
- [ ] Python dependencies installed: `pip install -r requirements.txt`
- [ ] Node dependencies installed: `cd WA-BOT-Base && npm install`

Optional (WhatsApp):
- [ ] WhatsApp bot enabled in config
- [ ] Bot URL configured correctly
- [ ] Auth password changed
- [ ] Authorized phone numbers added

Security:
- [ ] All default passwords changed
- [ ] Encryption key is strong (64+ chars)
- [ ] Firewall rules configured
- [ ] Running in isolated/authorized environment

### Verification Commands

```bash
# Check Python version
python3 --version

# Check Node version
node --version

# Verify dependencies
pip list | grep cryptography

# Validate config.json
python3 -m json.tool config.json

# Test imports
python3 -c "from crypto import CryptoHandler; print('OK')"

# Run auto-validation
python3 quickfix.py
```

---

## 🚀 Component Startup Guide

### Startup Order & Commands

#### Step 1: Start AETHER C2 Server
```bash
cd /path/to/aether
python3 server/aether_server.py

# Expected output:
# ╔═╗╔═╗╔╦╗╔═╗╦  ╔═╗╦═╗
# AETHER Server v1.0
# Listener: 0.0.0.0:443
# AETHER>
```

#### Step 2: Start WhatsApp Bot (Optional)
```bash
# In new terminal
cd WA-BOT-Base
npm start

# Expected output:
# [INFO] Connecting to WhatsApp...
# [INFO] Generating QR Code...
# Scan with WhatsApp in 45 seconds

# Then scan QR code with your phone
```

#### Step 3: Enable WhatsApp in AETHER (Optional)
```
# In AETHER console (terminal 1)
AETHER> whatsapp enable
AETHER> whatsapp status
```

#### Step 4: Build Agent
```
AETHER> generate
# Or in separate terminal:
python3 builder/compile.py
```

---

## 💻 Operational Reference

### Server Commands

| Command | Purpose |
|---------|---------|
| `help` | Show all commands |
| `sessions` | List active agents |
| `interact <id>` | Connect to agent |
| `back` | Return from agent |
| `broadcast <cmd>` | Execute on all |
| `generate` | Build agent |
| `whatsapp enable` | Start WhatsApp |
| `whatsapp status` | Check WhatsApp |
| `exit` | Shutdown server |

### Agent Commands (When Interacting)

| Command | Purpose |
|---------|---------|
| `whoami` | Current user |
| `hostname` | Computer name |
| `ps` | List processes |
| `ls <path>` | List directory |
| `cat <file>` | Read file |
| `screenshot` | Take screenshot |
| `download <file>` | Download file |
| `help` | Show commands |

### WhatsApp Commands (From Phone)

| Command | Purpose |
|---------|---------|
| `auth <pass>` | Authenticate |
| `sessions` | List agents |
| `link <id>` | Connect to agent |
| `whoami` | Current user |
| `screenshot` | Take screenshot |
| `help` | Show commands |

---

## 📱 WhatsApp Setup Steps

### Prerequisites
- [ ] AETHER Server running
- [ ] WhatsApp Bot running
- [ ] WhatsApp installed on phone
- [ ] Number in authorized_users list

### Setup Steps

1. **Start Bot**
   ```bash
   cd WA-BOT-Base
   npm start
   ```

2. **Scan QR Code**
   - Open WhatsApp on your phone
   - Settings → Linked Devices → Link a Device
   - Scan the QR code shown in terminal

3. **Enable in AETHER**
   ```
   AETHER> whatsapp enable
   AETHER> whatsapp status
   ```

4. **Authenticate from WhatsApp**
   ```
   You: auth aether2025
   Bot: ✅ Authorized!
   ```

5. **Start Using**
   ```
   You: sessions
   You: link agent_001
   You: whoami
   ```

Full guide: See `WHATSAPP_BOT_INTEGRATION.md`

---

## 🔒 Security Configuration

### Essential Security Changes

1. **Change Encryption Key**
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   # Copy output to config.json encryption_key
   ```

2. **Change WhatsApp Password**
   ```python
   # In server/comms/whatsapp_config.py
   'auth_password': 'YourStrongPassword123'
   ```

3. **Set Authorized Users**
   ```python
   # In server/comms/whatsapp_config.py
   'authorized_users': ['+1234567890']
   ```

4. **Update Agent C2 Host**
   ```json
   // In config.json
   "agent": {
     "c2_host": "your-actual-domain.com"
   }
   ```

5. **Configure Firewall**
   - Allow port 443 only from trusted IPs
   - Allow port 3000 for bot (if needed)
   - Deny all other inbound

### Pre-Production Checklist
- [ ] All default passwords changed
- [ ] Encryption key is strong (64+ chars)
- [ ] Agent C2 host is legitimate domain
- [ ] Firewall configured
- [ ] Logging enabled
- [ ] Tested in sandbox first
- [ ] Anti-debug enabled in builder
- [ ] Anti-VM checks enabled

---

## 📂 Project File Structure

```
AETHER/
├── Documentation/
│   ├── QUICK_START_REFERENCE.md      ← START HERE
│   ├── COMPLETE_CONFIG_GUIDE.md      ← Configuration guide
│   ├── COMPLETE_DEPLOYMENT_GUIDE.md  ← Deployment guide
│   ├── WHATSAPP_BOT_INTEGRATION.md   ← WhatsApp guide
│   └── README.md                      ← Overview
│
├── Setup/
│   ├── MASTER_SETUP.py                ← Interactive setup
│   ├── quickstart.sh                  ← Auto setup
│   ├── install_deps.py                ← Install packages
│   └── quickfix.py                    ← Validate setup
│
├── Configuration/
│   ├── config.json                    ← Main config (EDIT ME)
│   ├── requirements.txt               ← Python packages
│   └── .aether_config.json            ← Auto-generated
│
├── Server/
│   ├── aether_server.py               ← C2 server
│   ├── crypto.py                      ← Encryption
│   ├── sessions.py                    ← Session management
│   ├── comms/
│   │   ├── __init__.py
│   │   ├── whatsapp_bridge.py         ← Bot bridge
│   │   └── whatsapp_config.py         ← WhatsApp config
│   └── commands/
│       ├── command_suite.py
│       └── file_commands.py
│
├── Agent/
│   ├── aether_agent.py                ← Agent implant
│   ├── core/
│   │   ├── communicator.py            ← C2 comms
│   │   ├── evasion.py                 ← Evasion
│   │   └── persistence.py             ← Persistence
│   ├── modules/
│   │   ├── intelligence/              ← Data gathering
│   │   ├── system/                    ← System ops
│   │   ├── network/                   ← Network ops
│   │   └── advanced/                  ← Advanced features
│   └── utils/
│
├── Builder/
│   ├── compile.py                     ← Agent builder
│   ├── config_generator.py            ← Config gen
│   └── icon_forger.py                 ← Icon tool
│
├── Stager/
│   └── stager.py                      ← First stage loader
│
├── WhatsApp Bot/
│   ├── WA-BOT-Base/
│   │   ├── main.js                    ← Bot entry
│   │   ├── handler.js                 ← Command handler
│   │   ├── aether-bridge.js           ← Bridge (EDIT IF NEEDED)
│   │   ├── aether-handler.js          ← Message handler
│   │   ├── aether-integration.js      ← Integration
│   │   ├── package.json               ← Dependencies
│   │   └── AETHER_README.md           ← Bot guide
│   └── WHATSAPP_BOT_INTEGRATION.md    ← WhatsApp guide
│
└── Tests/
    ├── test_files.py
    ├── test2.py
    └── test_integration.py
```

---

## 🔧 Troubleshooting Quick Links

### Common Issues

| Issue | Solution |
|-------|----------|
| Port 443 in use | Check what's using it, change port in config.json |
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| Agent not connecting | Check C2 host/port, verify firewall |
| WhatsApp not responding | QR code scanned? Auth password correct? |
| Bot stuck on QR | Delete `WA-BOT-Base/auth_info_baileys/` folder |
| Config not loading | Verify JSON syntax: `python3 -m json.tool config.json` |

See `COMPLETE_DEPLOYMENT_GUIDE.md` § Troubleshooting for detailed solutions

---

## 📊 File Dependencies

### What depends on config.json?
- `server/aether_server.py` - Loads on startup
- `agent/aether_agent.py` - Uses agent settings
- `builder/compile.py` - Uses builder settings

### What depends on whatsapp_config.py?
- `server/aether_server.py` - Loads WhatsApp config
- `server/comms/whatsapp_bridge.py` - Uses settings

### What depends on requirements.txt?
- First time setup must run: `pip install -r requirements.txt`

### What depends on WA-BOT-Base/package.json?
- First time setup must run: `cd WA-BOT-Base && npm install`

---

## ✅ Verification Steps

### After Configuration

```bash
# 1. Verify Python imports
python3 << 'EOF'
from crypto import CryptoHandler
from sessions import SessionManager
from commands.command_suite import AetherCommandSuite
print("✓ Server modules OK")
EOF

# 2. Verify WhatsApp (if enabled)
python3 << 'EOF'
try:
    from comms import WhatsAppIntegration
    print("✓ WhatsApp modules OK")
except ImportError:
    print("⚠ WhatsApp optional")
EOF

# 3. Verify config syntax
python3 -m json.tool config.json > /dev/null && echo "✓ config.json syntax OK"

# 4. Verify port availability
netstat -an | grep 443 || echo "✓ Port 443 available"

# 5. Check dependencies
pip list | grep cryptography && echo "✓ Dependencies OK"
```

---

## 🎓 Learning Path

### Beginner (30 minutes)
1. Read `QUICK_START_REFERENCE.md`
2. Run `python3 MASTER_SETUP.py`
3. Start server: `python3 server/aether_server.py`
4. Build agent: `AETHER> generate`

### Intermediate (2 hours)
1. Read `COMPLETE_CONFIG_GUIDE.md`
2. Understand all configuration options
3. Deploy agent to test system
4. Practice basic commands

### Advanced (4+ hours)
1. Read `COMPLETE_DEPLOYMENT_GUIDE.md`
2. Set up WhatsApp integration
3. Configure custom domains
4. Implement operational security
5. Review all source code

### Expert (Ongoing)
1. Modify modules for custom operations
2. Implement custom C2 protocols
3. Create custom obfuscation
4. Optimize for stealth

---

## 📞 Quick Help

**Where do I start?**
→ `QUICK_START_REFERENCE.md`

**How do I configure everything?**
→ `COMPLETE_CONFIG_GUIDE.md`

**How do I deploy?**
→ `COMPLETE_DEPLOYMENT_GUIDE.md`

**How do I use WhatsApp?**
→ `WHATSAPP_BOT_INTEGRATION.md`

**I'm stuck!**
→ `COMPLETE_DEPLOYMENT_GUIDE.md` § Troubleshooting

**I want automated setup**
→ Run `python3 MASTER_SETUP.py`

---

## 📝 Files You MUST Edit

1. **config.json** - Critical
   - Encryption key
   - C2 host/port
   - Agent settings
   - Builder options

2. **server/comms/whatsapp_config.py** - If using WhatsApp
   - Auth password
   - Authorized users
   - Bot URL

3. **WA-BOT-Base/aether-bridge.js** - If using WhatsApp
   - AETHER host/port
   - API key if needed

## 📝 Files You DON'T Edit

- `requirements.txt` - Auto-managed
- `WA-BOT-Base/package.json` - Auto-managed
- `server/aether_server.py` - Core code
- `agent/aether_agent.py` - Core code
- `builder/compile.py` - Core code

---

## 🎯 Success Criteria

You'll know it's working when:

✅ Server starts without errors
✅ `AETHER>` prompt appears
✅ `AETHER> sessions` shows "No active sessions" (not error)
✅ You can run `AETHER> generate` to build agent
✅ Built agent runs on target system
✅ Agent appears in `AETHER> sessions`
✅ You can run `AETHER> interact <agent_id>`
✅ Commands execute on agent
✅ WhatsApp bot responds to messages (if enabled)
✅ WhatsApp commands work (if enabled)

---

## 🚨 Emergency/Reset

### Stop Everything
```bash
# Kill server
pkill -f "python3 server/aether_server.py"

# Kill bot
pkill -f "npm start"

# Or kill by terminal
Ctrl+C in each terminal
```

### Reset Configuration
```bash
# Backup old config
mv config.json config.json.backup

# Reset to defaults
python3 MASTER_SETUP.py
```

### Full Clean Reset
```bash
python3 install_deps.py
bash quickstart.sh
python3 MASTER_SETUP.py
```

---

## 📌 Important Notes

- ⚠️ **Change all default passwords before production**
- ⚠️ **Use strong encryption keys (64+ chars)**
- ⚠️ **Test in isolated environment first**
- ⚠️ **Configure firewall properly**
- ✅ **Follow security checklist before deployment**
- ✅ **Keep logs for audit trail**
- ✅ **Monitor for anomalies**
- ✅ **Document all changes**

---

## 📆 Version Information

```
AETHER C2 Framework
Version: 1.0
Status: Production Ready
Last Updated: December 7, 2025
Python: 3.8+
Node.js: 16+ (for WhatsApp)
```

---

**Total Documentation**: ~5 hours of guides
**Setup Time**: 5-30 minutes
**Learning Curve**: Beginner friendly
**Support Level**: Comprehensive

---

**Next Step**: Choose your starting point from the "Quick Navigation" section at the top! 🚀
