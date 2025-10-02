"""
Базовый класс для коннекторов встреч
"""
from abc import ABC, abstractmethod


class BaseMeetingConnector(ABC):
    """Абстрактный базовый класс для подключения к различным платформам встреч"""

    def __init__(self, driver, bot_name: str, take_screenshot_callback=None):
        """
        Args:
            driver: Selenium WebDriver instance
            bot_name: Имя бота для отображения на встрече
            take_screenshot_callback: Функция для создания скриншотов (опционально)
        """
        self.driver = driver
        self.bot_name = bot_name
        self.take_screenshot = take_screenshot_callback

    @abstractmethod
    def join_meeting(self, meeting_url: str) -> bool:
        """
        Подключиться к встрече

        Args:
            meeting_url: URL встречи

        Returns:
            bool: True если успешно подключились, False иначе
        """
        pass

    @abstractmethod
    def get_platform_name(self) -> str:
        """
        Получить название платформы

        Returns:
            str: Название платформы (например, "Zoom", "Google Meet")
        """
        pass

    @abstractmethod
    def leave_meeting(self) -> bool:
        """
        Выйти из встречи

        Returns:
            bool: True если успешно вышли, False иначе
        """
        pass

    @abstractmethod
    def check_in_meeting(self) -> bool:
        """
        Проверить находится ли бот во встрече

        Returns:
            bool: True если в встрече (кнопка Leave есть), False если встреча завершена
        """
        pass
