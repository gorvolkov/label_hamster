import os
from fpdf import FPDF
from PIL import Image

from logger import logger
from models import ProductWB
from . stamper_conf import _init_fonts


def stamp_for_wb_with_ean_barcode_h(product: ProductWB, save_to: str):
    """
    Create label 60 mm x 40 mm for Wildberries format, pdf.

    :param product: ProductWB object.
    :param save_to: path to directory the new label will be saved to.
    """


    page_width, page_height = 60.0, 40.0  # мм

    pdf = FPDF(unit='mm', format=(page_width, page_height))
    pdf.add_page()

    _init_fonts(pdf)  # инициализация шрифтов

    margin_left = 2.0
    margin_right = 2.0
    margin_top = 2.0
    margin_bottom = 0.0

    width = page_width - margin_left - margin_right
    height = page_height - margin_top - margin_bottom

    # междустрочный интервал
    paragraph = 1.0

    # явное указание переноса, который осуществляется только по margin_bottom
    pdf.set_auto_page_break(auto=True, margin=margin_bottom)

    # стартовая вертикальная позиция
    y = margin_top

    # title
    size = 8
    line_height = 3.0
    pdf.set_font("ArialTTF", "B", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(width, line_height, product.title, align='L')
    y = pdf.get_y() + paragraph

    # description
    size = 6
    line_height = 2.0
    pdf.set_font("ArialTTF", "", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(width, line_height, product.description, align='L')
    y = pdf.get_y()

    # art
    art = f"Артикул: {product.art}"
    size = 6
    line_height = 2.0
    pdf.set_font("ArialTTF", "", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(width, line_height, art, align='L')
    y = pdf.get_y() + paragraph

    # barcode
    bc_height = height - y

    with Image.open(product.barcode_path) as img:
        orig_width, orig_height = img.size    # pixels

        dpi = img.info.get('dpi', (72, 72))[0]    # convert to mm
        orig_width_mm = orig_width / dpi * 25.4
        orig_height_mm = orig_height / dpi * 25.4

        resize_coef = bc_height / orig_height_mm
        bc_width = orig_width_mm * resize_coef

    x = (page_width - bc_width) / 2
    pdf.image(product.barcode_path, x, y, w=bc_width, h=bc_height)

    # save label
    filename = f"{product.num}_{product.art}.pdf"
    output_path = os.path.join(save_to, filename)
    pdf.output(output_path)
    logger.info(f"PDF saved: {output_path}")