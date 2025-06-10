import xml.etree.ElementTree as ET
import cairosvg

def _to_pdf(input: str, output: str):
    cairosvg.svg2pdf(url='input.svg', write_to='output.pdf')


TEST_NUM = 11

input_svg_path = "label_examples/_PROTO.svg"
output_svg_path = f"label_output/test{TEST_NUM}.svg"
barcode_path = "../barcodes/1.png"

ns = {
    'svg': 'http://www.w3.org/2000/svg',
    'xlink': 'http://www.w3.org/1999/xlink'
}

ET.register_namespace('', ns['svg'])
ET.register_namespace('xlink', ns['xlink'])

tree = ET.parse(input_svg_path)
root = tree.getroot()

barcode_rect = root.find('.//svg:rect[@id="barcode"]', ns)

if barcode_rect is not None:
    x = barcode_rect.attrib.get('x', '0')
    y = barcode_rect.attrib.get('y', '0')
    width = barcode_rect.attrib.get('width', '100')
    height = barcode_rect.attrib.get('height', '100')

    image_elem = ET.Element('{http://www.w3.org/2000/svg}image', {
        'id': 'barcode_image',
        'x': x,
        'y': y,
        'width': width,
        'height': height,
        '{http://www.w3.org/1999/xlink}href': barcode_path,
        'href': barcode_path,
        'preserveAspectRatio': 'xMidYMid meet'
    })

    parent_map = {c: p for p in root.iter() for c in p}
    parent = parent_map.get(barcode_rect)
    if parent is not None:
        index = list(parent).index(barcode_rect)
        parent.remove(barcode_rect)
        parent.insert(index, image_elem)
    else:
        print("Не удалось найти родителя для элемента barcode.")
else:
    print("Элемент <rect id='barcode'> не найден.")

tree.write(output_svg_path, encoding='utf-8', xml_declaration=True)
print(f'Файл сохранён: {output_svg_path}')

_to_pdf(f"label_output/test{TEST_NUM}.svg", f"label_output/test{TEST_NUM}.pdf")