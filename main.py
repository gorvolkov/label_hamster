import datetime
import os.path
from typing import Optional
import sys

from xls_parser import check_xls, parse_xls
# from barcode import generate_with_orcascan
# from label import create_label_pdf
from logger import logger
from config import PROJECTS_DIR, REQUIRED_DATA_FIELDS
from models import Product, Label
from utils import create_project
from stamper import Stamper

# =============================================================
# для тестирования
# путь до Excel-файла
EXCEL_FILE = "xls_files/INPUT_DATA_EXAMPLE.xlsx"

# лист Excel-файла
EXCEL_SHEET = "List1"

# =============================================================



if __name__ == "__main__":
    logger.info("Welcome to Label Hamster! I eat excel sheets and poop with pdf labels.\n")

    # get variables
    xls_file = EXCEL_FILE
    xls_sheet = EXCEL_SHEET

    # check Excel files columns are correct
    try:
        check_xls(required=REQUIRED_DATA_FIELDS, xls=xls_file, sheet=xls_sheet)
        logger.info("Excel file is checked; OK")
    except Exception as e:
        logger.error(f"Excel file check failed: {e}")
        sys.exit(1)

    # create working directories
    proj_data = create_project(proj_dir=PROJECTS_DIR, add_name="test test")
    logger.info("Project folders successfully created")
    logger.debug(proj_data)

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
    number_length = len(str(len(products)))
    for idx, prod in enumerate(products, start=1):
        # получаем номер с ведущими нулями, учитывая общую длину списка
        curr_num = f"{idx:0{number_length}d}"
        try:
            # вычисляем длину номера для получения ведущих нулей
            label = Label(prod=prod, proj=proj_data, num=curr_num)
            logger.debug(f"Label {curr_num} created")
            label.prepare_all()
            logger.debug(f"All graphics created")
            labels.append(label)
        except Exception as e:
            logger.error(f"Failed label creation: {e}")
            sys.exit(1)
    logger.debug(labels)
    logger.info("Labels successfully prepared")

    stamper = Stamper(proj=proj_data)

    for label in labels:
        try:
            stamper.create_a4(label)
        except Exception as e:
            logger.error(f"Failed stamping label {label.num}: {e}")

    # # читаем Excel-файл и получаем список объектов MusicInstrument

    # music_instruments: list[MusicInstrument] = [MusicInstrument.from_dict(row) for row in raw_data]
    #
    # # длина полученного списка
    # num_len = len(str(len(music_instruments)))
    #
    # for idx, instrument in enumerate(music_instruments, start=1):
    #     # получаем номер с ведущими нулями, учитывая общую длину списка
    #     num = f"{idx:0{num_len}d}"
    #
    #     logger.debug(f"Processing: {num} {instrument.name}, EAN {instrument.ean13}")
    #
    #     # получаем штрих-код из orcascan
    #     instrument.barcode = generate_with_orcascan(file_name=num, ean=instrument.ean13)
    #
    #     # создаём этикетку
    #     create_label_pdf(instrument, label_num=num, output_dir=OUTPUT_DIR)
    #
    #
    # logger.info("All work is done.")
    #
    #
    # print(logo_simple)

# test
