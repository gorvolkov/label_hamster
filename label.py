import os
from fpdf import FPDF
from models import MusicInstrument


def create_label_pdf(instrument: MusicInstrument, label_num: str, output_dir: str):
    # адреса к системным шрифтам
    arial_regular = r"C:\Windows\Fonts\arial.ttf"
    arial_bold = r"C:\Windows\Fonts\arialbd.ttf"
    arial_italic = r"C:\Windows\Fonts\ariali.ttf"
    arial_bold_italic = r"C:\Windows\Fonts\arialbi.ttf"

    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()

    # добавляем шрифты
    # убрать uni=True
    # pdf.add_font("ArialTTF", "", arial_regular, uni=True)
    # pdf.add_font("ArialTTF", "B", arial_bold, uni=True)
    # pdf.add_font("ArialTTF", "I", arial_italic, uni=True)
    # pdf.add_font("ArialTTF", "BI", arial_bold_italic, uni=True)

    pdf.add_font("ArialTTF", "", arial_regular)
    pdf.add_font("ArialTTF", "B", arial_bold)
    pdf.add_font("ArialTTF", "I", arial_italic)
    pdf.add_font("ArialTTF", "BI", arial_bold_italic)

    # задаем координаты макета
    margin_left = 10
    margin_right = 10
    right_column_width = 90
    page_width = pdf.w
    text_width = page_width - margin_left - margin_right - right_column_width

    y = 20

    # ТЕКСТОВЫЕ БЛОКИ

    # name: жирный, капсом, размер 40
    pdf.set_font("ArialTTF", "B", 40)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_width, 10, instrument.name.upper())
    y = pdf.get_y() + 2

    # description: жирный, не капсом, размер 40
    size = 40
    line_height = size * 1.5  # полуторный интервал
    pdf.set_font("ArialTTF", "B", size)
    pdf.set_xy(margin_left, y)
    pdf.multi_cell(text_width, 12, instrument.description)
    y = pdf.get_y() + 4

    # characteristics: обычный, размер 16
    if instrument.characteristics:
        pdf.set_font("ArialTTF", "", 16)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_width, 7, instrument.characteristics)
        y = pdf.get_y() + 4

    # info: обычный, размер 14
    if instrument.info:
        pdf.set_font("ArialTTF", "", 14)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_width, 7, instrument.info)
        y = pdf.get_y() + 4

    # # Importer/vendor: обычный, размер 14
    if instrument.importer_vendor:
        pdf.set_font("ArialTTF", "", 14)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_width, 7, f"Импортер/Продавец: {instrument.importer_vendor}")
        y = pdf.get_y() + 4


    # manufacturer: обычный, размер 14
    if instrument.manufacturer:
        pdf.set_font("ArialTTF", "", 14)
        pdf.set_xy(margin_left, y)
        pdf.multi_cell(text_width, 7, f"Производитель: {instrument.manufacturer}")
        y = pdf.get_y() + 6

    # КАРТИНКИ
    # Справа размещаем logo, eac, barcode вертикально друг над другом
    # x_right = page_width - right_column_width - margin_right
    # y_right = 20
    # image_width = right_column_width
    # image_spacing = 5

    # КАРТИНКИ
    right_column_height = 210 - 20  # 210 мм высота A4 минус 10 мм сверху и снизу
    image_spacing = 5
    x_right = page_width - right_column_width - margin_right

    # Вычисляем высоту каждого изображения примерно равной, с учётом отступов
    image_height = (right_column_height - 2 * image_spacing) / 3

    y_start = 10  # отступ сверху 10 мм

    # Уменьшаем размер логотипа (например, до 50% от image_height)
    logo_height = image_height * 0.5

    # Логотип
    if instrument.logo and os.path.isfile(instrument.logo):
        pdf.image(instrument.logo, x=x_right, y=y_start, h=logo_height)
    else:
        # Если нет логотипа, сдвигаем старт вниз, чтобы не было пустого места
        y_start -= (logo_height + image_spacing)

    # static
    if instrument.eac and os.path.isfile(instrument.eac):
        y_eac = y_start + logo_height + image_spacing if instrument.logo and os.path.isfile(
            instrument.logo) else y_start
        # Рассчитываем ширину static с сохранением пропорций
        # Сначала получаем размеры оригинального изображения
        from PIL import Image
        img = Image.open(instrument.eac)
        img_width, img_height = img.size
        aspect_ratio = img_width / img_height

        # Вычисляем ширину для заданной высоты image_height
        eac_width = image_height * aspect_ratio
        # eac_width = image_height * 0.2

        # Если ширина превышает доступное пространство, уменьшаем
        if eac_width > right_column_width:
            eac_width = right_column_width
            image_height = eac_width / aspect_ratio

        pdf.image(instrument.eac, x=x_right, y=y_eac, h=image_height)

        # static Label - размещаем справа от static
        if instrument.eac_label and os.path.isfile(instrument.eac_label):
            # Рассчитываем положение и размер eac_label
            x_eac_label = x_right + eac_width + 1  # 5 мм отступ от eac
            remaining_width = page_width - margin_right - x_eac_label

            # Получаем размеры eac_label
            img_label = Image.open(instrument.eac_label)
            label_width, label_height = img_label.size
            label_aspect_ratio = label_width / label_height

            # Вычисляем максимально возможную высоту (равную высоте eac)
            max_label_height = image_height
            max_label_width = remaining_width

            # Рассчитываем ширину с сохранением пропорций
            label_width = max_label_height * label_aspect_ratio

            # Если ширина превышает доступное пространство, уменьшаем
            if label_width > max_label_width:
                label_width = max_label_width
                label_height = label_width / label_aspect_ratio

            # Размещаем eac_label
            pdf.image(instrument.eac_label, x=x_eac_label, y=(y_eac - 3), h=label_height)
    else:
        y_eac = y_start + logo_height + image_spacing

    # Штрихкод — ставим под static
    if instrument.barcode and os.path.isfile(instrument.barcode):
        y_barcode = y_eac + image_height + image_spacing
        pdf.image(instrument.barcode, x=x_right, y=y_barcode, h=image_height)

    # Сохраняем PDF
    filename = f"{label_num}_{instrument.name}.pdf"
    filename = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)
    output_path = os.path.join(output_dir, filename)
    pdf.output(output_path)
    print(f"PDF сохранён: {output_path}")



if __name__ == "__main__":
    test_instr_dict = {'brand': 'Aroma', 'name': 'AROMA TDX-N1', 'description': 'Электронная ударная\nустановка', 'characteristics': '7 пэдов (малый, три тома, краш, райд, хай-хэт), бас-бочка облегченная', 'expiry': '3', 'is_expiry': 'ДА', 'country': 'Китай', 'is_country': 'ДА', 'certification': 'Соответствует требованиям ТР ТС 004/2011 "О безопасности\nнизковольтного оборудования", ТР ТС 020/2011 "Электромагнитная\nсовместимость технических средств", ТР ЕАЭС 037/2016\n"Об ограничении применения опасных веществ в изделиях\nэлектротехники и радиоэлектроники', 'is_certification': 'ДА', 'importer_vendor': 'ООО «Мьюзик лайн» 127474, РФ, г. Москва,\nДмитровское шоссе, д. 64. корп. 4, этаж 1, пом. 3, комн. 3.', 'manufacturer': 'Aroma Music Co., Ltd. China, Aroma Park, Guwu Village,\nDanshui town, Huiyang District, Huizhou City, Guangdong, 516200', 'ean13': '6959556904536', 'eac': 'ДА', 'logo': 'ДА'}
    test_instrument = MusicInstrument.from_dict(test_instr_dict)
    test_instrument.barcode = "barcodes/1.png"
    create_label_pdf(instrument=test_instrument, output_dir="labels", label_num="1")
