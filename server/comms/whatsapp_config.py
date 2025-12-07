#!/usr/bin/env python3
"""
WhatsApp Integration Configuration
"""

WHATSAPP_CONFIG = {
    # Bot Server Configuration
    'bot_url': 'http://localhost:3000',
    'bot_api_key': 'your-api-key-here',
    
    # Security
    'auth_password': 'aether2025',  # Change this!
    'authorized_users': [],          # WhatsApp phone numbers
    
    # Features
    'enable_command_history': True,
    'enable_session_linking': True,
    'max_message_length': 4096,
    'command_timeout': 30,
}


class WhatsAppIntegration:
    """WhatsApp integration manager"""
    
    def __init__(self, config: dict = None):
        from .whatsapp_bridge import WhatsAppBridge
        self.config = config or WHATSAPP_CONFIG.copy()
        self.bridge = None
        self.initialized = False
    
    def initialize(self, session_manager, command_suite) -> bool:
        """Initialize integration"""
        try:
            from .whatsapp_bridge import WhatsAppBridge
            
            self.bridge = WhatsAppBridge(
                bot_url=self.config.get('bot_url', 'http://localhost:3000'),
                bot_api_key=self.config.get('bot_api_key', ''),
                session_manager=session_manager,
                command_suite=command_suite
            )
            
            for phone in self.config.get('authorized_users', []):
                self.bridge.authorize_user(phone)
            
            self.initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize: {e}")
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
    
    def get_status(self) -> dict:
        """Get status"""
        if not self.bridge:
            return {'status': 'not_initialized'}
        
        return self.bridge.get_status()
