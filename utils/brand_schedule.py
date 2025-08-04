import os
from config import LOGO_DIR

def get_brand_schedule():
    """Collect all brand names in logo dir"""

    brands = []

    for filename in os.listdir(LOGO_DIR):
        brand = filename.split(".")[0].capitalize()
        brands.append(brand)

    return brands


if __name__ == "__main__":
    brands = get_brand_schedule()
    print(brands)