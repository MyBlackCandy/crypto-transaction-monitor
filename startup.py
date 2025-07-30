#!/usr/bin/env python3
"""Startup script for Railway deployment"""

import threading
import time
import logging
from flask import Flask
from bot import main, app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Start Flask server in background
    def run_flask():
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port, debug=False)
    
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Give Flask time to start
    time.sleep(3)
    
    # Start the main bot
    main()
