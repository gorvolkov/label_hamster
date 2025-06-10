

from models import MusicInstrument

import os
import io
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfString, PdfObject, PageMerge
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4


ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'


def add_barcode_to_pdf(input_pdf_path, output_pdf_path, barcode_image_path, x_pt, y_pt, width_pt):
    template_pdf = PdfReader(input_pdf_path)
    page = template_pdf.pages[0]

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=landscape(A4))
    can.drawImage(barcode_image_path, x_pt, y_pt, width=width_pt, preserveAspectRatio=True, mask='auto')
    can.save()

    packet.seek(0)
    barcode_pdf = PdfReader(packet)
    barcode_page = barcode_pdf.pages[0]

    merger = PageMerge(page)
    merger.add(barcode_page).render()

    writer = PdfWriter()
    writer.addpage(page)
    writer.write(output_pdf_path)


def create_label(temp_path, output_path, music_instrument):
    template_pdf = PdfReader(temp_path)

    # Включаем NeedAppearances
    if template_pdf.Root:
        template_pdf.Root.update(PdfDict(NeedAppearances=PdfObject('true')))

    data_dict = {
        "title": music_instrument.title,
        "subtitle": music_instrument.subtitle,
        "description": music_instrument.description,
        "extra": music_instrument.extra,
        "importer": music_instrument.importer,
        "vendor": music_instrument.vendor,
        "manufacturer": " ".join(filter(None, [music_instrument.manufacturer, music_instrument.manufacturer_ru])),
    }

    for page in template_pdf.pages:
        annotations = page.get(ANNOT_KEY)
        if annotations:
            for annotation in annotations:
                if annotation.get(SUBTYPE_KEY) == WIDGET_SUBTYPE_KEY and annotation.get(ANNOT_FIELD_KEY):
                    key = annotation[ANNOT_FIELD_KEY][1:-1]
                    if key in data_dict:
                        text = data_dict[key]
                        annotation.update(PdfDict(V=PdfString.encode(text)))
                        annotation.update(PdfDict(AS=PdfString.encode(text)))

    PdfWriter().write(output_path, template_pdf)

    if music_instrument.barcode and os.path.isfile(music_instrument.barcode):
        mm_to_pt = 2.83465
        barcode_width_mm = 90
        barcode_width_pt = barcode_width_mm * mm_to_pt
        margin_right_mm = 10
        margin_right_pt = margin_right_mm * mm_to_pt
        page_width_pt = 842
        page_height_pt = 595

        x_pt = page_width_pt - barcode_width_pt - margin_right_pt
        y_pt = page_height_pt - 20 * mm_to_pt

        add_barcode_to_pdf(output_path, output_path, music_instrument.barcode, x_pt, y_pt, barcode_width_pt)

    print(f"Label created: {output_path}")


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
    create_label("label_temp/temp_1.pdf", "labels/test-2.pdf", instrument)
