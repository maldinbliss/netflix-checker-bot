# 💎 𝗔n𝟬𝗡𝗢t𝗙 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗡𝗘𝗧𝗙𝗟𝗜𝗑 𝗖𝗛𝗘𝗖𝗞𝗘𝗥 𝗕𝗢𝗧 Configuration
# Repository: https://github.com/heis448/netflix-checker-bot
# Developer: @unknownnumeralx

import os

# 🔑 BOT TOKEN - Choose ONE method below:

# METHOD 1: Direct hardcode in config.py
BOT_TOKEN = "8418801641:AAEFCnElRJQgzfjPDnLB6XZno6eNAvmQEd0"

# METHOD 2: Read from environment variable (comment above line, uncomment below)
# BOT_TOKEN = os.environ.get('BOT_TOKEN') or "YOUR_BOT_TOKEN_HERE"

# Platform-Specific Settings
MAX_ACCOUNTS_RAILWAY = 100
MAX_ACCOUNTS_RENDER = 100
MAX_ACCOUNTS_HEROKU = 50
MAX_ACCOUNTS_TERMUX = 50
MAX_ACCOUNTS_VPS = 500

# Performance Settings
REQUEST_TIMEOUT = 30
MAX_RETRIES = 2
DELAY_BETWEEN_ACCOUNTS = 3

# 🔒 Security Settings
CLEANUP_BROWSER = True
AUTO_DELETE_FILES = True

# No validation here - let app.py handle it
