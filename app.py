#!/usr/bin/env python3
"""Simple Flask app for Railway health checks"""

import os
import time
import threading
import logging
from flask import Flask, jsonify

# Setup logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Global status
app_status = {
    'status': 'starting',
    'start_time': time.time(),
    'bot_status': 'initializing'
}

@app.route('/health')
def health():
    uptime = time.time() - app_status['start_time']
    return jsonify({
        'status': 'ok',
        'uptime_seconds': round(uptime, 2),
        'service': 'crypto-monitor',
        'bot_status': app_status['bot_status']
    })

@app.route('/ping')
def ping():
    return "pong"

@app.route('/')
def index():
    return jsonify({
        'service': 'Crypto Transaction Monitor',
        'status': 'running',
        'endpoints': ['/health', '/ping']
    })

def start_main_bot():
    """Start the main bot in background"""
    try:
        app_status['bot_status'] = 'starting'
        logging.info("🤖 Starting main bot...")
        
        # Import and run main bot
        from bot import main
        main()
        
    except Exception as e:
        logging.error(f"Bot error: {e}")
        app_status['bot_status'] = 'error'

if __name__ == '__main__':
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_main_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    app_status['bot_status'] = 'running'
    
    # Start Flask app
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"🌐 Flask app starting on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
