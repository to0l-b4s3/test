# Communication modules for AETHER C2
from .whatsapp_bridge import WhatsAppBridge
from .whatsapp_config import WhatsAppIntegration, WHATSAPP_CONFIG

# Webhook handler (optional - requires Flask)
try:
    from .webhook_handler import WhatsAppWebhookHandler, WhatsAppCommandHandler
except ImportError:
    WhatsAppWebhookHandler = None
    WhatsAppCommandHandler = None

__all__ = [
    'WhatsAppBridge',
    'WhatsAppIntegration',
    'WHATSAPP_CONFIG',
    'WhatsAppWebhookHandler',
    'WhatsAppCommandHandler',
]
