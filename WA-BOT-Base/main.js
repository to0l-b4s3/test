import { Boom } from "@hapi/boom";
import NodeCache from "@cacheable/node-cache";
import readline from "readline";
import fs from "fs";
import path from "path";
import pino from "pino";
import makeWASocket, {
  BinaryInfo,
  Browsers,
  delay,
  DisconnectReason,
  encodeWAM,
  fetchLatestBaileysVersion,
  getAggregateVotesInPollMessage,
  isJidNewsletter,
  makeCacheableSignalKeyStore,
  proto,
  useMultiFileAuthState,
} from "@whiskeysockets/baileys";

import { handleCommand, loadPlugins } from "./handler.js"
import { createLogger } from "./src/utils/logger.js";
import qrcode from "qrcode-terminal";
const log = createLogger("Baileys");

const msgRetryCounterCache = new NodeCache({
  stdTTL: 300,
  maxKeys: 1000,
});

const onDemandMap = new Map();
const messageStore = new Map();
const pollStore = new Map();

const P = pino({
  level: "fatal",
  transport: {
    target: "pino-pretty",
    options: {
      colorize: true,
      translateTime: "yyyy-mm-dd HH:MM:ss",
      ignore: "pid,hostname",
    },
  },
});

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const question = (text) =>
  new Promise((resolve) => rl.question(text, resolve));

const ensureDirectoryExists = (dirPath) => {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    log.info(`Created directory: ${dirPath}`);
  }
};

const getMessage = async (key) => {
  try {
    const stored = messageStore.get(key.id);
    if (stored) {
      return stored.message;
    }
    
    return proto.Message.create({
      conversation: "Message not found in cache",
    });
  } catch (error) {
    log.error("Error retrieving message:", error.message);
    return proto.Message.create({
      conversation: "Error retrieving message",
    });
  }
};

const handleMessages = (sock) => {
  sock.ev.on("messages.upsert", async (m) => {
    try {
      const messages = m.messages;
      
      for (const message of messages) {
        if (message.key?.id) {
          messageStore.set(message.key.id, { message, timestamp: Date.now() });
        }

        if (message.key.fromMe) continue;

        if (!message.message) continue;
        
        handleCommand(sock, message)
      }
    } catch (error) {
      log.error("Error handling messages:", error.message);
    }
  });

  sock.ev.on("messages.update", (messageUpdate) => {
    for (const update of messageUpdate) {
      if (update.key?.id && messageStore.has(update.key.id)) {
        const stored = messageStore.get(update.key.id);
        messageStore.set(update.key.id, { ...stored, ...update });
      }
    }
  });

  sock.ev.on("presence.update", ({ id, presences }) => {
    log.debug(`Presence update for ${id}:`, Object.keys(presences));
  });

  sock.ev.on("groups.update", (updates) => {
    for (const update of updates) {
      log.info(`Group update for ${update.id}:`, update);
    }
  });
};

export const startSocket = async () => {
  let reconnectAttempts = 0;
  const maxReconnectAttempts = 10;
  const baseReconnectDelay = 3000;
  let authMethod = null; // Track which auth method is being used

  try {
    const sessionPath = "./data/sessions";
    ensureDirectoryExists(path.dirname(sessionPath));

    const { state, saveCreds } = await useMultiFileAuthState(sessionPath);
    const { version, isLatest } = await fetchLatestBaileysVersion();

    log.info(`\n📱 Using WhatsApp v${version.join(".")}, Latest: ${isLatest ? "✅ Yes" : "❌ No"}`);

    // Check if session exists
    const sessionExists = state.creds && state.creds.noiseKey;
    if (sessionExists) {
      log.success("✅ Existing session found. Connecting...\n");
    } else {
      log.warn("❌ No existing session found.");
      log.info("\n🔐 Choose your authentication method:\n");
      log.info("  1️⃣  QR Code Scan (Recommended)");
      log.info("       - Faster connection");
      log.info("       - Phone becomes linked device");
      log.info("       - Most stable method\n");
      log.info("  2️⃣  Pairing Code");
      log.info("       - Phone number required");
      log.info("       - WhatsApp Web style");
      log.info("       - Longer connection time\n");
      
      let validChoice = false;
      while (!validChoice) {
        const choice = await question("👉 Enter your choice (1 or 2): ");
        if (choice.trim() === "1" || choice.trim() === "2") {
          authMethod = choice.trim() === "2" ? "pairing" : "qr";
          validChoice = true;
        } else {
          log.warn("⚠️  Invalid input. Please enter 1 or 2.");
        }
      }
    }

    const sock = makeWASocket({
      version,
      logger: P,
      auth: {
        creds: state.creds,
        keys: makeCacheableSignalKeyStore(state.keys, P),
      },
      msgRetryCounterCache,
      generateHighQualityLinkPreview: true,
      getMessage,
      connectTimeoutMs: 60_000,
      defaultQueryTimeoutMs: 60_000,
      keepAliveIntervalMs: 10_000,
      markOnlineOnConnect: true,
      syncFullHistory: false,
      browser: Browsers.ubuntu("Edge"),
      printQRInTerminal: false,
    });

    if (!sock.authState.creds.registered && authMethod === "pairing") {
      log.info("\n📞 Pairing Code Authentication\n");
      log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
      
      let validPhone = false;
      let phoneNumber = "";
      
      while (!validPhone) {
        phoneNumber = await question("📱 Enter your phone number (with country code, e.g., +27694176088):\n> ");
        phoneNumber = phoneNumber.replace(/\s+/g, '').replace(/[^\d+]/g, '');
        
        if (!phoneNumber.startsWith('+')) {
          phoneNumber = '+' + phoneNumber;
        }
        
        if (/^\+\d{10,15}$/.test(phoneNumber)) {
          validPhone = true;
          log.success(`✅ Phone number accepted: ${phoneNumber}\n`);
        } else {
          log.warn("⚠️  Invalid phone number. Include country code (e.g., +27).\n");
        }
      }
      
      try {
        log.info("⏳ Requesting pairing code from WhatsApp servers...\n");
        const code = await sock.requestPairingCode(phoneNumber);
        
        log.success("\n╔════════════════════════════════════════════════════════════════╗");
        log.success(`║  🔐 YOUR PAIRING CODE: ${code}                                  ║`);
        log.success("╚════════════════════════════════════════════════════════════════╝\n");
        
        log.info("📖 Instructions:");
        log.info("  1. Open WhatsApp on your phone");
        log.info("  2. Go to: Settings → Linked Devices → Link a Device");
        log.info("  3. Enter this code when prompted");
        log.info("  4. Your phone will be linked in seconds\n");
        
        log.info("⏳ Waiting for authentication (this may take 30-60 seconds)...\n");
      } catch (error) {
        log.error("❌ Failed to request pairing code:", error.message);
        log.error("Possible reasons:");
        log.error("  - Network connection issue");
        log.error("  - Invalid phone number");
        log.error("  - WhatsApp server error");
        throw error;
      }
    } else if (!sock.authState.creds.registered && authMethod === "qr") {
      log.info("\n📲 QR Code Authentication\n");
      log.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
      log.info("⏳ Generating QR code...\n");
      log.info("Instructions:");
      log.info("  1. A QR code will appear below");
      log.info("  2. Open WhatsApp on your phone");
      log.info("  3. Tap Menu (⋮) → Linked Devices → Link a Device");
      log.info("  4. Scan the QR code with your phone camera\n");
      log.info("Waiting for QR code...\n");
    }

    sock.ev.on("creds.update", saveCreds);
    loadPlugins();

    sock.ev.on("connection.update", async (update) => {
      const { connection, lastDisconnect, qr } = update;

      if (qr) {
        try {
          log.info("\n🎯 Generating QR Code (expires in 60 seconds)...\n");
          qrcode.generate(qr, { small: true });
          log.info("\n📱 Scan the QR code above with WhatsApp camera\n");
        } catch (error) {
          log.warn("⚠️  QR code generation failed:", error.message);
          log.info("QR Code raw data:", qr);
        }
      }

      if (connection === "connecting") {
        log.info("🔗 Connecting to WhatsApp servers...");
      } else if (connection === "open") {
        log.success("\n✅ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        log.success("✅ Successfully connected to WhatsApp!");
        log.success("✅ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
        reconnectAttempts = 0;
        
        // Get bot info
        const jid = sock.user?.id;
        const name = sock.user?.name || 'Bot';
        log.success(`🤖 Bot Name: ${name}`);
        log.success(`📞 Bot JID: ${jid}\n`);
        
        await sendTestWAM(sock);
      } else if (connection === "close") {
        const shouldReconnect = 
          lastDisconnect?.error instanceof Boom &&
          lastDisconnect.error.output?.statusCode !== DisconnectReason.loggedOut;

        const disconnectCode = lastDisconnect?.error?.output?.statusCode;
        const disconnectMessage = DisconnectReason[disconnectCode] || "Unknown error";

        log.error(`\n❌ Connection closed (${disconnectCode}: ${disconnectMessage})`);

        if (disconnectCode === DisconnectReason.loggedOut) {
          log.warn("⚠️  You have been logged out. Delete ./data/sessions and restart.\n");
          process.exit(0);
        }

        if (shouldReconnect && reconnectAttempts < maxReconnectAttempts) {
          const delay = Math.min(baseReconnectDelay * Math.pow(2, reconnectAttempts), 60000);
          reconnectAttempts++;
          const seconds = (delay / 1000).toFixed(0);
          
          log.info(`🔄 Reconnecting in ${seconds}s (attempt ${reconnectAttempts}/${maxReconnectAttempts})...\n`);
          
          setTimeout(() => {
            startSocket();
          }, delay);
        } else if (reconnectAttempts >= maxReconnectAttempts) {
          log.error("❌ Maximum reconnection attempts reached (10/10). Exiting...");
          process.exit(1);
        } else {
          log.warn("⚠️  You have been logged out. Clearing session...");
          rl.close();
          process.exit(0);
        }
      }
    });

    handleMessages(sock);

    setInterval(() => {
      const now = Date.now();
      const maxAge = 24 * 60 * 60 * 1000;
      
      for (const [id, data] of messageStore.entries()) {
        if (now - data.timestamp > maxAge) {
          messageStore.delete(id);
        }
      }
      
      log.debug(`Message cache size: ${messageStore.size}`);
    }, 60 * 60 * 1000);

    return sock;

  } catch (error) {
    log.error("Failed to start socket:", error.message || JSON.stringify(error));
    
    // Log full stack trace for debugging
    if (error instanceof Error) {
      log.debug("Error stack:", error.stack);
    }
    
    // Check if this is an import/module error
    if (error.message?.includes("Cannot find module") || 
        error.message?.includes("ERR_MODULE_NOT_FOUND") ||
        error.message?.includes("ERR_UNKNOWN_FILE_EXTENSION")) {
      log.error("Module loading error detected. Checking dependencies...");
      log.error("Please run: npm install");
      process.exit(1);
    }
    
    if (reconnectAttempts < maxReconnectAttempts) {
      const delay = Math.min(baseReconnectDelay * Math.pow(2, reconnectAttempts), 60000);
      reconnectAttempts++;
      
      log.info(`Retrying in ${delay}ms (attempt ${reconnectAttempts}/${maxReconnectAttempts})`);
      
      setTimeout(() => {
        startSocket();
      }, delay);
    } else {
      log.error("Failed to start after maximum attempts. Exiting...");
      process.exit(1);
    }
  }
};

const sendTestWAM = async (sock, enabled = false) => {
  if (!enabled) return;

  try {
    const analyticsPath = "./data/boot_analytics_test.json";
    
    if (!fs.existsSync(analyticsPath)) {
      log.warn("Analytics test file not found, skipping WAM test");
      return;
    }

    const analyticsData = JSON.parse(fs.readFileSync(analyticsPath, "utf-8"));
    const {
      header: { wamVersion, eventSequenceNumber },
      events,
    } = analyticsData;

    const binaryInfo = new BinaryInfo({
      protocolVersion: wamVersion,
      sequence: eventSequenceNumber,
      events,
    });

    const buffer = encodeWAM(binaryInfo);
    const result = await sock.sendWAMBuffer(buffer);
    log.success("WAM sent:", result);
  } catch (error) {
    log.error("Failed to send WAM:", error.message);
  }
};
