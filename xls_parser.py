# Спарсить всё из эксель файла
# Обернуть инструмент в класс? Это пока непонятно

# Но в любом случае должны быть определены атрибуты для каждого инструмента (характеристики, которые будут писаться в этикетку)
# Так что да, идея с классом выглядит логично


from dataclasses import dataclass

@dataclass
class Instrument:
    """Music instrument class"""
    pass


def parse() -> Instrument:
    """Parse one Instrument item from .xls file"""
    ...


def parse_many() -> list[Instrument]:
    """Parse list of Instrument items from .xls file"""
    ...


# import pandas as pd

# book_1 = "xslx_files/Fleor для загрузки в базу  ШК.xlsx"
# sheet_1 = "ШК"
#
# @dataclass
# class MusicInstrument:
#     id: int
#     name: str
#     description: str
#     ean: int
#
#
# def read_from_xlsx(book: str, sheet: str) -> list[str]:
#
#     df = pd.read_excel(book, sheet_name=sheet)
#
#     # Выведите все строки построчно
#     for index, row in df.iterrows():
#         print(f"Строка {index + 1}: {row.tolist()}")
#
#     for index, row in df.iterrows():
#         print(f"Строка {index + 1}: Column1 = {row['Column1']}, Column2 = {row['Column2']}")
#
#
# def get_barcode(ean: int) -> None:
#     ...


