#!/usr/bin/env python3
"""
AETHER C2 SERVER STARTUP GUIDE
Comprehensive guide for starting the server with custom IP and port configurations
"""

STARTUP_GUIDE = """
╔════════════════════════════════════════════════════════════════════════════╗
║                  AETHER C2 SERVER - STARTUP GUIDE                          ║
║         IP and Port Configuration for Different Scenarios                  ║
╚════════════════════════════════════════════════════════════════════════════╝

================================================================================
QUICK START
================================================================================

LINUX/macOS (using bash script):
  ./start_server.sh                                    # Default (0.0.0.0:443)
  ./start_server.sh --host 127.0.0.1 --port 8443      # Custom
  
WINDOWS (using batch script):
  start_server.bat                                     # Default (0.0.0.0:443)
  start_server.bat --host 127.0.0.1 --port 8443       # Custom

Direct Python (any OS):
  python aether_server.py                              # Default
  python aether_server.py --host 127.0.0.1 --port 9999  # Custom

================================================================================
CONFIGURATION OPTIONS
================================================================================

--host HOST (or -h HOST)
  Description: IP address or hostname to bind to
  Default: 0.0.0.0 (listen on all interfaces)
  Examples:
    0.0.0.0           - Listen on all IPv4 interfaces (outbound agent C2)
    127.0.0.1         - Listen only on localhost (testing)
    192.168.1.100     - Listen on specific internal IP
    example.com       - Hostname (if DNS resolves correctly)

--port PORT (or -p PORT)
  Description: Port number to bind to
  Default: 443 (standard HTTPS)
  Range: 1-65535
  Examples:
    443               - Standard HTTPS port (requires root/admin)
    8443              - Alternative HTTPS port (no special privileges)
    5000              - Common dev/test port
    9999              - High port for testing
    80                - HTTP (requires root/admin)

================================================================================
COMMON DEPLOYMENT SCENARIOS
================================================================================

1. LOCAL TESTING / DEVELOPMENT
   Purpose: Test on your local machine
   Command: ./start_server.sh --host 127.0.0.1 --port 8443
   Details:
     - Only accessible from your machine
     - Doesn't require root/admin privileges
     - Perfect for development and debugging

2. PRIVATE NETWORK / INTERNAL LAB
   Purpose: Deploy within internal network
   Command: ./start_server.sh --host 192.168.1.100 --port 443
   Details:
     - Agents connect via internal IP
     - Requires root/admin for port 443
     - Use --port 8443 if port 443 is unavailable
     - Agents must be on same network

3. PUBLIC/INTERNET FACING
   Purpose: Deploy for remote agents
   Command: ./start_server.sh --host 0.0.0.0 --port 443
   Details:
     - Listens on all interfaces
     - Agents connect via public IP or domain
     - REQUIRES root/admin privileges
     - Consider using domain fronting (built-in)
     - SSL certificates should be configured

4. DOCKER/CONTAINER DEPLOYMENT
   Purpose: Run in containerized environment
   Command: ./start_server.sh --host 0.0.0.0 --port 5000
   Details:
     - Container usually runs as root
     - Expose port in docker-compose.yml
     - Map container port to host port
     - Example docker-compose mapping:
       ports:
         - "5000:5000"

5. MULTI-INSTANCE SETUP
   Purpose: Run multiple servers on same host
   Command: 
     ./start_server.sh --port 8001 &
     ./start_server.sh --port 8002 &
     ./start_server.sh --port 8003 &
   Details:
     - Each server runs independently
     - Separate session management
     - Useful for testing or staging
     - Don't exceed available ports

6. DOMAIN FRONTING / REVERSE PROXY
   Purpose: Hide C2 behind legitimate domain
   Command: ./start_server.sh --host 127.0.0.1 --port 8443
   Details:
     - Server listens locally
     - Nginx/Apache reverse proxy in front
     - Agents connect to proxy domain
     - Proxy forwards to backend (127.0.0.1:8443)
     - Built-in domain fronting also available

================================================================================
PORT SELECTION GUIDE
================================================================================

Privileged Ports (1-1024):
  - Require root/admin privileges
  - Standard for production
  - Common: 80 (HTTP), 443 (HTTPS), 53 (DNS)
  - Recommendation: Use if possible in production

Unprivileged Ports (1024-65535):
  - No special privileges needed
  - Good for development/testing
  - Common: 8080, 8443, 9000, 5000
  - Recommendation: Use for testing and development

NEVER USE:
  - Already in-use ports (will cause "Address already in use")
  - System reserved ports (varies by OS)
  - Check conflicts: netstat -tuln (Linux) or netstat -ano (Windows)

RECOMMENDED DEFAULTS:
  - Production: 443 (standard HTTPS)
  - Testing: 8443 or 9999
  - Docker: 5000-9999 (avoid common ports)
  - Local only: 8443-9999

================================================================================
TROUBLESHOOTING
================================================================================

ERROR: "Port X already in use" or "Address already in use"
Solution: Use different port
  ./start_server.sh --port 8444
  OR find what's using the port:
  - Linux: sudo lsof -i :443 | grep LISTEN
  - Windows: netstat -ano | findstr ":443"
  - Kill the process or use different port

ERROR: "Permission denied" on ports < 1024
Solution: Either use sudo/admin or pick higher port
  sudo ./start_server.sh --port 443
  OR
  ./start_server.sh --port 8443

ERROR: "Cannot bind to 0.0.0.0:X"
Solution: Check firewall, or use specific IP
  ./start_server.sh --host 192.168.1.100 --port 8443

ERROR: Agents cannot connect
Solution: Check configuration
  1. Verify host IP is reachable from agent machine
  2. Check firewall allows inbound traffic on specified port
  3. Verify agent has correct C2 server IP/port in config
  4. Check logs: tail -f server.log

ERROR: "Python not found"
Solution: Install Python 3 or ensure it's in PATH
  - Linux: sudo apt install python3
  - Windows: Download from python.org or use WSL
  - macOS: brew install python3

================================================================================
ADVANCED CONFIGURATION
================================================================================

ENVIRONMENT VARIABLES:
Set defaults without command line args:
  export AETHER_HOST="192.168.1.100"
  export AETHER_PORT="8443"
  ./start_server.sh  # Uses environment variables

CONFIGURATION FILE:
Edit config.json for permanent settings:
  {
    "c2_host": "your.server.com",
    "c2_port": 443,
    ...
  }

SYSTEMD SERVICE (Linux):
Create /etc/systemd/system/aether.service:
  [Unit]
  Description=AETHER C2 Server
  After=network.target
  
  [Service]
  Type=simple
  User=aether
  WorkingDirectory=/opt/aether
  ExecStart=/opt/aether/start_server.sh --host 0.0.0.0 --port 443
  Restart=always
  
  [Install]
  WantedBy=multi-user.target

Then:
  sudo systemctl enable aether
  sudo systemctl start aether
  sudo systemctl status aether

SUPERVISOR (Windows):
Use NSSM (Non-Sucking Service Manager) to create Windows service

================================================================================
VERIFICATION
================================================================================

Verify server is running:
  Linux: netstat -tuln | grep 8443
  Windows: netstat -ano | findstr ":8443"
  Check processes: ps aux | grep aether_server.py

Test connectivity:
  curl -k https://127.0.0.1:8443/  # Should get error or response
  telnet 127.0.0.1 8443           # Should connect

Check server logs:
  Look for "Listening on X.X.X.X:PORT" in output
  Verify "Listener started" message appears

Test agent connectivity:
  1. Configure agent with server IP:PORT
  2. Run agent
  3. Check "sessions" command on server
  4. New agent should appear in active sessions

================================================================================
IP AND PORT EXAMPLES BY USE CASE
================================================================================

┌─ LOCAL DEVELOPMENT ─────────────────────────────────────────────────┐
│ ./start_server.sh --host 127.0.0.1 --port 8443                     │
│ - Only accessible locally                                           │
│ - No special privileges needed                                      │
│ - Perfect for testing                                               │
└─────────────────────────────────────────────────────────────────────┘

┌─ INTERNAL NETWORK ──────────────────────────────────────────────────┐
│ ./start_server.sh --host 192.168.1.100 --port 443                  │
│ - Accessible from internal network                                  │
│ - Requires root/admin for port 443                                  │
│ - Configure agent to connect to 192.168.1.100:443                   │
└─────────────────────────────────────────────────────────────────────┘

┌─ PRODUCTION / INTERNET ─────────────────────────────────────────────┐
│ ./start_server.sh --host 0.0.0.0 --port 443                        │
│ - Listens on all interfaces                                         │
│ - Accessible from internet (if firewall allows)                     │
│ - Requires root/admin                                               │
│ - Configure agents with public IP or domain                         │
└─────────────────────────────────────────────────────────────────────┘

┌─ DOCKER CONTAINER ──────────────────────────────────────────────────┐
│ ./start_server.sh --host 0.0.0.0 --port 5000                       │
│ - Container maps port 5000 to host                                  │
│ - docker run -p 8443:5000 aether:latest                            │
│ - External agents connect to host IP:8443                           │
└─────────────────────────────────────────────────────────────────────┘

┌─ REVERSE PROXY / NGINX ─────────────────────────────────────────────┐
│ ./start_server.sh --host 127.0.0.1 --port 8443                     │
│ - Server runs locally on 127.0.0.1:8443                             │
│ - Nginx proxy on port 443 (public facing)                           │
│ - Agent connects to nginx hostname:443                              │
│ - Nginx forwards to backend 127.0.0.1:8443                          │
└─────────────────────────────────────────────────────────────────────┘

================================================================================
QUICK REFERENCE TABLE
================================================================================

Scenario              | Command
──────────────────────────────────────────────────────────────────────────
Local dev/test        | ./start_server.sh --host 127.0.0.1 --port 8443
LAN internal server   | ./start_server.sh --host 192.168.X.X --port 443
All interfaces        | ./start_server.sh --host 0.0.0.0 --port 443
Custom port only      | ./start_server.sh --port 9999
Custom host only      | ./start_server.sh --host 10.0.0.5
Both custom          | ./start_server.sh --host 10.0.0.5 --port 8443
Docker               | ./start_server.sh --host 0.0.0.0 --port 5000
Reverse proxy        | ./start_server.sh --host 127.0.0.1 --port 8443
Multiple instances   | ./start_server.sh --port 8001 &
                     | ./start_server.sh --port 8002 &

================================================================================
SUPPORT
================================================================================

For more information:
  - Check README.md for general information
  - Review config.json for other settings
  - Check server logs for error messages
  - See DEPLOYMENT_GUIDE.md for advanced setup
  - Review MODERN_STYLING_GUIDE.py for UI features

Available Commands (once server starts):
  help          - Show all commands
  help CMD      - Get help for specific command
  sessions      - List active agents
  interact ID   - Control an agent
  exit          - Shutdown server

================================================================================
"""

if __name__ == '__main__':
    print(STARTUP_GUIDE)
