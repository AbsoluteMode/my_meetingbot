#!/bin/bash

# Запускаем Xvfb (виртуальный X сервер) для headless режима
echo "🖥️  Запуск Xvfb..."
Xvfb :99 -screen 0 1200x800x24 &
XVFB_PID=$!

# Ждём пока Xvfb запустится
sleep 3

# Устанавливаем DISPLAY
export DISPLAY=:99

echo "✅ Xvfb запущен (PID: $XVFB_PID)"

# Проверяем что Xvfb работает
if xdpyinfo -display :99 >/dev/null 2>&1; then
    echo "✅ Display :99 доступен"
else
    echo "❌ Display :99 недоступен!"
fi

# Запускаем PulseAudio (виртуальный аудио сервер)
echo "🔊 Запуск PulseAudio..."
pulseaudio --start --exit-idle-time=-1 2>/dev/null
sleep 2

# Создаём виртуальный аудио sink для Chrome
pactl load-module module-null-sink sink_name=virtual_speaker 2>/dev/null

# Устанавливаем виртуальный sink как дефолтный
pactl set-default-sink virtual_speaker 2>/dev/null

echo "✅ PulseAudio запущен (виртуальный sink: virtual_speaker)"

# Диагностика PulseAudio
echo "🔍 Проверка аудио устройств:"
pactl list sinks short 2>/dev/null | grep virtual_speaker && echo "   ✅ virtual_speaker найден" || echo "   ❌ virtual_speaker не найден"

echo "🚀 Запуск бота..."

# Запускаем бота
python bot.py

# При завершении убиваем процессы
pulseaudio --kill 2>/dev/null
kill $XVFB_PID 2>/dev/null
