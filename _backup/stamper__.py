from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.units import mm as UNIT_MM
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os

from config import TEST_DIR
from models import MusicInstrument, Toy
from logger import logger

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os

class Stamper:
    def __init__(self, save_to: str):
        self.output_dir = save_to

    def _stamp_7x5(self, product):
        # Размер страницы 70x50 мм (7х5 см)
        page_width_mm, page_height_mm = 70, 50
        page_width = page_width_mm * mm
        page_height = page_height_mm * mm

        # Путь для сохранения
        filename = f"{product.num}_{product.model}.pdf"
        output_path = os.path.join(self.output_dir, filename)

        # Создаём canvas для PDF
        pdf = canvas.Canvas(output_path, pagesize=(page_width, page_height))

        # Отступы в мм, переведённые в пункты (points)
        margin_left = 5 * mm
        margin_top = page_height - 2 * mm  # считаем от верхнего края вниз

        # Вертикальный интервал между строками
        line_height_model = 9  # points (примерно 3.18 мм) для модели (большой текст)
        line_height_normal = 7  # points (~2.47 мм) для остального текста

        # Текущая координата по вертикали (от верхнего края вниз)
        y = margin_top

        # Вспомогательная функция рисования многострочного текста с переносом
        def draw_multiline(text, x, y, max_width, font_name, font_size, leading):
            from reportlab.pdfbase.pdfmetrics import stringWidth
            words = text.split()
            line = ''
            space_width = stringWidth(' ', font_name, font_size)
            cur_width = 0

            for word in words:
                w = stringWidth(word, font_name, font_size)
                if cur_width + w > max_width and line:
                    pdf.setFont(font_name, font_size)
                    pdf.drawString(x, y, line.strip())
                    y -= leading
                    line = word + ' '
                    cur_width = w + space_width
                else:
                    line += word + ' '
                    cur_width += w + space_width
            if line:
                pdf.setFont(font_name, font_size)
                pdf.drawString(x, y, line.strip())
                y -= leading
            return y

        # Максимальная ширина блока текста
        max_text_width = page_width - 2 * margin_left

        x_text = margin_left

        # Рисуем блоки текста последовательно

        # MODEL (большие буквы, жирный шрифт Helvetica-Bold)
        y = draw_multiline(product.model.upper(), x_text, y, max_text_width, "Helvetica-Bold", 12, line_height_model)

        # CATEGORY (жирный шрифт меньше)
        y = draw_multiline(product.category, x_text, y, max_text_width, "Helvetica-Bold", 9, line_height_normal)

        # DESCRIPTION (обычный шрифт)
        if product.description:
            desc = product.description.capitalize()
            y = draw_multiline(desc, x_text, y, max_text_width, "Helvetica", 7, line_height_normal)

        # INFO: expiry + country
        info_texts = []
        if getattr(product, "expiry", None):
            info_texts.append(f"Срок службы: {product.expiry}.")
        if getattr(product, "country", None):
            info_texts.append(f"Страна изготовления: {product.country}")
        if info_texts:
            y = draw_multiline(" ".join(info_texts), x_text, y, max_text_width, "Helvetica", 7, line_height_normal)

        # CERTIFICATION
        if getattr(product, "certification", None):
            y = draw_multiline(product.certification, x_text, y, max_text_width, "Helvetica", 7, line_height_normal)

        # IMPORTER / VENDOR
        if getattr(product, "manufacturer", None):
            importer_text = f"Импортёр / продавец: {product.importer_vendor}"
        else:
            importer_text = f"Импортёр и Организация, уполномоченная на принятие претензий:\n{product.importer_vendor}"
        # Заменим перенос строки на пробел для простоты рисовки
        importer_text = importer_text.replace('\n', ' ')
        y = draw_multiline(importer_text, x_text, y, max_text_width, "Helvetica", 7, line_height_normal)

        # VENDOR
        if getattr(product, "vendor", None):
            y = draw_multiline(f"Продавец: {product.vendor}", x_text, y, max_text_width, "Helvetica", 7, line_height_normal)

        # MANUFACTURER
        if getattr(product, "manufacturer", None):
            y = draw_multiline(f"Производитель: {product.manufacturer}", x_text, y, max_text_width, "Helvetica", 7, line_height_normal)

        # Сохраняем pdf
        pdf.save()

        # Лог
        print(f"PDF saved: {output_path}")

