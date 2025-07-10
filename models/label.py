import os
from typing import Optional

from generators import gen_barcode_orcascan, gen_qr
from config import CE_IMAGE, EAC_IMAGE, LOGO_DIR, TEMP_DIR
from logger import logger
from models import Product
from utils import find_logo


class Label:
    """A class preparing data to be printed"""
    def __init__(self, prod: Product, num: str):
        self.product = prod

        # number with leading zeros
        self.num: str = num

        # text data
        self.model: str = self.product.model
        self.category: str = self.product.category
        self.description: str = self.product.description
        self.info_block: str = ""
        self.certification: Optional[str] = prod.certification
        self.importer_vendor: str = prod.importer_vendor
        self.vendor: Optional[str] = prod.vendor
        self.manufacturer: str = prod.manufacturer

        # graphics
        self.logo: Optional[str] = None
        self.qr: Optional[str] = None
        self.ce: Optional[str] = CE_IMAGE if prod.ce else None
        self.eac: Optional[str] = EAC_IMAGE if prod.eac else None
        self.barcode: str = ""


    def compose_info_block(self):
        """Attach expiry and country info"""
        if self.product.expiry:
            exp_yrs = int(self.product.expiry)
            exp_text = f"**Срок службы**: {_format_exp_rus(exp_yrs)}."  # add expiry info in correct format
            self.info_block += exp_text

        if self.product.country:
            self.info_block += f" **Страна изготовления**: {self.product.country}"  # added markdown


    def attach_barcode(self):
        """Generate barcode and attach link to an object"""
        barcode_name = f"{self.num}_{self.product.model}_barcode.png"
        path = os.path.join(TEMP_DIR, barcode_name)

        try:
            gen_barcode_orcascan(ean=self.product.ean13, save_to=path)
            # в случае успешной генерации штрих-кода добавляем ссылку на него в модель
            self.barcode = path
        except Exception:
            logger.error("Failed barcode generation")


    def attach_qr(self):
        """Generate qr with link and attach link to an object"""
        qr_name = f"{self.num}_{self.product.model}_qr.png"
        path = os.path.join(TEMP_DIR, qr_name)

        try:
            gen_qr(link=self.product.instruction, save_to=path)
            self.qr = path
        except Exception:
            logger.error("Failed QR generation")


    def attach_logo(self):
        """Find logo from logo dirs and attach path"""
        try:
            self.logo = find_logo(brand=self.product.brand, search_in=LOGO_DIR)
        except Exception:
            logger.error("No logo was found")


    def prepare_all(self):
        self.compose_info_block()
        logger.info("Info block composed")

        self.attach_barcode()
        logger.info("Barcode successfully generated and attached")

        if self.product.instruction:
            self.attach_qr()
            logger.info("QR Code with link to instruction successfully generated and attached")

        if self.product.logo:
            self.attach_logo()
            logger.info("Logo attached")



def _format_exp_rus(y_value: int) -> str:
    """Attach correct year values in russian"""
    if 11 <= y_value <= 19:
        return f"{y_value} лет"
    mod = y_value % 10

    if mod == 1:
        return f"{y_value} год"
    elif 2 <= mod <= 4:
        return f"{y_value} года"
    else:
        return f"{y_value} лет"
