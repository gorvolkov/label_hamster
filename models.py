from dataclasses import dataclass
from typing import Optional
import pandas as pd


EAC_LABEL_PATH = "EAC/eac.png"

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
class MusicInstrument:
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
            exp_text = f"Срок службы: {_format_exp_rus(exp_yrs)}."
            composed_info_text += exp_text

        if data["is_country"] == "ДА":
            country_text = f"  Страна изготовления: {data["country"]}"
            composed_info_text += country_text

        if data["is_certification"] == "ДА":
            cert_text = f"\n\n{data["certification"]}"
            composed_info_text += cert_text

        logo_path = None
        if data["logo"] == "ДА":
            logo_path = f"logo/{data["brand"].lower()}.png"

        eac_path, eac_label_path = None, None
        if data["eac"] == "ДА":
            eac_path = f"EAC/{data["brand"].lower()}_eac.png"
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
    """Read all data from Excel doc"""
    df = pd.read_excel(book, sheet_name=sheet)
    # переводим все в строковый формат и обрезаем пробелы
    df = df.map(lambda x: str(x).strip())
    all_rows = df.to_dict(orient='records')

    return all_rows


if __name__ == "__main__":
    # путь к файлу
    TEST_EXCEL_FILE = "xls_files/_INPUT_DATA_TEMPLATE v.2.xlsx"

    # лист Excel-файла
    TEST_SHEET = "List1"

    test_data: list[dict] = read_from_xlsx(book=TEST_EXCEL_FILE, sheet=TEST_SHEET)
    print(test_data)

    test_instr = MusicInstrument.from_dict(test_data[0])
    print(test_instr)
    print(test_instr.info)
    print(test_instr.logo)
    print(test_instr.eac)