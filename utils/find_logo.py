import os

def find_logo(brand: str, search_in: str, ) -> str:
    """Find logo image by passed brand name

    First tries to find exact match: 'brand.png'.
    If not found, tries to find files starting with 'brand'.
    """
    brand = brand.lower().strip()
    exact_match = f"{brand}.png"

    # First pass: look for exact match
    for filename in os.listdir(search_in):
        if filename.lower() == exact_match:
            return os.path.join(search_in, filename)

    # Second pass: look for files starting with brand
    for filename in os.listdir(search_in):
        if filename.lower().startswith(brand):
            return os.path.join(search_in, filename)

    raise Exception("No logo was found for this brand")

# test
if __name__ == "__main__":
    from config import LOGO_DIR
    brand = input("Input brand: ")
    logo = find_logo(brand=brand, search_in=LOGO_DIR)
    print(logo)