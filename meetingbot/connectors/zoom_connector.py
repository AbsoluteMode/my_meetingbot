"""
Zoom Meeting Connector
"""
import time
import random
from .base_connector import BaseMeetingConnector


class ZoomConnector(BaseMeetingConnector):
    """Коннектор для подключения к Zoom встречам"""

    def get_platform_name(self) -> str:
        return "Zoom"

    def _human_like_delay(self, min_sec=1, max_sec=3):
        """Случайная задержка как у человека"""
        delay = random.uniform(min_sec, max_sec)
        print(f"⏳ Задержка {delay:.2f} сек...")
        time.sleep(delay)

    def _human_like_click(self, x, y, x_variance=5, y_variance=5, show_marker=True):
        """Эмулирует человеческий клик по координатам через JavaScript"""
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

        # Прямой JavaScript клик
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

    def join_meeting(self, meeting_url: str) -> bool:
        """Подключиться к Zoom встрече"""
        try:
            print(f"\n🔗 Открываю Zoom встречу: {meeting_url}")
            self.driver.get(meeting_url)

            # Скриншот после загрузки
            print(f"⏳ Ожидание загрузки...")
            self._human_like_delay(3, 5)
            if self.take_screenshot:
                self.take_screenshot("01_page_loaded.png")

            # Клик по кнопке "Принять куки"
            print("\n🍪 Нажимаю кнопку 'Принять куки'...")
            self._human_like_click(677, 262)
            self._human_like_delay(2, 3)
            if self.take_screenshot:
                self.take_screenshot("02_after_cookie_accept.png")

            # Клик по кнопке "Присоединиться"
            print("\n🎥 Нажимаю кнопку 'Присоединиться'...")
            self._human_like_click(592, 439)
            self._human_like_delay(2, 3)
            if self.take_screenshot:
                self.take_screenshot("03_after_join.png")

            # Клик по ссылке "Join from your browser"
            print("\n🌐 Нажимаю 'Join from your browser'...")
            self._human_like_click(736, 616)
            self._human_like_delay(3, 5)
            if self.take_screenshot:
                self.take_screenshot("04_after_browser_join.png")

            # Переключаемся в iframe где находится Zoom интерфейс
            print("\n🔄 Переключаюсь в iframe Zoom...")
            try:
                iframe = self.driver.find_element("id", "webclient")
                self.driver.switch_to.frame(iframe)
                print("   ✅ Переключен в iframe 'webclient'")
                if self.take_screenshot:
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
                return False

            # Находим родительские кнопки для Mute и Stop Video
            print("\n🔍 Ищу кнопки по aria-label...")
            print("   ℹ️  Звук динамиков управляется браузером автоматически")

            # Клик "Mute" микрофон - используем JavaScript клик (headless compatible)
            print("\n🔇 Нажимаю кнопку 'Mute' (микрофон)...")
            try:
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

            self._human_like_delay(1, 2)
            if self.take_screenshot:
                self.take_screenshot("05_after_mute.png")

            # Клик "Stop Video" - используем JavaScript клик (headless compatible)
            print("\n📹 Нажимаю кнопку 'Stop Video'...")
            try:
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

            self._human_like_delay(1, 2)
            if self.take_screenshot:
                self.take_screenshot("06_after_stop_video.png")

            # Ввод имени бота - CDP Input.insertText
            print(f"\n✍️  Ввожу имя бота: '{self.bot_name}'...")
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
                self._human_like_delay(0.5, 0.7)

                # Пробуем CDP Input.insertText
                print(f"   ⌨️  Ввод через CDP Input.insertText...")
                self.driver.execute_cdp_cmd('Input.insertText', {
                    'text': self.bot_name
                })

                self._human_like_delay(0.3, 0.5)

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
                    self._human_like_delay(0.3, 0.5)

                    # Входим обратно
                    iframe = self.driver.find_element("id", "webclient")
                    self.driver.switch_to.frame(iframe)
                    self._human_like_delay(0.3, 0.5)

                    # Пробуем снова
                    name_input = self.driver.find_element("id", "input-for-name")
                    name_input.click()
                    self._human_like_delay(0.3, 0.5)
                    name_input.send_keys(self.bot_name)

                    entered_value = name_input.get_attribute('value')
                    print(f"   ✅ После повторного входа: '{entered_value}'")

            except Exception as e:
                print(f"   ⚠️  Ошибка ввода имени: {e}")
                import traceback
                traceback.print_exc()

            self._human_like_delay(1, 2)
            if self.take_screenshot:
                self.take_screenshot("07_after_name_input.png")

            # Клик "Join" - входим в конференцию
            print("\n🚪 Нажимаю кнопку 'Join'...")
            try:
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

            self._human_like_delay(2, 3)
            if self.take_screenshot:
                self.take_screenshot("08_after_join.png")

            print(f"📄 Заголовок страницы: {self.driver.title}")
            print(f"✅ Успешно подключился к {self.get_platform_name()}")

            return True

        except Exception as e:
            print(f"❌ Ошибка подключения к {self.get_platform_name()}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def leave_meeting(self) -> bool:
        """Выйти из Zoom встречи"""
        try:
            print(f"🚪 Выхожу из {self.get_platform_name()} встречи...")

            # Сначала выходим из iframe если мы в нём
            try:
                self.driver.switch_to.default_content()
            except:
                pass

            # Переключаемся в iframe
            try:
                iframe = self.driver.find_element("id", "webclient")
                self.driver.switch_to.frame(iframe)
                print(f"   ✅ Переключился в iframe")
            except Exception as e:
                print(f"   ⚠️  Не удалось переключиться в iframe: {e}")
                return False

            # Кликаем по координатам кнопки Leave (x: 1142-1178, y: 668-708)
            leave_x = 1160  # Середина диапазона 1142-1178
            leave_y = 688   # Середина диапазона 668-708

            print(f"   🖱️  Кликаю на Leave кнопку ({leave_x}, {leave_y})...")

            clicked = self.driver.execute_script(f"""
                var elem = document.elementFromPoint({leave_x}, {leave_y});
                // Поднимаемся по DOM до тега BUTTON
                while (elem && elem.tagName !== 'BUTTON') {{
                    elem = elem.parentElement;
                }}
                if (elem) {{
                    console.log('Leave button:', elem);
                    elem.click();
                    return {{success: true, aria: elem.getAttribute('aria-label'), text: elem.textContent}};
                }}
                return {{success: false}};
            """)

            if clicked.get('success'):
                print(f"   ✅ Нажал кнопку Leave: '{clicked.get('text')}' (aria: {clicked.get('aria')})")
                time.sleep(2)

                # Если появился диалог подтверждения - ищем "Leave Meeting" кнопку
                confirm_clicked = self.driver.execute_script("""
                    var buttons = document.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {
                        var btn = buttons[i];
                        var text = btn.textContent || btn.innerText || '';
                        if (text.toLowerCase().includes('leave meeting')) {
                            console.log('Confirming leave:', btn);
                            btn.click();
                            return {success: true, text: text};
                        }
                    }
                    return {success: false};
                """)

                if confirm_clicked.get('success'):
                    print(f"   ✅ Подтвердил выход: {confirm_clicked.get('text')}")

                return True
            else:
                print(f"   ⚠️  Кнопка Leave не найдена в точке ({leave_x}, {leave_y})")
                return False

        except Exception as e:
            print(f"   ❌ Ошибка при выходе: {e}")
            return False

    def check_in_meeting(self) -> bool:
        """Проверить находится ли бот в Zoom встрече"""
        try:
            # Переключаемся в iframe
            try:
                self.driver.switch_to.default_content()
                iframe = self.driver.find_element("id", "webclient")
                self.driver.switch_to.frame(iframe)
            except:
                # Если iframe не найден - встреча завершена
                return False

            # Проверяем наличие кнопки Leave по координатам
            leave_x = 1160
            leave_y = 688

            leave_exists = self.driver.execute_script(f"""
                var elem = document.elementFromPoint({leave_x}, {leave_y});
                // Поднимаемся по DOM до тега BUTTON
                while (elem && elem.tagName !== 'BUTTON') {{
                    elem = elem.parentElement;
                }}
                if (elem) {{
                    var text = elem.textContent || elem.innerText || '';
                    var aria = elem.getAttribute('aria-label') || '';
                    // Проверяем что это действительно кнопка Leave
                    if (text.toLowerCase().includes('leave') || aria.toLowerCase().includes('leave')) {{
                        return true;
                    }}
                }}
                return false;
            """)

            return leave_exists

        except Exception as e:
            # Если произошла ошибка - считаем что встреча завершена
            return False
