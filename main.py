from models import MusicInstrument, read_from_xlsx
from barcode import generate_with_orcascan
from label import create_label_pdf


OUTPUT_DIR = "labels"


if __name__ == "__main__":
    print("Welcome to Label Hamster! I eat excel sheets and poop with pdf labels.\n")

    # путь до Excel-файла
    EXCEL_FILE = "xls_files/_INPUT_DATA_3.xlsx"

    # лист Excel-файла
    SHEET = "List1"

    # читаем Excel-файл и получаем список объектов MusicInstrument
    raw_data : list[dict] = read_from_xlsx(book=EXCEL_FILE, sheet=SHEET)
    music_instruments: list[MusicInstrument] = [MusicInstrument.from_dict(row) for row in raw_data]

    # длина полученного списка
    num_len = len(str(len(music_instruments)))

    for idx, instrument in enumerate(music_instruments, start=1):
        # получаем номер с ведущими нулями, учитывая общую длину списка
        num = f"{idx:0{num_len}d}"

        print(f"Processing: {num} {instrument.name}, EAN {instrument.ean13}")

        # получаем штрих-код из orcascan
        instrument.barcode = generate_with_orcascan(file_name=num, ean=instrument.ean13)

        # # костыль для тестирования, потому что отлетел интернет
        # instrument.barcode = "barcodes/1.png"

        # создаём этикетку
        create_label_pdf(instrument, label_num=num, output_dir=OUTPUT_DIR)

        # просто отбивка
        print()

    print("All work is done.")