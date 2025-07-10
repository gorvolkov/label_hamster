import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# папка всех проектов
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# папка, куда загружается Excel-таблица для обработки
XLS_DIR  = os.path.join(BASE_DIR, "xls_files")

# папка с логотипами (потом можно будет положить в Static)
LOGO_DIR = os.path.join(BASE_DIR, "logo")

STATIC_FILES_FOLDER = os.path.join(BASE_DIR, "static")

TEST_DIR = os.path.join(BASE_DIR, "_tests")

# файл изображения маркировки CE
CE_IMAGE = os.path.join(STATIC_FILES_FOLDER, "CE.png")

# файл изображения маркировки EAC
EAC_IMAGE = os.path.join(STATIC_FILES_FOLDER, "EAC.png")

# названия полей во входной Excel-таблице
REQUIRED_DATA_FIELDS = required_fields = {
    "brand",
    "model",
    "category",
    "description",
    "expiry",
    "country",
    "certification",
    "importer_vendor",
    "vendor",
    "manufacturer",
    "ean13",
    "eac",
    "ce",
    "logo",
    "instruction"
}
