import os
from fpdf import FPDF
from models import MusicInstrument
from PIL import Image

# импортируем статические файлы картинок
from config import EAC_IMAGE, CE_IMAGE, LABELS_DIR, BARCODES_DIR
from models import read_from_xlsx, parse_crafter
from barcode import generate_with_orcascan

def create_label_crafter(instrument: MusicInstrument, label_num: str, output_dir: str):
    # адреса к системным шрифтам
    arial_regular = r"C:\Windows\Fonts\arial.ttf"
    arial_bold = r"C:\Windows\Fonts\arialbd.ttf"
    arial_italic = r"C:\Windows\Fonts\ariali.ttf"
    arial_bold_italic = r"C:\Windows\Fonts\arialbi.ttf"


    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()

    pdf.add_font("ArialTTF", "", arial_regular)
    pdf.add_font("ArialTTF", "B", arial_bold)
    pdf.add_font("ArialTTF", "I", arial_italic)
    pdf.add_font("ArialTTF", "BI", arial_bold_italic)

    # задаем координаты макета
    margin_left = 10
    margin_right = 10
    right_column_width = 90
    page_width = pdf.w
    text_width = page_width - margin_left - margin_right - right_column_width

    y = 20

    # ТЕКСТОВЫЕ БЛОКИ

    # name: жирный, капсом, размер 40
    pdf.set_font("ArialTTF", "B", 36)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_width, 12, instrument.name.upper(), align='L')
    y = pdf.get_y() + 2

    # description: жирный, не капсом, размер 40
    size = 28
    line_height = size * 1.5  # полуторный интервал
    pdf.set_font("ArialTTF", "B", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_width, 12, instrument.description)
    y = pdf.get_y() + 4

    # characteristics: обычный, размер 16
    pdf.set_font("ArialTTF", "", 14)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_width, 6, instrument.characteristics)
    y = pdf.get_y() + 4

    # info: обычный, размер 14
    pdf.set_font("ArialTTF", "", 12)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_width, 6, instrument.info)
    y = pdf.get_y() + 4

    # Импортер / продавец: обычный, размер 14
    pdf.set_font("ArialTTF", "", 12)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_width, 6, f"{instrument.importer_vendor}")
    y = pdf.get_y() + 4

    # Производитель
    pdf.set_font("ArialTTF", "", 12)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_width, 6, f"{instrument.manufacturer}")
    y = pdf.get_y() + 6

    # КАРТИНКИ
    right_column_height = 210 - 20  # 210 мм высота A4 минус 10 мм сверху и снизу
    image_spacing = 5
    x_right = page_width - right_column_width - margin_right
    y_bottom = 210 - 10  # нижний край страницы минус отступ

    # Задаём высоты
    barcode_height = 60  # мм, высота штрихкода
    eac_height = 20 # мм, высота EAC (уменьшено)
    total_height = eac_height + image_spacing + barcode_height

    # Координаты по Y для выравнивания по нижнему краю
    y_eac = y_bottom - total_height
    y_barcode = y_eac + eac_height + image_spacing

    # EAC
    if instrument.with_eac:
        img = Image.open(EAC_IMAGE)
        img_width, img_height = img.size
        # aspect_ratio = img_width / img_height
        aspect_ratio = 0.3
        eac_width = eac_height * aspect_ratio
        if eac_width > right_column_width:
            eac_width = right_column_width
            eac_height = eac_width / aspect_ratio
        pdf.image(EAC_IMAGE, x=x_right + 50, y=y_eac, h=eac_height)

    # Штрихкод
    img = Image.open(instrument.barcode)
    # img_width, img_height = img.size
    # aspect_ratio = img_width / img_height
    # barcode_width = barcode_height * aspect_ratio
    # if barcode_width > right_column_width:
    #     barcode_width = right_column_width
    #     barcode_height = barcode_width / aspect_ratio
    pdf.image(instrument.barcode, x=x_right, y=y_barcode, h=barcode_height)




    # СОХРАНЕНИЕ
    filename = f"{label_num}_{instrument.name}.pdf"
    filename = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)
    output_path = os.path.join(output_dir, filename)
    pdf.output(output_path)
    print(f"PDF сохранён: {output_path}")



if __name__ == "__main__":
    EXCEL_BOOK = "xls_files/Crafter electro 2025.xlsx"
    BOOK_SHEET = "Лист1"
    data = read_from_xlsx(book=EXCEL_BOOK, sheet=BOOK_SHEET)
    instruments = parse_crafter(data)

    num_len = len(str(len(instruments)))

    for idx, instrument in enumerate(instruments, start=1):
        # получаем номер с ведущими нулями, учитывая общую длину списка
        num = f"{idx:0{num_len}d}"

        print(f"Processing: {num} {instrument.name}, EAN {instrument.ean13}")

        # получаем штрих-код из orcascan
        instrument.barcode = generate_with_orcascan(file_name=num, ean=instrument.ean13, output_dir=BARCODES_DIR)

        # создаём этикетку
        create_label_crafter(instrument, label_num=num, output_dir=LABELS_DIR)



