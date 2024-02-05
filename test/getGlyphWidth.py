from fontTools.ttLib import TTFont

variable_font_path = "font/split/Source Han Sans/SourceHanSansSC-Regular.otf"

font = TTFont(variable_font_path)

glyph = font.getGlyphSet()['dollar']

width = glyph.width

print(width)

