import datetime
from pathlib import Path

from config import TEMP_DIR
from logger import logger
from models import MusicInstrument, ProductWB
from stampers import stamp_for_wb, stamp_6x4, stamp_7x5
from utils import setup_workdir, cleanup_temp
from xls_parser import parse_xls


FORMATS = {
    "7x5": {
        "model": MusicInstrument,
        "stamper": stamp_7x5
    },
    "6x4": {
        "model": MusicInstrument,
        "stamper": stamp_6x4
    },
    "WB": {
        "model": ProductWB,
        "stamper": stamp_for_wb
    }
}


def main(file: str, sheet: str, format: str) -> None:
    """
    Main func

    :param file: path to file
    :param sheet: sheet of the file
    :param format: required format of the label
    """
    setup_workdir(temp_dir=TEMP_DIR)    # create workdir if not exists
    logger.info('Started')

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
    for idx, row in enumerate(raw_data[:1], start=1):
        num = f"{idx:0{number_length}d}"    # get current item number with leading zeros

        try:
            product = model.from_dict(row)
            product.num = num

            # prepare graphics
            product.prepare()
            logger.info("Successfully prepared")

            # stamp label
            stamp(product, label_dir)    # noqa
            logger.info("Stamped")

        except Exception as e:
            logger.error(f"Failed stamping label {num}: {e}")

    # cleanup_temp(dir=TEMP_DIR)    # cleanup workdir
    # logger.info("Finished.")



if __name__ == "__main__":
    xls_file = "D:\! DOWNLOADS\EASTTOP_BEE_Stikers2025_6х4.xlsx"
    xls_sheet = "Лист1"
    label_format = "7x5"

    main(xls_file, xls_sheet, label_format)
