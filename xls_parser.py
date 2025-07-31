import pandas as pd

def check_xls(required: set, xls: str, sheet: str):
    """Check that all the necessary columns are present in the excel table"""
    df = pd.read_excel(xls, sheet_name=sheet, nrows=0)  # read first row
    df = df.map(lambda x: x.strip())    # strip all spaces
    columns = set(df.columns)

    if columns != required:
        missing = required - columns
        extra = columns - required
        error_msg = "Incorrect fields in the input table."
        if missing:
            error_msg += f" Missing fields: {missing}."
        if extra:
            error_msg += f" Unexpected fields: {extra}."
        raise ValueError(error_msg)


# парсит сырые данные из Эксель, возвращает словарь, ключами которого являются названия столбцов (1 строка)
def parse_xls(xls: str, sheet: str) -> list[dict[str, str]]:
    """
    Parses raw data from Excel

    :param xls: path to Excel doc
    :param sheet: sheet name
    :return: a dictionary whose keys are column names (1 row)
    """
    try:
        df = pd.read_excel(xls, sheet_name=sheet)
        df = df.map(lambda x: str(x).strip())   # обрезать пробелы
        df = df.map(lambda x: str(x).replace("\n", " ") if x is not None else x)  # убрать переносы
        all_rows = df.to_dict(orient='records')
        return all_rows
    except Exception:
        raise


if __name__ == "__main__":
    EXCEL_FILE = "D:\! DOWNLOADS\JET_FLIGHT_Stickers2025.xlsx"

    # лист Excel-файла
    EXCEL_SHEET = "Лист1"

    goods = parse_xls(EXCEL_FILE, EXCEL_SHEET)
    for g in goods:
        print(g)
        print()
        for k, v in g.items():
            print(f"{k}: {v}")
        print()
