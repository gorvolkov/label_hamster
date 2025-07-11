import datetime
import sys
import os

from config import REQUIRED_DATA_FIELDS, TEMP_DIR, TEST_DIR
from logger import logger
from models import Product, Label
from stamper import Stamper
from utils import cleanup_temp
from xls_parser import check_xls, parse_xls


def main_script(xls_file: str, xls_sheet: str) -> None:
    """
    Main script

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

    try:
        os.mkdir(label_dir_path)
    except Exception as e:
        logger.error(f"Failed label folder creation: {e}")

    # read from Excel file
    raw_data: list[dict]
    try:
        raw_data = parse_xls(xls=xls_file, sheet=xls_sheet)
        logger.info("Tha data from Excel successfully read")
        logger.debug(raw_data)
    except Exception as e:
        logger.error(f"Failed to read data from Excel: {e}")
        sys.exit(1)

    products: list[Product]
    try:
        products = [Product.from_dict(r) for r in raw_data]
        logger.debug("Data validated, OK")
        logger.debug(products)
    except Exception as e:
        logger.error(f"Failed data validation: {e}")
        sys.exit(1)

    labels: list[Label] = []
    number_length = len(str(len(products)))  # calculate number length

    for idx, prod in enumerate(products, start=1):
        # get curr number with leading zeros
        num = f"{idx:0{number_length}d}"

        try:
            label = Label(prod=prod, num=num)
            logger.debug(f"Label {num} created")
            label.prepare_all()
            logger.debug(f"All graphics created")
            labels.append(label)
        except Exception as e:
            logger.error(f"Failed label creation: {e}")
            sys.exit(1)

    logger.debug(labels)
    logger.info("Labels successfully prepared")

    stamper = Stamper(save_to=label_dir_path)

    for label in labels:
        try:
            stamper.create_a4(label)
        except Exception as e:
            logger.error(f"Failed stamping label {label.num}: {e}")



if __name__ == "__main__":
    print("Hi! I'm Label Hamster. I eat excel sheets and poop with labels.")

    # для тестирования
    TEST_FILE_PATH = os.path.join(TEST_DIR, "INPUT_DATA_TEST.xlsx")
    print("TEST_FILE = ", TEST_FILE_PATH)
    print("TEST_SHEET = List1")

    xls_file = input("Select Excel file (full path without quotes): ")

    xls_sheet = input("Select sheet: ")

    main_script(xls_file=xls_file, xls_sheet=xls_sheet)
    print("All labels were stamped, yo-hoo!")

    cleanup_temp(dir=TEMP_DIR)
    print("...and I always flush the toilet after myself.")

