#!/bin/bash
echo "🚀 Building 𝗔n𝟬𝗡𝗢t𝗙 Netflix Checker Bot..."
echo "📦 Repository: https://github.com/heis448/netflix-checker-bot"

# Install GeckoDriver for Linux
echo "📦 Installing GeckoDriver..."
wget -q https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
tar -xzf geckodriver-v0.34.0-linux64.tar.gz
chmod +x geckodriver
sudo mv geckodriver /usr/local/bin/
rm geckodriver-v0.34.0-linux64.tar.gz

# Install Firefox
echo "🦊 Installing Firefox..."
sudo apt-get update
sudo apt-get install -y firefox-esr

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build completed! Bot is ready to run."
echo "🚀 Start with: python app.py"