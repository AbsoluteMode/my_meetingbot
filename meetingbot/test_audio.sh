#!/bin/bash
# Тестовый скрипт для проверки аудио в контейнере

echo "🔍 Проверка PulseAudio..."
pactl list sinks short

echo ""
echo "🔍 Тест записи аудио (5 секунд)..."
timeout 5 ffmpeg -f pulse -i virtual_speaker.monitor -f null - 2>&1 | grep -i "audio\|stream\|duration"

echo ""
echo "✅ Проверка завершена"
