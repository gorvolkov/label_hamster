import datetime
import sys
import os

from config import REQUIRED_DATA_FIELDS, TEMP_DIR, TEST_DIR
from logger import logger
from models import MusicInstrument, Toy, ProductWB
from stamper import Stamper
from utils import setup_workdir, cleanup_temp
from xls_parser import check_xls, parse_xls


def main(xls_file: str, xls_sheet: str, format: str = "") -> None:
    """
    NEW main script

    :param xls_file: path to Excel file with data
    :param xls_sheet: list name in Excel file
    """
    # check Excel files columns are correct
    try:
        check_xls(required=REQUIRED_DATA_FIELDS, xls=xls_file, sheet=xls_sheet)
        logger.info("Excel file is checked; OK")
    except Exception as e:
        logger.error(f"Excel file check failed: {e}")
        sys.exit(1)

    # create label output folder
    work_dir = os.path.dirname(os.path.abspath(xls_file))
    filename = os.path.basename(xls_file).split(".")[0]

    # postfix with time attached for uniqueness if restart will be required
    now = datetime.datetime.now()
    now_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    label_dir_name = f"{filename}_{now_string}"
    label_dir_path = os.path.join(work_dir, label_dir_name)

    logger.debug(f"LABEL DIR {label_dir_name}")

    try:
        os.mkdir(label_dir_path)
    except Exception as e:
        logger.error(f"Failed label folder creation: {e}")
        sys.exit(1)

    # read from Excel file
    raw_data: list[dict]
    try:
        raw_data = parse_xls(xls=xls_file, sheet=xls_sheet)
        logger.info("Tha data from Excel successfully read")
        logger.debug(raw_data)
    except Exception as e:
        logger.error(f"Failed to read data from Excel: {e}")
        sys.exit(1)

    if format == "6*4_WB":
        products = list[ProductWB]


    products: list[MusicInstrument] = []
    number_length = len(str(len(raw_data)))  # calculate number length


    for idx, row in enumerate(raw_data, start=1):
        # get curr number with leading zeros
        num = f"{idx:0{number_length}d}"

        try:
            product = MusicInstrument.from_dict(row)
            product.num = num
            product.prepare_all()
            products.append(product)
        except Exception as e:
            logger.error(f"Failed label creation: {e}")


    logger.debug(products)
    logger.info("Labels successfully prepared")

    stamper = Stamper(save_to=label_dir_path)

    for product in products:
        try:
            stamper.stamp(product=product, format=format if format != "" else None)
        except Exception as e:
            logger.error(f"Failed stamping label {product.num}: {e}")


def main_wb(xls_file: str, xls_sheet: str) -> None:
    """
    NEW main script

    :param xls_file: path to Excel file with data
    :param xls_sheet: list name in Excel file
    """

    # # check Excel files columns are correct
    # try:
    #     check_xls(required=REQUIRED_DATA_FIELDS, xls=xls_file, sheet=xls_sheet)
    #     logger.info("Excel file is checked; OK")
    # except Exception as e:
    #     logger.error(f"Excel file check failed: {e}")
    #     sys.exit(1)

    # create label output folder
    work_dir = os.path.dirname(os.path.abspath(xls_file))
    filename = os.path.basename(xls_file).split(".")[0]

    # postfix with time attached for uniqueness if restart will be required
    now = datetime.datetime.now()
    now_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    label_dir_name = f"{filename}_{now_string}"
    label_dir_path = os.path.join(work_dir, label_dir_name)
    logger.debug(f"LABEL DIR {label_dir_name}")

    try:
        os.mkdir(label_dir_path)
    except Exception as e:
        logger.error(f"Failed label folder creation: {e}")
        sys.exit(1)

    # read from Excel file
    raw_data: list[dict]
    try:
        raw_data = parse_xls(xls=xls_file, sheet=xls_sheet)
        logger.info("Tha data from Excel successfully read")
        logger.debug(raw_data)
    except Exception as e:
        logger.error(f"Failed to read data from Excel: {e}")
        sys.exit(1)

    products: list[ProductWB] = []
    number_length = len(str(len(raw_data)))  # calculate number length

    for idx, row in enumerate(raw_data, start=1):
        # get curr number with leading zeros
        num = f"{idx:0{number_length}d}"

        try:
            product = ProductWB.from_dict(row)
            product.num = num
            product.attach_barcode()
            products.append(product)
        except Exception as e:
            logger.error(f"Failed label creation: {e}")

    logger.debug(products)
    logger.info("Labels successfully prepared")

    from stamper import stamp_for_wb

    for product in products:
        try:
            stamp_for_wb(product, label_dir_path)
        except Exception as e:
            logger.error(f"Failed stamping label {product.num}: {e}")

if __name__ == "__main__":
    # создание директории для временных файлов
    setup_workdir(temp_dir=TEMP_DIR)


    print("Hi! I'm Label Hamster. I read excel sheets and produce labels for your goods.")

    # блок ввода
    # # Excel-файл
    # xls_file = input("Select Excel file (full path without quotes): ")
    #
    # # лист таблицы
    # xls_sheet = input("Select sheet: ")
    #
    # # формат
    # # добавить проверку на поддерживаемые форматы, вынести их в конфиги можно вообще
    # format = input("Enter format: ")

    # для тестирования
    xls_file = "E:\ДИНАТОН\Этикетки\WB\Стикеры ВБ FBO_decompose.xlsx"
    xls_sheet = "Лист1"
    format = "7*5"

    # основной скрипт
    # main(xls_file, xls_sheet, format)

    main_wb(xls_file, xls_sheet)
    print("All labels were stamped, yo-hoo!")

    # удаление временных файлов
    cleanup_temp(dir=TEMP_DIR)
    print("...and I always clean it up after myself.")
