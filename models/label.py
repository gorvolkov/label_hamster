import os
from typing import Optional

from generators import gen_barcode_orcascan, gen_qr
from config import CE_IMAGE, EAC_IMAGE, LOGO_DIR
from logger import logger

from models import Product
from utils import find_logo


class Label:
    """A class preparing data to be printed"""
    def __init__(self, prod: Product, proj: dict[str, str], num: str):
        # project obj to create label from
        self.product = prod

        # data of project
        self.project_data: str = proj

        # номер с ведущими нулями
        self.num: str = num


        # text data
        self.model: str = self.product.model
        self.category: str = self.product.category
        self.description: str = self.product.description
        self.info_block: str = ""
        self.addresses_block: str = ""

        # graphics
        self.logo: Optional[str] = None
        self.qr: Optional[str] = None
        self.ce: Optional[str] = CE_IMAGE if prod.ce else None
        self.eac: Optional[str] = EAC_IMAGE if prod.eac else None
        self.barcode: str = ""

    def compose_info_block(self):
        if self.product.expiry:
            exp_yrs = int(self.product.expiry)

            # вставляем информацию о сроке службы в корректном формате
            exp_text = f"Срок службы: {_format_exp_rus(exp_yrs)}."
            self.info_block += exp_text

        if self.product.country:
            self.info_block += f" Страна изготовления: {self.product.country}"

        if self.product.certification:
            self.info_block += f"\n{self.product.certification}"


    def compose_addresses(self):
        self.addresses_block = f"Импортёр / продавец: {self.product.importer_vendor}\n"

        # если у продукта отдельно указан продавец (как у Крафтеров Асмик), то добавляем его отдельным блоком сюда
        if self.product.vendor:
            self.addresses_block += f"Продавец: {self.product.vendor}\n\n"

        self.addresses_block += f"Производитель: {self.product.manufacturer}"


    def attach_barcode(self):
        """Generate barcode and attach link to an object"""
        barcode_name = f"{self.num}_{self.product.model}_barcode.png"
        path = os.path.join(self.project_data["graphs"], barcode_name)

        try:
            gen_barcode_orcascan(ean=self.product.ean13, barcode_path=path)
            # в случае успешной генерации штрих-кода добавляем ссылку на него в модель
            self.barcode = path
        except Exception:
            logger.error("Failed barcode generation")


    def attach_qr(self):
        """Generate qr with link and attach link to an object"""
        qr_name = f"{self.num}_{self.product.model}_qr.png"
        path = os.path.join(self.project_data["graphs"], qr_name)

        try:
            self.qr = gen_qr(link=self.product.instruction)
        except Exception:
            logger.error("Failed QR generation")


    def attach_logo(self):
        """Find logo_simple from logo_simple dirs and attach path"""
        try:
            self.logo = find_logo(brand=self.product.brand, search_in=LOGO_DIR)
        except Exception:
            logger.error("No logo_simple was found")


    def prepare_all(self):
        self.compose_info_block()
        logger.info("Info block composed")

        self.compose_addresses()
        logger.info("Addresses block composed")

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

