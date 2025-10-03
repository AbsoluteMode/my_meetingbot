FROM python:3.11-bookworm

# Установка зависимостей (Chrome, ChromeDriver, ffmpeg, Xvfb, PulseAudio, x11-utils)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
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

# Установка ChromeDriver (matching Chrome version)
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') \
    && echo "Chrome version: $CHROME_VERSION" \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip \
    || wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver* \
    && chromedriver --version

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
