import io
import os
from fpdf import FPDF
from config import TEST_DIR
from models import MusicInstrument, Toy, ProductWB
from logger import logger
from PIL import Image

from . stamper_conf import _init_fonts


class Stamper:
    def __init__(self, save_to: str):
        self.output_dir = save_to

        self.formats = {
            "7*5": self._stamp_7x5,
            "6*4": self._stamp_6x4
        }


    def _stamp_7x5(self, product: MusicInstrument):
        # Размер страницы 7 см по ширине и 5 см по высоте (альбомная ориентация)
        page_width, page_height = 70, 50  # мм

        pdf = FPDF(unit='mm', format=(page_width, page_height))
        pdf.add_page()

        _init_fonts(pdf)  # инициализация шрифтов

        margin_left = 2.0
        margin_right = 5.0
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

        # строчка для конкатенации бренда и модели
        title_text = f"{product.brand} {product.model}"
        # ВНИМАНИЕ! Это может быть нужно не во всех кейсах. Надо уточнить этот момент с БМ

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
        pdf.multi_cell(text_block_width, line_height, product.category.capitalize())
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
        line_height = 1.5
        pdf.set_font("ArialTTF", "", size)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, tiny_text, markdown=True, align="L")
        y = pdf.get_y()

        # --- ГРАФИЧЕСКИЙ БЛОК ---

        x_graphs_left = margin_left + text_block_width   # левая граница графического блока

        # LOGO

        floor_h = available_height / 4    # высота 1/4
        y = margin_top

        if product.logo:
            logo_size = floor_h
            x_logo_centered = x_graphs_left + (graph_block_width - logo_size) / 2   # центрирование изображения
            pdf.image(product.logo, x_logo_centered, y, logo_size)    # вставка по центру с масштабированием под нужный размер

        y = margin_top + floor_h    # сдвигаем курсор

        # MIDDLE_BLOCK (QR, EAC/CE)
        half_graph_w = graph_block_width / 2    # половина ширины графического блока
        x_graphs_center = x_graphs_left + half_graph_w    # серединная координата

        if product.qr:
            qr_size = min(floor_h, half_graph_w)
            x = x_graphs_center - qr_size    # вычисляем левую границу qr от серединной оси блока, по левой границе всего блока - некрасиво
            pdf.image(product.qr, x, y, qr_size)

        half_floor_h = floor_h / 2

        if product.eac:
            eac_size = min(half_floor_h, half_graph_w)
            x = x_graphs_center + (half_graph_w - eac_size) / 2    # вычисляем координату для вставки по центру правого полу-блока
            pdf.image(product.eac, x, y, eac_size)

        y += half_floor_h

        if product.ce:
            ce_size = min(half_floor_h, half_graph_w)
            x = x_graphs_center + (half_graph_w - ce_size) / 2     # вычисляем координату для вставки по центру правого полу-блока
            pdf.image(product.ce, x, y, ce_size)

        y += half_floor_h

        # BARCODE
        floor_h = floor_h * 2   # для ШК высота этажа 2/4 всей доступной

        # масштабируем исходное изображение под нужный размер блока
        with Image.open(product.barcode) as img:
            orig_width, orig_height = img.size

        if orig_width > graph_block_width:
            barcode_width = graph_block_width
            barcode_height = orig_height / orig_width * barcode_width

        barcode_height = floor_h
        barcode_width = orig_width / orig_height * barcode_height

        pdf.image(product.barcode, x_graphs_left, y, w=barcode_width, h=barcode_height)

        # Сохранение
        filename = f"{product.num}_{title_text}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        pdf.output(output_path)
        logger.info(f"PDF saved: {output_path}")

    def _stamp_6x4(self, product: MusicInstrument):
        """Create label 60 mm x 40 mm, pdf"""

        # Размер страницы 6 см по ширине и 4 см по высоте (альбомная ориентация)
        page_width, page_height = 60.0, 40.0  # мм

        pdf = FPDF(unit='mm', format=(page_width, page_height))
        pdf.add_page()

        _init_fonts(pdf)  # инициализация шрифтов

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

        # строчка для конкатенации бренда и модели
        title_text = f"{product.brand} {product.model}"
        # ВНИМАНИЕ! Это может быть нужно не во всех кейсах. Надо уточнить этот момент с БМ

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
        y = pdf.get_y()

        # --- ГРАФИЧЕСКИЙ БЛОК ---
        # в этой версии вставляем только ШК вертикально
        # barcode

        x_barcode = margin_left + text_block_width + margin_between
        y_barcode = margin_top

        max_width = graph_block_width  # ограничение по ширине, мм
        max_height = available_height  # ограничение по высоте, мм

        with Image.open(product.barcode) as img:
            # Поворот изображения на 90 градусов против часовой стрелки
            img_rotated = img.rotate(90, expand=True)
            rot_width_px, rot_height_px = img_rotated.size  # размеры в пикселях после поворота
            aspect_ratio = rot_width_px / rot_height_px  # отношение ширины к высоте после поворота

            barcode_height = min(rot_height_px, max_height)
            barcode_width = barcode_height * aspect_ratio
            if barcode_width > max_width:
                barcode_width = max_width
                barcode_height = barcode_width / aspect_ratio

            # Сохраняем повернутое изображение во временный буфер
            buf = io.BytesIO()
            img_rotated.save(buf, format='PNG')
            buf.seek(0)

            # вставляем в файл этикетки
            pdf.image(buf, x=x_barcode, y=y_barcode, w=barcode_width, h=barcode_height)

        # Сохранение
        # ВНИМАНИЕ! Сохраняет с именем текста заголовка (бренд + модель)
        filename = f"{product.num}_{title_text}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        pdf.output(output_path)
        logger.info(f"PDF saved: {output_path}")


    def stamp(self, product: MusicInstrument, format: str|None=None):
        if format is None:
            stamp_func = self.formats["7*5"]
        else:
            stamp_func = self.formats[format]

        stamp_func(product=product)     # noqa


def stamp_for_wb(product: ProductWB, save_to: str):
    """
    Create label 60 mm x 40 mm for Wildberries format, pdf.

    :param product: ProductWB object.
    :param save_to: path to directory the new label will be saved to.
    """

    # Размер страницы 6 см по ширине и 4 см по высоте (альбомная ориентация)
    page_width, page_height = 60.0, 40.0  # мм

    pdf = FPDF(unit='mm', format=(page_width, page_height))
    pdf.add_page()

    _init_fonts(pdf)  # инициализация шрифтов

    margin_left = 2.0
    margin_right = 2.0
    margin_top = 2.0
    margin_bottom = 2.0

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
    pdf.multi_cell(width, line_height, product.title, align='C')
    y = pdf.get_y() + paragraph

    # art
    art = f"Арт: {product.art}"
    size = 6
    line_height = 2.0
    pdf.set_font("ArialTTF", "", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(width, line_height, art)
    y = pdf.get_y() + paragraph

    # description
    size = 6
    line_height = 2.0
    pdf.set_font("ArialTTF", "", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(width, line_height, product.description)
    y = pdf.get_y() + paragraph

    # barcode
    y = height / 2
    bc_height = height / 3

    with Image.open(product.barcode_path) as img:
        orig_width, orig_height = img.size
        bc_width = min(width, orig_width)

    pdf.image(product.barcode_path, x=margin_left, y=y, w=bc_width, h=bc_height)
    y += bc_height + paragraph

    # barcode digits
    size = 8
    line_height = 2.0
    pdf.set_font("ArialTTF", "", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(width, line_height, product.barcode, align='C')

    # save this shit
    filename = f"{product.num}_{product.art}.pdf"
    output_path = os.path.join(save_to, filename)
    pdf.output(output_path)
    logger.info(f"PDF saved: {output_path}")


def stamp_for_wb_with_ean_barcode_h(product: ProductWB, save_to: str):
    """
    Create label 60 mm x 40 mm for Wildberries format, pdf.

    :param product: ProductWB object.
    :param save_to: path to directory the new label will be saved to.
    """

    # Размер страницы 6 см по ширине и 4 см по высоте (альбомная ориентация)
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