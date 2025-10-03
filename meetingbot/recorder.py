"""
Screen Recorder - запись экрана через ffmpeg
"""
import subprocess
import time
from pathlib import Path


class ScreenRecorder:
    """Класс для записи экрана через ffmpeg"""

    def __init__(self, output_path: Path, display=":99", resolution="1200x800", fps=15):
        """
        Args:
            output_path: Путь к выходному видеофайлу
            display: DISPLAY для X11 (по умолчанию :99 для Xvfb)
            resolution: Разрешение записи
            fps: Частота кадров
        """
        self.output_path = output_path
        # Временный файл - не будет виден пользователю до финализации
        self.temp_path = output_path.parent / f"{output_path.stem}.tmp{output_path.suffix}"
        self.display = display
        self.resolution = resolution
        self.fps = fps
        self.process = None

    def start(self):
        """Запуск записи"""
        print(f"🎬 Запуск записи экрана...")
        print(f"   Финальный файл: {self.output_path.name}")
        print(f"   Временный файл: {self.temp_path.name}")
        print(f"   Разрешение: {self.resolution}")
        print(f"   FPS: {self.fps}")

        # ffmpeg команда для записи X11 display + PulseAudio
        # ПИШЕМ ВО ВРЕМЕННЫЙ ФАЙЛ
        cmd = [
            "ffmpeg",
            "-f", "x11grab",
            "-video_size", self.resolution,
            "-framerate", str(self.fps),
            "-i", self.display,
            "-f", "pulse",
            "-i", "virtual_speaker.monitor",  # Захват аудио с виртуального устройства
            "-codec:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-codec:a", "aac",
            "-b:a", "128k",
            "-y",  # Перезаписать если файл существует
            str(self.temp_path)  # Пишем во временный файл
        ]

        # Проверяем что display доступен
        import subprocess as sp
        try:
            sp.run(["xdpyinfo", "-display", self.display],
                   check=True, capture_output=True, timeout=2)
        except (sp.CalledProcessError, FileNotFoundError, sp.TimeoutExpired):
            print(f"   ❌ Display {self.display} недоступен! Убедитесь что Xvfb запущен.")
            return False

        try:
            # Запускаем ffmpeg с выводом stderr в консоль для диагностики
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE  # Отдельный stderr
            )
            time.sleep(2)  # Даём ffmpeg время на инициализацию

            if self.process.poll() is not None:
                # Процесс уже завершился - ошибка
                stdout, stderr = self.process.communicate()
                print(f"   ❌ Ошибка запуска ffmpeg:")
                if stderr:
                    print(stderr.decode())
                if stdout:
                    print(stdout.decode())
                return False

            print(f"   ✅ Запись начата (PID: {self.process.pid})")

            # Читаем первые несколько строк вывода ffmpeg для диагностики
            import select
            if select.select([self.process.stderr], [], [], 0.5)[0]:
                diagnostic = self.process.stderr.read(500).decode(errors='ignore')
                if 'pulse' in diagnostic.lower() or 'audio' in diagnostic.lower():
                    print(f"   🔍 FFmpeg аудио: {diagnostic[:200]}")

            return True

        except FileNotFoundError:
            print(f"   ❌ ffmpeg не найден! Установите ffmpeg")
            return False
        except Exception as e:
            print(f"   ❌ Ошибка запуска записи: {e}")
            return False

    def stop(self):
        """Остановка записи"""
        if not self.process:
            print("⚠️  Запись не была запущена")
            return False

        print(f"🛑 Остановка записи...")

        try:
            # Отправляем SIGINT (как Ctrl+C) для graceful shutdown
            import signal
            self.process.send_signal(signal.SIGINT)

            # Ждём завершения (увеличено до 10 секунд)
            try:
                self.process.wait(timeout=10)
                print(f"   ✅ Временный файл финализирован")

                # Проверяем временный файл
                if self.temp_path.exists():
                    size_mb = self.temp_path.stat().st_size / (1024 * 1024)
                    print(f"   📊 Размер временного файла: {size_mb:.2f} MB")

                    # Переименовываем временный файл в финальный
                    import shutil
                    shutil.move(str(self.temp_path), str(self.output_path))
                    print(f"   ✅ Файл готов: {self.output_path.name}")

                return True
            except subprocess.TimeoutExpired:
                print(f"   ⚠️  ffmpeg не завершился за 10 сек, принудительное завершение...")
                self.process.kill()
                self.process.wait()

                # Пробуем переименовать даже после kill
                if self.temp_path.exists():
                    import shutil
                    shutil.move(str(self.temp_path), str(self.output_path))
                    print(f"   ⚠️  Файл сохранён (после kill): {self.output_path.name}")

                return True

        except Exception as e:
            print(f"   ❌ Ошибка остановки записи: {e}")
            return False

    def is_recording(self):
        """Проверка, идёт ли запись"""
        return self.process is not None and self.process.poll() is None
