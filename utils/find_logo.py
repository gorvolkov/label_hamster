import os

from config import LOGO_DIR


def find_logo(brand: str, search_in: str, ) -> str:
    """Find logo image by passed brand name"""
    brand_lower = brand.lower()
    for filename in os.listdir(search_in):
        if filename.lower().startswith(brand_lower):
            return os.path.join(search_in, filename)
    raise Exception("No logo was found for this brand")

# test
if __name__ == "__main__":
    from config import LOGO_DIR
    brand = input("Input brand: ")
    logo = find_logo(brand=brand, search_in=LOGO_DIR)
    print(logo)