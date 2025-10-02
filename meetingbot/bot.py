#!/usr/bin/env python3
"""
MeetingBot - автоматизация встреч
Открывает встречу по ссылке и делает скриншоты
"""
import os
import time
import random
import signal
import sys
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from connectors import ZoomConnector
from recorder import ScreenRecorder

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
ENABLE_RECORDING = os.getenv("ENABLE_RECORDING", "false").lower() == "true"
MAX_MEETING_DURATION_SECONDS = int(os.getenv("MAX_MEETING_DURATION_SECONDS", "7200"))  # 2 часа по умолчанию

# Пути
BASE_DIR = Path(__file__).parent
SESSIONS_DIR = BASE_DIR / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


class MeetingBot:
    """Бот для автоматизации встреч"""

    def __init__(self):
        self.driver = None
        self.connector = None
        self.recorder = None
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = SESSIONS_DIR / self.session_id
        self.screenshots_dir = self.session_dir / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_counter = 0

    def setup_browser(self):
        """Настройка и запуск браузера"""
        print("🚀 Запуск браузера...")

        chrome_options = Options()

        # ВАЖНО: если запись включена, НЕ используем headless
        # Chrome должен рендериться на Xvfb display для записи ffmpeg
        if HEADLESS and not ENABLE_RECORDING:
            chrome_options.add_argument("--headless=new")
            print("   Режим: headless (без GUI)")
        else:
            if ENABLE_RECORDING:
                print("   Режим: с GUI на Xvfb (для записи)")
            else:
                print("   Режим: с отображением браузера")

        # Базовые опции
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
        chrome_options.add_argument("--disable-gpu")

        # Аудио опции для PulseAudio
        chrome_options.add_argument("--enable-audio-service-sandbox=false")
        chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")

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
        """Закрывает браузер и останавливает запись"""
        # Выходим из встречи
        if self.connector and self.driver:
            print("\n👋 Выхожу из встречи...")
            try:
                # Проверяем что driver ещё жив
                self.driver.current_url  # Попытка обращения к driver
                self.connector.leave_meeting()
            except Exception as e:
                print(f"   ⚠️  Не удалось выйти из встречи: {e}")
                print(f"   (Driver возможно уже закрыт)")

        # Останавливаем запись ПЕРЕД закрытием браузера
        if self.recorder and self.recorder.is_recording():
            print("\n🛑 Останавливаю запись...")
            self.recorder.stop()
            # Даём ffmpeg время на финализацию
            time.sleep(2)

        # Закрываем браузер
        if self.driver:
            print("\n🛑 Закрываю браузер...")
            try:
                self.driver.quit()
                print("✅ Браузер закрыт")
            except Exception as e:
                print(f"   ⚠️  Ошибка при закрытии браузера: {e}")

    def signal_handler(self, sig, frame):
        """Обработчик сигналов для graceful shutdown"""
        print(f"\n\n⚠️  Получен сигнал {sig} (Docker stop или Ctrl+C)")
        print("🔄 Корректное завершение...")
        self.close()
        sys.exit(0)

    def run(self):
        """Основной процесс бота"""
        # Регистрируем обработчики сигналов
        signal.signal(signal.SIGTERM, self.signal_handler)  # Docker stop
        signal.signal(signal.SIGINT, self.signal_handler)   # Ctrl+C

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

            # Запуск записи ПОСЛЕ успешного подключения
            if ENABLE_RECORDING:
                recording_path = self.session_dir / "recording.mp4"
                self.recorder = ScreenRecorder(
                    output_path=recording_path,
                    resolution=f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
                )
                if not self.recorder.start():
                    print("⚠️  Не удалось запустить запись, продолжаем без неё...")
                    self.recorder = None

            print("\n" + "="*60)
            print("✅ Подключение к встрече успешно!")
            print(f"   Скриншоты сохранены в: {self.screenshots_dir}")
            print("="*60)

            # Мониторинг встречи
            print(f"\n⏱️  Мониторинг встречи...")
            print(f"   📏 Максимальная длительность: {MAX_MEETING_DURATION_SECONDS // 60} минут ({MAX_MEETING_DURATION_SECONDS} сек)")
            print(f"   🔍 Проверка кнопки Leave каждую секунду")
            print(f"   🚪 Выход при: 1) истечении времени, 2) исчезновении кнопки Leave")
            print(f"\n⏸️  Бот на встрече. Нажмите Ctrl+C для досрочного выхода...\n")

            start_time = time.time()
            check_counter = 0

            while True:
                elapsed_time = time.time() - start_time

                # Проверка 1: Превышено максимальное время
                if elapsed_time >= MAX_MEETING_DURATION_SECONDS:
                    elapsed_min = int(elapsed_time // 60)
                    print(f"\n\n⏰ Достигнута максимальная длительность встречи ({elapsed_min} минут)")
                    print("   Завершаю сессию...")
                    self.close()
                    return

                # Проверка 2: Кнопка Leave исчезла (КАЖДУЮ СЕКУНДУ)
                in_meeting = self.connector.check_in_meeting()

                elapsed_min = int(elapsed_time // 60)
                elapsed_sec = int(elapsed_time % 60)

                if not in_meeting:
                    print(f"\n\n🚪 Кнопка Leave исчезла (встреча завершена или бот выгнан)")
                    print(f"   Время в встрече: {elapsed_min}м {elapsed_sec}с")
                    print("   Завершаю сессию...")
                    self.close()
                    return

                # Статус каждую минуту
                if check_counter > 0 and check_counter % 60 == 0:
                    remaining_min = (MAX_MEETING_DURATION_SECONDS - elapsed_time) // 60
                    print(f"   ✅ В встрече: {elapsed_min}м {elapsed_sec}с | Осталось до автовыхода: ~{int(remaining_min)}м")

                time.sleep(1)
                check_counter += 1

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.close()


if __name__ == "__main__":
    bot = MeetingBot()
    bot.run()
