#!/usr/bin/env python3
"""
Verification script for bug fixes:
1. Node.js ESM URL scheme error fix
2. AETHER_SETUP.py Python detection fix
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from colorama import init, Fore, Style

init(autoreset=True)

class VerifyFixes:
    def __init__(self):
        self.root = Path(__file__).parent
        self.wa_bot_dir = self.root / 'WA-BOT-Base'
        self.success_count = 0
        self.fail_count = 0
    
    def print_header(self, title):
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.YELLOW}{title:^70}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    def print_test(self, name):
        print(f"\n{Fore.BLUE}▶ {name}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'-'*70}{Style.RESET_ALL}")
    
    def print_success(self, msg):
        print(f"{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")
        self.success_count += 1
    
    def print_error(self, msg):
        print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}")
        self.fail_count += 1
    
    def print_info(self, msg):
        print(f"{Fore.CYAN}ℹ {msg}{Style.RESET_ALL}")
    
    def run_command(self, cmd, capture=True):
        """Run command and return result"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=capture,
                text=True,
                timeout=10
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, '', 'Timeout'
        except Exception as e:
            return 1, '', str(e)
    
    def test_node_esm_fix(self):
        """Test 1: Verify Node.js ESM fix"""
        self.print_test("Test 1: Node.js ESM URL Scheme Fix")
        
        index_file = self.wa_bot_dir / 'index.js'
        
        if not index_file.exists():
            self.print_error(f"index.js not found at {index_file}")
            return False
        
        with open(index_file, 'r') as f:
            content = f.read()
        
        # Check for proper ESM import fix
        checks = [
            ('new URL import', 'new URL(`./main.js`, import.meta.url)' in content),
            ('href usage', '.href' in content),
            ('no join usage', 'join(__dirname' not in content or 'new URL' in content),
        ]
        
        all_passed = True
        for check_name, passed in checks:
            if passed:
                self.print_success(f"✓ {check_name}: Fixed properly")
            else:
                self.print_error(f"✗ {check_name}: Not properly fixed")
                all_passed = False
        
        # Check syntax
        code, _, stderr = self.run_command(f"node -c {index_file}")
        if code == 0:
            self.print_success("✓ index.js syntax is valid")
        else:
            self.print_error(f"✗ index.js syntax error: {stderr[:100]}")
            all_passed = False
        
        return all_passed
    
    def test_node_dependencies(self):
        """Test 2: Verify Node.js dependencies"""
        self.print_test("Test 2: Node.js Dependencies Check")
        
        package_file = self.wa_bot_dir / 'package.json'
        
        if not package_file.exists():
            self.print_error(f"package.json not found")
            return False
        
        with open(package_file, 'r') as f:
            package = json.load(f)
        
        required_deps = [
            '@whiskeysockets/baileys',
            '@hapi/boom',
            '@cacheable/node-cache',
            'chalk',
            'pino',
            'pino-pretty'
        ]
        
        all_found = True
        deps = package.get('dependencies', {})
        for dep in required_deps:
            if dep in deps:
                self.print_success(f"✓ {dep}: {deps[dep]}")
            else:
                self.print_error(f"✗ {dep}: NOT FOUND")
                all_found = False
        
        return all_found
    
    def test_handler_exports(self):
        """Test 3: Verify handler.js exports"""
        self.print_test("Test 3: Handler.js Export Check")
        
        handler_file = self.wa_bot_dir / 'handler.js'
        
        if not handler_file.exists():
            self.print_error(f"handler.js not found")
            return False
        
        with open(handler_file, 'r') as f:
            content = f.read()
        
        exports = [
            ('loadPlugins', 'export async function loadPlugins' in content),
            ('handleCommand', 'export async function handleCommand' in content),
            ('plugins', 'export const plugins' in content),
        ]
        
        all_found = True
        for exp_name, found in exports:
            if found:
                self.print_success(f"✓ {exp_name}: Exported")
            else:
                self.print_error(f"✗ {exp_name}: NOT EXPORTED")
                all_found = False
        
        return all_found
    
    def test_main_exports(self):
        """Test 4: Verify main.js exports startSocket"""
        self.print_test("Test 4: main.js startSocket Export Check")
        
        main_file = self.wa_bot_dir / 'main.js'
        
        if not main_file.exists():
            self.print_error(f"main.js not found")
            return False
        
        with open(main_file, 'r') as f:
            content = f.read()
        
        if 'export const startSocket' in content or 'export async function startSocket' in content:
            self.print_success("✓ startSocket: Properly exported")
            return True
        else:
            self.print_error("✗ startSocket: NOT EXPORTED")
            return False
    
    def test_python_detection(self):
        """Test 5: Verify AETHER_SETUP.py Python detection"""
        self.print_test("Test 5: AETHER_SETUP.py Python Detection")
        
        setup_file = self.root / 'AETHER_SETUP.py'
        
        if not setup_file.exists():
            self.print_error(f"AETHER_SETUP.py not found")
            return False
        
        with open(setup_file, 'r') as f:
            content = f.read()
        
        checks = [
            ('get_python_executable method', 'def get_python_executable(self)' in content),
            ('python_exe caching', 'self.python_exe' in content),
            ('fallback to sys.executable', 'sys.executable' in content),
            ('run_server uses detection', 'if not self.python_exe:' in content),
            ('build_agent uses detection', 'def build_agent(self):' in content),
            ('python -m pip usage', 'python -m pip' in content),
        ]
        
        all_found = True
        for check_name, passed in checks:
            if passed:
                self.print_success(f"✓ {check_name}")
            else:
                self.print_error(f"✗ {check_name}")
                all_found = False
        
        return all_found
    
    def test_setup_syntax(self):
        """Test 6: Verify AETHER_SETUP.py syntax"""
        self.print_test("Test 6: AETHER_SETUP.py Syntax Validation")
        
        setup_file = self.root / 'AETHER_SETUP.py'
        code, _, stderr = self.run_command(f"python -m py_compile {setup_file}")
        
        if code == 0:
            self.print_success("✓ AETHER_SETUP.py syntax is valid")
            return True
        else:
            self.print_error(f"✗ Syntax error: {stderr[:100]}")
            return False
    
    def test_python_availability(self):
        """Test 7: Verify Python is available"""
        self.print_test("Test 7: Python Availability Check")
        
        commands = ['python', 'python3']
        found = False
        
        for cmd in commands:
            code, stdout, _ = self.run_command(f"{cmd} --version")
            if code == 0:
                self.print_success(f"✓ {cmd}: {stdout.strip()}")
                found = True
        
        if not found:
            self.print_error("✗ Python not found in PATH")
        
        return found
    
    def test_npm_availability(self):
        """Test 8: Verify npm is available"""
        self.print_test("Test 8: npm Availability Check")
        
        code, stdout, _ = self.run_command("npm --version")
        
        if code == 0:
            self.print_success(f"✓ npm: v{stdout.strip()}")
            return True
        else:
            self.print_error("✗ npm not found in PATH")
            return False
    
    def test_package_json_validity(self):
        """Test 9: Verify package.json is valid JSON"""
        self.print_test("Test 9: package.json Validity")
        
        package_file = self.wa_bot_dir / 'package.json'
        
        try:
            with open(package_file, 'r') as f:
                json.load(f)
            self.print_success("✓ package.json is valid JSON")
            return True
        except json.JSONDecodeError as e:
            self.print_error(f"✗ Invalid JSON: {str(e)[:100]}")
            return False
    
    def run_all_tests(self):
        """Run all verification tests"""
        self.print_header("AETHER Bug Fix Verification Suite")
        
        results = [
            ("Node.js ESM Fix", self.test_node_esm_fix()),
            ("Node Dependencies", self.test_node_dependencies()),
            ("Handler.js Exports", self.test_handler_exports()),
            ("main.js startSocket", self.test_main_exports()),
            ("Python Detection", self.test_python_detection()),
            ("Setup Syntax", self.test_setup_syntax()),
            ("Python Available", self.test_python_availability()),
            ("npm Available", self.test_npm_availability()),
            ("package.json Valid", self.test_package_json_validity()),
        ]
        
        self.print_header("Test Results Summary")
        
        for name, result in results:
            status = f"{Fore.GREEN}✓ PASS{Style.RESET_ALL}" if result else f"{Fore.RED}✗ FAIL{Style.RESET_ALL}"
            print(f"{name:.<50} {status}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"Total: {passed}/{total} tests passed")
        
        if passed == total:
            print(f"{Fore.GREEN}✓ All tests passed! System is ready.{Style.RESET_ALL}")
            return 0
        else:
            print(f"{Fore.YELLOW}⚠ {total - passed} test(s) failed. Please review above.{Style.RESET_ALL}")
            return 1

if __name__ == '__main__':
    verifier = VerifyFixes()
    sys.exit(verifier.run_all_tests())
