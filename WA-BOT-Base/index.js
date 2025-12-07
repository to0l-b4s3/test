#!/usr/bin/env node
/**
 * AETHER WhatsApp Bot - Main Entry Point
 * This file starts the Baileys WhatsApp bot with proper clustering support
 */

import cluster from 'cluster';
import os from 'os';
import { createLogger } from './src/utils/logger.js';
import { startSocket } from './main.js';

const logger = createLogger('Cluster');

const numCPUs = os.cpus().length;
const numWorkers = process.env.WORKERS || 1;

if (cluster.isMaster) {
  logger.info(`Master ${process.pid} is running`);
  
  // Fork workers
  for (let i = 0; i < numWorkers; i++) {
    cluster.fork();
  }

  cluster.on('exit', (worker, code, signal) => {
    logger.warn(`Worker ${worker.process.pid} died (${signal || code}). Restarting...`);
    cluster.fork();
  });

} else {
  // Worker process
  logger.success(`Worker ${process.pid} started`);
  
  try {
    // Start the main socket/bot
    startSocket();
  } catch (error) {
    logger.error(`Failed to start main.js: ${error.message}`);
    console.error(error);
    process.exit(1);
  }
}
