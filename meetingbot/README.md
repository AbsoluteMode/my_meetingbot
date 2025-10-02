# MeetingBot

Автоматизация встреч с помощью Selenium.

## Возможности

- ✅ Открывает встречу по URL (Zoom, Google Meet, etc.)
- ✅ Headless режим (работает в фоне)
- ✅ Автоматические скриншоты
- ✅ Сохранение по сессиям

## Установка

```bash
cd meetingbot
pip install selenium webdriver-manager python-dotenv
```

## Настройка

1. Скопируйте `.env.example` в `.env`:
```bash
cp .env.example .env
```

2. Отредактируйте `.env`:
```env
MEETING_URL=https://zoom.us/j/ваш_id_встречи
HEADLESS=true
WINDOW_WIDTH=1920
WINDOW_HEIGHT=1080
SCREENSHOT_DELAY=3
```

## Запуск

```bash
python bot.py
```

## Структура файлов

```
meetingbot/
├── bot.py              # Основной скрипт бота
├── .env               # Конфигурация (создать из .env.example)
├── .env.example       # Пример конфигурации
└── sessions/          # Папка с данными сессий
    └── screenshots/   # Скриншоты по сессиям
        └── 20251001_143000/  # Сессия с timestamp
            └── initial.png   # Скриншоты
```

## Опции

### HEADLESS
- `true` - браузер работает в фоне (без окна)
- `false` - браузер отображается на экране

### SCREENSHOT_DELAY
Сколько секунд ждать перед скриншотом после загрузки страницы.

## Примеры использования

### Скриншот Google
```env
MEETING_URL=https://www.google.com
HEADLESS=false
```

### Zoom встреча
```env
MEETING_URL=https://zoom.us/j/123456789?pwd=ваш_пароль
HEADLESS=true
```
