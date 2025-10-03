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

    def _human_like_click(self, x, y, x_variance=5, y_variance=5, show_marker=True, screenshot_name=None):
        """Эмулирует человеческий клик по координатам через JavaScript

        Args:
            screenshot_name: имя скриншота С маркером (делается до клика)
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

            # Скриншот с маркером ДО клика
            if screenshot_name and self.take_screenshot:
                time.sleep(0.3)  # Даём маркеру отрисоваться
                self.take_screenshot(screenshot_name)
                print(f"   📸 Скриншот с маркером: {screenshot_name}")

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

            # Прокрутка страницы вниз для 800x600
            print("\n📜 Прокрутка страницы вниз...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self._human_like_delay(1, 1)
            if self.take_screenshot:
                self.take_screenshot("01a_after_scroll.png")

            # Клик по центральной кнопке после скрола (с маркером на скриншоте)
            print("\n🖱️  Клик по центральной кнопке...")
            self._human_like_click(400, 208, x_variance=0, y_variance=0, screenshot_name="01b_center_click_MARKER.png")
            self._human_like_delay(2, 3)
            if self.take_screenshot:
                self.take_screenshot("01c_after_center_click.png")

            # Клик по ссылке (536, 392)
            print("\n🔗 Клик по ссылке...")
            self._human_like_click(536, 392, x_variance=0, y_variance=0, screenshot_name="01d_link_click_MARKER.png")
            self._human_like_delay(2, 3)
            if self.take_screenshot:
                self.take_screenshot("01e_after_link_click.png")

            # Закрываем xdg-open диалог через xdotool (реальный X11 клик)
            print("\n🧹 Закрываю xdg-open диалог (xdotool)...")
            try:
                import subprocess

                # Координаты кнопки Cancel (800x600: 510, 275)
                # xdotool кликает на реальные координаты экрана X11
                result = subprocess.run(
                    ['xdotool', 'mousemove', '510', '275', 'click', '1'],
                    env={'DISPLAY': ':99'},
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    print(f"   ✅ xdotool клик выполнен (510, 275)")
                else:
                    print(f"   ⚠️  xdotool ошибка: {result.stderr}")

                time.sleep(1)

            except Exception as e:
                print(f"   ⚠️  Ошибка xdotool: {e}")

            if self.take_screenshot:
                self.take_screenshot("01b_after_xdg_close.png")

            # Старые клики для 1200x800 УДАЛЕНЫ (заменены на скрол + 2 клика выше)

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

                # Mute button (800x600)
                mute_info = self.driver.execute_script("""
                    var elem = document.elementFromPoint(350, 212);
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
                print(f"   Mute (350, 212): {mute_info}")

                # Stop Video button (800x600)
                video_info = self.driver.execute_script("""
                    var elem = document.elementFromPoint(437, 212);
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
                print(f"   Stop Video (437, 212): {video_info}")

                # Name input (800x600)
                name_info = self.driver.execute_script("""
                    var elem = document.elementFromPoint(395, 386);
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

            # Задержка перед кликами Mute/Video
            print("\n⏳ Ожидание 3 секунды перед кликами Mute/Video...")
            self._human_like_delay(3, 3)

            # Клик "Mute" микрофон (800x600: 350, 212)
            print("\n🔇 Нажимаю кнопку 'Mute' (микрофон)...")
            try:
                # Добавляем маркер
                self.driver.execute_script("""
                    var marker = document.createElement('div');
                    marker.id = 'mute-marker';
                    marker.style.position = 'fixed';
                    marker.style.left = '350px';
                    marker.style.top = '212px';
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
                time.sleep(0.3)
                if self.take_screenshot:
                    self.take_screenshot("05a_mute_MARKER.png")

                clicked = self.driver.execute_script("""
                    var elem = document.elementFromPoint(350, 212);
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
                self.take_screenshot("05b_after_mute.png")

            # Клик "Stop Video" (800x600: 437, 212)
            print("\n📹 Нажимаю кнопку 'Stop Video'...")
            try:
                # Добавляем маркер
                self.driver.execute_script("""
                    var marker = document.createElement('div');
                    marker.id = 'video-marker';
                    marker.style.position = 'fixed';
                    marker.style.left = '437px';
                    marker.style.top = '212px';
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
                time.sleep(0.3)
                if self.take_screenshot:
                    self.take_screenshot("06a_video_MARKER.png")

                clicked = self.driver.execute_script("""
                    var elem = document.elementFromPoint(437, 212);
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

            # Клик "Join" - входим в конференцию (800x600: 394, 507)
            print("\n🚪 Нажимаю кнопку 'Join'...")
            try:
                clicked = self.driver.execute_script("""
                    var elem = document.elementFromPoint(394, 507);
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

            # Дополнительный клик через 3 секунды (закрытие диалога/уведомления)
            print("\n⏳ Ожидание 3 секунды перед дополнительным кликом...")
            self._human_like_delay(3, 3)

            print(f"🖱️  Клик по (660, 200)...")
            clicked = self.driver.execute_script("""
                var elem = document.elementFromPoint(660, 200);
                if (elem) {
                    var events = ['mousedown', 'mouseup', 'click'];
                    events.forEach(function(eventType) {
                        var event = new MouseEvent(eventType, {
                            'view': window,
                            'bubbles': true,
                            'cancelable': true,
                            'clientX': 660,
                            'clientY': 200
                        });
                        elem.dispatchEvent(event);
                    });
                    return {success: true, tag: elem.tagName, text: elem.textContent.substring(0, 50)};
                }
                return {success: false};
            """)

            if clicked.get('success'):
                print(f"   ✅ Клик выполнен: {clicked.get('tag')} - '{clicked.get('text')}'")
            else:
                print(f"   ℹ️  Элемент не найден (возможно диалог не появился)")

            if self.take_screenshot:
                self.take_screenshot("09_after_dialog_click.png")

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

            # Кликаем по координатам кнопки Leave (800x600: x: 735-785, y: 465-505)
            leave_x = 760  # Середина диапазона 735-785
            leave_y = 485  # Середина диапазона 465-505

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

            # Проверяем наличие кнопки Leave по координатам (800x600)
            leave_x = 760
            leave_y = 485

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
