from fontTools.ttLib import TTFont
from os import path
from fontTools.pens.freetypePen import FreeTypePen
from fontTools.misc.transform import Offset

def drawFont(font, uni: str) -> None:
  pen = FreeTypePen(None) # 实例化Pen子类
  glyph = font.getGlyphSet()[uni] # 通过字形名称选择某一字形对象
  print(glyph)
  glyph.draw(pen)
  width, ascender, descender = glyph.width, font['OS/2'].usWinAscent, -font['OS/2'].usWinDescent # 获取字形的宽度和上沿以及下沿
  height = ascender - descender # 利用上沿和下沿计算字形高度
  pen.show(width=width, height=height, transform=Offset(0, -descender)) # 显示以及矫正

# 用来检查字体支持的语言
def getLangId():
  langIDs = set()
  for record in font['name'].names:
    langIDs.add(record.langID)
  print(langIDs)    

  
if __name__=="__main__":
  notosans = 'font/split/Source Han Sans/regular.otf'
  alibaba = 'font/split/Alibaba Pu Hui Ti 2/regular.ttf'
  roboto = '/Users/duanduan/min/font-server/font/split/Roboto/Roboto-Regular.ttf'
  genVfont = '100.otf'

  fontpath = path.join(path.abspath('.'), roboto)

  print(fontpath)

  font = TTFont('/Users/duanduan/min/font-server/font/split/Source Han Sans/SourceHanSansSC-Regular.otf')

  print("=== 字体信息 ===")
  print(f"字体格式: {font.sfntVersion}")
  print(f"字体名称: {font['name'].getName(1, 3, 1, 1033).string.decode('utf-8')}")
  print(f"字体全名: {font['name'].getName(4, 3, 1, 1033).string.decode('utf-8')}")
  print(f"字体家族: {font['name'].getName(1, 3, 1, 1033)}")
  print(f"字体风格: {font['name'].getName(2, 1, 1, 1033)}")
  print(f"字体权重: {font['OS/2'].usWeightClass}")
  # print(font)
  # print(font['name'])
  # font.saveXML('font.xml')

  # pen = FreeTypePen(None) # 实例化Pen子类
  # font = TTFont("Resources/simsun.ttf") # 实例化TTFont
  # glyph = font.getGlyphSet()["uni70E0"] # 通过字形名称选择某一字形对象
  # glyph.draw(pen) # “画”出字形轮廓
  # width, ascender, descender = glyph.width, font['OS/2'].usWinAscent, -font['OS/2'].usWinDescent # 获取字形的宽度和上沿以及下沿
  # height = ascender - descender # 利用上沿和下沿计算字形高度
  # pen.show(width=width, height=height, transform=Offset(0, -descender)) # 显示以及矫正
  # drawFont(font, "dollar")
  # getLangId()
  print(f'是否是VF字体: {'fvar' in font}')
  font.close()