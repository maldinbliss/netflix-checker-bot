# 💎 𝗔n𝟬𝗡𝗢t𝗙 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗡𝗘𝗧𝗙𝗟𝗜𝗑 𝗖𝗛𝗘𝗖𝗞𝗘𝗥 𝗕𝗢𝗧 Configuration
# Repository: https://github.com/heis448/netflix-checker-bot
# Developer: @unknownnumeralx

import os

# 🔑 Get bot token from environment variable first, then config
BOT_TOKEN = os.environ.get('BOT_TOKEN') or "8381285267:AAHFZNWVqGi4QDNpyAoh3gtZaMP-CaiU9aE"
 #Replace with your actual bot token 

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

# Bot will check if token is valid
if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    print("❌ ERROR: Please set your BOT_TOKEN in environment variables or edit config.py")
    print("💡 Get token from @BotFather on Telegram")
    exit(1)
   
   #made with love in Kenya 🇰🇪🇰🇪
