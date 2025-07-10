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


