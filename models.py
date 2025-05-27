from dataclasses import dataclass
from typing import Optional

import pandas as pd

@dataclass
class MusicInstrument:

    num: str    # строковое представление порядкового номера с ведущими нулями (для правильной нумерации файлов)
    title: str
    subtitle: str
    description: str

    # эти 4 поля можно объединить, т.к. они идут одним блоком одного шрифта. Но по смыслу это 4 раздела, так что пока разбил.
    importer: str
    vendor: str
    manufacturer: str
    manufacturer_ru: str

    # а это поле можно разбить на три: срок службы, страна происхождения и сертификация. Но пока всё в одно
    extra: str

    logo: Optional[str] = None      # ссылка на логотип, задается одна и та же на все инструменты
    barcode: Optional[str] = None   # ссылка на сгенерированный штрих-код, задается после получения eac
    ean: Optional[str] = None
    ce: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'MusicInstrument':
        return cls(**data)

    # получает штрих-код для каждого объекта и присоединяет в объект ссылку на файл
    def attach_barcode(self):
        ...


def read_from_xlsx(book: str, sheet: str) -> list[MusicInstrument]:
    df = pd.read_excel(book, sheet_name=sheet)
    # переводим все в строковый формат и обрезаем пробелы
    df = df.map(lambda x: str(x).strip())
    all_rows = df.to_dict(orient='records')

    # рассчитываем длину номера для правильного дополнения ведущими нулями
    num_len = len(str(len(all_rows)))
    for i, row in enumerate(all_rows, start=1):
        row["num"] = f"{i:0{num_len}d}"

    instruments = [MusicInstrument.from_dict(row_dict) for row_dict in all_rows]
    return instruments

