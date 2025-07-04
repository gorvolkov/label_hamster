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

EAC_LABEL_PATH = "../static/EAC.png"

def _format_exp_rus(y_value: int) -> str:
    if 11 <= y_value <= 19:
        return f"{y_value} лет"

    mod = y_value % 10

    if mod == 1:
        return f"{y_value} год"
    elif 2 <= mod <= 4:
        return f"{y_value} года"
    else:
        return f"{y_value} лет"


@dataclass
class MusicInstrument1:
    name: str
    description: str
    characteristics: str
    info: str
    importer_vendor: str
    manufacturer: str
    ean13: str
    barcode: str | None
    eac: str | None
    eac_label: str | None
    logo: str | None


    @classmethod
    def from_dict(cls, data: dict) -> 'MusicInstrument1':
        composed_info_text = ""

        if data["is_expiry"] == "ДА":
            exp_yrs = int(data["expiry"])
            exp_text = f"Срок службы {_format_exp_rus(exp_yrs)}"
            composed_info_text += exp_text

        if data["is_country"] == "ДА":
            country_text = f"  Страна изготовления: {data["country"]}"
            composed_info_text += country_text

        if data["is_certification"] == "ДА":
            cert_text = f"\n\n{data["certification"]}"
            composed_info_text += cert_text

        logo_path = None
        if data["logo_simple"] == "ДА":
            logo_path = f"logo_simple/{data["brand"].lower()}.png"

        eac_path, eac_label_path = None, None
        if data["eac"] == "ДА":
            eac_path = f"static/{data["brand"].lower()}_eac.png"
            eac_label_path = EAC_LABEL_PATH

        return cls(
            name=data["name"],
            description=data["description"],
            characteristics=data["characteristics"],
            info=composed_info_text,
            importer_vendor=data["importer_vendor"],
            manufacturer=data["manufacturer"],
            ean13=data["ean13"],
            barcode=None,
            logo=logo_path,
            eac=eac_path,
            eac_label=eac_label_path
        )



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


def read_from_xlsx1(book: str, sheet: str) -> list[MusicInstrument]:
    df = pd.read_excel(book, sheet_name=sheet)
    # переводим все в строковый формат и обрезаем пробелы
    df = df.map(lambda x: str(x).strip())
    all_rows = df.to_dict(orient='records')

    return all_rows


if __name__ == "__main__":
    TEST_EXCEL_FILE = "../xls_files/_INPUT_DATA_TEMPLATE v.2.xlsx"
    # лист Excel-файла
    TEST_SHEET = "List1"
    test_dict = read_from_xlsx1(book=TEST_EXCEL_FILE, sheet=TEST_SHEET)
    print(test_dict)

    test_instr = MusicInstrument1.from_dict(test_dict[0])
    print(test_instr)
    print(test_instr.info)
    print(test_instr.logo)
    print(test_instr.eac)