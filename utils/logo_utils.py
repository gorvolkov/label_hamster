"""
Это небольшой пакет функций для работы с файлами логотипов.
Ничто из этого не используется в основном функционале скрипта.
Однако модуль может быть полезен для подготовки к работе папки с логотипами.

ВАЖНО! Перед использованием нужно убедиться, что логотип каждого бренда имеет вариант в .png-формате.
Если такого нет, нужно запросить у дизайнера.
Или можно конвертировать имеющийся .jpg/.jpeg-вариант в .png с помощью функции _convert_jpg_to_png (она в самом низу).

В блоке main реализован скрипт подготовки к работе
"""

import os
import shutil
from PIL import Image

from config import LOGO_DIR, LOGO_DOWNLOAD


def _put_all_in_one(old_dir: str, new_dir: str) -> None:
    """Переносит все графические файлы из распакованного архива с логотипами с Яндекс Диска в одну папку"""
    for root, dirs, files in os.walk(old_dir):
        for filename in files:
            old_path = os.path.join(root, filename)
            new_path = os.path.join(new_dir, filename)
            shutil.copy(old_path, new_path)


def _lower_all_names(dir: str) -> None:
    """Приводит имена всех файлов в заданной директории к нижнему регистру"""
    for file in os.listdir(dir):
        old_filepath = os.path.join(dir, file)
        new_filepath = os.path.join(dir, file.lower())
        os.rename(old_filepath, new_filepath)


def _remove_non_png(dir: str) -> None:
    """Удаляет вcе файлы, кроме .png"""
    for filename in os.listdir(dir):
        if not filename.lower().endswith('.png'):
            filepath = os.path.join(dir, filename)
            try:
                os.remove(filepath)
                print(f'Removed: {filepath}')
            except Exception as e:
                print(f'Error while removing file {filepath}: {e}')


def _square(dir: str, square_size: int = None) -> None:
    """
    Дополняет все изображения в заданной папке до квадратов и унифицирует по размеру

    :param dir: путь до папки с изображениями (обрабатывает только .png, остальные будут пропущены)
    :param square_size: размер стороны квадрата в пикселях (если не установлен, то будет отформатировано по большей стороне прямоугольного исходника)

    """

    for filename in os.listdir(dir):
        filepath = os.path.join(dir, filename)

        with Image.open(filepath) as img:
            width, height = img.size

            # Определяем размер квадрата
            if square_size is None:
                size = max(width, height)
            else:
                size = square_size

            # Масштабируем изображение, если задан размер квадрата и он отличается от максимального размера
            if square_size is not None and (width != size or height != size):
                # Сохраняем пропорции, вписывая изображение в квадрат нужного размера
                img.thumbnail((size, size), Image.Resampling.LANCZOS)
                width, height = img.size

            # Создаём новое квадратное изображение с прозрачным фоном
            new_img = Image.new('RGBA', (size, size), (255, 255, 255, 0))

            # Центрируем изображение в квадрате
            x_offset = (size - width) // 2
            y_offset = (size - height) // 2
            new_img.paste(img, (x_offset, y_offset))

            # Сохраняем результат, заменяя исходный файл
            new_img.save(filepath)


def _grayscale(dir: str):
    """Переводит все изображения в переданной директории в оттенки серого"""

    for filename in os.listdir(dir):
        filepath = os.path.join(dir, filename)

        img = Image.open(filepath)
        if img.mode in ('RGBA', 'LA'):
            # Создаём белый фон
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])  # Альфа-канал как маска
            img = background
        else:
            img = img.convert('RGB')
        img_gray = img.convert('L')
        img_gray.save(filepath)


def _convert_jpg_to_png(file: str):
    """
    Конвертирует переданный .jpg/.jpeg в .png

    :param file: абсолютный путь к файлу, который нужно конвертировать
    """

    png_path = os.path.splitext(file)[0] + '.png'
    try:
        with Image.open(file) as img:
            img.save(png_path, 'PNG')
        os.remove(file)  # Удаляем исходный JPG
        print(f'Converted and removed: {file} -> {png_path}')
    except Exception as e:
        print(f'An error with file {file}: {e}')


if __name__ == "__main__":
    # Перед запуском необходимо скачать все логотипы с Яндекс Диска и положить их в папку _logo_download

    raw_logo_dir, logo_dir = LOGO_DOWNLOAD, LOGO_DIR

    # 1. вынимаем все графические файлы и складываем их в рабочую папку
    _put_all_in_one(old_dir=raw_logo_dir, new_dir=logo_dir)

    # 2. приводим все наименования к нижнему регистру
    _lower_all_names(dir=logo_dir)

    # 3. удаляем всё, кроме .png
    _remove_non_png(dir=logo_dir)

    # 4. приводим все логотипы к квадратному формату со стороной 500 px
    _square(dir=logo_dir, square_size=500)

    # 5. переводим всё в оттенки серого
    _grayscale(dir=logo_dir)

    # Далее, к сожалению, всё равно надо пройтись руками по вариантам и оставить только необходимое.
    # Потому что в исходниках будут дубли и разные варианты логотипов для одного и того же бренда.
    # Кроме того, часть названий на китайском, их надо переименовать человеческой латиницей.

    # # 6. удаляем исходники. НО ПЕРЕД ЭТИМ ЛУЧШЕ ПРОВЕРИТЬ, ЧТО ВСЕ БРЕНДЫ ПОЛУЧИЛИ СВОИ ЛОГОТИПЫ.
    # from utils import cleanup_temp_recursive
    # cleanup_temp_recursive(dir=raw_logo_dir)

