#!/usr/bin/env python3
"""
AETHER Setup Verification Script
Verifies that all components are properly configured and ready to run
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class Verifier:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.successes = []
    
    def check_python(self):
        """Check Python availability"""
        print("\n📦 Checking Python...")
        try:
            result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.successes.append(f"Python found: {version}")
                print(f"✅ {version}")
                return True
        except:
            pass
        
        self.errors.append("Python not found or not in PATH")
        print("❌ Python not found")
        return False
    
    def check_nodejs(self):
        """Check Node.js availability"""
        print("\n📦 Checking Node.js...")
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.successes.append(f"Node.js found: {version}")
                print(f"✅ {version}")
                return True
        except:
            pass
        
        self.warnings.append("Node.js not found (optional, only needed for WhatsApp bot)")
        print("⚠️ Node.js not found (optional)")
        return False
    
    def check_npm(self):
        """Check npm availability"""
        if not os.path.exists('WA-BOT-Base'):
            self.warnings.append("WA-BOT-Base directory not found")
            return False
        
        print("\n📦 Checking npm...")
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.successes.append(f"npm found: {version}")
                print(f"✅ {version}")
                return True
        except:
            pass
        
        self.warnings.append("npm not found (needed for WhatsApp bot)")
        print("⚠️ npm not found")
        return False
    
    def check_files(self):
        """Check required files exist"""
        print("\n📁 Checking required files...")
        
        required_files = [
            'config.json',
            'server/aether_server.py',
            'agent/aether_agent.py',
            'builder/compile.py',
            'stager/stager.py',
            'AETHER_SETUP.py',
            'WA-BOT-Base/main.js',
            'WA-BOT-Base/index.js',
            'WA-BOT-Base/handler.js',
            'requirements.txt',
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path}")
                self.successes.append(f"Found: {file_path}")
            else:
                print(f"❌ {file_path}")
                self.errors.append(f"Missing: {file_path}")
        
        return len([f for f in required_files if os.path.exists(f)]) == len(required_files)
    
    def check_config(self):
        """Check config.json is valid"""
        print("\n⚙️ Checking configuration...")
        
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            print("✅ config.json is valid JSON")
            self.successes.append("config.json is valid")
            
            # Check for key sections
            sections = ['c2', 'agent', 'builder', 'stager']
            for section in sections:
                if section in config:
                    print(f"✅ config.json has '{section}' section")
                else:
                    print(f"⚠️ config.json missing '{section}' section")
                    self.warnings.append(f"config.json missing '{section}' section")
            
            return True
        except json.JSONDecodeError:
            self.errors.append("config.json is not valid JSON")
            print("❌ config.json is not valid JSON")
            return False
        except FileNotFoundError:
            self.errors.append("config.json not found")
            print("❌ config.json not found")
            return False
    
    def check_python_deps(self):
        """Check Python dependencies"""
        print("\n📚 Checking Python dependencies...")
        
        if not os.path.exists('requirements.txt'):
            self.warnings.append("requirements.txt not found")
            print("⚠️ requirements.txt not found")
            return False
        
        print("✅ requirements.txt found")
        self.successes.append("requirements.txt found")
        
        try:
            with open('requirements.txt', 'r') as f:
                deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            print(f"✅ Found {len(deps)} dependencies")
            self.successes.append(f"Found {len(deps)} Python dependencies")
            
            return True
        except Exception as e:
            self.errors.append(f"Failed to read requirements.txt: {str(e)}")
            print(f"❌ Failed to read requirements.txt: {str(e)}")
            return False
    
    def check_node_deps(self):
        """Check Node.js dependencies"""
        print("\n📚 Checking Node.js dependencies...")
        
        if not os.path.exists('WA-BOT-Base/package.json'):
            self.warnings.append("WA-BOT-Base/package.json not found")
            print("⚠️ WA-BOT-Base/package.json not found")
            return False
        
        try:
            with open('WA-BOT-Base/package.json', 'r') as f:
                package = json.load(f)
            
            deps = package.get('dependencies', {})
            print(f"✅ Found {len(deps)} Node.js dependencies")
            self.successes.append(f"Found {len(deps)} Node.js dependencies")
            
            if os.path.exists('WA-BOT-Base/node_modules'):
                print("✅ node_modules installed")
                self.successes.append("Node.js dependencies installed")
                return True
            else:
                self.warnings.append("WA-BOT-Base/node_modules not installed (run: cd WA-BOT-Base && npm install)")
                print("⚠️ node_modules not installed")
                print("   Run: cd WA-BOT-Base && npm install")
                return False
        except Exception as e:
            self.errors.append(f"Failed to read package.json: {str(e)}")
            print(f"❌ Failed to read package.json: {str(e)}")
            return False
    
    def check_directories(self):
        """Check required directories"""
        print("\n📂 Checking directories...")
        
        required_dirs = [
            'server',
            'agent',
            'builder',
            'stager',
            'WA-BOT-Base',
            'data',
        ]
        
        for dir_path in required_dirs:
            if os.path.isdir(dir_path):
                print(f"✅ {dir_path}/")
                self.successes.append(f"Found directory: {dir_path}")
            else:
                print(f"❌ {dir_path}/ (missing)")
                self.errors.append(f"Missing directory: {dir_path}")
        
        return len([d for d in required_dirs if os.path.isdir(d)]) == len(required_dirs)
    
    def check_imports(self):
        """Check key Python files can be imported"""
        print("\n🔍 Checking Python imports...")
        
        sys.path.insert(0, '.')
        
        # Try importing key modules
        modules = {
            'server.aether_server': 'server/aether_server.py',
            'agent.aether_agent': 'agent/aether_agent.py',
            'builder.compile': 'builder/compile.py',
        }
        
        for module_name, file_path in modules.items():
            try:
                __import__(module_name.split('.')[0])
                print(f"✅ {module_name}")
                self.successes.append(f"Can import {module_name}")
            except ImportError as e:
                print(f"⚠️ {module_name}: {str(e)}")
                self.warnings.append(f"Import warning for {module_name}: {str(e)}")
            except Exception as e:
                print(f"⚠️ {module_name}: {str(e)}")
                self.warnings.append(f"Error importing {module_name}: {str(e)}")
    
    def run_all_checks(self):
        """Run all verification checks"""
        print("\n" + "="*80)
        print("AETHER SETUP VERIFICATION".center(80))
        print("="*80)
        
        # Run checks
        self.check_python()
        self.check_nodejs()
        self.check_npm()
        self.check_files()
        self.check_directories()
        self.check_config()
        self.check_python_deps()
        self.check_node_deps()
        self.check_imports()
        
        # Print summary
        print("\n" + "="*80)
        print("VERIFICATION SUMMARY".center(80))
        print("="*80)
        
        print(f"\n✅ Successes: {len(self.successes)}")
        for success in self.successes[:5]:
            print(f"   • {success}")
        if len(self.successes) > 5:
            print(f"   ... and {len(self.successes) - 5} more")
        
        if self.warnings:
            print(f"\n⚠️ Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.errors:
            print(f"\n❌ Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"   • {error}")
        
        print("\n" + "="*80)
        
        if self.errors:
            print("\n⚠️ ISSUES FOUND - Please fix the errors above before proceeding")
            return False
        elif self.warnings:
            print("\n✅ Setup looks good, but there are some warnings to address")
            return True
        else:
            print("\n✅ ALL CHECKS PASSED - System is ready to use!")
            return True

if __name__ == '__main__':
    verifier = Verifier()
    success = verifier.run_all_checks()
    sys.exit(0 if success else 1)
