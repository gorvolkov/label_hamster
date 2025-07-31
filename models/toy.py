import os
from typing import Optional

from generators import gen_barcode_orcascan, gen_qr
from config import CE_IMAGE, EAC_IMAGE, LOGO_DIR, TEMP_DIR
from logger import logger
from utils import find_logo


class Toy:
    ...