#!/usr/bin/env python3
"""
Headless browser screenshot script
Открывает браузер в фоновом режиме и делает скриншот
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def take_screenshot(url, output_file="screenshot.png"):
    """
    Открывает URL в headless браузере и делает скриншот

    Args:
        url: URL страницы для скриншота
        output_file: Имя файла для сохранения скриншота
    """
    print(f"Запуск headless браузера...")

    # Настройка Chrome в headless режиме
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Новый headless режим
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")

    # Инициализация драйвера
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print(f"Открываю страницу: {url}")
        driver.get(url)

        # Ждем загрузки страницы
        time.sleep(2)

        print(f"Делаю скриншот...")
        driver.save_screenshot(output_file)

        print(f"✅ Скриншот сохранен: {output_file}")
        print(f"   Размер окна: {driver.get_window_size()}")
        print(f"   Заголовок страницы: {driver.title}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        driver.quit()
        print("Браузер закрыт")

if __name__ == "__main__":
    # Пример использования
    url = "https://www.google.com"
    output = "google_screenshot.png"

    take_screenshot(url, output)
