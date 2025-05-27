import requests


def generate_with_orcascan(ean: str, file_name: str, binary: bool = False) -> None:
    """Generate barcode using passing EAN data and download it"""
    host = "https://barcode.orcascan.com"
    output_dir = "barcodes"
    file_format = "svg"  # формат файла, который нам нужен на выходе
    file_path = f"{output_dir}/{file_name}.{file_format}"
    barcode_type = "ean13"  # тип штрих-кода

    response = requests.get(url=f"{host}/?type={barcode_type}&data={ean}&description={file_format.upper()}")

    if response.status_code == 200:
        # если в ответе приходит бинарный файл (может пригодиться, если поменяем формат на .png или еще что-то)
        if binary:
            with open(file_path, 'wb') as file:
                file.write(response.content)  # сохраняем бинарные данные
        # сохраняет ответ как строку в .svg-файл (т.к. по умолчанию svg передается как xml-строка, но как конкретно он передается от orcascan, я пока не выяснил)
        else:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)
    else:
        print("Something went wrong")


if __name__ == "__main__":
    # test
    some_ean_code = "3831120901840"
    generate_with_orcascan(ean=some_ean_code, file_name="test4")