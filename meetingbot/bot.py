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
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Конфигурация
MEETING_URL = os.getenv("MEETING_URL", "https://www.google.com")
BOT_NAME = os.getenv("BOT_NAME", "MeetingBot")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
WINDOW_WIDTH = int(os.getenv("WINDOW_WIDTH", "1920"))
WINDOW_HEIGHT = int(os.getenv("WINDOW_HEIGHT", "1080"))
SCREENSHOT_DELAY = int(os.getenv("SCREENSHOT_DELAY", "3"))

# Пути
BASE_DIR = Path(__file__).parent
SESSIONS_DIR = BASE_DIR / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


class MeetingBot:
    """Бот для автоматизации встреч"""

    def __init__(self):
        self.driver = None
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

    def human_like_mouse_movement(self, duration=2):
        """
        Эмулирует человеческие движения мыши через JavaScript

        Args:
            duration: длительность движений в секундах
        """
        print("🖱️  Эмуляция движений мыши...")

        # Генерируем случайные точки для движения
        num_movements = random.randint(3, 7)

        for _ in range(num_movements):
            # Случайные координаты в пределах размера окна
            x = random.randint(50, WINDOW_WIDTH - 50)
            y = random.randint(50, WINDOW_HEIGHT - 50)

            # Эмулируем движение мыши через JavaScript
            self.driver.execute_script(f"""
                var event = new MouseEvent('mousemove', {{
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'clientX': {x},
                    'clientY': {y}
                }});
                document.dispatchEvent(event);
            """)

            # Случайная задержка между движениями
            time.sleep(random.uniform(0.1, 0.3))

        # Дополнительная задержка
        time.sleep(random.uniform(0.5, 1.0))

    def human_like_scroll(self):
        """
        Эмулирует человеческий скроллинг страницы
        """
        print("📜 Эмуляция скроллинга...")

        # Случайное количество скроллов
        num_scrolls = random.randint(1, 3)

        for _ in range(num_scrolls):
            # Случайная величина скролла
            scroll_amount = random.randint(100, 300)

            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.3, 0.8))

    def human_like_delay(self, min_sec=1, max_sec=3):
        """
        Случайная задержка как у человека

        Args:
            min_sec: минимальная задержка в секундах
            max_sec: максимальная задержка в секундах
        """
        delay = random.uniform(min_sec, max_sec)
        print(f"⏳ Задержка {delay:.2f} сек...")
        time.sleep(delay)

    def human_like_click(self, x, y, x_variance=5, y_variance=5, show_marker=True, use_action_chains=False):
        """
        Эмулирует человеческий клик по координатам

        Args:
            x: координата X
            y: координата Y
            x_variance: разброс по X (по умолчанию ±5)
            y_variance: разброс по Y (по умолчанию ±5)
            show_marker: показывать визуальный маркер на месте клика
            use_action_chains: использовать ActionChains (для интерактивных элементов)
        """
        print(f"🖱️  Клик по координатам ({x}, {y})...")

        # Добавляем случайность к координатам
        x_random = x + random.randint(-x_variance, x_variance)
        y_random = y + random.randint(-y_variance, y_variance)

        # Добавляем визуальный маркер на место клика
        if show_marker:
            self.driver.execute_script(f"""
                var marker = document.createElement('div');
                marker.style.position = 'fixed';
                marker.style.left = '{x_random}px';
                marker.style.top = '{y_random}px';
                marker.style.width = '20px';
                marker.style.height = '20px';
                marker.style.borderRadius = '50%';
                marker.style.backgroundColor = 'red';
                marker.style.border = '3px solid yellow';
                marker.style.zIndex = '999999';
                marker.style.pointerEvents = 'none';
                marker.style.transform = 'translate(-50%, -50%)';
                document.body.appendChild(marker);
            """)

        if use_action_chains:
            # Используем ActionChains для интерактивных элементов (Zoom UI)
            print(f"   🎯 Использую ActionChains (реальное движение мыши)")

            element = self.driver.execute_script(f"""
                var elem = document.elementFromPoint({x_random}, {y_random});
                if (elem) {{
                    console.log('Найден элемент:', elem.tagName, elem.className, elem.id);
                }}
                return elem;
            """)

            if element:
                element_info = self.driver.execute_script("""
                    return {
                        tag: arguments[0].tagName,
                        class: arguments[0].className,
                        id: arguments[0].id,
                        text: arguments[0].textContent ? arguments[0].textContent.substring(0, 50) : ''
                    };
                """, element)
                print(f"   📍 Элемент: {element_info}")

                try:
                    actions = ActionChains(self.driver)
                    actions.move_to_element_with_offset(element, 0, 0)
                    actions.pause(random.uniform(0.1, 0.3))
                    actions.click()
                    actions.perform()
                    print(f"   ✅ ActionChains клик выполнен (РЕАЛЬНЫЙ КЛИК МЫШЬЮ)")
                except Exception as e:
                    print(f"   ⚠️  Ошибка ActionChains: {e}")
                    print(f"   Пробую прямой WebElement.click()...")
                    try:
                        element.click()
                        print(f"   ✅ WebElement.click() выполнен")
                    except Exception as e2:
                        print(f"   ❌ WebElement.click() тоже не сработал: {e2}")
            else:
                print(f"   ⚠️  Элемент не найден в точке ({x_random}, {y_random})")
        else:
            # Прямой JavaScript клик для простых элементов (кнопки, ссылки)
            clicked = self.driver.execute_script(f"""
                var element = document.elementFromPoint({x_random}, {y_random});
                if (element) {{
                    // Эмулируем полный цикл событий клика
                    var events = ['mouseenter', 'mouseover', 'mousedown', 'mouseup', 'click'];
                    events.forEach(function(eventType) {{
                        var event = new MouseEvent(eventType, {{
                            'view': window,
                            'bubbles': true,
                            'cancelable': true,
                            'clientX': {x_random},
                            'clientY': {y_random}
                        }});
                        element.dispatchEvent(event);
                    }});
                    return true;
                }}
                return false;
            """)

            if clicked:
                print(f"   ✅ JavaScript клик выполнен по ({x_random}, {y_random})")
            else:
                print(f"   ⚠️  Элемент не найден в точке ({x_random}, {y_random})")

        time.sleep(random.uniform(0.3, 0.7))

    def human_like_type(self, text):
        """
        Эмулирует человеческий ввод текста в активный элемент

        Args:
            text: текст для ввода
        """
        print(f"⌨️  Ввод текста '{text}'...")

        # Вводим текст посимвольно через send_keys
        try:
            from selenium.webdriver.common.keys import Keys

            # Получаем активный элемент
            active_element = self.driver.switch_to.active_element

            # Очищаем поле
            active_element.clear()

            # Вводим посимвольно
            for char in text:
                active_element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))

            print(f"   ✅ Текст '{text}' введен посимвольно")
        except Exception as e:
            print(f"   ⚠️  Ошибка ввода: {e}")

        time.sleep(random.uniform(0.3, 0.5))

    def open_meeting(self, url):
        """Открывает встречу по URL"""
        print(f"\n🔗 Открываю встречу: {url}")
        self.driver.get(url)

        # Скриншот после загрузки
        print(f"⏳ Ожидание загрузки...")
        self.human_like_delay(3, 5)
        self.take_screenshot("01_page_loaded.png")

        # Клик по кнопке "Принять куки"
        print("\n🍪 Нажимаю кнопку 'Принять куки'...")
        cookie_elem = self.driver.execute_script("""
            var elem = document.elementFromPoint(677, 262);
            if (elem) {
                return {
                    tag: elem.tagName,
                    id: elem.id,
                    class: elem.className,
                    text: elem.textContent ? elem.textContent.substring(0, 50) : ''
                };
            }
            return null;
        """)
        print(f"   🔍 Элемент в точке (677, 262): {cookie_elem}")
        self.human_like_click(677, 262)
        self.human_like_delay(2, 3)
        self.take_screenshot("02_after_cookie_accept.png")

        # Клик по кнопке "Присоединиться"
        print("\n🎥 Нажимаю кнопку 'Присоединиться'...")
        self.human_like_click(592, 439)
        self.human_like_delay(2, 3)
        self.take_screenshot("03_after_join.png")

        # Клик по ссылке "Join from your browser"
        print("\n🌐 Нажимаю 'Join from your browser'...")
        self.human_like_click(736, 616)
        self.human_like_delay(3, 5)
        self.take_screenshot("04_after_browser_join.png")

        # Переключаемся в iframe где находится Zoom интерфейс
        print("\n🔄 Переключаюсь в iframe Zoom...")
        try:
            iframe = self.driver.find_element("id", "webclient")
            self.driver.switch_to.frame(iframe)
            print("   ✅ Переключен в iframe 'webclient'")
            self.take_screenshot("04b_inside_iframe.png")

            # Выводим информацию об элементах по нашим координатам
            print("\n🔍 Ищу селекторы элементов...")

            # Mute button
            mute_info = self.driver.execute_script("""
                var elem = document.elementFromPoint(339, 486);
                if (elem) {
                    return {
                        tag: elem.tagName,
                        id: elem.id,
                        class: elem.className,
                        ariaLabel: elem.getAttribute('aria-label'),
                        role: elem.getAttribute('role'),
                        type: elem.getAttribute('type')
                    };
                }
                return null;
            """)
            print(f"   Mute (339, 486): {mute_info}")

            # Stop Video button
            video_info = self.driver.execute_script("""
                var elem = document.elementFromPoint(427, 486);
                if (elem) {
                    return {
                        tag: elem.tagName,
                        id: elem.id,
                        class: elem.className,
                        ariaLabel: elem.getAttribute('aria-label'),
                        role: elem.getAttribute('role'),
                        type: elem.getAttribute('type')
                    };
                }
                return null;
            """)
            print(f"   Stop Video (427, 486): {video_info}")

            # Name input
            name_info = self.driver.execute_script("""
                var elem = document.elementFromPoint(969, 256);
                if (elem) {
                    return {
                        tag: elem.tagName,
                        id: elem.id,
                        class: elem.className,
                        name: elem.getAttribute('name'),
                        placeholder: elem.getAttribute('placeholder'),
                        type: elem.getAttribute('type')
                    };
                }
                return null;
            """)
            print(f"   Name Input (969, 256): {name_info}")

        except Exception as e:
            print(f"   ⚠️  Не удалось переключиться в iframe: {e}")

        # Находим родительские кнопки для Mute и Stop Video
        print("\n🔍 Ищу кнопки по aria-label...")

        # Клик "Mute" - используем JavaScript клик (headless compatible)
        print("\n🔇 Нажимаю кнопку 'Mute'...")
        try:
            # Получаем родительскую кнопку для SVG path и кликаем через JavaScript
            clicked = self.driver.execute_script("""
                var elem = document.elementFromPoint(339, 486);
                // Поднимаемся по DOM до тега BUTTON
                while (elem && elem.tagName !== 'BUTTON') {
                    elem = elem.parentElement;
                }
                if (elem) {
                    console.log('Mute button:', elem);
                    elem.click();
                    return {success: true, aria: elem.getAttribute('aria-label')};
                }
                return {success: false};
            """)

            if clicked.get('success'):
                print(f"   ✅ Нажал кнопку через JavaScript: {clicked.get('aria')}")
            else:
                print(f"   ⚠️  Кнопка не найдена")
        except Exception as e:
            print(f"   ⚠️  Ошибка: {e}")

        self.human_like_delay(1, 2)
        self.take_screenshot("05_after_mute.png")

        # Клик "Stop Video" - используем JavaScript клик (headless compatible)
        print("\n📹 Нажимаю кнопку 'Stop Video'...")
        try:
            # Получаем родительскую кнопку для SVG и кликаем через JavaScript
            clicked = self.driver.execute_script("""
                var elem = document.elementFromPoint(427, 486);
                // Поднимаемся по DOM до тега BUTTON
                while (elem && elem.tagName !== 'BUTTON') {
                    elem = elem.parentElement;
                }
                if (elem) {
                    console.log('Video button:', elem);
                    elem.click();
                    return {success: true, aria: elem.getAttribute('aria-label')};
                }
                return {success: false};
            """)

            if clicked.get('success'):
                print(f"   ✅ Нажал кнопку через JavaScript: {clicked.get('aria')}")
            else:
                print(f"   ⚠️  Кнопка не найдена")
        except Exception as e:
            print(f"   ⚠️  Ошибка: {e}")

        self.human_like_delay(1, 2)
        self.take_screenshot("06_after_stop_video.png")

        # Ввод имени бота - CDP Input.insertText (последняя надежда)
        print(f"\n✍️  Ввожу имя бота: '{BOT_NAME}'...")
        try:
            # Активируем поле через JavaScript
            self.driver.execute_script("""
                var input = document.getElementById('input-for-name');
                if (input) {
                    input.focus();
                    input.click();
                }
            """)

            print(f"   ✅ Поле активировано")
            self.human_like_delay(0.5, 0.7)

            # Пробуем CDP Input.insertText - это специальный метод для вставки текста
            print(f"   ⌨️  Ввод через CDP Input.insertText...")
            self.driver.execute_cdp_cmd('Input.insertText', {
                'text': BOT_NAME
            })

            self.human_like_delay(0.3, 0.5)

            # Проверяем результат
            entered_value = self.driver.execute_script("""
                var input = document.getElementById('input-for-name');
                return input ? input.value : null;
            """)

            print(f"   ✅ Результат: '{entered_value}'")

            # Если не сработало, выходим из iframe и пробуем заново
            if not entered_value:
                print(f"   ⚠️  Пусто! Пробую выйти из iframe и вернуться...")

                # Выходим из iframe
                self.driver.switch_to.default_content()
                self.human_like_delay(0.3, 0.5)

                # Входим обратно
                iframe = self.driver.find_element("id", "webclient")
                self.driver.switch_to.frame(iframe)
                self.human_like_delay(0.3, 0.5)

                # Пробуем снова
                name_input = self.driver.find_element("id", "input-for-name")
                name_input.click()
                self.human_like_delay(0.3, 0.5)
                name_input.send_keys(BOT_NAME)

                entered_value = name_input.get_attribute('value')
                print(f"   ✅ После повторного входа: '{entered_value}'")

        except Exception as e:
            print(f"   ⚠️  Ошибка ввода имени: {e}")
            import traceback
            traceback.print_exc()

        self.human_like_delay(1, 2)
        self.take_screenshot("07_after_name_input.png")

        # Клик "Join" - входим в конференцию (используем JavaScript как с Mute/Video)
        print("\n🚪 Нажимаю кнопку 'Join'...")
        try:
            # Получаем родительскую кнопку и кликаем через JavaScript
            clicked = self.driver.execute_script("""
                var elem = document.elementFromPoint(969, 379);
                // Поднимаемся по DOM до тега BUTTON
                while (elem && elem.tagName !== 'BUTTON') {
                    elem = elem.parentElement;
                }
                if (elem) {
                    console.log('Join button:', elem);
                    elem.click();
                    return {success: true, aria: elem.getAttribute('aria-label'), text: elem.textContent};
                }
                return {success: false};
            """)

            if clicked.get('success'):
                print(f"   ✅ Нажал кнопку через JavaScript: '{clicked.get('text')}' (aria: {clicked.get('aria')})")
            else:
                print(f"   ⚠️  Кнопка не найдена")
        except Exception as e:
            print(f"   ⚠️  Ошибка: {e}")

        self.human_like_delay(2, 3)
        self.take_screenshot("08_after_join.png")

        print(f"📄 Заголовок страницы: {self.driver.title}")

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

            # Открытие встречи
            self.open_meeting(MEETING_URL)

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
