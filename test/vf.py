from fontTools.ttLib import TTFont
from fontTools.varLib import mutator
from readFont import drawFont
import time

locations = [
  {'wght': 100},
  {'wght': 300},
  {'wght': 400},
  {'wght': 500},
  {'wght': 600},
  {'wght': 700},
  {'wght': 800},
  {'wght': 900},
]

font_map = {}

start = time.time()
variable_font_path = "font/split/Source Han Sans/SourceHanSansSC-Regular.otf"
vfont = TTFont(variable_font_path)
print(vfont)

for location in locations:
  font = mutator.instantiateVariableFont(vfont, location)
  font.save(f'./{location['wght']}.ttf')
  break

print(font_map)
print(vfont)
vfont.close()

print(time.time() - start)
# # drawFont(font, 'uni6BB5')

# for key, val in font_map.items():
#   drawFont(val, 'uni6BB5')

