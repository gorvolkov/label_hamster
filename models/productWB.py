from dataclasses import dataclass
from typing import Optional
import os

from generators import gen_barcode_orcascan
from config import TEMP_DIR
from logger import logger


@dataclass
class ProductWB:
    title: str
    description: str
    stock_id: str    # артикул
    barcode: str
    num: Optional[str] = None
    barcode_path: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'ProductWB':
        return cls(**data)

    def _attach_barcode(self):
        """Generate barcode and attach link to an object"""
        barcode_name = f"{self.num}_barcode.png"
        barcode_path = os.path.join(TEMP_DIR, barcode_name)
        print(barcode_name, barcode_path)
        try:
            gen_barcode_orcascan(self.barcode, barcode_path)
            self.barcode_path = barcode_path
        except Exception:    # noqa
            logger.error("Failed barcode generation")

    def prepare(self):
        self._attach_barcode()


if __name__ == "__main__":
    test_wb = {
        'title': 'Термос 3 литра, черный, металлический',
        'description': "askjhg",
        'stock_id': 'Panacotti ML-TR001-3000A',
        'barcode': '3831120939683'}
    prod = ProductWB.from_dict(test_wb)
    prod.num = "1"
    print(prod)
    # prod.attach_barcode()