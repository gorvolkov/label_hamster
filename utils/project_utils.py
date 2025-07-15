import os
import shutil
from logger import logger

# вынесено в отдельную функцию сюда,
# т.к. в дальнейшем возможно понадобится расширения функционала
def setup_workdir(temp_dir: str) -> None:
    """
    Создаёт папку temp, куда складывается вся сгенерированная графика,
    если папки не существует в проекте (напр., если проект только скачан из удалённого репозитория)
    """

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        logger.info(f"Temp dir '{temp_dir}' was created")


def cleanup_temp(dir: str) -> None:
    """
    Удаляет все файлы в указанной директории.

    :param dir: путь к директории
    """
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            os.remove(file_path)
            logger.debug(f"Removed {file_path}")
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
                logger.debug(f"Removed file {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                logger.debug(f"Removed folder {file_path}")
        except Exception as e:
            raise