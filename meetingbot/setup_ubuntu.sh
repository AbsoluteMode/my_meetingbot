#!/bin/bash
# Скрипт установки зависимостей для MeetingBot на Ubuntu сервере

echo "🚀 Установка зависимостей для MeetingBot на Ubuntu..."

# Обновление пакетов
echo "📦 Обновление списка пакетов..."
sudo apt-get update

# Установка Chrome
echo "🌐 Установка Google Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Установка дополнительных зависимостей для headless режима
echo "📚 Установка зависимостей для headless браузера..."
sudo apt-get install -y \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    fonts-liberation \
    libasound2 \
    libcups2 \
    libdbus-1-3 \
    libgbm1 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    xdg-utils

# Установка Python зависимостей
echo "🐍 Установка Python пакетов..."
pip install selenium webdriver-manager python-dotenv

# Проверка установки Chrome
echo "✅ Проверка установки Chrome..."
google-chrome --version

echo ""
echo "="*60
echo "✅ Установка завершена!"
echo "="*60
echo ""
echo "Для запуска бота:"
echo "1. Скопируйте .env.example в .env"
echo "2. Отредактируйте .env с вашими настройками"
echo "3. Запустите: python bot.py"
echo ""
