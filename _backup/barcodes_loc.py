# Здесь можно будет потом доработать код для локальной генерации бар-кодов


from generators.barcode import EAN13
from generators.barcode import SVGWriter

# https://python-barcode.readthedocs.io/en/stable/getting-started.html#installation

ean_code = "3831120901840"
output_dir = "../barcodes"
file_name = "test1"
my_file_path = f"{output_dir}/{file_name}.svg"

# генерирует локально
def generate_here(file_path: str) -> None:
    options = {
        "write_text": True,   # Не выводим текст
        "module_width": 0.6,   # ширина минимальной полоски
        "module_height": 60,   # подгон высоты
        "quiet_zone": 2.0,     # Минимальные отступы
        "background": "white",
        "foreground": "black"
    }

    with open(file_path, "wb") as f:
        EAN13(ean_code, writer=SVGWriter()).write(f, options=options)

# generate_here(file_path=my_file_path)

# генерирует с использованием API orcascan
barcode_type = "ean13"
file_format = "SVG"
clean_file_name = "test3"
output_filename = f"{clean_file_name}.{file_format.lower()}"