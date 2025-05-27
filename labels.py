#
# Здесь код для проработки этикетки
#
from pypdf import PdfReader

file = f"label_temp/FLIGHT Aviator Mango Baritone.pdf"

reader = PdfReader(file)
page = reader.pages[0]
print(page.extract_text("plain"))

# # extract only text oriented up
# print(page.extract_text(0))
#
# # extract text oriented up and turned left
# print(page.extract_text((0, 90)))
#
# # extract text in a fixed width format that closely adheres to the rendered
# # layout in the source pdf
# print(page.extract_text(extraction_mode="layout"))
#
# # extract text preserving horizontal positioning without excess vertical
# # whitespace (removes blank and "whitespace only" lines)
# print(page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False))
#
# # adjust horizontal spacing
# print(page.extract_text(extraction_mode="layout", layout_mode_scale_weight=1.0))
#
# # exclude (default) or include (as shown below) text rotated w.r.t. the page
# print(page.extract_text(extraction_mode="layout", layout_mode_strip_rotated=False))

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
import io

def fill_pdf_template(template_path, output_path, data):
    # Читаем шаблон
    template = PdfReader(template_path)
    writer = PdfWriter()

    # Создаем слой с данными
    packet = io.BytesIO()
    c = canvas.Canvas(packet)
    c.drawString(100, 500, data["title"])
    # ... добавляем штрих-код и другие элементы
    c.save()

    # Наложение данных на шаблон
    overlay = PdfReader(packet)
    page = template.pages[0]
    page.merge_page(overlay.pages[0])
    writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

fill_pdf_template("template.pdf", "result.pdf", {"title": "Гитара"})
