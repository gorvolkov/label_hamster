import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from models import MusicInstrument

def create_instrument_pdf(instrument: MusicInstrument, output_dir: str):
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

    margin_left = 10
    margin_right = 10
    barcode_width = 90
    page_width = pdf.w
    text_width = page_width - margin_left - margin_right - barcode_width

    y = 20

    # title: жирный, капсом, уменьшен с 50 до 40
    pdf.set_font("ArialTTF", "B", 40)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_width, 14, instrument.title.upper())
    y = pdf.get_y() + 2

    # subtitle: жирный, без капса, уменьшен с 50 до 40
    pdf.set_font("ArialTTF", "B", 40)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_width, 14, instrument.subtitle)
    subtitle_y = y  # для выравнивания баркода
    y = pdf.get_y() + 4

    # description: обычный, уменьшен с 24 до 20
    pdf.set_font("ArialTTF", "", 20)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_width, 10, instrument.description)
    y = pdf.get_y() + 4

    # extra: без заголовка, уменьшен с 12 до 10
    if instrument.extra:
        pdf.set_font("ArialTTF", "", 10)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_width, 7, instrument.extra)
        y = pdf.get_y() + 6

    # importer -> "Импортер/Продавец", уменьшен с 12 до 10
    if instrument.importer:
        pdf.set_font("ArialTTF", "", 10)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_width, 7, f"Импортер/Продавец: {instrument.importer}")
        y = pdf.get_y() + 4

    # vendor -> "Продавец", уменьшен с 12 до 10
    if instrument.vendor:
        pdf.set_font("ArialTTF", "", 10)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_width, 7, f"Продавец: {instrument.vendor}")
        y = pdf.get_y() + 4

    # manufacturer + manufacturer_ru объединяем в одну строку
    manufacturer_text = " ".join(filter(None, [instrument.manufacturer, instrument.manufacturer_ru]))
    if manufacturer_text:
        pdf.set_font("ArialTTF", "", 10)
        pdf.set_xy(margin_left, y)
        full_text = f"Производитель: {manufacturer_text}"
        pdf.multi_cell(text_width, 7, full_text)
        y = pdf.get_y() + 6

    # ean и ce не выводим

    # Баркод выравниваем по верхнему краю subtitle
    if instrument.barcode and os.path.isfile(instrument.barcode):
        x_pos = page_width - barcode_width - margin_right
        y_pos = subtitle_y
        pdf.image(instrument.barcode, x=x_pos, y=y_pos, w=barcode_width)

    # Сохраняем PDF
    filename = f"{instrument.num}_{instrument.title}.pdf"
    filename = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)
    output_path = os.path.join(output_dir, filename)
    pdf.output(output_path)
    print(f"PDF сохранён: {output_path}")


if __name__ == "__main__":
    instrument_data = {
        "num": "001",
        "title": "BUMBLEBEE OGO-111",
        "subtitle": "Басовая флейта",
        "description": "Цвет: шмелиный. Пожужжим.",
        "importer": "ООО «Мьюзик лайн» 127474, РФ, г. Москва, Дмитровское шоссе, д. 64. корп. 4, этаж 1, пом. 3, комн. 3.",
        "vendor": "ООО «Музыкальные инструменты» 127474, РФ, г. Москва, Дмитровское шоссе, д. 64. корп. 4, этаж 1, пом. 3, комн. 2.",
        "manufacturer": "FOSHAN DROME DAI IMPORT AND EXPORT CO., LTD, Rm.B104 Zhengjie building No 8 Sanshan Road Zhengjie East group Guicheng street of Nanhai District, Foshan city, Guangdong China.",
        "manufacturer_ru": "Фошан Дроме Дай Импорт энд Экспорт Ко., ЛТД, Рм. Б104 Женгжи билдинг №8 Саншан Роад Женгжи Ист груп Гуиченг стрит оф Нанхай Дистрикт, Фошан сити, Гуангдонг Китай",
        "extra": "Срок службы 3 года. Страна изготовления: Китай. Соответствует требованиям безопасности электротехнического оборудования и т.д. и т.п.",
        "barcode": r"barcodes/1.png",
        "ean": "1234567890123",
        "ce": "EAC"
    }

    instrument = MusicInstrument.from_dict(instrument_data)
    create_instrument_pdf(instrument, output_dir="label_output")