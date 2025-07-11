import os
import shutil

def cleanup_temp(dir: str) -> None:
    """
    Удаляет все файлы в указанной директории.

    :param dir: путь к директории
    """
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            os.remove(file_path)
        except Exception as e:
            raise


def cleanup_temp_recursive(dir: str) -> None:
    """
    Удаляет и файлы, и папки в указанной директории.

    :param dir: путь к директории
    """
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            raise