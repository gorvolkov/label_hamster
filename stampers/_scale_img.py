from PIL import Image


def scale_img(image: str, w_limit: float, h_limit: float) -> tuple[float, float]:
    """
    Resize image preserving proportions

    :param image: path to origin image
    :param w_limit: max possible width in milimmetres
    :param h_limit: max possible heigth in milimmetres
    :returns: tuple with width and height values in milimmetres for resized image
    """

    with Image.open(image) as img:
        w_orig, h_orig = img.size    # get original width and height in pixels
        dpi = img.info.get('dpi', (72, 72))[0]    # get DPI of image

    # convert original width and height in milimmetres
    w_orig_mm = w_orig / dpi * 25.4
    h_orig_mm = h_orig / dpi * 25.4

    # Calculate the scale factors for width and height to fit the limits
    scale_w = w_limit / w_orig_mm
    scale_h = h_limit / h_orig_mm

    # Take the smaller scale if one of sizes of original image is greater than required;
    # otherwise greater scale:
    if w_orig_mm >= w_limit or h_orig_mm >= h_limit:
        scale = min(scale_w,scale_h)
    else:
        scale = max(scale_w,scale_h)

    w_new = w_orig_mm * scale
    h_new = h_orig_mm * scale

    return w_new, h_new




