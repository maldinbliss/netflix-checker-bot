#!/bin/bash
echo "📱 Setting up 𝗔n𝟬𝗡𝗢t𝗙 Netflix Checker on Termux..."

echo "🔄 Cloning repository..."
git clone https://github.com/heis448/netflix-checker-bot
cd netflix-checker-bot

echo "🔄 Updating packages..."
pkg update && pkg upgrade -y

echo "📦 Installing dependencies..."
pkg install python firefox geckodriver -y

echo "🐍 Installing Python packages..."
pip install selenium python-telegram-bot requests

echo "🔧 Setting up bot..."
if [ ! -f "config.py" ]; then
    echo "📝 Creating config file..."
    cat > config.py << EOL
# 💎 𝗔n𝟬𝗡𝗢t𝗙 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗡𝗘𝗧𝗙𝗟𝗜𝗑 𝗖𝗛𝗘𝗖𝗞𝗘𝗥 𝗕𝗢𝗧 Configuration
# Repository: https://github.com/heis448/netflix-checker-bot
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
EOL
    echo "⚠️  Please edit config.py and add your bot token from @BotFather!"
fi

echo "✅ Setup completed!"
echo "🚀 Start the bot with: python app.py"
echo "📖 Repository: https://github.com/heis448/netflix-checker-bot"