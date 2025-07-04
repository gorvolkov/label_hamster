import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# папка всех проектов
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")

# папка, куда загружается Excel-таблица для обработки
XLS_DIR  = os.path.join(BASE_DIR, "xls_files")

# папка с логотипами (потом можно будет положить в Static)
_LOGO_DIR_NAME = "logo_simple"
LOGO_DIR = os.path.join(BASE_DIR, _LOGO_DIR_NAME)

STATIC_FILES_FOLDER = os.path.join(BASE_DIR, "static")

# файл изображения маркировки CE
_CE_FILE_NAME = "CE.png"
CE_IMAGE = os.path.join(STATIC_FILES_FOLDER, _CE_FILE_NAME)

# файл изображения маркировки EAC
_EAC_FILE_NAME = "EAC.png"
EAC_IMAGE = os.path.join(STATIC_FILES_FOLDER, _EAC_FILE_NAME)

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
    "logo_simple",
    "instruction"
}

QR_DUMMY = os.path.join(STATIC_FILES_FOLDER, "QR_DUMMY.png")

print(EAC_IMAGE)