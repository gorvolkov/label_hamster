import os
import io

from fpdf import FPDF
from PIL import Image

from logger import logger
from models import MusicInstrument
from . _setup_fonts import setup_fonts
from . _scale_img import scale_img


def stamp_6x4(self, product: MusicInstrument):
    """Create label 60 mm x 40 mm, pdf"""

    # Размер страницы 6 см по ширине и 4 см по высоте (альбомная ориентация)
    page_width, page_height = 60.0, 40.0  # мм

    pdf = FPDF(unit='mm', format=(page_width, page_height))
    pdf.add_page()

    setup_fonts(pdf)  # инициализация шрифтов

    margin_left = 2.0
    margin_right = 2.0
    margin_top = 2.0
    margin_bottom = 2.0
    margin_between = 0.0  # отступ между текстовым и графическим блоками

    available_width = page_width - margin_left - margin_right
    available_height = page_height - margin_top - margin_bottom

    # устанавливаем соотношение ширины текстового и графического блоков как 2 : 1
    graph_block_width = available_width * 0.45 - margin_between / 2
    text_block_width = available_width - graph_block_width - margin_between / 2

    # отступ между блоками (параграф)
    paragraph = 1.0

    # явное указание переноса, который осуществляется только по margin_bottom
    pdf.set_auto_page_break(auto=True, margin=margin_bottom)

    # стартовая вертикальная позиция
    y = margin_top

    # --- ТЕКСТОВЫЙ БЛОК ---
    # model

    title_text = f"{product.brand} {product.model}"
    size = 6
    line_height = 2.0
    pdf.set_font("ArialTTF", "B", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_block_width, line_height, title_text, align='L')
    y = pdf.get_y() + paragraph

    # category
    size = 4
    line_height = 1.5
    pdf.set_font("ArialTTF", "B", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_block_width, line_height, product.category)
    y = pdf.get_y() + paragraph

    # compose tiny block
    tiny = []

    if product.description:
        tiny.append(f"{product.description}\n")

    # expiry and country block
    exp_and_country = []

    if product.expiry:
        exp_text = f"**Срок службы**: {product.expiry}."  # add expiry info in correct format
        exp_and_country.append(exp_text)

    if product.country:
        country_text = f"**Страна изготовления**: {product.country}"  # added markdown
        exp_and_country.append(country_text)

    exp_and_country_str = " ".join(exp_and_country)

    if exp_and_country:
        tiny.append(exp_and_country_str)

    # certification
    if product.certification:
        tiny.append(product.certification)

    # importer/vendor
    importer_vendor_text = f"**Импортёр / продавец:** {product.importer_vendor}" \
        if product.manufacturer \
        else f"**Импортёр и Организация, уполномоченная на принятие претензий:**\n{product.importer_vendor}"

    tiny.append(importer_vendor_text)

    # vendor
    if product.vendor:
        tiny.append(f"**Продавец:** {product.vendor}")

    # manufacturer
    if product.manufacturer:
        tiny.append(f"**Производитель:** {product.manufacturer}")

    tiny_text = "\n".join(tiny)

    size = 3
    line_height = 1.25
    pdf.set_font("ArialTTF", "", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_block_width, line_height, tiny_text, markdown=True)
    # y = pdf.get_y()

    # barcode
    x = margin_left + text_block_width + margin_between
    y = margin_top

    max_width = graph_block_width  # ограничение по ширине, мм
    max_height = available_height  # ограничение по высоте, мм

    barcode = product.barcode

    bc_width, bc_height = scale_img(barcode, max_height, max_width)

    with Image.open(product.barcode) as img:
        # Поворот изображения на 90 градусов против часовой стрелки
        img_rotated = img.rotate(90, expand=True)

        # Сохраняем повернутое изображение во временный буфер
        buf = io.BytesIO()
        img_rotated.save(buf, format='PNG')
        buf.seek(0)

        # вставляем в файл этикетки
        pdf.image(buf, x, y, bc_width, bc_height)

    # Сохранение
    # ВНИМАНИЕ! Сохраняет с именем текста заголовка (бренд + модель)
    filename = f"{product.num}_{title_text}.pdf"
    output_path = os.path.join(self.output_dir, filename)
    pdf.output(output_path)
    logger.info(f"PDF saved: {output_path}")