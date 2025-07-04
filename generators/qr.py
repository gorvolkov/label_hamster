from config import QR_DUMMY

def gen_qr(link: str) -> str:
    """
    Generate and save QR code for passed link string

    :param link: URL to encode
    :return: path to saved QR code file
    """

    return QR_DUMMY