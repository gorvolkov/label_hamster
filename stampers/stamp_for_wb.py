import os
from fpdf import FPDF

from logger import logger
from models import ProductWB
from . _setup_fonts import setup_fonts
from . _scale_img import scale_img

def stamp_for_wb(product: ProductWB, save_to: str):
    """
    Create label 60 mm x 40 mm for Wildberries format, pdf.

    :param product: ProductWB object.
    :param save_to: path to directory the new label will be saved to.
    """

    page_width, page_height = 60.0, 40.0  # мм

    pdf = FPDF(unit='mm', format=(page_width, page_height))
    pdf.add_page()

    setup_fonts(pdf)  # initialize fonts for PDF document

    margin_left = 2.0
    margin_right = 2.0
    margin_top = 2.0
    margin_bottom = 0.0

    width = page_width - margin_left - margin_right
    height = page_height - margin_top - margin_bottom
    paragraph = 1.0   # interval between the lines

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

    description = product.description.capitalize()

    pdf.multi_cell(width, line_height, description, align='L')
    y = pdf.get_y()

    # stock_id
    stock_id = f"Артикул: {product.stock_id}"
    size = 6
    line_height = 2.0
    pdf.set_font("ArialTTF", "", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(width, line_height, stock_id, align='L')
    y = pdf.get_y() + paragraph

    # barcode
    barcode = product.barcode_path
    bc_width, bc_height = scale_img(barcode, width, height - y)    # scale image
    x = (page_width - bc_width) / 2     # center position of scaled barcode
    pdf.image(product.barcode_path, x, y, w=bc_width, h=bc_height)

    # save label
    filename = f"{product.num}_{product.stock_id}.pdf"
    output_path = os.path.join(save_to, filename)
    pdf.output(output_path)
    logger.info(f"PDF saved: {output_path}")