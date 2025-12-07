#!/usr/bin/env python3
"""
WhatsApp Bridge for AETHER C2 Framework
Lightweight bridge connecting Node.js Baileys bot to Python AETHER
"""
import requests
import json
import threading
import time
from datetime import datetime
from colorama import Fore, Style
from typing import Dict, List, Optional, Any


class WhatsAppBridge:
    """
    WhatsApp Bridge for AETHER C2
    Connects Baileys bot to AETHER agents
    """
    
    def __init__(self, bot_url: str = "http://localhost:3000", 
                 bot_api_key: str = "",
                 session_manager=None,
                 command_suite=None):
        """
        Initialize WhatsApp Bridge
        
        Args:
            bot_url: URL of Baileys bot
            bot_api_key: API key for authentication
            session_manager: AETHER SessionManager instance
            command_suite: AETHER CommandSuite instance
        """
        self.bot_url = bot_url
        self.bot_api_key = bot_api_key
        self.sessions = session_manager
        self.command_suite = command_suite
        self.running = False
        self.authorized_users = set()
        self.user_sessions = {}
        self.command_history = {}
        
        print(f"{Fore.CYAN}[*] WhatsApp Bridge initialized - {bot_url}{Style.RESET_ALL}")
    
    def authorize_user(self, phone: str) -> bool:
        """Authorize a WhatsApp user"""
        self.authorized_users.add(phone)
        print(f"{Fore.GREEN}[+] Authorized: {phone}{Style.RESET_ALL}")
        return True
    
    def revoke_user(self, phone: str) -> bool:
        """Revoke WhatsApp user"""
        if phone in self.authorized_users:
            self.authorized_users.discard(phone)
            self.user_sessions.pop(phone, None)
            print(f"{Fore.YELLOW}[-] Revoked: {phone}{Style.RESET_ALL}")
            return True
        return False
    
    def is_authorized(self, phone: str) -> bool:
        """Check if user is authorized"""
        return phone in self.authorized_users
    
    def link_session(self, phone: str, session_id: str) -> bool:
        """Link user to session"""
        if self.sessions and self.sessions.get(session_id):
            self.user_sessions[phone] = session_id
            print(f"{Fore.GREEN}[+] Linked {phone} to {session_id}{Style.RESET_ALL}")
            return True
        return False
    
    def send_message(self, phone: str, message: str) -> bool:
        """Send WhatsApp message"""
        try:
            payload = {
                'to': phone,
                'message': message,
                'api_key': self.bot_api_key
            }
            response = requests.post(
                f"{self.bot_url}/api/send-message",
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"{Fore.RED}[-] Send failed: {e}{Style.RESET_ALL}")
            return False
    
    def execute_command(self, phone: str, command_text: str) -> Dict[str, Any]:
        """Execute command for user"""
        if not self.is_authorized(phone):
            return {'status': 'error', 'message': '❌ Unauthorized'}
        
        session_id = self.user_sessions.get(phone)
        if not session_id:
            return {'status': 'error', 'message': '❌ No session linked'}
        
        try:
            if self.command_suite:
                result = self.command_suite.execute(session_id, command_text)
            else:
                result = {'error': 'Command suite not available'}
            
            return {'status': 'success', 'result': result}
        except Exception as e:
            return {'status': 'error', 'message': f'❌ Error: {str(e)}'}
    
    def get_status(self) -> Dict[str, Any]:
        """Get bridge status"""
        return {
            'running': self.running,
            'bot_url': self.bot_url,
            'authorized_users': len(self.authorized_users),
            'active_sessions': len(self.user_sessions),
        }


class WhatsAppIntegration:
    """Manager for WhatsApp integration"""
    
    def __init__(self, config: dict = None):
        """Initialize integration"""
        self.config = config or {}
        self.bridge = None
        self.initialized = False
    
    def initialize(self, session_manager, command_suite) -> bool:
        """Initialize bridge"""
        try:
            self.bridge = WhatsAppBridge(
                bot_url=self.config.get('bot_url', 'http://localhost:3000'),
                bot_api_key=self.config.get('bot_api_key', ''),
                session_manager=session_manager,
                command_suite=command_suite
            )
            
            # Add authorized users
            for phone in self.config.get('authorized_users', []):
                self.bridge.authorize_user(phone)
            
            self.initialized = True
            return True
        except Exception as e:
            print(f"{Fore.RED}[-] Init failed: {e}{Style.RESET_ALL}")
            return False
    
    def start(self) -> bool:
        """Start integration"""
        if self.bridge:
            self.bridge.running = True
            return True
        return False
    
    def stop(self):
        """Stop integration"""
        if self.bridge:
            self.bridge.running = False
    
    def get_status(self) -> Dict[str, Any]:
        """Get status"""
        if not self.bridge:
            return {'status': 'not_initialized'}
        
        return {
            'status': 'running' if self.bridge.running else 'stopped',
            'bot_url': self.bridge.bot_url,
            'authorized_users': len(self.bridge.authorized_users),
            'active_sessions': len(self.bridge.user_sessions),
        }


# Default configuration
WHATSAPP_CONFIG = {
    'bot_url': 'http://localhost:3000',
    'bot_api_key': '',
    'auth_password': 'aether2025',
    'authorized_users': [],
    'webhook_enabled': False,
    'webhook_port': 5000,
}
