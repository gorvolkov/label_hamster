from fpdf import FPDF

# System Fonts  (Win 10)
FONTS = {
        "arial_regular": r"C:\Windows\Fonts\arial.ttf",
        "arial_bold": r"C:\Windows\Fonts\arialbd.ttf"
}

def _init_fonts(pdf: FPDF):
    pdf.add_font("ArialTTF", "", FONTS["arial_regular"])
    pdf.add_font("ArialTTF", "B", FONTS["arial_bold"])
