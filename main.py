from models import MusicInstrument, read_from_xlsx
from barcodes_api import generate_with_orcascan


# путь до Excel-файла
EXCEL_FILE = "xls_files/_INPUT_DATA_TEMPLATE.xlsx"

# лист Excel-файла
SHEET = "List1"



if __name__ == "__main__":
    print("Welcome to Label Hamster")

    # читаем Excel-файл и получаем список объектов MusicInstrument
    music_instruments: list[MusicInstrument] = read_from_xlsx(book=EXCEL_FILE, sheet=SHEET)

    # for i in music_instruments:
    #     print(music_instruments)

    # генерируем штрих-коды для каждого инструмента и складываем в папку
    for idx, model in enumerate(music_instruments, start=1):
        generate_with_orcascan(file_name=model.num, ean=model.ean)
