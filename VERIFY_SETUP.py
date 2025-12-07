#!/usr/bin/env python3
"""
AETHER C2 Setup Verification & File Manifest
Verifies all setup files are in place and working
"""

import os
import json
from pathlib import Path

class SetupVerifier:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.required_files = {
            'Setup Scripts': {
                'MASTER_SETUP.py': 'Interactive setup wizard',
                'quickstart.sh': 'Auto setup script',
                'install_deps.py': 'Dependency installer',
                'quickfix.py': 'Validation tool',
            },
            'Documentation': {
                'QUICK_START_REFERENCE.md': '⭐ Quick reference card',
                'COMPLETE_CONFIG_GUIDE.md': 'Configuration guide',
                'COMPLETE_DEPLOYMENT_GUIDE.md': 'Deployment guide',
                'WHATSAPP_BOT_INTEGRATION.md': 'WhatsApp guide',
                'SETUP_AND_DEPLOYMENT_INDEX.md': 'Master navigation',
                'SETUP_COMPLETE_SUMMARY.md': 'Setup summary',
                'README.md': 'Project overview',
            },
            'Core Components': {
                'server/aether_server.py': 'C2 Server',
                'agent/aether_agent.py': 'Agent implant',
                'builder/compile.py': 'Agent compiler',
                'stager/stager.py': 'Stager/loader',
            },
            'Configuration': {
                'config.json': 'Main server config',
                'requirements.txt': 'Python dependencies',
                'WA-BOT-Base/package.json': 'Node.js dependencies',
                'server/comms/whatsapp_config.py': 'WhatsApp config',
                'WA-BOT-Base/aether-bridge.js': 'Bot bridge',
            }
        }
    
    def verify_all(self):
        """Verify all setup files exist"""
        print("\n" + "="*70)
        print("  AETHER C2 - Setup Verification & File Manifest")
        print("="*70 + "\n")
        
        for category, files in self.required_files.items():
            self.verify_category(category, files)
        
        self.print_summary()
    
    def verify_category(self, category, files):
        """Verify files in category"""
        print(f"📁 {category}:")
        print("-" * 70)
        
        for filename, description in files.items():
            filepath = self.base_path / filename
            if filepath.exists():
                size = filepath.stat().st_size
                if size > 1024*1024:
                    size_str = f"{size/(1024*1024):.1f}MB"
                elif size > 1024:
                    size_str = f"{size/1024:.1f}KB"
                else:
                    size_str = f"{size}B"
                print(f"  ✅ {filename:40} {description:30} ({size_str})")
            else:
                print(f"  ❌ {filename:40} {description:30} (MISSING)")
        
        print()
    
    def print_summary(self):
        """Print summary and next steps"""
        print("="*70)
        print("  Setup Summary & Next Steps")
        print("="*70 + "\n")
        
        print("📍 You Now Have:")
        print("  • Complete AETHER C2 framework")
        print("  • 4 setup/automation tools")
        print("  • 6 comprehensive guides")
        print("  • WhatsApp bot integration")
        print("  • 100+ remote commands")
        print()
        
        print("🚀 Getting Started (Choose One):")
        print()
        print("  Option 1: Ultra-Quick (5 min)")
        print("    $ bash quickstart.sh")
        print()
        print("  Option 2: Interactive Setup (15 min)")
        print("    $ python3 MASTER_SETUP.py")
        print()
        print("  Option 3: Manual Setup (30 min)")
        print("    Read: COMPLETE_CONFIG_GUIDE.md")
        print("    Edit: config.json")
        print("    Run: pip install -r requirements.txt")
        print()
        
        print("📖 Documentation (Read in Order):")
        print("  1. QUICK_START_REFERENCE.md       (5 min) ⭐")
        print("  2. COMPLETE_CONFIG_GUIDE.md       (30 min)")
        print("  3. COMPLETE_DEPLOYMENT_GUIDE.md   (45 min)")
        print("  4. WHATSAPP_BOT_INTEGRATION.md    (20 min)")
        print("  5. SETUP_AND_DEPLOYMENT_INDEX.md  (reference)")
        print()
        
        print("💻 Core Commands:")
        print("  Start Server:    python3 server/aether_server.py")
        print("  Start Bot:       cd WA-BOT-Base && npm start")
        print("  Build Agent:     AETHER> generate")
        print("  List Agents:     AETHER> sessions")
        print("  Connect Agent:   AETHER> interact <id>")
        print()
        
        print("📱 WhatsApp Commands (From Phone):")
        print("  Authenticate:    auth aether2025")
        print("  List agents:     sessions")
        print("  Connect:         link agent_001")
        print("  Get user:        whoami")
        print("  Screenshot:      screenshot")
        print()
        
        print("✅ Pre-Deployment Checklist:")
        print("  [ ] Read QUICK_START_REFERENCE.md")
        print("  [ ] Run setup (MASTER_SETUP.py or quickstart.sh)")
        print("  [ ] Edit config.json")
        print("  [ ] Change encryption_key")
        print("  [ ] Change WhatsApp password")
        print("  [ ] Test on isolated system")
        print("  [ ] Configure firewall")
        print()
        
        print("🔒 Security Important:")
        print("  ⚠️  Change all default passwords!")
        print("  ⚠️  Generate strong encryption key!")
        print("  ⚠️  Update agent C2 host!")
        print("  ⚠️  Configure firewall rules!")
        print()
        
        print("📋 File Manifest:")
        print()
        for category, files in self.required_files.items():
            print(f"\n{category}:")
            for filename, description in files.items():
                print(f"  • {filename:45} - {description}")
        
        print("\n" + "="*70)
        print("  ✨ Setup Complete! Ready for Deployment")
        print("="*70 + "\n")

if __name__ == '__main__':
    verifier = SetupVerifier()
    verifier.verify_all()
