import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# папка для времменных графических файлов
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# папка, куда распаковываем архив с логотипами с Яндекс Диска
LOGO_DOWNLOAD = os.path.join(BASE_DIR, "_logo_download")

# папка с логотипами (потом можно будет положить в Static)
LOGO_DIR = os.path.join(BASE_DIR, "logo")

# папка для тестирования
TEST_DIR = os.path.join(BASE_DIR, "_tests")

STATIC_FILES_FOLDER = os.path.join(BASE_DIR, "static")

# файл изображения маркировки CE
CE_IMAGE = os.path.join(STATIC_FILES_FOLDER, "CE.png")

# файл изображения маркировки EAC
EAC_IMAGE = os.path.join(STATIC_FILES_FOLDER, "EAC.png")
