import os
import io
from fpdf import FPDF
from PIL import Image

from logger import logger
from models import ProductWB
from . stamper_conf import _init_fonts


def stamp_for_wb_with_ean_barcode_v(product: ProductWB, save_to: str):
    """Create label 60 mm x 40 mm, pdf"""

    page_width, page_height = 60.0, 40.0  # мм
    pdf = FPDF(unit='mm', format=(page_width, page_height))
    pdf.add_page()
    _init_fonts(pdf)  # инициализация шрифтов

    margin_left = 2.0
    margin_right = 2.0
    margin_top = 2.0
    margin_bottom = 0.0

    width = page_width - margin_left - margin_right
    half_width = width / 2
    height = page_height - margin_top - margin_bottom
    paragraph = 1.0

    pdf.set_auto_page_break(auto=True, margin=margin_bottom)

    # y start pos
    y = margin_top

    # title
    size = 8
    line_height = 3.0
    pdf.set_font("ArialTTF", "B", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(half_width, line_height, product.title, align='L')
    y = pdf.get_y() + paragraph

    # description
    size = 6
    line_height = 2.0
    pdf.set_font("ArialTTF", "", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(half_width, line_height, product.description, align='L')
    y = pdf.get_y()

    # art
    art = f"Артикул: {product.art}"
    size = 6
    line_height = 2.0
    pdf.set_font("ArialTTF", "", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(half_width, line_height, art, align='L')
    y = pdf.get_y() + paragraph

    # barcode

    # resizing
    bc_height = half_width
    with Image.open(product.barcode_path) as img:
        orig_width, orig_height = img.size    # pixels
        dpi = img.info.get('dpi', (72, 72))[0]    # convert to mm
        orig_width_mm = orig_width / dpi * 25.4
        orig_height_mm = orig_height / dpi * 25.4
        resize_coef = bc_height / orig_height_mm
        bc_width = orig_width_mm * resize_coef

        img_rotated = img.rotate(90, expand=True)
        buf = io.BytesIO()
        img_rotated.save(buf, format='PNG')
        buf.seek(0)

    x = page_width / 2
    pdf.image(product.barcode_path, x, y, w=bc_width, h=bc_height)


    # with Image.open(product.barcode) as img:
    #     # Поворот изображения на 90 градусов против часовой стрелки
    #     img_rotated = img.rotate(90, expand=True)
    #     rot_width_px, rot_height_px = img_rotated.size  # размеры в пикселях после поворота
    #     dpi = img_rotated.info.get('dpi', (72, 72))[0]  # convert to mm
    #     rot_width_mm = orig_width / dpi * 25.4
    #     rot_height_mm = orig_height / dpi * 25.4
    #     resize_coef = rot_height_mm / orig_height_mm
    #
    #
    #     barcode_height = min(rot_height_px, height)
    #     barcode_width = barcode_height * aspect_ratio
    #     if barcode_width > max_width:
    #         barcode_width = max_width
    #         barcode_height = barcode_width / aspect_ratio
    #
    #     # Сохраняем повернутое изображение во временный буфер
    #     buf = io.BytesIO()
    #     img_rotated.save(buf, format='PNG')
    #     buf.seek(0)
    #
    #     # вставляем в файл этикетки
    #     pdf.image(buf, x=x_barcode, y=y_barcode, w=barcode_width, h=barcode_height)


    # save label
    filename = f"{product.num}_{product.art}.pdf"
    output_path = os.path.join(save_to, filename)
    pdf.output(output_path)
    logger.info(f"PDF saved: {output_path}")


# код для тестирования работы с пдф
if __name__ == "__main__":

    # test_data = {'brand': 'FLIGHT', 'model': 'Pathfinder Baritone BRG', 'category': 'Электроукулеле с чехлом', 'description': 'Размер: баритон Материал корпуса: тополь запеченный Цвет: British Racing Green / зеленый', 'expiry': '3', 'country': 'Китай', 'certification': 'Соответствует требованиям ТР ТС 020/2011 "Электромагнитная совместимость технических средств", ТР ЕАЭС 037/2016 "Об ограничении применения опасных веществ в изделиях электротехники и радиоэлектроники”', 'importer_vendor': 'ООО «Мьюзик лайн» 127474, РФ, г. Москва, Дмитровское шоссе, д. 64. корп. 4, этаж 1, пом. 3, комн. 3.', 'vendor': 'ООО «Музыкальные инструменты» 127474, РФ, г. Москва, Дмитровское шоссе, д. 64. корп. 4, этаж 1, пом. 3, комн. 2.', 'manufacturer': 'JIANGSU KAIBAO MUSICAL INSTRUMENT CO., LTD NO.13, TONGDA ROAD, LIKOU TOWN, SIYANG COUNTY, SUQIAN CITY, JIANGSU PROVINCE, CHINA ЙИАНГСУ КАИБАО МЬЮЗИКАЛ ИНСТРУМЕНТ КО., ЛТД  №.13, ТОНГДА РОАД, ЛИКОУ ТАУН, СИЯНГ КАУНТИ, СУЯИАН СИТИ, ЙИАНГСУ ПРОВИНЦ, КИТАЙ', 'ean13': '3831120933735', 'eac': 'ДА', 'ce': 'ДА', 'logo': 'ДА', 'instruction': 'https://example.com'}
    #
    # # подготовка экземпляра продукта
    # test_product = MusicInstrument.from_dict(test_data)
    # test_product.num = test_num
    # test_product.prepare_all()

    # штамповка
    # stamper = Stamper(save_to=TEST_DIR)
    # stamper.stamp(product=test_product, format="6*4")

    test_wb = {'title': 'Термос 3 литра, черный, металлический', 'art': 'Panacotti ML-TR001-3000A', 'description': 'Классный продукт', 'barcode': '3831120939683'}
    product = ProductWB.from_dict(test_wb)
    product.num = "1"
    product.attach_barcode()

    stamp_for_wb_with_ean_barcode_h(product=product, save_to="E:\PYCHARM PROJECTS\label_hamster\_tests")