from models.label import Product

def get_instruments_from_old_format_data(data: list[dict]) -> list[MusicInstrument]:
    """
    Читает из старого формата Эксель, где три колонки: в первой свалена вся текстовая информация, во второй static, в третьей EAN.

    Перед использованием обязательно добавить строчку сверху и поименовать столбцы: text, eac, ean.

    :param data: словарь, который вернет read_from_xlsx
    :return:
    """

    instruments = []

    for row in data:
        text =  row["text"].split("\n")

        # для очистки от пустых строк
        text = [s for s in text if s]

        # тут поменялись поля. Надо будет исправить.
        instrument = Product(
            name=text[0],
            description = text[1],
            characteristics = "\n".join(text[2:6]),
            info = "\n\n".join(text[6:8]),
            importer_vendor = "\n".join(text[8:10]),
            manufacturer = "\n".join(text[10:12]),
            ean13 = row["ean"],
            barcode=None,
            with_eac=True
        )

        instruments.append(instrument)

    return instruments
