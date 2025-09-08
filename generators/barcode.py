import os.path

import requests

def gen_barcode_orcascan(ean: str, save_to: str) -> None:
    """
    Generate and save barcode image (PNG), using orcascan API

    :param ean: EAN13 string
    :param save_to: path to saved image
    :return: None
    """

    host = "https://barcode.orcascan.com"
    response = requests.get(url=f"{host}/?type=ean13&data={ean}&format=png")
    if response.status_code == 200:
        with open(save_to, 'wb') as file:
            file.write(response.content)
    else:
        raise Exception("Something went wrong")


#  можно дописать для локальной генерации ШК
def gen_barcode_locally() -> None:
    """Generate barcode locally without any API usage"""
    pass


def gen_barcode_orcascan_narrow(data: str, file: str) -> None:
    """
        Generate and save barcode image (PNG), using orcascan API

        :param data: Code 128 string (recommended for Wildberries)
        :param save_to: path to saved image
        :return: None
        """

    host = "https://barcode.orcascan.com"
    response = requests.get(url=f"{host}/?type=code128&data={data}&format=png")
    if response.status_code == 200:
        with open(file, 'wb') as f:
            f.write(response.content)
    else:
        raise Exception("Something went wrong")


if __name__ == "__main__":
    from config import TEMP_DIR
    test_file = os.path.join(TEMP_DIR, "01_barcode.png")

    gen_barcode_orcascan_narrow(data="3831120939683", file=test_file)