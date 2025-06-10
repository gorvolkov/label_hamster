import requests
from config import BARCODES_DIR
from logger import logger


def generate_with_orcascan(ean: str, file_name: str, binary: bool = False) -> str | None:
    """Генерирует штрих-код, используя переданный EAN, и сохраняет в папку BARCODES_DIR"""
    host = "https://barcode.orcascan.com"
    output_dir = BARCODES_DIR
    file_format = "png"  # формат файла, который нам нужен на выходе
    file_path = f"{output_dir}/{file_name}.{file_format}"
    barcode_type = "ean13"  # тип штрих-кода

    response = requests.get(url=f"{host}/?type={barcode_type}&data={ean}&format={file_format}")

    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        logger.debug(f"Attached barcode: {file_path}")
        return file_path
    else:
        logger.warning("Something went wrong")
        return None


if __name__ == "__main__":
    # test
    some_ean_code = "3831120901840"
    generate_with_orcascan(ean=some_ean_code, file_name="test")

