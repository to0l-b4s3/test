#!/usr/bin/env python3
"""
AETHER Modern Styling System
Provides dope, modern responses for terminal and WhatsApp
"""

import sys
from datetime import datetime

class ModernStyle:
    """Modern styling for AETHER responses"""
    
    # ANSI Colors (Terminal)
    class Colors:
        RESET = '\033[0m'
        BOLD = '\033[1m'
        DIM = '\033[2m'
        ITALIC = '\033[3m'
        
        # Foreground
        BLACK = '\033[30m'
        RED = '\033[31m'
        GREEN = '\033[32m'
        YELLOW = '\033[33m'
        BLUE = '\033[34m'
        MAGENTA = '\033[35m'
        CYAN = '\033[36m'
        WHITE = '\033[37m'
        
        # Bright
        BRIGHT_RED = '\033[91m'
        BRIGHT_GREEN = '\033[92m'
        BRIGHT_YELLOW = '\033[93m'
        BRIGHT_BLUE = '\033[94m'
        BRIGHT_MAGENTA = '\033[95m'
        BRIGHT_CYAN = '\033[96m'
        
        # Background
        BG_BLACK = '\033[40m'
        BG_RED = '\033[41m'
        BG_GREEN = '\033[42m'
        BG_YELLOW = '\033[43m'
        BG_BLUE = '\033[44m'
        BG_MAGENTA = '\033[45m'
        BG_CYAN = '\033[46m'
    
    # Symbols
    class Symbols:
        SUCCESS = '✅'
        ERROR = '❌'
        WARNING = '⚠️'
        INFO = 'ℹ️'
        ARROW = '➜'
        BULLET = '●'
        STAR = '⭐'
        FIRE = '🔥'
        ROCKET = '🚀'
        LOCK = '🔒'
        GEAR = '⚙️'
        DOWNLOAD = '⬇️'
        UPLOAD = '⬆️'
        CHART = '📊'
        FOLDER = '📁'
        FILE = '📄'
        COMMAND = '💻'
        NETWORK = '🌐'
        TIMER = '⏱️'
        CLOCK = '🕐'
        TERMINAL = '▶️'
        EYES = '👀'
    
    @staticmethod
    def banner():
        """Modern AETHER banner"""
        return f"""{ModernStyle.Colors.CYAN}{ModernStyle.Colors.BOLD}
    ╔═╗╔═╗╔╦╗╔═╗╦  ╔═╗╦═╗
    ║ ╦╠═╝ ║ ╠═╝║  ║╣ ╠╦╝
    ╚═╝╩   ╩ ╩  ╩═╝╚═╝╩╚═
    
    {ModernStyle.Symbols.ROCKET} Universal Class Control v1.0
    {ModernStyle.Colors.YELLOW}[*] Modern & Stylized Edition
    {ModernStyle.Colors.RESET}"""
    
    @staticmethod
    def success(title, message="", details=None):
        """Format success message"""
        output = f"{ModernStyle.Colors.BRIGHT_GREEN}{ModernStyle.Symbols.SUCCESS} {title}{ModernStyle.Colors.RESET}"
        if message:
            output += f"\n  {ModernStyle.Colors.DIM}{message}{ModernStyle.Colors.RESET}"
        if details:
            for key, value in details.items():
                output += f"\n  {ModernStyle.Colors.CYAN}→{ModernStyle.Colors.RESET} {key}: {value}"
        return output
    
    @staticmethod
    def error(title, message="", details=None):
        """Format error message"""
        output = f"{ModernStyle.Colors.BRIGHT_RED}{ModernStyle.Symbols.ERROR} {title}{ModernStyle.Colors.RESET}"
        if message:
            output += f"\n  {ModernStyle.Colors.RED}{message}{ModernStyle.Colors.RESET}"
        if details:
            for key, value in details.items():
                output += f"\n  {ModernStyle.Colors.CYAN}→{ModernStyle.Colors.RESET} {key}: {value}"
        return output
    
    @staticmethod
    def warning(title, message=""):
        """Format warning message"""
        return f"{ModernStyle.Colors.BRIGHT_YELLOW}{ModernStyle.Symbols.WARNING} {title}{ModernStyle.Colors.RESET}\n  {message}"
    
    @staticmethod
    def info(title, message=""):
        """Format info message"""
        return f"{ModernStyle.Colors.BRIGHT_BLUE}{ModernStyle.Symbols.INFO} {title}{ModernStyle.Colors.RESET}\n  {ModernStyle.Colors.DIM}{message}{ModernStyle.Colors.RESET}"
    
    @staticmethod
    def header(text, emoji=""):
        """Modern header"""
        border = f"{ModernStyle.Colors.CYAN}{'─' * 70}{ModernStyle.Colors.RESET}"
        header_text = f"{ModernStyle.Colors.BOLD}{ModernStyle.Colors.CYAN}{emoji} {text}{ModernStyle.Colors.RESET}"
        return f"\n{border}\n{header_text}\n{border}\n"
    
    @staticmethod
    def command_response(command, result, duration=None):
        """Format command response"""
        output = f"{ModernStyle.Colors.GREEN}[✓]{ModernStyle.Colors.RESET} {ModernStyle.Colors.BOLD}{command}{ModernStyle.Colors.RESET}\n"
        if result:
            output += f"{result}\n"
        if duration:
            output += f"{ModernStyle.Colors.DIM}⏱️  {duration}ms{ModernStyle.Colors.RESET}\n"
        return output
    
    @staticmethod
    def table(headers, rows):
        """Format data as table"""
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Header
        header_row = " | ".join(f"{h:{w}}" for h, w in zip(headers, col_widths))
        separator = "─" * len(header_row)
        
        output = f"{ModernStyle.Colors.CYAN}{separator}{ModernStyle.Colors.RESET}\n"
        output += f"{ModernStyle.Colors.BOLD}{ModernStyle.Colors.CYAN}{header_row}{ModernStyle.Colors.RESET}\n"
        output += f"{ModernStyle.Colors.CYAN}{separator}{ModernStyle.Colors.RESET}\n"
        
        # Rows
        for row in rows:
            row_str = " | ".join(f"{str(c):{w}}" for c, w in zip(row, col_widths))
            output += f"{row_str}\n"
        
        output += f"{ModernStyle.Colors.CYAN}{separator}{ModernStyle.Colors.RESET}\n"
        return output
    
    @staticmethod
    def session_box(session_id, hostname, user, status="active"):
        """Format session info box"""
        status_color = ModernStyle.Colors.BRIGHT_GREEN if status == "active" else ModernStyle.Colors.BRIGHT_YELLOW
        
        box = f"""
{ModernStyle.Colors.CYAN}┌─ {ModernStyle.Symbols.COMMAND} Session Info {ModernStyle.Colors.RESET}
{ModernStyle.Colors.CYAN}│{ModernStyle.Colors.RESET}
{ModernStyle.Colors.CYAN}├─{ModernStyle.Colors.RESET} {ModernStyle.Symbols.FIRE} Session: {ModernStyle.Colors.BOLD}{session_id}{ModernStyle.Colors.RESET}
{ModernStyle.Colors.CYAN}├─{ModernStyle.Colors.RESET} {ModernStyle.Symbols.FOLDER} Host: {hostname}
{ModernStyle.Colors.CYAN}├─{ModernStyle.Colors.RESET} {ModernStyle.Symbols.EYES} User: {user}
{ModernStyle.Colors.CYAN}└─{ModernStyle.Colors.RESET} {status_color}{ModernStyle.Symbols.BULLET} {status.upper()}{ModernStyle.Colors.RESET}
"""
        return box


class WhatsAppStyle:
    """Modern styling for WhatsApp messages"""
    
    # Emojis for WhatsApp
    class Emojis:
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
        SUCCESS_MARK = '✓'
        DOUBLE_CHECK = '✓✓'
        EYES = '👀'
        ALERT = '🚨'
        CHART = '📊'
        LINK = '🔗'
        ARROW = '➜'
        CHECK = '✓'
    
    @staticmethod
    def success(title, details=""):
        """WhatsApp success response"""
        msg = f"{WhatsAppStyle.Emojis.SUCCESS} *{title}*"
        if details:
            msg += f"\n{details}"
        return msg
    
    @staticmethod
    def error(title, details=""):
        """WhatsApp error response"""
        msg = f"{WhatsAppStyle.Emojis.ERROR} *{title}*"
        if details:
            msg += f"\n{details}"
        return msg
    
    @staticmethod
    def info(title, details=""):
        """WhatsApp info response"""
        msg = f"{WhatsAppStyle.Emojis.INFO} *{title}*"
        if details:
            msg += f"\n{details}"
        return msg
    
    @staticmethod
    def list_items(title, items):
        """WhatsApp formatted list"""
        msg = f"{WhatsAppStyle.Emojis.CHART} *{title}*\n\n"
        for i, item in enumerate(items, 1):
            msg += f"{WhatsAppStyle.Emojis.ARROW} {item}\n"
        return msg.strip()
    
    @staticmethod
    def code_block(content):
        """WhatsApp code block"""
        return f"```\n{content}\n```"
    
    @staticmethod
    def bold(text):
        """WhatsApp bold"""
        return f"*{text}*"
    
    @staticmethod
    def italic(text):
        """WhatsApp italic"""
        return f"_{text}_"
    
    @staticmethod
    def strikethrough(text):
        """WhatsApp strikethrough"""
        return f"~{text}~"
    
    @staticmethod
    def command_help(cmd_name, description, usage, options, example, output_location=""):
        """Format command help for WhatsApp"""
        msg = f"""{WhatsAppStyle.Emojis.INFO} *Command Help: {cmd_name}*

{WhatsAppStyle.Emojis.DOCUMENT} *Description:*
{description}

{WhatsAppStyle.Emojis.COMPUTER} *Usage:*
{usage}

{WhatsAppStyle.Emojis.GEAR} *Options:*
{options}

{WhatsAppStyle.Emojis.ARROW} *Example:*
{example}"""
        
        if output_location:
            msg += f"\n\n{WhatsAppStyle.Emojis.FOLDER} *Output Location:*\n{output_location}"
        
        return msg


class TerminalPrinter:
    """Modern terminal printer"""
    
    @staticmethod
    def print_section(title, emoji="📌"):
        """Print section header"""
        print(f"\n{ModernStyle.Colors.CYAN}{'═' * 70}{ModernStyle.Colors.RESET}")
        print(f"{ModernStyle.Colors.BOLD}{emoji} {title}{ModernStyle.Colors.RESET}")
        print(f"{ModernStyle.Colors.CYAN}{'═' * 70}{ModernStyle.Colors.RESET}\n")
    
    @staticmethod
    def print_item(icon, label, value):
        """Print labeled item"""
        print(f"  {icon} {ModernStyle.Colors.BOLD}{label}:{ModernStyle.Colors.RESET} {value}")
    
    @staticmethod
    def print_status(running=True):
        """Print server status"""
        status = f"{ModernStyle.Colors.BRIGHT_GREEN}● RUNNING{ModernStyle.Colors.RESET}" if running else f"{ModernStyle.Colors.BRIGHT_RED}● STOPPED{ModernStyle.Colors.RESET}"
        return status
    
    @staticmethod
    def print_progress(current, total, label="Progress"):
        """Print progress bar"""
        percent = (current / total) * 100
        filled = int(20 * current / total)
        bar = f"{'█' * filled}{'░' * (20 - filled)}"
        
        return f"{label}: {ModernStyle.Colors.CYAN}{bar}{ModernStyle.Colors.RESET} {percent:.0f}%"


if __name__ == '__main__':
    # Demo
    print(ModernStyle.banner())
    print(ModernStyle.header("Modern Styling System", "🎨"))
    print(ModernStyle.success("System Initialized", "All systems ready for operation"))
    print(ModernStyle.info("Ready", "AETHER is now listening for connections"))
    print(ModernStyle.session_box("agent_001", "DESKTOP-XYZ", "SYSTEM"))
    
    print(WhatsAppStyle.command_help(
        "screenshot",
        "Capture a screenshot of the target screen",
        "screenshot",
        "No options available",
        "screenshot",
        "/var/lib/aether/screenshots/"
    ))
