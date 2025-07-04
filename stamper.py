import os
from fpdf import FPDF
from PIL import Image

from models import Label
from logger import logger

# System Fonts panths on Win 10
FONTS = {
        "arial_regular": r"C:\Windows\Fonts\arial.ttf",
        "arial_bold": r"C:\Windows\Fonts\arialbd.ttf",
        "arial_italic": r"C:\Windows\Fonts\ariali.ttf",
        "arial_bold_italic":  r"C:\Windows\Fonts\arialbi.ttf",
}

class Stamper:
    def __init__(self, proj: dict[str, str]):
        self.project = proj


    def create_a4(self, label: Label):
        # create template pdf
        pdf = FPDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()

        # load fonts
        pdf.add_font("ArialTTF", "", FONTS["arial_regular"])
        pdf.add_font("ArialTTF", "B", FONTS["arial_bold"])
        pdf.add_font("ArialTTF", "I", FONTS["arial_italic"])
        pdf.add_font("ArialTTF", "BI", FONTS["arial_bold_italic"])

        # отступы слева и справа
        margin_left = 10
        margin_right = 10

        # ширина правого блока для графических компонентов
        graph_block_width = 100

        # ширина левого блока для текста
        page_width = pdf.w
        text_block_width = page_width - margin_left - margin_right - graph_block_width

        y = 20

        paragraph = 4
        # ТЕКСТОВЫЕ БЛОКИ
        # model
        size, line_height = 36, 12
        pdf.set_font("ArialTTF", "B", size)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, label.model.upper())
        y = pdf.get_y() + paragraph

        # category
        size, line_height = 28, 14
        pdf.set_font("ArialTTF", "B", size)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, label.category)
        y = pdf.get_y() + paragraph

        # description
        size, line_height = 16, 6

        pdf.set_font("ArialTTF", "", size)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, label.description)
        y = pdf.get_y() + paragraph

        # info
        size, line_height = 14, 6
        pdf.set_font("ArialTTF", "", size)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, label.info_block)
        y = pdf.get_y() + paragraph

        # addresses
        size, line_height = 14, 6
        pdf.set_font("ArialTTF", "", size)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_block_width, line_height, label.addresses_block)
        # y = pdf.get_y() + paragraph

        # ГРАФИЧЕСКИЙ БЛОК
        page_height = pdf.h
        # отступы по верху и низу
        margin_top = 10
        margin_bottom = 10
        # Высота доступная для правого блока
        available_height = page_height - margin_top - margin_bottom

        # Делим на три части для трёх подблоков
        block_height = available_height / 3

        x_right = page_width - graph_block_width - margin_right

        # 1. Логотип (если есть)
        if label.logo is not None:
            size = graph_block_width * 0.7

            # Масштабируем логотип по ширине graph_block_width и по высоте block_height
            x_centered = x_right + (graph_block_width - size) / 2
            pdf.image(label.logo, x=x_centered, y=margin_top, w=size, h=size)

        # 2. Средняя строка (qr слева, eac/ce справа)
        middle_block_y = margin_top + block_height
        qr_size = block_height * 0.8 # квадратный блок по высоте

        if label.qr is not None:
            pdf.image(label.qr, x=x_right, y=middle_block_y, w=qr_size, h=qr_size)

        right_subblock_x = x_right + qr_size + 5
        right_subblock_width = graph_block_width - qr_size - 5

        # Высота для eac и ce делим пополам с отступом
        half_height = (block_height - 5) / 2

        if label.eac is not None:
            # для отладки, убрать потом
            coef = 0.8
            pdf.image(label.eac, x=right_subblock_x, y=middle_block_y, w=right_subblock_width * coef, h=half_height * coef)

        if label.ce is not None:
            coef = 0.8
            pdf.image(label.ce, x=right_subblock_x, y=middle_block_y + half_height + 5, w=right_subblock_width * coef,
                      h=half_height * coef)

        # 3. Штрихкод (если есть)
        barcode_y = margin_top + 2 * block_height
        if label.barcode is not None:
            pdf.image(label.barcode, x=x_right, y=barcode_y, w=graph_block_width, h=block_height)


        # Сохраняем PDF
        filename = f"{label.num}_{label.model}.pdf"
        output_path = os.path.join(self.project["labels"], filename)
        pdf.output(output_path)
        logger.debug(f"PDF saved: {output_path}")


# отладка
if __name__ == "__main__":
    from models import Label, Product

    test_num = input("test num = ")
    project = {
        "project_name": "test",
        "project_folder": "projects/test",
        "graphs": "projects/test/graphs",
        "labels": "projects/test/labels"
    }

    test_data = {'brand': 'golden cup', 'model': f'TEST{test_num} TDX-N1', 'category': 'Электронная ударная\nустановка', 'description': '7 пэдов (малый, три тома, краш, райд, хай-хэт), бас-бочка облегченная', 'expiry': '3', 'country': 'Китай', 'certification': 'Соответствует требованиям ТР ТС 004/2011 "О безопасности\nнизковольтного оборудования", ТР ТС 020/2011 "Электромагнитная\nсовместимость технических средств", ТР ЕАЭС 037/2016\n"Об ограничении применения опасных веществ в изделиях\nэлектротехники и радиоэлектроники', 'importer_vendor': 'ООО «Мьюзик лайн» 127474, РФ, г. Москва,\nДмитровское шоссе, д. 64. корп. 4, этаж 1, пом. 3, комн. 3.', 'vendor': 'nan', 'manufacturer': 'Aroma Music Co., Ltd. China, Aroma Park, Guwu Village,\nDanshui town, Huiyang District, Huizhou City, Guangdong, 516200', 'ean13': '6959556904536', 'eac': 'nan', 'ce': 'nan', 'logo': '1', 'instruction': 'nan'}
    product = Product.from_dict(test_data)
    label = Label(prod=product, proj=project, num="001")
    label.prepare_all()
    stamper = Stamper(proj=project)
    stamper.create_a4(label)