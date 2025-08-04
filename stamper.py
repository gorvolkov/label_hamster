import io
import os
from fpdf import FPDF
from config import TEST_DIR
from models import MusicInstrument, Toy
from logger import logger
from PIL import Image

# System Fonts  (Win 10)
FONTS = {
        "arial_regular": r"C:\Windows\Fonts\arial.ttf",
        "arial_bold": r"C:\Windows\Fonts\arialbd.ttf"
}


def _init_fonts(pdf: FPDF):
    pdf.add_font("ArialTTF", "", FONTS["arial_regular"])
    pdf.add_font("ArialTTF", "B", FONTS["arial_bold"])




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
        margin_right = 2.0
        margin_top = 2.0
        margin_bottom = 2.0
        margin_between = 0.0 # отступ между текстовым и графическим блоками

        available_width = page_width - margin_left - margin_right
        available_height = page_height - margin_top - margin_bottom

        # устанавливаем соотношение ширины текстового и графического блоков как 2 : 1
        graph_block_width = available_width * 0.33 - margin_between / 2
        text_block_width = available_width - graph_block_width - margin_between / 2

        # отступ между блоками (параграф)
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

        size = 4
        line_height = 1.5
        pdf.set_font("ArialTTF", "", size)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, tiny_text, markdown=True)
        y = pdf.get_y()

        # --- ГРАФИЧЕСКИЙ БЛОК ---

        x_graphs = margin_left + text_block_width + margin_between

        # высота "этажа" с графикой
        floor_height = available_height / 3

        # logo
        if product.logo:
            # масштабируем логотип под размер высоты "этажа"
            size = floor_height

            # координаты
            x_centered = x_graphs + (graph_block_width - size) / 2
            y_top_floor = margin_top

            # вставка
            pdf.image(product.logo, x=x_centered, y=y_top_floor, h=size)

        # middle block (QR, EAC/CE)

        # вертикальная координата
        y_mid_floor = margin_top + floor_height

        # отступ между QR и EAC/CE, по умолчанию 1 мм
        margin_sub = margin_between
        subblock_width = (graph_block_width - margin_sub) / 2

        if product.qr:
            qr_size = min(floor_height, subblock_width)
            y_centered = y_mid_floor + (floor_height - qr_size) / 2
            pdf.image(product.qr, x=x_graphs, y=y_centered, h=qr_size)

        right_subblock_x = x_graphs + subblock_width + margin_sub
        margin_ce_eac = margin_between
        half_floor_height = floor_height / 2
        right_subblock_width = graph_block_width / 2

        if product.eac:
            eac_height = half_floor_height
            eac_width = eac_height
            if eac_width > right_subblock_width:
                eac_width = right_subblock_width
                eac_height = eac_width
            pdf.image(product.eac, x=right_subblock_x, y=y_mid_floor, w=eac_width, h=eac_height)

        if product.ce:
            ce_height = half_floor_height
            ce_width = ce_height
            if ce_width > right_subblock_width:
                ce_width = right_subblock_width
                ce_height = ce_width
            pdf.image(product.ce, x=right_subblock_x, y=y_mid_floor + half_floor_height + margin_ce_eac, w=ce_width,
                      h=ce_height)

        # barcode
        # координата по высоте
        y = margin_top + 2 * floor_height

        # масштабируем исходное изображение под нужный размер блока
        with Image.open(product.barcode) as img:
            orig_width, orig_height = img.size
            aspect_ratio = orig_width / orig_height
        max_width = graph_block_width
        max_height = floor_height

        if aspect_ratio >= 1:
            # Ширина больше или равна высоте, ширина ограничивает
            barcode_width = min(orig_width, max_width)
            barcode_height = barcode_width / aspect_ratio
            if barcode_height > max_height:
                barcode_height = max_height
                barcode_width = barcode_height * aspect_ratio
        else:
            # Высота больше ширины, высота ограничивает
            barcode_height = min(orig_height, max_height)
            barcode_width = barcode_height * aspect_ratio
            if barcode_width > max_width:
                barcode_width = max_width
                barcode_height = barcode_width / aspect_ratio

        # координата по горизонтали для вставки по центру
        x_centered = x_graphs + (graph_block_width - barcode_width) / 2
        pdf.image(product.barcode, x=x_centered, y=y, w=barcode_width, h=barcode_height)

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


# код для тестирования работы с пдф
if __name__ == "__main__":
    test_num = input("test num = ")

    test_data = {'brand': 'FLIGHT', 'model': 'Pathfinder Baritone BRG', 'category': 'Электроукулеле с чехлом', 'description': 'Размер: баритон Материал корпуса: тополь запеченный Цвет: British Racing Green / зеленый', 'expiry': '3', 'country': 'Китай', 'certification': 'Соответствует требованиям ТР ТС 020/2011 "Электромагнитная совместимость технических средств", ТР ЕАЭС 037/2016 "Об ограничении применения опасных веществ в изделиях электротехники и радиоэлектроники”', 'importer_vendor': 'ООО «Мьюзик лайн» 127474, РФ, г. Москва, Дмитровское шоссе, д. 64. корп. 4, этаж 1, пом. 3, комн. 3.', 'vendor': 'ООО «Музыкальные инструменты» 127474, РФ, г. Москва, Дмитровское шоссе, д. 64. корп. 4, этаж 1, пом. 3, комн. 2.', 'manufacturer': 'JIANGSU KAIBAO MUSICAL INSTRUMENT CO., LTD NO.13, TONGDA ROAD, LIKOU TOWN, SIYANG COUNTY, SUQIAN CITY, JIANGSU PROVINCE, CHINA ЙИАНГСУ КАИБАО МЬЮЗИКАЛ ИНСТРУМЕНТ КО., ЛТД  №.13, ТОНГДА РОАД, ЛИКОУ ТАУН, СИЯНГ КАУНТИ, СУЯИАН СИТИ, ЙИАНГСУ ПРОВИНЦ, КИТАЙ', 'ean13': '3831120933735', 'eac': 'ДА', 'ce': 'ДА', 'logo': 'ДА', 'instruction': 'https://example.com'}

    # подготовка экземпляра продукта
    test_product = MusicInstrument.from_dict(test_data)
    test_product.num = test_num
    test_product.prepare_all()

    # штамповка
    stamper = Stamper(save_to=TEST_DIR)
    stamper.stamp(product=test_product, format="6*4")