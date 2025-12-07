/**
 * AETHER Integration Extension for Baileys Bot
 * Add this to your main.js to enable AETHER C2 control via WhatsApp
 */

import AETHERMessageHandler from './aether-handler.js';

/**
 * Initialize AETHER integration
 * Call this function in startSocket after socket is created
 */
export const initializeAETHER = (sock, config = {}) => {
    const aetherConfig = {
        aetherHost: config.aetherHost || process.env.AETHER_HOST || 'http://localhost',
        aetherPort: config.aetherPort || process.env.AETHER_PORT || 5000,
        apiKey: config.apiKey || process.env.AETHER_API_KEY || '',
        authorizedUsers: config.authorizedUsers || process.env.AETHER_USERS?.split(',') || [],
        commandTimeout: config.commandTimeout || 30000,
    };

    const aetherHandler = new AETHERMessageHandler(sock, aetherConfig);

    console.log('[AETHER] Integration initialized');
    console.log(`  Server: ${aetherConfig.aetherHost}:${aetherConfig.aetherPort}`);
    console.log(`  Authorized Users: ${aetherHandler.bridge.authorizedUsers.size}`);

    return aetherHandler;
};

/**
 * Enhanced message handler with AETHER support
 * Replace handleCommand call with this in main.js messages.upsert event
 */
export const handleMessagesWithAETHER = (sock, aetherHandler, handleCommand) => {
    return async (m) => {
        try {
            const messages = m.messages;
            
            for (const message of messages) {
                if (message.key?.id) {
                    // Store message (existing logic)
                }

                if (message.key.fromMe) continue;
                if (!message.message) continue;

                const text = message.message?.conversation || 
                            message.message?.extendedTextMessage?.text || '';

                // Check if this is an AETHER command
                if (text.startsWith('aether ') || 
                    text.startsWith('auth ') ||
                    text.startsWith('link ') ||
                    text.startsWith('help') ||
                    text.startsWith('sessions')) {
                    // Handle with AETHER
                    await aetherHandler.handleMessage(message);
                } else {
                    // Handle with regular command system
                    handleCommand(sock, message);
                }
            }
        } catch (error) {
            console.error("Error handling messages:", error.message);
        }
    };
};

/**
 * Configuration template for AETHER
 */
export const getAETHERConfigTemplate = () => ({
    // AETHER Server settings
    aetherHost: 'http://localhost',
    aetherPort: 5000,
    apiKey: 'your-api-key-here',
    
    // WhatsApp settings
    maxMessageLength: 4096,
    commandTimeout: 30000,
    
    // Security
    authPassword: 'aether2025', // Change this!
    authorizedUsers: [
        // '+1234567890',
    ],
    
    // Features
    enableCommandHistory: true,
    maxHistoryPerUser: 50,
    enableSessionLinking: true,
});

export default {
    initializeAETHER,
    handleMessagesWithAETHER,
    getAETHERConfigTemplate,
};
