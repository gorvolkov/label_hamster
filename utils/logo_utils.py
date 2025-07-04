"""
Функционал для подготовки папки logo_simple к корректному использованию.
Чтобы не перебирать руками.
"""

from logger import logger
import os
import shutil

from PIL import Image

LOGOS_DIR = "../logo_simple"


def clear_dir_names(logo_dir):
    """Clear folder names"""
    brands = os.listdir(logo_dir)
    for b in brands:
        old_path = os.path.join(logo_dir, b)
        new_name = b.split(" - лого")[0]  # оставляем в новом имени папки всё, что было до " - лого", напр. "Vic Firth - лого" -> "Vic Firth"
        new_path = os.path.join(LOGOS_DIR, new_name)
        os.rename(old_path, new_path)


def remove_non_png(logo_dir):
    """Remove from brand folders all files exclude .png"""
    for dirpath, dirnames, filenames in os.walk(logo_dir):
        for filename in filenames:
            if not filename.lower().endswith('.png'):
                file_path = os.path.join(dirpath, filename)
                try:
                    os.remove(file_path)
                    print(f'Removed: {file_path}')
                except Exception as e:
                    print(f'Error while removing file {file_path}: {e}')


def convert_pngs_to_grayscale(root_dir):
    """Convert all color PNG to grayscale files"""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.png'):
                file_path = os.path.join(dirpath, filename)
                img = Image.open(file_path)
                if img.mode in ('RGBA', 'LA'):
                    # Создаём белый фон
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])  # Альфа-канал как маска
                    img = background
                else:
                    img = img.convert('RGB')
                img_gray = img.convert('L')
                img_gray.save(file_path)
                print(f'Converted: {file_path}')


# конвертировать в jpg те файлы, на которые не нашлось png
def convert_jpg_to_png(root_dir):
    """Convert JPG/JPEG to PNG files"""
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                jpg_path = os.path.join(dirpath, filename)
                png_path = os.path.splitext(jpg_path)[0] + '.png'
                try:
                    with Image.open(jpg_path) as img:
                        img.save(png_path, 'PNG')
                    os.remove(jpg_path)  # Удаляем исходный JPG
                    print(f'Converted and removed: {jpg_path} -> {png_path}')
                except Exception as e:
                    print(f'An error with file {jpg_path}: {e}')



def unpack_and_transfer(old_dir, new_dir):
    """Transfer all logo_simple files to new workdir"""
    for root, dirs, files in os.walk(old_dir):
        for filename in files:
            old_path = os.path.join(root, filename)
            new_path = os.path.join(new_dir, filename)
            shutil.copy(old_path, new_path)


def lower_all_names(logo_dir: str):
    for file in os.listdir(logo_dir):
        old_filepath = os.path.join(logo_dir, file)
        new_filepath = os.path.join(logo_dir, file.lower())
        os.rename(old_filepath, new_filepath)



from PIL import Image
import os

def fit_images_in_squares(directory) -> None:
    # Создаём папку для сохранённых квадратных изображений
    output_dir = '../logo_simple_squares'
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(directory):
        if filename.lower().endswith('.png'):
            filepath = os.path.join(directory, filename)
            with Image.open(filepath) as img:
                width, height = img.size
                max_side = max(width, height)

                # Создаём новое квадратное изображение с прозрачным фоном
                new_img = Image.new('RGBA', (max_side, max_side), (255, 255, 255, 0))

                # Центрируем исходное изображение в новом квадрате
                x_offset = (max_side - width) // 2
                y_offset = (max_side - height) // 2
                new_img.paste(img, (x_offset, y_offset))

                # Сохраняем результат в папку output
                new_img.save(os.path.join(output_dir, filename))

    logger.info(f'Обработано изображений: {len(os.listdir(output_dir))}')


def resize_images_to_square(input_dir, output_dir, square_side):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.png'):
            filepath = os.path.join(input_dir, filename)
            with Image.open(filepath) as img:
                resized_img = img.resize((square_side, square_side), Image.Resampling.LANCZOS)
                resized_img.save(os.path.join(output_dir, filename))

    logger.info(f'Обработано изображений: {len(os.listdir(output_dir))}')


# для использования с вложенными папками
def fit_images_in_squares_recursive(input_dir: str, output_dir: str = 'logo_simple_squares') -> None:
    os.makedirs(output_dir, exist_ok=True)
    count = 0

    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith('.png'):
                filepath = os.path.join(root, filename)
                with Image.open(filepath) as img:
                    width, height = img.size
                    max_side = max(width, height)

                    new_img = Image.new('RGBA', (max_side, max_side), (255, 255, 255, 0))

                    x_offset = (max_side - width) // 2
                    y_offset = (max_side - height) // 2
                    new_img.paste(img, (x_offset, y_offset))

                    # Сохраняем все файлы в одну выходную папку, чтобы избежать дублирования имён,
                    # можно добавить префикс с относительным путём или просто имя файла
                    # Для простоты сохраняем по имени файла:
                    new_img.save(os.path.join(output_dir, filename))
                    count += 1

    logger.info(f'Обработано изображений: {count}')

# для использования с вложенными папками
def resize_images_to_square_recursive(input_dir: str, output_dir: str, square_side: int) -> None:
    os.makedirs(output_dir, exist_ok=True)
    count = 0

    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if filename.lower().endswith('.png'):
                filepath = os.path.join(root, filename)
                with Image.open(filepath) as img:
                    resized_img = img.resize((square_side, square_side), Image.Resampling.LANCZOS)

                    # Чтобы сохранить структуру папок в output_dir, формируем относительный путь
                    rel_path = os.path.relpath(root, input_dir)
                    output_subdir = os.path.join(output_dir, rel_path)
                    os.makedirs(output_subdir, exist_ok=True)

                    resized_img.save(os.path.join(output_subdir, filename))
                    count += 1

    logger.info(f'Обработано изображений: {count}')



if __name__ == "__main__":
    # clear_dir_names(LOGOS_DIR)
    # remove_non_png(LOGOS_DIR)
    ## здесь добавить те логотипы, на которые не было png и конвертировать в jpg
    convert_jpg_to_png("../logo_simple")
    # convert_pngs_to_grayscale(LOGOS_DIR)


    # lower_all_names("logo_simple")

    # fit_images_in_squares(directory="logo_simple")
    resize_images_to_square(input_dir="../logo_simple_squares", output_dir="../logo_simple", square_side=500)