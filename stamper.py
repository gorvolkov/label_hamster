import os
from fpdf import FPDF

from config import TEST_DIR
from models import Label, ProductRaw
from logger import logger


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

    def create_a4(self, label: Label):
        # create template pdf
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()

        # load fonts
        _init_fonts(pdf)

        # get full page width and height
        page_height = pdf.h
        page_width = pdf.w

        # set margins
        margin_left = 12
        margin_right = 10
        margin_top = 16
        margin_bottom = 0
        margin_text_graph = 6    # a margin between text and graph blocks

        # available for printing width and height
        available_width = page_width - margin_left - margin_right
        available_height = page_height - margin_top - margin_bottom

        # setup graph_block_width = 1/3, text_block_width = 2/3
        graph_block_width = available_width * 0.33 - margin_text_graph / 2
        text_block_width = available_width - graph_block_width - margin_text_graph / 2

        y = margin_top

        # setup paragraph shift
        paragraph = 4

        # TEXT BLOCK (LEFT)
        # model
        size, line_height = 40, 16
        pdf.set_font("ArialTTF", "B", size)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, label.model.upper())
        y = pdf.get_y() + paragraph

        # category
        size, line_height = 36, 14
        pdf.set_font("ArialTTF", "B", size)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, label.category)
        y = pdf.get_y() + paragraph

        # description
        size, line_height = 16, 6
        pdf.set_font("ArialTTF", "", size)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, label.description)
        y = pdf.get_y() + 2 * paragraph

        # for all other text
        size, line_height = 14, 6
        pdf.set_font("ArialTTF", "", size)

        # expiry and country
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, label.info_block, markdown=True)
        y = pdf.get_y() + paragraph

        # certification
        if label.certification:
            pdf.set_xy(margin_left, y)
            pdf.multi_cell(text_block_width, line_height, label.certification, markdown=True)
            y = pdf.get_y() + paragraph
        else:
            y = pdf.get_y() + 6 * paragraph      # если сертификации нет, пропускаем 6 строк

        # importer / vendor
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, f"**Импортёр / продавец:** {label.importer_vendor}", markdown=True)
        y = pdf.get_y() + paragraph

        # vendor
        if label.vendor:
            pdf.set_xy(margin_left, y)
            pdf.multi_cell(text_block_width, line_height, f"**Продавец:** {label.vendor}", markdown=True)
            y = pdf.get_y() + paragraph
        else:
            y = pdf.get_y() + 3 * paragraph

        # manufacturer
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, f"**Производитель:** {label.manufacturer}", markdown=True)

        # GRAPHS BLOCK (RIGHT)
        x_graphs = margin_left + text_block_width + margin_text_graph

        # margin floors
        floor_margin = 2

        # calculate width for every graphics "floor"
        floor_height = available_height / 3 - 2 * floor_margin

        # 1. Logo floor (upper)
        if label.logo is not None:
            size = floor_height
            x_centered = x_graphs + (graph_block_width - size) / 2   # center logo
            pdf.image(label.logo, x=x_centered, y=margin_top, h=size)

        # 2. Middle block (qr слева, eac/ce справа)
        middle_block_y = margin_top + floor_height + floor_margin
        margin_sub = 2   # margin between QR block and CE/EAC block
        subblock_width = (graph_block_width - margin_sub) / 2

        if label.qr is not None:
            qr_size = floor_height if floor_height < subblock_width else subblock_width
            trim_coef = 0.9  # looks better
            qr_size *= trim_coef
            y_centered = middle_block_y + (floor_height - qr_size) / 2
            pdf.image(label.qr, x=x_graphs, y=y_centered, h=qr_size)

        right_subblock_x = x_graphs + subblock_width + margin_sub
        margin_ce_eac = 6  # margin between CE block and EAC block
        half_floor_height = (floor_height / 2 - margin_ce_eac)
        right_subblock_width = graph_block_width / 2 - margin_ce_eac

        if label.eac is not None:
            coef = 1.152
            eac_height = half_floor_height
            eac_width = eac_height * coef

            # если рассчитанная ширина EAC больше ширины, выделенной под суб-блок, то пересчитываем:
            if eac_width > right_subblock_width:
                eac_width = right_subblock_width
                eac_height = eac_width / coef

            pdf.image(label.eac, x=right_subblock_x, y=middle_block_y, w=eac_width, h=eac_height)

        if label.ce is not None:
            coef = 1.028
            ce_height = half_floor_height
            ce_width = ce_height * coef

            # если рассчитанная ширина CE больше ширины, выделенной под суб-блок, то пересчитываем:
            if ce_width > right_subblock_width:
                ce_width = right_subblock_width
                ce_height = ce_width / coef

            pdf.image(label.ce, x=right_subblock_x, y=middle_block_y + half_floor_height + margin_ce_eac, w=ce_width, h=ce_height)

        # 3. Barcode floor (low)
        barcode_y = margin_top + 2 * floor_height + 2 * floor_margin
        if label.barcode is not None:
            barcode_height = floor_height
            coef = 1.417     # =  width / height
            barcode_width = floor_height * coef
            if barcode_width > graph_block_width:
                barcode_width = graph_block_width
                barcode_height = floor_height / coef
            x_centered = x_graphs + (graph_block_width - barcode_width) / 2
            pdf.image(label.barcode, x=x_centered, y=barcode_y, w=barcode_width, h=barcode_height)

        # SAVE LABEL
        filename = f"{label.num}_{label.model}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        pdf.output(output_path)
        logger.info(f"PDF saved: {output_path}")

    def create_7x5(self, label: Label):
        # Размер страницы 7 см по ширине и 5 см по высоте (альбомная ориентация)
        page_width, page_height = 70, 50  # мм

        # Исходный размер A4 ландшафт (ширина x высота) для масштабирования
        a4_width, a4_height = 297, 210  # мм

        scale_x = page_width / a4_width
        scale_y = page_height / a4_height
        scale = min(scale_x, scale_y)  # пропорциональное масштабирование

        pdf = FPDF(unit='mm', format=(page_width, page_height))
        pdf.add_page()

        _init_fonts(pdf)  # инициализация шрифтов

        scale = 0.185

        margin_left = 12 * scale
        margin_right = 10 * scale
        margin_top = 16 * scale
        margin_bottom = 0  # можно скорректировать при необходимости
        margin_text_graph = 6 * scale

        available_width = page_width - margin_left - margin_right
        available_height = page_height - margin_top - margin_bottom
        graph_block_width = available_width * 0.33 - margin_text_graph / 2
        text_block_width = available_width - graph_block_width - margin_text_graph / 2

        y = margin_top
        paragraph = 4 * scale

        # --- ТЕКСТОВЫЙ БЛОК ---

        # model
        size = 8
        line_height = 3
        pdf.set_font("ArialTTF", "B", size)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, label.model.upper())
        y = pdf.get_y() + paragraph

        # category
        size = 7
        line_height = 3
        pdf.set_font("ArialTTF", "B", size)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, label.category)
        y = pdf.get_y() + paragraph

        # description
        size = 3
        line_height = 1.5
        pdf.set_font("ArialTTF", "", size)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, label.description)
        y = pdf.get_y() + 2 * paragraph

        size = 3
        line_height = 1.5
        pdf.set_font("ArialTTF", "", size)

        # expiry and country
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, label.info_block, markdown=True)
        y = pdf.get_y() + paragraph

        # certification
        if label.certification:
            pdf.set_xy(margin_left, y)
            pdf.multi_cell(text_block_width, line_height, label.certification, markdown=True)
            y = pdf.get_y() + paragraph
        else:
            y = pdf.get_y() + 6 * paragraph

        # importer/vendor
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, f"**Импортёр / продавец:** {label.importer_vendor}",
                       markdown=True)
        y = pdf.get_y() + paragraph

        # vendor
        if label.vendor:
            pdf.set_xy(margin_left, y)
            pdf.multi_cell(text_block_width, line_height, f"**Продавец:** {label.vendor}", markdown=True)
            y = pdf.get_y() + paragraph
        else:
            y = pdf.get_y() + 2 * paragraph

        # manufacturer
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, f"**Производитель:** {label.manufacturer}", markdown=True)

        # --- ГРАФИЧЕСКИЙ БЛОК ---

        x_graphs = margin_left + text_block_width + margin_text_graph
        floor_margin = 2 * scale
        floor_height = available_height / 3 - 2 * floor_margin

        # logo
        if label.logo is not None:
            size = floor_height
            x_centered = x_graphs + (graph_block_width - size) / 2
            pdf.image(label.logo, x=x_centered, y=margin_top, h=size)

        # middle block (QR, EAC/CE)
        middle_block_y = margin_top + floor_height + floor_margin
        margin_sub = 2 * scale
        subblock_width = (graph_block_width - margin_sub) / 2

        if label.qr is not None:
            qr_size = min(floor_height, subblock_width) * 0.9
            y_centered = middle_block_y + (floor_height - qr_size) / 2
            pdf.image(label.qr, x=x_graphs, y=y_centered, h=qr_size)

        right_subblock_x = x_graphs + subblock_width + margin_sub
        margin_ce_eac = 6 * scale
        half_floor_height = floor_height / 2 - margin_ce_eac
        right_subblock_width = graph_block_width / 2 - margin_ce_eac

        if label.eac is not None:
            coef = 1.152
            eac_height = half_floor_height
            eac_width = eac_height * coef
            if eac_width > right_subblock_width:
                eac_width = right_subblock_width
                eac_height = eac_width / coef
            pdf.image(label.eac, x=right_subblock_x, y=middle_block_y, w=eac_width, h=eac_height)

        if label.ce is not None:
            coef = 1.028
            ce_height = half_floor_height
            ce_width = ce_height * coef
            if ce_width > right_subblock_width:
                ce_width = right_subblock_width
                ce_height = ce_width / coef
            pdf.image(label.ce, x=right_subblock_x, y=middle_block_y + half_floor_height + margin_ce_eac, w=ce_width,
                      h=ce_height)

        # barcode floor
        barcode_y = margin_top + 2 * floor_height + 2 * floor_margin
        if label.barcode is not None:
            barcode_height = floor_height
            coef = 1.417
            barcode_width = floor_height * coef
            if barcode_width > graph_block_width:
                barcode_width = graph_block_width
                barcode_height = floor_height / coef
            x_centered = x_graphs + (graph_block_width - barcode_width) / 2
            pdf.image(label.barcode, x=x_centered, y=barcode_y, w=barcode_width, h=barcode_height)

        # Сохранение
        filename = f"{label.num}_{label.model}_7x5_landscape.pdf"
        output_path = os.path.join(self.output_dir, filename)
        pdf.output(output_path)
        logger.info(f"PDF saved: {output_path}")

    def create_7x5_from_prod(self, product: ProductRaw):
        # Размер страницы 7 см по ширине и 5 см по высоте (альбомная ориентация)
        page_width, page_height = 70, 50  # мм

        # Исходный размер A4 ландшафт (ширина x высота) для масштабирования
        a4_width, a4_height = 297, 210  # мм

        scale_x = page_width / a4_width
        scale_y = page_height / a4_height
        scale = min(scale_x, scale_y)  # пропорциональное масштабирование

        pdf = FPDF(unit='mm', format=(page_width, page_height))
        pdf.add_page()

        _init_fonts(pdf)  # инициализация шрифтов

        scale = 0.185

        margin_left = 12 * scale
        margin_right = 10 * scale
        margin_top = 16 * scale
        margin_bottom = 0  # можно скорректировать при необходимости
        margin_text_graph = 6 * scale

        available_width = page_width - margin_left - margin_right
        available_height = page_height - margin_top - margin_bottom
        graph_block_width = available_width * 0.33 - margin_text_graph / 2
        text_block_width = available_width - graph_block_width - margin_text_graph / 2

        y = margin_top
        paragraph = 4 * scale

        # --- ТЕКСТОВЫЙ БЛОК ---

        # model
        size = 8
        line_height = 3
        pdf.set_font("ArialTTF", "B", size)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, product.model.upper(), align='L')
        y = pdf.get_y() + paragraph

        # category
        size = 7
        line_height = 3
        pdf.set_font("ArialTTF", "B", size)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, product.category)
        y = pdf.get_y() + paragraph

        if product.description:
            # description
            description_text = product.description.capitalize()
            size = 3
            line_height = 1.5
            pdf.set_font("ArialTTF", "", size)
            pdf.set_xy(margin_left, y)
            pdf.multi_cell(text_block_width, line_height, description_text)
            y = pdf.get_y() + 2 * paragraph

        size = 3
        line_height = 1.5
        pdf.set_font("ArialTTF", "", size)

        info = []
        # info block
        if product.expiry:
            exp_text = f"**Срок службы**: {product.expiry}."  # add expiry info in correct format
            info.append(exp_text)

        if product.country:
            country_text = f"**Страна изготовления**: {product.country}"  # added markdown
            info.append(country_text)

        info_text = " ".join(info)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, info_text, markdown=True)
        y = pdf.get_y() + paragraph

        # certification
        if product.certification:
            pdf.set_xy(margin_left, y)
            pdf.multi_cell(text_block_width, line_height, product.certification, markdown=True)
            y = pdf.get_y() + paragraph
        else:
            y = pdf.get_y() + 3 * paragraph

        # importer/vendor
        importer_vendor_text = f"**Импортёр / продавец:** {product.importer_vendor}" \
            if product.manufacturer \
            else f"**Импортёр и Организация, уполномоченная на принятие претензий:**\n{product.importer_vendor}"
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, importer_vendor_text,
                       markdown=True)
        y = pdf.get_y() + paragraph

        # vendor
        if product.vendor:
            pdf.set_xy(margin_left, y)
            pdf.multi_cell(text_block_width, line_height, f"**Продавец:** {product.vendor}", markdown=True)
            y = pdf.get_y() + paragraph
        else:
            y = pdf.get_y() + 2 * paragraph

        # manufacturer
        if product.manufacturer:
            pdf.set_xy(margin_left, y)
            pdf.multi_cell(text_block_width, line_height, f"**Производитель:** {product.manufacturer}", markdown=True)

        # --- ГРАФИЧЕСКИЙ БЛОК ---

        x_graphs = margin_left + text_block_width + margin_text_graph
        floor_margin = 2 * scale
        floor_height = available_height / 3 - 2 * floor_margin

        # logo
        if product.logo:
            size = floor_height
            x_centered = x_graphs + (graph_block_width - size) / 2
            pdf.image(product.logo, x=x_centered, y=margin_top, h=size)

        # middle block (QR, EAC/CE)
        middle_block_y = margin_top + floor_height + floor_margin
        margin_sub = 2 * scale
        subblock_width = (graph_block_width - margin_sub) / 2

        if product.qr:
            qr_size = min(floor_height, subblock_width) * 0.9
            y_centered = middle_block_y + (floor_height - qr_size) / 2
            pdf.image(product.qr, x=x_graphs, y=y_centered, h=qr_size)

        right_subblock_x = x_graphs + subblock_width + margin_sub
        margin_ce_eac = 6 * scale
        half_floor_height = floor_height / 2 - margin_ce_eac
        right_subblock_width = graph_block_width / 2 - margin_ce_eac

        if product.eac:
            coef = 1.152
            eac_height = half_floor_height
            eac_width = eac_height * coef
            if eac_width > right_subblock_width:
                eac_width = right_subblock_width
                eac_height = eac_width / coef
            pdf.image(product.eac, x=right_subblock_x, y=middle_block_y, w=eac_width, h=eac_height)

        if product.ce:
            coef = 1.028
            ce_height = half_floor_height
            ce_width = ce_height * coef
            if ce_width > right_subblock_width:
                ce_width = right_subblock_width
                ce_height = ce_width / coef
            pdf.image(product.ce, x=right_subblock_x, y=middle_block_y + half_floor_height + margin_ce_eac, w=ce_width,
                      h=ce_height)

        # barcode floor
        barcode_y = margin_top + 2 * floor_height + 2 * floor_margin
        if product.barcode:
            barcode_height = floor_height
            coef = 1.417
            barcode_width = floor_height * coef
            if barcode_width > graph_block_width:
                barcode_width = graph_block_width
                barcode_height = floor_height / coef
            x_centered = x_graphs + (graph_block_width - barcode_width) / 2
            pdf.image(product.barcode, x=x_centered, y=barcode_y, w=barcode_width, h=barcode_height)

        # Сохранение
        filename = f"{product.num}_{product.model}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        pdf.output(output_path)
        logger.info(f"PDF saved: {output_path}")


# код для тестирования работы с пдф
# if __name__ == "__main__":
#     from models import Label, Product
#
#     test_num = input("test num = ")
#     # test_num = "1"
#     project = {
#         "project_name": "test",
#         "project_folder": "temp/test",
#         "graphs": "temp/test/graphs",
#         "labels": "temp/test/labels"
#     }
#
#     test_data = {'brand': 'stands&cables',
#                  'model': f'Модель {test_num}',
#                  'category': 'Электронная ударная установка',
#                  'description': 'Цвет: черный\nВ комплекте: адаптер питания, микрофон\nТехнические характеристики: 61 миниклавиша, 16 тембров, 10 ритмов\n'
#                                 'Питание: 220В-240В, адаптер питания (в комплекте)',
#                  'expiry': '3',
#                  'country': 'Китай',
#                 'certification': 'nan',
#                  # 'certification': 'Соответствует требованиям ТР ТС 004/2011 "О безопасности низковольтного оборудования", ТР ТС 020/2011 "Электромагнитная совместимость технических средств", ТР ЕАЭС 037/2016 "Об ограничении применения опасных веществ в изделиях электротехники и радиоэлектроники',
#                  'importer_vendor': 'ООО «Мьюзик лайн» 127474, РФ, г. Москва, Дмитровское шоссе, д. 64. корп. 4, этаж 1, пом. 3, комн. 3.',
#                   'vendor': 'nan',
#
#                   # 'vendor': 'Aroma Music Co., Ltd. China, Aroma Park, Guwu Village, Danshui town, Huiyang District, Huizhou City, Guangdong, 516200', 'ean13': '6959556904536',
#                  'manufacturer': 'Aroma Music Co., Ltd. China, Aroma Park, Guwu Village, Danshui town, Huiyang District, Huizhou City, Guangdong, 516200', 'ean13': '6959556904536',
#                  'eac': '1',
#                  'ce': '1',
#                  'logo': '1',
#                  'instruction': 'https://errors.pydantic.dev/2.11/v/value_error'}
#     # product = Product.from_dict(test_data)
#     # label = Label(prod=product, num="001")
#     # label.prepare_all()
#
#     prod = ProductRaw.from_dict(test_data)
#     prod.num = "001"
#     prod.prepare_all()
#     stamper = Stamper(save_to=TEST_DIR)
#     stamper.create_7x5_from_prod(product=prod)