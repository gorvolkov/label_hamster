import qrcode


def gen_qr(link: str, save_to: str) -> None:
    """
    Generate and save QR code for passed link string

    :param link: link to encode
    :param save_to: path for generated qr
    """

    # Создаем объект QRCode
    qr = qrcode.QRCode(
        version=1,  # размер кода (1-40)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,  # размер квадратиков
        border=2,  # ширина рамки
    )

    qr.add_data(link)
    qr.make(fit=True)

    # Создаем изображение
    img = qr.make_image(fill_color="black", back_color="white")

    # Сохраняем в файл
    img.save(save_to)

