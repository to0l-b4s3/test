#!/bin/bash
# AETHER C2 Server Startup Script
# Provides convenient server launching with IP and port options

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_error() {
    echo -e "${RED}[-]${NC} $1"
}

print_usage() {
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════════╗
║           AETHER C2 SERVER - STARTUP SCRIPT                        ║
╚════════════════════════════════════════════════════════════════════╝

USAGE:
  ./start_server.sh [OPTIONS]

OPTIONS:
  -h, --host HOST     Set bind host/IP (default: 0.0.0.0)
  -p, --port PORT     Set bind port (default: 443)
  --help              Show this help message

EXAMPLES:
  ./start_server.sh                          # Start on 0.0.0.0:443
  ./start_server.sh --host 127.0.0.1         # Start on 127.0.0.1:443
  ./start_server.sh --port 8443              # Start on 0.0.0.0:8443
  ./start_server.sh -h 192.168.1.100 -p 9999  # Custom host and port

COMMON SCENARIOS:
  Local testing:      ./start_server.sh --host 127.0.0.1 --port 8443
  Private network:    ./start_server.sh --host 192.168.1.100 --port 443
  Public facing:      ./start_server.sh --host 0.0.0.0 --port 443 (needs root)
  Docker/Container:   ./start_server.sh --host 0.0.0.0 --port 5000

EOF
}

# Default values
HOST="0.0.0.0"
PORT="443"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        --help)
            print_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Validate port
if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
    print_error "Invalid port: $PORT (must be 1-65535)"
    exit 1
fi

# Check if port is privileged and user is not root
if [ "$PORT" -lt 1024 ] && [ "$EUID" -ne 0 ]; then
    print_error "Port $PORT requires root privileges"
    echo "Run with 'sudo' or use a port >= 1024"
    exit 1
fi

# Change to server directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/server" || {
    print_error "Cannot find server directory"
    exit 1
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

# Check if required modules exist
if [ ! -f "aether_server.py" ]; then
    print_error "aether_server.py not found"
    exit 1
fi

# Display banner
echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                    AETHER C2 SERVER                               ║"
echo "║                   Starting Server...                              ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
print_info "Configuration:"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo ""
print_success "Starting AETHER server..."
echo ""

# Start the server with arguments
python3 aether_server.py --host "$HOST" --port "$PORT"
