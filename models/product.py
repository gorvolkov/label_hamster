from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
import re



class Product(BaseModel):
    """
    Class for two tasks:
    1. convert raw values such as 'nan', 'Нет', 'нет' etc. for strict None or False for corresponding fields
    2. validates input data
    """
    # Required fields
    brand: str = Field(..., min_length=1, description="Бренд продукта")
    model: str = Field(..., min_length=1, description="Модель продукта")
    category: str = Field(..., min_length=1, description="Категория продукта")
    description: str = Field(..., min_length=1, description="Описание продукта")
    importer_vendor: str = Field(..., min_length=1, description="Поставщик/импортер")
    ean13: str = Field(..., min_length=13, max_length=13, description="EAN13 код продукта")
    manufacturer: str = Field(..., min_length=1, description="Производитель")

    # Optional fields (None by default)
    vendor: Optional[str] = Field(None, description="Дополнительный поставщик")
    expiry: Optional[str] = Field(None, description="Срок годности/хранения (текст)")
    country: Optional[str] = Field(None, description="Страна производства")
    certification: Optional[str] = Field(None, description="Информация о сертификации")
    instruction: Optional[str] = Field(None, description="Путь/ссылка на инструкцию")

    # Flag fields (Booleans)
    logo: bool = Field(False, description="Наличие логотипа")
    ce: bool = Field(False, description="Наличие CE маркировки")
    eac: bool = Field(False, description="Наличие EAC маркировки")

    @model_validator(mode='before')
    def convert(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Convert negative input values into None for optional fields and False for boolean fields"""
        fields_bool = {'logo', 'ce', 'eac'}
        none_values = {'nan', 'нет'}
        true_values = {'да', '+', '1'}

        # Создаем копию данных и работаем с ней, чтобы не менять исходный словарь
        data_clean = data.copy()

        for k, v in data.items():
            if k in fields_bool:
                # Для булевых полей: если значение не в true_values, ставим False
                data_clean[k] = v.lower() in true_values

            # Для остальных полей: если приходит 'nan' или аналоги, конвертируем в None (если это было обязательное поле, будет выброшена ошибка валидации)
            elif v.lower() in none_values:
                data_clean[k] = None

        return data_clean


    @field_validator('ean13')
    def validate_ean13(cls, v: str):
        """
        Check if passed ean13 is correct
        :param v: ean13 value (string)
        :raises: ValueError if ean13 value isn't correct
        :return: ean13 field value if it's OK
        """
        # check if not 13 digits
        if not (v.isdigit() and len(v) == 13):
            raise ValueError('EAN13 should consist of 13 digits')

        # check sum
        digits = list(map(int, v))
        check_sum = sum(digits[i] if i % 2 == 0 else digits[i] * 3 for i in range(12))
        check_digit = (10 - (check_sum % 10)) % 10
        if digits[-1] != check_digit:
            raise ValueError('Incorrect EAN13 value')
        return v


    @field_validator('instruction')
    def validate_instruction_url(cls, v: Optional[str]) -> Optional[str]:
        """Check if instruction field (if it's not None) is correct URL"""
        if v is None:
            return v
        # Простой regex для проверки http:// или https://
        pattern = re.compile(r'^(https?://)')
        if not pattern.match(v):
            raise ValueError('Instruction must be a valid URL starting with http:// or https://')
        return v

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)



# test
if __name__ == "__main__":
    product_data_1 = {
        "brand": "AwesomeBrand",
        "model": "SuperModel",
        "category": "Electronics",
        "description": "A very useful electronic device.",
        "importer_vendor": "GlobalImportCo",
        "ean13": "4607100342939",  # Корректный EAN13 (без пробелов)
        "vendor": "nan",
        "manufacturer": "TechCorp",
        "logo": "ДА",
        "ce": "nan",
        "eac": "nan",
        "expiry": "12 months",
        "country": "China",
        "certification": "ISO 9001",
        "instruction": "http://example.com/instruction.pdf",
    }
    product_data_2 = {'brand': 'davinci', 'model': 'DAVINCI DCK-142 BK', 'category': 'Синтезатор', 'description': 'Цвет: черный\nВ комплекте: адаптер питания, микрофон\nТехнические характеристики: 61 миниклавиша, 16 тембров, 10 ритмов\nПитание: 220В-240В, адаптер питания (в комплекте) / \nБатарейки: AAx4 шт. (в комплект не входят)', 'expiry': '3', 'country': 'Китай', 'certification': 'Соответствует требованиям ТР ТС 004/2011 "О безопасности\nнизковольтного оборудования", ТР ТС 020/2011 "Электромагнитная\nсовместимость технических средств", ТР ЕАЭС 037/2016\n"Об ограничении применения опасных веществ в изделиях\nэлектротехники и радиоэлектроники', 'importer_vendor': 'ООО «Мьюзик лайн» 127474, РФ, г. Москва,\nДмитровское шоссе, д. 64. корп. 4, этаж 1, пом. 3, комн. 3.', 'vendor': 'ООО «Мьюзик лайн» 127474, РФ, г. Москва,\nДмитровское шоссе, д. 64. корп. 4, этаж 1, пом. 3, комн. 3.', 'manufacturer': 'Aroma Music Co., Ltd. China, Aroma Park, Guwu Village,\nDanshui town, Huiyang District, Huizhou City, Guangdong, 516200', 'ean13': '3831120929622', 'eac': 'nan', 'ce': 'nan', 'logo': 'nan', 'instruction': 'https://example.com'}
    try:
        product = Product.from_dict(product_data_2)
        print(product)
    except ValidationError as e:
        print("Ошибка валидации:")
        print(e)