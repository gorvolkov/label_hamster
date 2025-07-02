import os
from dataclasses import dataclass
from typing import Optional

from barcode import generate_with_orcascan
from config import CE_IMAGE, EAC_IMAGE, QR_DUMMY, LOGO_DIR, REQUIRED_DATA_FIELDS
from logger import logger

EAC_LABEL_PATH = "static/EAC.png"


def _format_exp_rus(y_value: int) -> str:
    if 11 <= y_value <= 19:
        return f"{y_value} лет"

    mod = y_value % 10

    if mod == 1:
        return f"{y_value} год"
    elif 2 <= mod <= 4:
        return f"{y_value} года"
    else:
        return f"{y_value} лет"



@dataclass
class Product:
    number: str
    brand: str
    model: str
    category: str
    description: str
    importer_vendor: str
    vendor: Optional[str] = ""
    manufacturer: str = ""
    ean13: str = ""
    logo: bool = False
    expiry: Optional[str] = None
    country: Optional[str] = None
    certification: Optional[str] = None
    instruction: Optional[str] = None
    ce: bool = False
    eac: bool = False

    @classmethod
    def from_dict(cls, num: str, data: dict):
        data_copy = data.copy()
        data_copy["number"] = num
        # здесь можно добавить валидацию значений из таблицы
        return cls(**data_copy)


def get_qr_link(link: str) -> str:
    """Получает QR-код для ссылки на инструкцию, возвращает путь к сохраненному QR"""
    ...


def find_logo(brand: str, search_in: str, ) -> str:
    """Find logo image by passed brand name"""
    brand_lower = brand.lower()
    for filename in os.listdir(search_in):
        if filename.lower().startswith(brand_lower):
            return os.path.join(search_in, filename)
    raise Exception("No logo was found for this brand")


class Label:
    def __init__(self, product: Product, project_dir: str, num: str):
        # директория проекта
        self.project_dir: str = project_dir
        # номер с ведущими нулями
        self.num: str = num

        self.product = product

        # text data
        self.title: str = self.product.model
        self.subtitle: str = self.product.category
        self.description: str = self.product.description
        self.info_block: str = ""
        self.addresses_block: str = ""

        # graphics
        self.logo_path: Optional[str] = None
        self.qr_path: Optional[str] = None
        self.ce_path: Optional[str] = CE_IMAGE if product.ce else None
        self.eac_path: Optional[str] = EAC_IMAGE if product.eac else None
        self.barcode_path: str = ""

    def compose_info_block(self):
        if self.product.expiry:
            exp_yrs = int(self.product.expiry)

            # вставляем информацию о сроке службы в корректном формате
            exp_text = f"Срок службы: {_format_exp_rus(exp_yrs)}."
            self.info_block += exp_text

        if self.product.country:
            self.info_block += f" Страна изготовления: {self.product.country}"

        if self.product.certification:
            self.info_block += f"\n\n{self.product.certification}"


    def compose_addresses(self):
        self.addresses_block = f"Импортёр / продавец: {self.product.importer_vendor}\n\n"

        # если у продукта отдельно указан продавец (как у Крафтеров Асмик), то добавляем его отдельным блоком сюда
        if self.product.vendor:
            self.addresses_block += f"Продавец: {self.product.vendor}\n\n"

        self.addresses_block += f"Производитель: {self.product.manufacturer}"


    def attach_barcode(self, graphs_dir: str):
        """Generate barcode and attach link to an object"""
        barcode_name = f"{self.num}_{self.product.model}_barcode.png"
        path = os.path.join(graphs_dir, barcode_name)

        try:
            generate_with_orcascan(ean=self.product.ean13, barcode_path=path)
            # в случае успешной генерации штрих-кода добавляем ссылку на него в модель
            self.barcode_path = path
        except Exception:
            logger.error("Failed barcode generation")


    def attach_qr(self, graphs_dir):
        """Generate qr with link and attach link to an object"""
        qr_name = f"{self.num}_{self.product.model}_qr.png"

        # пока возвращаем заглушку
        self.qr_path = QR_DUMMY


    def attach_logo(self):
        """Find logo from logo dirs and attach path"""
        try:
            self.logo_path = find_logo(brand=self.product.brand, search_in=LOGO_DIR)
        except Exception:
            logger.error("No logo was found")


    def prepare_all(self, graphs_dir: str):
        self.compose_info_block()
        logger.info("Info block composed")

        self.compose_addresses()
        logger.info("Addresses block composed")

        self.attach_barcode(graphs_dir)
        logger.info("Barcode successfully generated and attached")

        if self.product.instruction:
            self.attach_qr(graphs_dir)
            logger.info("QR Code with link to instruction successfully generated and attached")

        if self.product.logo:
            self.attach_logo()
            logger.info("Logo attached")

