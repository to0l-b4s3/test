#!/usr/bin/env python3
"""
Modern WhatsApp Message Formatter
Dope and modern WhatsApp responses for AETHER
"""

class WhatsAppFormatter:
    """Modern WhatsApp message formatting"""
    
    # Emojis
    class E:
        SUCCESS = '✅'
        ERROR = '❌'
        WARNING = '⚠️'
        INFO = 'ℹ️'
        FIRE = '🔥'
        ROCKET = '🚀'
        LOCK = '🔒'
        GEAR = '⚙️'
        SCREENSHOT = '📸'
        DOCUMENT = '📄'
        FOLDER = '📁'
        COMPUTER = '💻'
        NETWORK = '🌐'
        TIMER = '⏱️'
        CLOCK = '🕐'
        EYES = '👀'
        ALERT = '🚨'
        CHART = '📊'
        LINK = '🔗'
        ARROW = '➜'
        CHECK = '✓'
        LIST = '📋'
        CODE = '💻'
        SHIELD = '🛡️'
        TOOLS = '🛠️'
        BOMB = '💣'
        SKULL = '💀'
        STAR = '⭐'
        ZAPP = '⚡'
        CYCLE = '🔄'
    
    @staticmethod
    def bold(text):
        """Make text bold in WhatsApp"""
        return f"*{text}*"
    
    @staticmethod
    def italic(text):
        """Make text italic in WhatsApp"""
        return f"_{text}_"
    
    @staticmethod
    def code(text):
        """Format as code block"""
        return f"```{text}```"
    
    @staticmethod
    def success(title, message="", details=None):
        """Modern success message"""
        msg = f"{WhatsAppFormatter.E.SUCCESS} {WhatsAppFormatter.bold(title)}"
        if message:
            msg += f"\n{message}"
        if details:
            for key, value in details.items():
                msg += f"\n{WhatsAppFormatter.E.ARROW} {key}: {value}"
        return msg
    
    @staticmethod
    def error(title, message="", details=None):
        """Modern error message"""
        msg = f"{WhatsAppFormatter.E.ERROR} {WhatsAppFormatter.bold(title)}"
        if message:
            msg += f"\n{message}"
        if details:
            for key, value in details.items():
                msg += f"\n{WhatsAppFormatter.E.ARROW} {key}: {value}"
        return msg
    
    @staticmethod
    def warning(title, message=""):
        """Modern warning message"""
        msg = f"{WhatsAppFormatter.E.WARNING} {WhatsAppFormatter.bold(title)}"
        if message:
            msg += f"\n{message}"
        return msg
    
    @staticmethod
    def info(title, message=""):
        """Modern info message"""
        msg = f"{WhatsAppFormatter.E.INFO} {WhatsAppFormatter.bold(title)}"
        if message:
            msg += f"\n{message}"
        return msg
    
    @staticmethod
    def list_items(title, items, emoji=None):
        """Format list of items"""
        if emoji is None:
            emoji = WhatsAppFormatter.E.LIST
        
        msg = f"{emoji} {WhatsAppFormatter.bold(title)}\n\n"
        for item in items:
            msg += f"{WhatsAppFormatter.E.ARROW} {item}\n"
        return msg.strip()
    
    @staticmethod
    def table(title, headers, rows):
        """Format table data"""
        msg = f"{WhatsAppFormatter.E.CHART} {WhatsAppFormatter.bold(title)}\n\n"
        
        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Header
        header_row = " | ".join(f"{h:^{w}}" for h, w in zip(headers, col_widths))
        msg += f"`{header_row}`\n"
        
        # Separator
        sep = "-" * len(header_row)
        msg += f"`{sep}`\n"
        
        # Rows
        for row in rows:
            row_str = " | ".join(f"{str(c):^{w}}" for c, w in zip(row, col_widths))
            msg += f"`{row_str}`\n"
        
        return msg.strip()
    
    @staticmethod
    def command_result(command, result, status="success"):
        """Format command result"""
        status_emoji = WhatsAppFormatter.E.SUCCESS if status == "success" else WhatsAppFormatter.E.ERROR
        
        msg = f"{status_emoji} {WhatsAppFormatter.bold(f'Command: {command}')}\n\n"
        
        # Truncate result if too long (WhatsApp limit)
        max_length = 4000
        if len(result) > max_length:
            result = result[:max_length] + f"\n\n{WhatsAppFormatter.E.ALERT} Output truncated (too long)"
        
        if result:
            msg += f"{WhatsAppFormatter.code(result)}"
        
        return msg
    
    @staticmethod
    def sessions_list(sessions):
        """Format sessions list for WhatsApp"""
        if not sessions:
            return f"{WhatsAppFormatter.E.INFO} {WhatsAppFormatter.bold('No Active Sessions')}\nWaiting for agents to check in..."
        
        msg = f"{WhatsAppFormatter.E.COMPUTER} {WhatsAppFormatter.bold('Active Sessions')}\n\n"
        for session_id, info in sessions.items():
            msg += f"{WhatsAppFormatter.E.FIRE} {session_id}\n"
            msg += f"   {WhatsAppFormatter.E.COMPUTER} Host: {info.get('hostname', 'Unknown')}\n"
            msg += f"   {WhatsAppFormatter.E.EYES} User: {info.get('user', 'Unknown')}\n"
            msg += f"   {WhatsAppFormatter.E.CLOCK} Last Seen: {info.get('last_seen', 'Unknown')}\n\n"
        
        return msg.strip()
    
    @staticmethod
    def command_help(cmd_name, cmd_info):
        """Format detailed command help"""
        msg = f"{WhatsAppFormatter.E.INFO} {WhatsAppFormatter.bold(f'Help: {cmd_name}')}\n\n"
        
        msg += f"{WhatsAppFormatter.E.DOCUMENT} {WhatsAppFormatter.bold('Description:')}\n"
        msg += f"{cmd_info['description']}\n\n"
        
        msg += f"{WhatsAppFormatter.E.COMPUTER} {WhatsAppFormatter.bold('Usage:')}\n"
        msg += f"{WhatsAppFormatter.code(cmd_info['usage'])}\n"
        
        msg += f"{WhatsAppFormatter.E.GEAR} {WhatsAppFormatter.bold('Options:')}\n"
        msg += f"{cmd_info['options']}\n\n"
        
        msg += f"{WhatsAppFormatter.E.ARROW} {WhatsAppFormatter.bold('Example:')}\n"
        msg += f"{WhatsAppFormatter.code(cmd_info['example'])}\n"
        
        msg += f"{WhatsAppFormatter.E.CHART} {WhatsAppFormatter.bold('Output:')}\n"
        msg += f"{cmd_info['output']}\n"
        
        if 'output_location' in cmd_info:
            msg += f"\n{WhatsAppFormatter.E.FOLDER} {WhatsAppFormatter.bold('Location:')}\n"
            msg += f"{cmd_info['output_location']}\n"
        
        return msg
    
    @staticmethod
    def auth_help():
        """Authentication help"""
        return f"""{WhatsAppFormatter.E.LOCK} {WhatsAppFormatter.bold('Authentication')}

{WhatsAppFormatter.E.ARROW} Send: {WhatsAppFormatter.code('auth <password>')}
{WhatsAppFormatter.E.ARROW} Example: {WhatsAppFormatter.code('auth aether2025')}

{WhatsAppFormatter.E.SUCCESS} Once authenticated, you can use all commands
{WhatsAppFormatter.E.INFO} Type {WhatsAppFormatter.bold('help')} for command list"""
    
    @staticmethod
    def main_help():
        """Main help message"""
        return f"""{WhatsAppFormatter.E.ROCKET} {WhatsAppFormatter.bold('AETHER C2 - WhatsApp Control')}

{WhatsAppFormatter.E.ZAPP} {WhatsAppFormatter.bold('Quick Commands:')}
{WhatsAppFormatter.E.ARROW} auth <pass> - Authenticate
{WhatsAppFormatter.E.ARROW} sessions - List agents
{WhatsAppFormatter.E.ARROW} link <id> - Connect to agent
{WhatsAppFormatter.E.ARROW} whoami - Current user
{WhatsAppFormatter.E.ARROW} hostname - Computer name
{WhatsAppFormatter.E.ARROW} screenshot - Take screenshot
{WhatsAppFormatter.E.ARROW} ps - List processes
{WhatsAppFormatter.E.ARROW} ls <path> - List directory
{WhatsAppFormatter.E.ARROW} help <cmd> - Command help

{WhatsAppFormatter.E.INFO} Type {WhatsAppFormatter.bold('help')} for full command list"""
    
    @staticmethod
    def status_bar(agent_id, hostname, user, status="active"):
        """Modern status bar"""
        status_emoji = WhatsAppFormatter.E.SUCCESS if status == "active" else WhatsAppFormatter.E.WARNING
        
        return f"""{WhatsAppFormatter.E.COMPUTER} {WhatsAppFormatter.bold('Connected')}

{WhatsAppFormatter.E.FIRE} Session: {agent_id}
{WhatsAppFormatter.E.COMPUTER} Host: {hostname}
{WhatsAppFormatter.E.EYES} User: {user}
{status_emoji} Status: {status.upper()}"""
    
    @staticmethod
    def command_categories():
        """List command categories"""
        msg = f"{WhatsAppFormatter.E.LIST} {WhatsAppFormatter.bold('Command Categories')}\n\n"
        
        categories = {
            'System Information': ['whoami', 'hostname', 'sysinfo'],
            'File Operations': ['ls', 'cat', 'rm', 'mkdir', 'find'],
            'Intelligence': ['screenshot', 'webcam', 'audio', 'keylog', 'clipboard', 'browser'],
            'Process Management': ['ps', 'kill', 'inject'],
            'File Transfer': ['download', 'upload'],
            'Privilege & Persistence': ['getsystem', 'persist', 'uacbypass'],
            'Evasion': ['defender', 'amsibypass'],
            'Network': ['netstat', 'scan', 'portscan', 'smb'],
        }
        
        for category, commands in categories.items():
            msg += f"{WhatsAppFormatter.E.GEAR} {WhatsAppFormatter.bold(category)}\n"
            for cmd in commands:
                msg += f"   {WhatsAppFormatter.E.ARROW} {cmd}\n"
            msg += "\n"
        
        return msg.strip()
    
    @staticmethod
    def file_operation_result(operation, filepath, success=True):
        """Format file operation result"""
        emoji = WhatsAppFormatter.E.SUCCESS if success else WhatsAppFormatter.E.ERROR
        
        return f"""{emoji} {WhatsAppFormatter.bold(f'{operation} Complete')}

{WhatsAppFormatter.E.FOLDER} File: {filepath}
{WhatsAppFormatter.E.CLOCK} Time: {WhatsAppFormatter.italic('Just now')}"""
    
    @staticmethod
    def process_list(processes):
        """Format process list"""
        msg = f"{WhatsAppFormatter.E.COMPUTER} {WhatsAppFormatter.bold('Running Processes')}\n\n"
        
        # Limit to first 20 processes for WhatsApp
        for i, proc in enumerate(processes[:20], 1):
            msg += f"{i}. {proc['name']} (PID: {proc['pid']}, RAM: {proc['memory']}MB)\n"
        
        if len(processes) > 20:
            msg += f"\n{WhatsAppFormatter.E.ALERT} ... and {len(processes) - 20} more processes"
        
        return msg.strip()
    
    @staticmethod
    def progress(current, total, label="Operation"):
        """Modern progress message"""
        percent = int((current / total) * 100)
        filled = int(percent / 10)
        empty = 10 - filled
        bar = f"{'█' * filled}{'░' * empty}"
        
        return f"{WhatsAppFormatter.E.TIMER} {label}: {bar} {percent}%"


# Example formatting functions for specific commands
class CommandFormatters:
    """Specific formatters for individual commands"""
    
    @staticmethod
    def screenshot_result(filepath, size_mb):
        """Format screenshot result"""
        return f"""{WhatsAppFormatter.E.SCREENSHOT} {WhatsAppFormatter.bold('Screenshot Captured')}

{WhatsAppFormatter.E.FOLDER} Location: {filepath}
{WhatsAppFormatter.E.CHART} Size: {size_mb}MB
{WhatsAppFormatter.E.CLOCK} Captured: Just now

{WhatsAppFormatter.E.INFO} Image ready for download"""
    
    @staticmethod
    def webcam_result(filepath, size_mb):
        """Format webcam result"""
        return f"""{WhatsAppFormatter.E.EYES} {WhatsAppFormatter.bold('Webcam Image Captured')}

{WhatsAppFormatter.E.FOLDER} Location: {filepath}
{WhatsAppFormatter.E.CHART} Size: {size_mb}MB
{WhatsAppFormatter.E.ROCKET} Quality: High Resolution"""
    
    @staticmethod
    def keylog_result(logs_count, content_preview=""):
        """Format keylog result"""
        msg = f"""{WhatsAppFormatter.E.KEYBOARD} {WhatsAppFormatter.bold('Keylog Data')}

{WhatsAppFormatter.E.CHART} Keys Captured: {logs_count}"""
        
        if content_preview:
            msg += f"\n{WhatsAppFormatter.E.ARROW} Preview: {WhatsAppFormatter.code(content_preview[:100])}"
        
        return msg
    
    @staticmethod
    def browser_data_result(browsers_found):
        """Format browser data extraction result"""
        msg = f"""{WhatsAppFormatter.E.COMPUTER} {WhatsAppFormatter.bold('Browser Data Extracted')}

{WhatsAppFormatter.E.CHART} Browsers Found:"""
        
        for browser, data in browsers_found.items():
            msg += f"\n{WhatsAppFormatter.E.ARROW} {browser}"
            msg += f"\n   • Passwords: {data.get('passwords', 0)}"
            msg += f"\n   • Cookies: {data.get('cookies', 0)}"
            msg += f"\n   • History: {data.get('history', 0)}"
        
        return msg


if __name__ == '__main__':
    # Test
    print(WhatsAppFormatter.success("Operation Successful", "All systems ready"))
    print("\n")
    print(WhatsAppFormatter.list_items("Active Sessions", ["agent_001", "agent_002", "agent_003"]))
    print("\n")
    print(WhatsAppFormatter.command_help("screenshot", {
        'description': 'Capture screen',
        'usage': 'screenshot',
        'options': 'None',
        'example': 'screenshot',
        'output': 'PNG image',
        'output_location': '/screenshots/'
    }))
