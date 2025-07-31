import os
from typing import Optional

from generators import gen_barcode_orcascan, gen_qr
from config import CE_IMAGE, EAC_IMAGE, LOGO_DIR, TEMP_DIR
from logger import logger
from utils import find_logo


class MusicInstrument:
    def __init__(self):
        # number in string format with leading zeros
        self.num: str = ""

        # text data
        self.brand: str = ""
        self.model: str = ""
        self.category: str = ""
        self.description: str = ""
        self.expiry: Optional[str] = ""
        self.country: Optional[str] = ""
        self.certification: Optional[str] = None
        self.importer_vendor: str = ""
        self.vendor: Optional[str] = None
        self.manufacturer: Optional[str] = ""

        self.ean13: str = ""
        self.barcode: str = ""

        self.eac: Optional[str] = None
        self.ce: Optional[str] = None
        self.logo: Optional[str] = None

        self.instruction: Optional[str] = ""
        self.qr: Optional[str] = ""

    @classmethod
    def from_dict(cls, data: dict) -> 'ProductRaw':
        prod = cls()
        for key, value in data.items():
            if hasattr(prod, key):
                # 'nan' заменяем на None
                cleared_value = value if value != "nan" else None
                setattr(prod, key, cleared_value)
        return prod

    def __repr__(self):
        return (
            f"ProductRaw(num={self.num!r}, brand={self.brand!r}, model={self.model!r}, "
            f"category={self.category!r}, description={self.description!r}, expiry={self.expiry!r}, "
            f"country={self.country!r}, certification={self.certification!r}, "
            f"importer_vendor={self.importer_vendor!r}, vendor={self.vendor!r}, "
            f"manufacturer={self.manufacturer!r}, ean13={self.ean13!r}, barcode={self.barcode!r}, "
            f"eac={self.eac!r}, ce={self.ce!r}, logo={self.logo!r}, "
            f"instruction={self.instruction!r}, qr={self.qr!r})"
        )

    def __str__(self):
        return (
            f"ProductRaw:\n"
            f"  num: {self.num}\n"
            f"  brand: {self.brand}\n"
            f"  model: {self.model}\n"
            f"  category: {self.category}\n"
            f"  description: {self.description}\n"
            f"  expiry: {self.expiry}\n"
            f"  country: {self.country}\n"
            f"  certification: {self.certification}\n"
            f"  importer_vendor: {self.importer_vendor}\n"
            f"  vendor: {self.vendor}\n"
            f"  manufacturer: {self.manufacturer}\n"
            f"  ean13: {self.ean13}\n"
            f"  barcode: {self.barcode}\n"
            f"  eac: {self.eac}\n"
            f"  ce: {self.ce}\n"
            f"  logo: {self.logo}\n"
            f"  instruction: {self.instruction}\n"
            f"  qr: {self.qr}\n"
        )


    def attach_barcode(self):
        """Generate barcode and attach link to an object"""
        barcode_name = f"{self.model}_barcode.png"
        path = os.path.join(TEMP_DIR, barcode_name)

        try:
            gen_barcode_orcascan(ean=self.ean13, save_to=path)
            # в случае успешной генерации штрих-кода добавляем ссылку на него в модель
            self.barcode = path
        except Exception:
            logger.error("Failed barcode generation")


    def attach_qr(self):
        """Generate qr with link and attach link to an object"""
        qr_name = f"{self.model}_qr.png"
        path = os.path.join(TEMP_DIR, qr_name)

        try:
            gen_qr(link=self.instruction, save_to=path)
            self.qr = path
        except Exception:
            logger.error("Failed QR generation")


    def attach_logo(self):
        """Find logo from logo dirs and attach path"""
        try:
            self.logo = find_logo(brand=self.brand, search_in=LOGO_DIR)
        except Exception:
            logger.error("No logo was found")


    def prepare_all(self) -> None:
        self.attach_barcode()
        logger.debug("Barcode generated and attached")

        if self.expiry:
            self.expiry = _format_exp_rus(self.expiry)

        if self.eac:
            self.eac = EAC_IMAGE
            logger.debug("EAC label attached")

        if self.ce:
            self.ce = CE_IMAGE
            logger.debug("CE label attached")

        if self.logo:
            self.attach_logo()
            logger.debug("Logo attached")

        if self.instruction:
            self.attach_qr()
            logger.debug("QR with link to instruction generated and attached")


def _format_exp_rus(exp_yrs: str) -> str:
    """Attach correct year values in russian"""
    years = int(exp_yrs)
    if 11 <= years <= 19:
        return f"{years} лет"
    mod = years % 10

    if mod == 1:
        return f"{years} год"
    elif 2 <= mod <= 4:
        return f"{years} года"
    else:
        return f"{years} лет"


if __name__ == "__main__":
    d1 = {
        "brand": "AwesomeBrand",
        "model": "SuperModel",
        "category": "Electronics",
        "description": "A very useful electronic device.",
        "importer_vendor": "GlobalImportCo",
        "ean13": "4607100342939",  # Корректный EAN13 (без пробелов)
        "vendor": "nan",
        "manufacturer": "TechCorp",
        "logo": "ДА",
        "ce": "nan",
        "eac": "nan",
        "expiry": "12 months",
        "country": "China",
        "certification": "ISO 9001",
        "instruction": "http://example.com/instruction.pdf",
    }
    d2 = {'brand': 'davinci', 'model': 'DAVINCI DCK-142 BK', 'category': 'Синтезатор', 'description': 'Цвет: черный\nВ комплекте: адаптер питания, микрофон\nТехнические характеристики: 61 миниклавиша, 16 тембров, 10 ритмов\nПитание: 220В-240В, адаптер питания (в комплекте) / \nБатарейки: AAx4 шт. (в комплект не входят)', 'expiry': '3', 'country': 'Китай', 'certification': 'Соответствует требованиям ТР ТС 004/2011 "О безопасности\nнизковольтного оборудования", ТР ТС 020/2011 "Электромагнитная\nсовместимость технических средств", ТР ЕАЭС 037/2016\n"Об ограничении применения опасных веществ в изделиях\nэлектротехники и радиоэлектроники', 'importer_vendor': 'ООО «Мьюзик лайн» 127474, РФ, г. Москва,\nДмитровское шоссе, д. 64. корп. 4, этаж 1, пом. 3, комн. 3.', 'vendor': 'ООО «Мьюзик лайн» 127474, РФ, г. Москва,\nДмитровское шоссе, д. 64. корп. 4, этаж 1, пом. 3, комн. 3.', 'manufacturer': 'Aroma Music Co., Ltd. China, Aroma Park, Guwu Village,\nDanshui town, Huiyang District, Huizhou City, Guangdong, 516200', 'ean13': '3831120929622', 'eac': 'nan', 'ce': 'nan', 'logo': 'nan', 'instruction': 'https://example.com'}

    p1 = ProductRaw.from_dict(d1)
    print(p1)