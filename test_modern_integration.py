#!/usr/bin/env python3
"""
Test script to demonstrate modern styling integration in AETHER C2.
Shows terminal styling, help system, and WhatsApp formatting.
"""

import sys
sys.path.insert(0, '/workspaces/test/server')

from modern_style import ModernStyle, TerminalPrinter
from command_help import get_command_help, get_commands_by_category
from whatsapp_formatter import WhatsAppFormatter

def test_banner():
    """Test the modern banner."""
    print("\n" + "="*80)
    print("TEST 1: Modern Banner")
    print("="*80 + "\n")
    print(ModernStyle.banner())

def test_help_system():
    """Test the help system."""
    print("\n" + "="*80)
    print("TEST 2: Help System")
    print("="*80 + "\n")
    
    # Show single command help
    print("Single Command Help (screenshot):\n")
    help_info = get_command_help('screenshot')
    print(ModernStyle.header(f"Help: screenshot", "📖"))
    print(f"{ModernStyle.Symbols.FILE} Description:\n  {help_info['description']}\n")
    print(f"{ModernStyle.Symbols.COMMAND} Usage:\n  {help_info['usage']}\n")
    print(f"{ModernStyle.Symbols.GEAR} Options:\n  {help_info['options']}\n")
    print(f"{ModernStyle.Symbols.ARROW} Example:\n  {help_info['example']}\n")
    
    # Show commands by category
    print("\n\nCommands by Category:\n")
    print(ModernStyle.header("Agent Commands", "💻"))
    categories = get_commands_by_category()
    for category in sorted(categories.keys()):
        commands = categories[category]
        print(f"\n{ModernStyle.Colors.BRIGHT_CYAN}{category}{ModernStyle.Colors.RESET}")
        print(f"  {' '.join(f'{cmd:<15}' for cmd in commands)}")

def test_terminal_messages():
    """Test various terminal message styles."""
    print("\n" + "="*80)
    print("TEST 3: Terminal Message Styles")
    print("="*80 + "\n")
    
    print("SUCCESS MESSAGE:")
    print(ModernStyle.success("Command Executed", "Screenshot captured successfully", 
                            {"File": "screenshot_123.png", "Size": "2.4 MB", "Time": "0.5s"}))
    
    print("\n\nERROR MESSAGE:")
    print(ModernStyle.error("Permission Denied", "Cannot access C:\\Windows\\System32"))
    
    print("\n\nWARNING MESSAGE:")
    print(ModernStyle.warning("UAC Detected", "User Account Control is enabled on target"))
    
    print("\n\nINFO MESSAGE:")
    print(ModernStyle.info("Agent Connected", "New agent from 192.168.1.100 connected"))

def test_session_box():
    """Test the session information box."""
    print("\n" + "="*80)
    print("TEST 4: Session Information Box")
    print("="*80 + "\n")
    
    session_info = {
        'address': '192.168.1.100',
        'hostname': 'DESKTOP-ABC123',
        'user': 'Administrator',
        'os': 'Windows 10',
        'privilege': 'admin',
        'last_seen': '2024-01-15T14:23:45'
    }
    
    print(ModernStyle.session_box('agent_001', session_info['hostname'], session_info['user']))

def test_whatsapp_messages():
    """Test WhatsApp formatting."""
    print("\n" + "="*80)
    print("TEST 5: WhatsApp Message Formatting")
    print("="*80 + "\n")
    
    print("Text Formatting Examples:")
    print(f"  Bold: {WhatsAppFormatter.bold('Important')}")
    print(f"  Italic: {WhatsAppFormatter.italic('Note')}")
    print(f"  Code: {WhatsAppFormatter.code('python -c')}\n")
    
    print("Status Message - Success:")
    print(WhatsAppFormatter.success("Data Exfiltration", "All files transferred successfully"))
    
    print("\n\nStatus Message - Error:")
    print(WhatsAppFormatter.error("Connection Failed", "Target host unreachable"))
    
    print("\n\nCommand Help:")
    help_info = get_command_help('keylog')
    msg = WhatsAppFormatter.command_help('keylog', help_info)
    print(msg[:500] + "..." if len(msg) > 500 else msg)

def test_command_table():
    """Test table formatting."""
    print("\n" + "="*80)
    print("TEST 6: Modern Table Formatting")
    print("="*80 + "\n")
    
    headers = ['Command', 'Category', 'Risk Level', 'Status']
    rows = [
        ['screenshot', 'Intelligence', '🟡 Medium', '✅ Ready'],
        ['keylog', 'Intelligence', '🟠 High', '✅ Ready'],
        ['wifi', 'Intelligence', '🟡 Medium', '✅ Ready'],
        ['persist', 'Persistence', '🔴 Critical', '⚠️ Beta'],
        ['defender', 'Evasion', '🔴 Critical', '✅ Ready'],
    ]
    
    print(ModernStyle.table(headers, rows))

def main():
    """Run all tests."""
    print("\n")
    print(f"{ModernStyle.Colors.BRIGHT_CYAN}{ModernStyle.Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════════════════╗")
    print("║       AETHER C2 - MODERN STYLING INTEGRATION TEST SUITE                    ║")
    print("╚════════════════════════════════════════════════════════════════════════════╝")
    print(ModernStyle.Colors.RESET)
    
    try:
        test_banner()
        test_help_system()
        test_terminal_messages()
        test_session_box()
        test_whatsapp_messages()
        test_command_table()
        
        # Final summary
        print("\n" + "="*80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(ModernStyle.success("Integration Complete", "All modern styling modules working perfectly!"))
        print(f"\n{ModernStyle.info('Next Steps', 'Deploy these modules to production and monitor terminal output')}\n")
        
    except Exception as e:
        print(ModernStyle.error("Test Failed", str(e)))
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
