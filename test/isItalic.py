normal_font = 'font/split/Roboto/Roboto-Regular.ttf'
italic_font = 'font/small/Roboto Italic/Roboto-LightItalic.ttf'

from fontTools.ttLib import TTFont

def is_font_italic(font_path):
    try:
        font = TTFont(font_path)
        italic_angle = font['post'].italicAngle
        print(italic_angle)
        if italic_angle != 0:
            return True
    except Exception as e:
        print(f"Error processing font: {e}")
    
    # font.saveXML(f'{font_path.replace(r'/', '-')}.xml')
    return False


# print(is_font_italic(normal_font))
# print(is_font_italic(italic_font))

# 阿里巴巴字体
print(is_font_italic('font/split/AlibabaPuHuiTi-2/AlibabaPuHuiTi-2-35-Thin.ttf'))

# 得意黑
print(is_font_italic('font/split/smiley-sans/SmileySans-Regular.ttf'))

# roboto
print(is_font_italic(normal_font))

# transfromed roboto
print(is_font_italic('dist/transform/split/Roboto/250/22.woff2'))