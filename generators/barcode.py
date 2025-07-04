import requests

# получает ШК, используя API orcascan
def gen_barcode_orcascan(ean: str, barcode_path: str) -> None:
    """Генерирует штрих-код, используя переданный EAN, и сохраняет в папку BARCODES_DIR"""
    host = "https://barcode.orcascan.com"
    response = requests.get(url=f"{host}/?type=ean13&data={ean}&format=png")
    if response.status_code == 200:
        with open(barcode_path, 'wb') as file:
            file.write(response.content)
    else:
        raise Exception("Something went wrong")


#  можно дописать для локальной генерации ШК
def gen_barcode_locally() -> None:
    """Generate barcode locally without any API usage"""
    pass


