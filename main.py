import datetime
import sys
import os
from pathlib import Path

from config import TEMP_DIR
from logger import logger
from models import MusicInstrument, ProductWB
from stampers import stamp_for_wb, stamp_6x5, stamp_7x5
from utils import setup_workdir, cleanup_temp
from xls_parser import parse_xls

FORMATS = {
    "7x5": {
        "model": MusicInstrument,
        "stamper": stamp_7x5
    },
    "6x4": {
        "model": MusicInstrument,
        "stamper": stamp_6x5
    },
    "WB": {
        "model": ProductWB,
        "stamper": stamp_for_wb
    }
}


def main(file: str, sheet: str, format: str = "") -> None:
    """
    NEW main script

    :param file: path to Excel file with data
    :param sheet: list name in Excel file
    """

    # create output folder
    xls_path = Path(file)
    workdir = xls_path.parent
    filename = xls_path.stem
    now: str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")    # curr timestamp
    label_dir = workdir / f"{filename}_{now}"
    label_dir.mkdir(parents=True, exist_ok=True)

    # read Excel file
    raw_data: list[dict] = parse_xls(file, sheet)

    # select product model and stamper func
    model = FORMATS[format]["model"]
    stamp = FORMATS[format]["stamper"]

    # calculate number length
    number_length = len(str(len(raw_data)))

    # main cycle
    for idx, row in enumerate(raw_data, start=1):
        num = f"{idx:0{number_length}d}"    # get current item number with leading zeros

        try:
            product = model.from_dict(row)
            product.num = num
            product.prepare()
            logger.info("Successfully prepared")
            # stamp label
            stamp(product, label_dir)    # noqa
            logger.info("Stamped")
        except Exception as e:
            logger.error(f"Failed stamping label {num}: {e}")



# def main_wb(xls_file: str, xls_sheet: str) -> None:
#     """
#     NEW main script
#
#     :param xls_file: path to Excel file with data
#     :param xls_sheet: list name in Excel file
#     """
#
#     # create label output folder
#     work_dir = os.path.dirname(os.path.abspath(xls_file))
#     filename = os.path.basename(xls_file).split(".")[0]
#
#     # postfix with time attached for uniqueness if restart will be required
#     now = datetime.datetime.now()
#     now_string = now.strftime("%Y-%m-%d_%H-%M-%S")
#     label_dir_name = f"{filename}_{now_string}"
#     label_dir_path = os.path.join(work_dir, label_dir_name)
#     logger.debug(f"LABEL DIR {label_dir_name}")
#
#     try:
#         os.mkdir(label_dir_path)
#     except Exception as e:
#         logger.error(f"Failed label folder creation: {e}")
#         sys.exit(1)
#
#     # read from Excel file
#     raw_data: list[dict]
#     try:
#         raw_data = parse_xls(xls=xls_file, sheet=xls_sheet)
#         logger.info("Tha data from Excel successfully read")
#         logger.debug(raw_data)
#     except Exception as e:
#         logger.error(f"Failed to read data from Excel: {e}")
#         sys.exit(1)
#
#     products: list[ProductWB] = []
#     number_length = len(str(len(raw_data)))  # calculate number length
#
#     for idx, row in enumerate(raw_data, start=1):
#         # get curr number with leading zeros
#         num = f"{idx:0{number_length}d}"
#
#         try:
#             product = ProductWB.from_dict(row)
#             product.num = num
#             product.prepare()
#             products.append(product)
#         except Exception as e:
#             logger.error(f"Failed label creation: {e}")
#
#     logger.info("Labels successfully prepared")
#
#     for product in products:
#         try:
#             stamp_for_wb(product, label_dir_path)
#         except Exception as e:
#             logger.error(f"Failed stamping label {product.num}: {e}")
#

if __name__ == "__main__":
    setup_workdir(temp_dir=TEMP_DIR)    # create workdir
    logger.info('Started')

    # input
    file = "D:\! DOWNLOADS\Стикеры ВБ FBO капсулы.xlsx"
    sheet = "Лист1"
    label_format = "WB"
    #
    main(fr"{file}", sheet, label_format)

    # main_wb(file, sheet)

    cleanup_temp(dir=TEMP_DIR)    # cleanup workdir
    logger.info("Finished.")
