# Деплой MeetingBot на Ubuntu сервер

## Требования

- Ubuntu 20.04+ (или Debian-based дистрибутив)
- Python 3.8+
- Sudo права для установки пакетов

## Быстрая установка

### 1. Клонирование/загрузка проекта

```bash
# Загрузите проект на сервер
cd /opt  # или любая другая директория
```

### 2. Установка зависимостей

```bash
cd meetingbot
chmod +x setup_ubuntu.sh
./setup_ubuntu.sh
```

Скрипт установит:
- Google Chrome
- Все необходимые системные библиотеки
- Python пакеты (selenium, webdriver-manager, python-dotenv)

### 3. Настройка

```bash
cp .env.example .env
nano .env  # или vim
```

Укажите URL встречи и другие параметры.

### 4. Запуск

```bash
python bot.py
```

## Ручная установка

Если автоматический скрипт не работает:

### Установка Chrome

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
```

### Установка системных зависимостей

```bash
sudo apt-get update
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
    libasound2
```

### Установка Python зависимостей

```bash
pip install selenium webdriver-manager python-dotenv
```

## Проверка работы

```bash
# Проверить версию Chrome
google-chrome --version

# Проверить Python пакеты
pip list | grep selenium
```

## Запуск в production

### Использование systemd service

Создайте файл `/etc/systemd/system/meetingbot.service`:

```ini
[Unit]
Description=MeetingBot Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/opt/meetingbot
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 bot.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запуск сервиса:

```bash
sudo systemctl daemon-reload
sudo systemctl enable meetingbot
sudo systemctl start meetingbot
sudo systemctl status meetingbot
```

### Использование screen/tmux

```bash
# Screen
screen -S meetingbot
python bot.py
# Ctrl+A, D для отключения

# Tmux
tmux new -s meetingbot
python bot.py
# Ctrl+B, D для отключения
```

## Troubleshooting

### Chrome binary not found

```bash
# Убедитесь что Chrome установлен
which google-chrome
google-chrome --version

# Если не найден, переустановите
sudo apt-get remove google-chrome-stable
sudo apt-get install -y google-chrome-stable
```

### Headless режим не работает

Убедитесь что установлены все зависимости:

```bash
sudo apt-get install -y xvfb
```

### Permission denied

```bash
chmod +x bot.py
chmod +x setup_ubuntu.sh
```

## Мониторинг

### Логи

Добавьте логирование в bot.py или используйте:

```bash
python bot.py >> logs/bot.log 2>&1
```

### Скриншоты

Скриншоты сохраняются в `sessions/screenshots/{session_id}/`

```bash
ls -lh sessions/screenshots/
```
