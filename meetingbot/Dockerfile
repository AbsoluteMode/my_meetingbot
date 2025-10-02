FROM python:3.11-bookworm

# Установка зависимостей (Chrome, ffmpeg, Xvfb, PulseAudio, x11-utils)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ffmpeg \
    xvfb \
    x11-utils \
    pulseaudio \
    xdotool \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Удаляем/блокируем xdg-open чтобы Zoom не пытался открыть desktop приложение
RUN rm -f /usr/bin/xdg-open && \
    echo '#!/bin/bash\nexit 0' > /usr/bin/xdg-open && \
    chmod +x /usr/bin/xdg-open

# Рабочая директория
WORKDIR /app

# Копируем requirements.txt и устанавливаем Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота, коннекторы и recorder
COPY bot.py .
COPY recorder.py .
COPY connectors/ ./connectors/

# Создаем директорию для sessions (будет маунтиться как volume)
RUN mkdir -p /app/sessions

# Скрипт запуска с Xvfb
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Запуск через entrypoint
CMD ["/entrypoint.sh"]
