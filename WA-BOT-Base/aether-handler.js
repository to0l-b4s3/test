/**
 * AETHER Message Handler for WhatsApp
 * Processes incoming WhatsApp messages and routes them to AETHER
 */

import AETHERBridge from './aether-bridge.js';

class AETHERMessageHandler {
    constructor(sock, config = {}) {
        this.sock = sock;
        this.bridge = new AETHERBridge(config);
        this.commandHistory = new Map();
        this.userStates = new Map();
        
        console.log('[AETHER Handler] Initialized');
    }

    /**
     * Handle incoming message
     */
    async handleMessage(msg) {
        try {
            const senderId = msg.key.remoteJid;
            const text = msg.message?.conversation || msg.message?.extendedTextMessage?.text || '';
            
            if (!text.trim()) return;

            console.log(`[AETHER] Message from ${senderId}: ${text}`);

            // Parse command
            const parts = text.trim().split(/\s+/);
            const command = parts[0].toLowerCase();
            const args = parts.slice(1);

            // Route command
            const response = await this.routeCommand(senderId, command, args, text);

            // Send response
            if (response) {
                await this.sendMessage(senderId, response);
            }
        } catch (error) {
            console.error(`[AETHER] Error handling message:`, error);
            await this.sendMessage(msg.key.remoteJid, `❌ Error: ${error.message}`);
        }
    }

    /**
     * Route command to appropriate handler
     */
    async routeCommand(userId, command, args, fullText) {
        // Authentication
        if (command === 'auth') {
            return this.handleAuth(userId, args);
        }

        // Help
        if (command === 'help') {
            return this.bridge.getHelpMenu(this.bridge.isAuthorized(userId));
        }

        // Check authorization for other commands
        if (!this.bridge.isAuthorized(userId)) {
            return '❌ Unauthorized. Use: *auth <password>*';
        }

        // Session management
        if (command === 'link') {
            return this.handleLink(userId, args);
        }
        if (command === 'unlink') {
            return this.handleUnlink(userId);
        }
        if (command === 'sessions') {
            return await this.bridge.getSessions(userId);
        }
        if (command === 'status') {
            return this.handleStatus(userId);
        }

        // Command history
        if (command === 'history') {
            return this.handleHistory(userId);
        }

        // AETHER commands
        const result = await this.bridge.sendCommand(userId, fullText);
        
        if (result.status === 'success') {
            const data = result.result?.data || result.result || {};
            const formattedResult = this.formatResult(data);
            
            // Store in history
            this.storeHistory(userId, fullText, formattedResult);
            
            return formattedResult;
        } else {
            return result.message;
        }
    }

    /**
     * Handle authentication
     */
    handleAuth(userId, args) {
        const password = args.join(' ');
        
        // Check password (should be from config)
        if (password === 'aether2025') { // Default - change in production!
            this.bridge.authorizeUser(userId);
            return `✅ Authorized! Welcome to AETHER\n\nUse: *help* for available commands`;
        }
        
        return '❌ Invalid password';
    }

    /**
     * Handle session linking
     */
    handleLink(userId, args) {
        if (args.length === 0) {
            return '❌ Usage: link <session_id>';
        }

        const sessionId = args[0];
        this.bridge.linkSession(userId, sessionId);
        return `✅ Linked to session: *${sessionId}*`;
    }

    /**
     * Handle session unlinking
     */
    handleUnlink(userId) {
        this.bridge.userSessions.delete(userId);
        return '✅ Unlinked from session';
    }

    /**
     * Handle status command
     */
    handleStatus(userId) {
        const sessionId = this.bridge.getUserSession(userId);
        if (!sessionId) {
            return '❌ Not linked to any session';
        }
        return `📊 Current Session: *${sessionId}*`;
    }

    /**
     * Handle history command
     */
    handleHistory(userId) {
        const history = this.commandHistory.get(userId) || [];
        if (history.length === 0) {
            return 'No command history';
        }

        const recent = history.slice(-5);
        return '📜 Recent Commands:\n' + 
            recent.map((h, i) => `${i + 1}. ${h.command}`).join('\n');
    }

    /**
     * Format result for WhatsApp
     */
    formatResult(data) {
        if (!data) {
            return '✅ Command executed';
        }

        const text = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
        
        // Limit to WhatsApp message size
        const maxLength = 4096;
        if (text.length > maxLength) {
            return `✅ Result (truncated):\n${text.substring(0, maxLength)}...\n\n_[Full output on server]_`;
        }

        return `✅ Result:\n${text}`;
    }

    /**
     * Store command in history
     */
    storeHistory(userId, command, result) {
        if (!this.commandHistory.has(userId)) {
            this.commandHistory.set(userId, []);
        }

        const history = this.commandHistory.get(userId);
        history.push({
            timestamp: new Date().toISOString(),
            command: command,
            result: result.substring(0, 100), // Store truncated result
        });

        // Keep last 50 commands
        if (history.length > 50) {
            history.shift();
        }
    }

    /**
     * Send message to user
     */
    async sendMessage(userId, text) {
        try {
            await this.sock.sendMessage(userId, { text });
            console.log(`[AETHER] Sent response to ${userId}`);
        } catch (error) {
            console.error(`[AETHER] Failed to send message:`, error);
        }
    }

    /**
     * Get authorized users count
     */
    getAuthorizedCount() {
        return this.bridge.authorizedUsers.size;
    }

    /**
     * Get handler status
     */
    getStatus() {
        return {
            authorized_users: this.bridge.authorizedUsers.size,
            active_sessions: this.bridge.userSessions.size,
            history_entries: Array.from(this.commandHistory.values()).reduce((a, b) => a + b.length, 0),
        };
    }
}

export default AETHERMessageHandler;
