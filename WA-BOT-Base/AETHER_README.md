# AETHER WhatsApp Bot Integration

This directory contains the Baileys-based WhatsApp bot integration for AETHER C2 framework.

## Quick Start

### 1. Install Dependencies

```bash
cd WA-BOT-Base
npm install
```

### 2. Start the Bot

```bash
npm start
```

A QR code will appear in your terminal. Scan it with WhatsApp on your phone.

### 3. Start AETHER Server (new terminal)

```bash
cd ..
python3 server/aether_server.py
```

### 4. Enable WhatsApp Integration

In the AETHER server console:

```
AETHER> whatsapp enable
AETHER> whatsapp authorize +1234567890
```

### 5. Send Commands via WhatsApp

Send a message to the bot (yourself or another WhatsApp number):

```
auth aether2025
sessions
link agent_001
whoami
```

## Files

- **aether-bridge.js** - Main bridge connecting WhatsApp to AETHER server
- **aether-handler.js** - Message routing and command processing
- **aether-integration.js** - Integration helpers for main.js
- **main.js** - Baileys bot main entry point (original Baileys code)
- **handler.js** - Original command handler (can be extended)
- **package.json** - Node.js dependencies

## Configuration

Edit `aether-bridge.js` to customize:

```javascript
const config = {
    aetherHost: 'http://localhost',  // AETHER server host
    aetherPort: 5000,                // AETHER server port
    apiKey: 'your-key',              // API key if needed
    authorizedUsers: [],              // Whitelist WhatsApp numbers
    commandTimeout: 30000,            // Command execution timeout
};
```

## Available Commands

### Authentication
- `auth <password>` - Authenticate with AETHER

### Session Management
- `link <session_id>` - Link to an agent
- `unlink` - Unlink from current agent
- `sessions` - List all active sessions
- `status` - Show current session info

### Agent Commands
- `whoami` - Current user
- `hostname` - System name
- `ps` - List processes
- `screenshot` - Take screenshot
- `ls <path>` - List directory
- `cat <file>` - Read file
- `download <file>` - Download from target
- `upload <file>` - Upload to target

### Other
- `help` - Show help menu
- `history` - Command history

## Integration with main.js

To enable automatic routing to AETHER, edit `main.js`:

```javascript
// At the top of startSocket function:
import { initializeAETHER } from './aether-integration.js';
const aetherHandler = initializeAETHER(sock, {
    aetherHost: 'http://localhost',
    aetherPort: 5000,
});

// Replace the handleCommand call:
// OLD:
// handleCommand(sock, message);

// NEW:
// await aetherHandler.handleMessage(message);
```

## Security Notes

⚠️ **Important:**
- Use a dedicated WhatsApp account, not your personal number
- Change the default password "aether2025"
- Whitelist authorized numbers only
- Enable rate limiting to prevent brute force
- Monitor command history and logs

## Troubleshooting

### QR Code Not Appearing
Make sure WhatsApp is installed on your phone and you have internet connectivity.

### Bot Not Responding
- Check if AETHER server is running
- Verify WhatsApp is still connected (rescan QR code if needed)
- Check logs for errors

### Commands Failing
- Verify you've authenticated: `auth <password>`
- Link to a session: `link <session_id>`
- Check AETHER server is listening on correct port

## Environment Variables

Set these before running:

```bash
export AETHER_HOST=http://localhost
export AETHER_PORT=5000
export AETHER_API_KEY=your-api-key
export AETHER_USERS=+1234567890,+0987654321
```

## Documentation

- See `WHATSAPP_SETUP.py` in parent directory for detailed setup guide
- See `server/comms/WHATSAPP_GUIDE.py` for full command reference
- Original Baileys documentation: https://github.com/WhiskeySockets/Baileys

## License

See LICENSE file in project root (MIT)
