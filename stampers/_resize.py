from PIL import Image

def resize(image: str, w: int | float, h: int | float, units: str="mm") -> None:
    """
    Resize image with proportions preserve

    :param image: path to origin image
    :param w: required width
    :param h: required heigth
    :param units: required units in pixels or mm
    :return:
    """
    units_req = ["px", "mm"]

    if units not in units_req:
        raise ValueError("Unknown units value")

    with Image.open(image) as img:
        orig_width, orig_height = img.size    # pixels

        if units == "mm":
            dpi = img.info.get('dpi', (72, 72))[0]    # convert to mm
            orig_width_mm = orig_width / dpi * 25.4
            orig_height_mm = orig_height / dpi * 25.4

        aspect_ratio = ...

        # resize_coef = bc_height / orig_height_mm
        # bc_width = orig_width_mm * resize_coef
        #
        #
