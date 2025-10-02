#!/usr/bin/env python3
"""
MeetingBot - автоматизация встреч
Открывает встречу по ссылке и делает скриншоты
"""
import os
import time
import random
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from connectors import ZoomConnector

# Загрузка переменных окружения
load_dotenv()

# Конфигурация
MEETING_URL = os.getenv("MEETING_URL", "https://www.google.com")
BOT_NAME = os.getenv("BOT_NAME", "MeetingBot")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
WINDOW_WIDTH = int(os.getenv("WINDOW_WIDTH", "1920"))
WINDOW_HEIGHT = int(os.getenv("WINDOW_HEIGHT", "1080"))
SCREENSHOT_DELAY = int(os.getenv("SCREENSHOT_DELAY", "3"))
CONNECTOR_TYPE = os.getenv("CONNECTOR_TYPE", "zoom").lower()

# Пути
BASE_DIR = Path(__file__).parent
SESSIONS_DIR = BASE_DIR / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


class MeetingBot:
    """Бот для автоматизации встреч"""

    def __init__(self):
        self.driver = None
        self.connector = None
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = SESSIONS_DIR / self.session_id
        self.screenshots_dir = self.session_dir / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_counter = 0

    def setup_browser(self):
        """Настройка и запуск браузера"""
        print("🚀 Запуск браузера...")

        chrome_options = Options()

        if HEADLESS:
            chrome_options.add_argument("--headless=new")
            print("   Режим: headless (без GUI)")
        else:
            print("   Режим: с отображением браузера")

        # Базовые опции
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
        chrome_options.add_argument("--disable-gpu")

        # Антидетект опции
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Скрыть автоматизацию
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Убрать флаг автоматизации
        chrome_options.add_experimental_option('useAutomationExtension', False)  # Отключить расширение автоматизации

        # Реалистичный User-Agent
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

        # Опции для встреч
        chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Автоматически разрешать доступ к микро/камере
        chrome_options.add_argument("--use-fake-device-for-media-stream")  # Использовать виртуальные устройства

        # Инициализация драйвера
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Инициализация коннектора
        if CONNECTOR_TYPE == "zoom":
            self.connector = ZoomConnector(self.driver, BOT_NAME, self.take_screenshot)
            print(f"   Коннектор: {self.connector.get_platform_name()}")
        else:
            raise ValueError(f"Неизвестный тип коннектора: {CONNECTOR_TYPE}")

        # Удаление webdriver флага через JavaScript
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // Переопределение других детектируемых свойств
                window.navigator.chrome = {
                    runtime: {}
                };

                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });

                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en', 'ru']
                });
            '''
        })

        print(f"   Размер окна: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        print("✅ Браузер запущен")

    def take_screenshot(self, name=None):
        """Делает скриншот текущей страницы"""
        self.screenshot_counter += 1

        if name is None:
            name = f"{self.screenshot_counter:02d}_screenshot.png"

        screenshot_path = self.screenshots_dir / name

        self.driver.save_screenshot(str(screenshot_path))
        print(f"📸 Скриншот #{self.screenshot_counter} сохранен: {screenshot_path}")

        return screenshot_path

    def close(self):
        """Закрывает браузер"""
        if self.driver:
            print("\n🛑 Закрываю браузер...")
            self.driver.quit()
            print("✅ Браузер закрыт")

    def run(self):
        """Основной процесс бота"""
        try:
            print("="*60)
            print("🤖 MeetingBot запущен")
            print(f"   Session ID: {self.session_id}")
            print("="*60)

            # Запуск браузера
            self.setup_browser()

            # Подключение к встрече через коннектор
            success = self.connector.join_meeting(MEETING_URL)

            if not success:
                print(f"❌ Не удалось подключиться к встрече")
                return

            print("\n" + "="*60)
            print("✅ Задача выполнена успешно!")
            print(f"   Скриншоты сохранены в: {self.screenshots_dir}")
            print("="*60)
            print("\n⏸️  Бот продолжает работу. Нажмите Ctrl+C для выхода...")

            # Ждем пока пользователь не закроет
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n👋 Получен сигнал остановки...")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.close()


if __name__ == "__main__":
    bot = MeetingBot()
    bot.run()
