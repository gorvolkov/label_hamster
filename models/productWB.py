import os

from generators import gen_barcode_orcascan_narrow
from config import TEMP_DIR
from logger import logger


class ProductWB:
    def __init__(self):
        # number in string format with leading zeros
        self.num: str = ""

        # text data
        self.title: str = ""
        self.art: str = ""
        self.vendor: str = ""
        self.barcode: str = ""
        self.barcode_path: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> 'ProductWB':
        prod = cls()
        for key, value in data.items():
            if hasattr(prod, key):
                # 'nan' заменяем на None
                cleared_value = value if value != "nan" else None
                setattr(prod, key, cleared_value)
        return prod

    def __repr__(self):
        return (
            f"ProductWB(num={self.num!r}, title={self.title!r}, art={self.art!r}, "
            f"vendor={self.vendor!r}, barcode_data={self.barcode!r}, barcode_path={self.barcode_path!r}"
        )

    def __str__(self):
        return (
            f"ProductRaw:\n"
            f"  num: {self.num}\n"
            f"  title: {self.title}\n"
            f"  art: {self.art}\n"
            f"  vendor: {self.vendor}\n"
            f"  barcode: {self.barcode}\n"
            f"  barcode_path: {self.barcode_path}\n"
        )


    def attach_barcode(self):
        """Generate barcode and attach link to an object"""
        barcode_name = f"{self.num}_barcode.png"
        barcode_path = os.path.join(TEMP_DIR, barcode_name)
        print(barcode_name, barcode_path)
        try:
            gen_barcode_orcascan_narrow(data=self.barcode, file=barcode_path)
            self.barcode_path = barcode_path
        except Exception:
            logger.error("Failed barcode generation")


if __name__ == "__main__":
    test_wb = {'title': 'Термос 3 литра, черный, металлический', 'art': 'Panacotti ML-TR001-3000A', 'vendor': 'ООО "МьюзикЛайн"', 'barcode': '3831120939683'}
    prod = ProductWB.from_dict(test_wb)
    prod.num = "1"
    print(prod)
    prod.attach_barcode()