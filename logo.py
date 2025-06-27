"""
Функционал для подготовки папки logo к корректному использованию.
Чтобы не перебирать руками.
"""


import os
from PIL import Image

LOGOS_DIR = "logo"


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
            if filename.lower().endswith('.jpg'):
                jpg_path = os.path.join(dirpath, filename)
                png_path = os.path.splitext(jpg_path)[0] + '.png'
                try:
                    with Image.open(jpg_path) as img:
                        img.save(png_path, 'PNG')
                    os.remove(jpg_path)  # Удаляем исходный JPG
                    print(f'Converted and removed: {jpg_path} -> {png_path}')
                except Exception as e:
                    print(f'An error with file {jpg_path}: {e}')



if __name__ == "__main__":
    clear_dir_names(LOGOS_DIR)
    # remove_non_png(LOGOS_DIR)
    ## здесь добавить те логотипы, на которые не было png и конвертировать в jpg
    # convert_jpg_to_png(LOGOS_DIR)
    # convert_pngs_to_grayscale(LOGOS_DIR)