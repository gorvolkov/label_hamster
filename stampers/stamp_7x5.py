import os
from fpdf import FPDF

from logger import logger
from models import MusicInstrument
from . _setup_fonts import setup_fonts
from . _scale_img import scale_img


def stamp_7x5(product: MusicInstrument, save_to: str):
    page_width, page_height = 70, 50  # мм

    pdf = FPDF(unit='mm', format=(page_width, page_height))
    pdf.add_page()

    setup_fonts(pdf)

    margin_left = 2.0
    margin_right = 2.0
    margin_top = 2.0
    margin_bottom = 2.0

    available_width = page_width - margin_left - margin_right
    available_height = page_height - margin_top - margin_bottom

    # устанавливаем соотношение ширины текстового и графического блоков как 2 : 1
    graph_block_width = available_width * 0.4
    text_block_width = available_width - graph_block_width

    # перенос строки
    paragraph = 1.5

    # явное указание переноса, который осуществляется только по margin_bottom
    pdf.set_auto_page_break(auto=True, margin=margin_bottom)

    # стартовая вертикальная позиция
    y = margin_top

    # --- ТЕКСТОВЫЙ БЛОК ---
    # model
    title_text = f"{product.brand} {product.model}"
    size = 10
    line_height = 4
    pdf.set_font("ArialTTF", "B", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_block_width, line_height, title_text, align='L')
    y = pdf.get_y() + paragraph

    # category
    size = 8
    line_height = 2
    pdf.set_font("ArialTTF", "B", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_block_width, line_height, product.category.capitalize(), align='L')
    y = pdf.get_y() + paragraph

    # compose tiny block
    tiny = []

    if product.description:
        tiny.append(f"{product.description}\n")

    # expiry and country block
    exp_and_country = []

    if product.expiry:
        exp_text = f"**Срок службы:** {product.expiry}."  # add expiry info in correct format
        exp_and_country.append(exp_text)

    if product.country:
        country_text = f"**Страна изготовления:** {product.country}"  # added markdown
        exp_and_country.append(country_text)

    exp_and_country_str = " ".join(exp_and_country)

    if exp_and_country:
        tiny.append(exp_and_country_str)

    # certification
    if product.certification:
        tiny.append(product.certification)

    # importer/vendor
    importer_vendor_text = f"**Импортёр / продавец:** {product.importer_vendor}" \
        if product.vendor \
        else f"**Импортёр и Организация, уполномоченная на принятие претензий на территории РФ:** {product.importer_vendor}"

    tiny.append(importer_vendor_text)

    # vendor
    if product.vendor:
        tiny.append(f"**Продавец:** {product.vendor}")

    # manufacturer
    if product.manufacturer:
        tiny.append(f"**Производитель:** {product.manufacturer}")

    tiny_text = "\n".join(tiny)

    size = 3
    line_height = 2.0
    pdf.set_font("ArialTTF", "", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_block_width, line_height, tiny_text, markdown=True, align="L")
    y = pdf.get_y()

    # --- ГРАФИЧЕСКИЙ БЛОК ---

    x_graphs_left = margin_left + text_block_width  # левая граница графического блока

    # LOGO
    floor_h = available_height / 4  # высота 1/4
    y = margin_top

    if product.logo:
        logo_size = floor_h
        x_logo_centered = x_graphs_left + (graph_block_width - logo_size) / 2  # центрирование изображения
        pdf.image(product.logo, x_logo_centered, y, logo_size)  # вставка по центру с масштабированием под нужный размер

    y = margin_top + floor_h  # сдвигаем курсор

    # MIDDLE_BLOCK (QR, EAC/CE)
    half_graph_w = graph_block_width / 2  # половина ширины графического блока
    x_graphs_center = x_graphs_left + half_graph_w  # серединная координата

    if product.qr:
        qr_size = min(floor_h, half_graph_w)
        x = x_graphs_center - qr_size  # вычисляем левую границу qr от серединной оси блока, по левой границе всего блока - некрасиво
        pdf.image(product.qr, x, y, qr_size)

    half_floor_h = floor_h / 2

    if product.eac:
        eac_size = min(half_floor_h, half_graph_w)
        x = x_graphs_center + (
                    half_graph_w - eac_size) / 2  # вычисляем координату для вставки по центру правого полу-блока
        pdf.image(product.eac, x, y, eac_size)

    y += half_floor_h

    if product.ce:
        ce_size = min(half_floor_h, half_graph_w)
        x = x_graphs_center + (
                    half_graph_w - ce_size) / 2  # вычисляем координату для вставки по центру правого полу-блока
        pdf.image(product.ce, x, y, ce_size)

    y += half_floor_h

    # BARCODE
    barcode = product.barcode
    floor_h = floor_h * 2  # для ШК высота этажа 2/4 всей доступной

    # use all place without margins because barcode has mergins itself
    h_limit = floor_h + margin_bottom
    w_limit = graph_block_width + margin_right
    bc_width, bc_height = scale_img(barcode, w_limit, h_limit)
    pdf.image(barcode, x_graphs_left, y, w=bc_width, h=bc_height)

    # Сохранение
    filename = f"{product.num}_{title_text}.pdf"
    output_path = os.path.join(save_to, filename)
    pdf.output(output_path)
    logger.info(f"PDF saved: {output_path}")
