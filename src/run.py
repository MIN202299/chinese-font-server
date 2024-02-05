import os
import json
import warnings
from os import path
from fontTools.ttLib import TTFont
from fontTools import subset
from fetchSplitRules import fetchSplitRules
from concurrent.futures import ProcessPoolExecutor, as_completed
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from waitress import serve
from fontTools.varLib import mutator

# https://dcwjoy.oss-cn-hangzhou.aliyuncs.com/transform/
CSS_HOST_URI = 'http://localhost:3000/transform'
HOST='0.0.0.0'
PORT='3000'

OUTPUT_ROOT = path.join(path.abspath('.'), 'dist')
OUTPUT_FONT_CHUNKS = path.join(OUTPUT_ROOT, 'transform')
METADATA_PATH = path.join(OUTPUT_ROOT, 'metadata.json')
RULES_PATH = path.join(OUTPUT_ROOT, 'rules.json')
DIR_FONT_FAMILY_PATH = path.join(OUTPUT_ROOT, 'dir_font_fammily.json')
WEIGHT_CONFIG = [250, 300, 400, 500, 600, 700, 800, 900]

def getFontDetail(dir, fontpath):
  global DIR_FONT_FAMILY_MAP

  font = TTFont(fontpath)
  weight = font['OS/2'].usWeightClass
  global DIR_FONT_FAMILY_MAP
  if dir not in DIR_FONT_FAMILY_MAP:
    DIR_FONT_FAMILY_MAP[dir] = None

  font_family = DIR_FONT_FAMILY_MAP[dir]
  font_name = font['name'].getName(1, 3, 1, 0x409)
  current_font_family = font['name'].getName(16, 3, 1, 0x409)

  isVf = 'fvar' in font

  if current_font_family:
    font_family = current_font_family.string.decode('utf-8').replace('\u0000', '')
    if DIR_FONT_FAMILY_MAP[dir]:
      if len(DIR_FONT_FAMILY_MAP[dir]) > len(font_family):
        DIR_FONT_FAMILY_MAP[dir] = font_family
    else:
      DIR_FONT_FAMILY_MAP[dir] = font_family
  
  if font_name:
    font_name = font_name.string.decode('utf-8').replace('\u0000', '')

  # vf 字体自动生成不同字重的字体
  if isVf:
    global WEIGHT_CONFIG
    for wght in WEIGHT_CONFIG:
      location = { 'wght': wght }
      tran_fontpath = getTransFp(fontpath, wght)
      if not os.path.exists(tran_fontpath):
        print(f'正在转换VF字体: {font_name}, 字重: {wght}')
        _font = mutator.instantiateVariableFont(font, location)
        _font.save(tran_fontpath)
        _font.close()

  font.close()

  return {
    'dir': dir,
    'font_name': font_name,
    'weight': weight,
    'isVf': isVf
  }

def getTransFp(fontpath, wght):
  cur_dir = '/'.join(fontpath.split('/')[:-1])
  return path.join(cur_dir, f'{wght}.ttf')

def getFontList(fontdir):
  fontlist = []
  global SUPPORT_FONT_FORMAT

  for font_family_dir in os.listdir(fontdir):
    for root, subdir, files in os.walk(path.join(fontdir, font_family_dir)):
      for file in files:
        if file.split('.')[-1] in SUPPORT_FONT_FORMAT:
          fontlist.append({
            'dir': font_family_dir,     # 同一字体家族所在的文件夹名字
            'fp': path.join(root, file) # 字体所在路径
          })
  return fontlist

def checkMakeDir(dir):
  if not os.path.exists(dir):
    os.makedirs(dir)

def getCompleleTaskKey():
  tasks = []
  global output
  global SUPPORT_FONT_FORMAT
  for root, sub, files in os.walk(output):
      for file in files:
        if not file.split('.')[-1] == 'woff2':
          continue
        fp = path.join(root, file)
        keypath = fp.split(r'/')[-4:]
        tasks.append('/'.join(keypath))

  return tasks

def getFontMetadata():
  global nrfontlist
  global splitfontlist
  global DIR_FONT_FAMILY_MAP
  global WEIGHT_CONFIG

   # 字体分割过程中的元信息
  metadata = []
  for item in nrfontlist:
    font_detail = getFontDetail(item['dir'], item['fp'])
    if not font_detail['isVf']:
      metadata.append({
        'type': 'normal',
        'fp': item['fp'],
        'weight': font_detail['weight'],
        'isVf': font_detail['isVf'],
        'dir': font_detail['dir'],
        'font_name': font_detail['font_name'],
        'transformed': False
      })

    else:
      for wght in WEIGHT_CONFIG:
        metadata.append({
          'type': 'normal',
          'fp': getTransFp(item['fp'], wght),
          'weight': wght,
          'isVf': False,
          'dir': font_detail['dir'],
          'font_name': font_detail['font_name'],
          'transformed': False
        })
  
  for item in splitfontlist:
    font_detail = getFontDetail(item['dir'], item['fp']) 
    if not font_detail['isVf']:
      metadata.append({
        'type': 'split',
        'fp': item['fp'],
        'weight': font_detail['weight'],
        'isVf': font_detail['isVf'],
        'dir': font_detail['dir'],
        'font_name': font_detail['font_name'],
        'transformed': False
      })
    else:
      for wght in WEIGHT_CONFIG:
        metadata.append({
          'type': 'split',
          'fp': getTransFp(item['fp'], wght),
          'weight': wght,
          'isVf': False,
          'dir': font_detail['dir'],
          'font_name': font_detail['font_name'],
          'transformed': False
        })
      

  # print(metadata)
  for item in metadata:
    if DIR_FONT_FAMILY_MAP[item['dir']]:
      item['font_family'] = DIR_FONT_FAMILY_MAP[item['dir']]
    else:
      item['font_family'] = item['font_name']
    if not item['font_family']:
      warnings.warn(f'找不到 font family: {item["fp"]}')

  return metadata

def splitFont(task):
  subset.main(task)

def getAllFont():
  global metadata
  all_font = {}
  for item in metadata:
    if item['font_family'] not in all_font:
      all_font[item['font_family']] = []
    
    if str(item['weight']) not in all_font[item['font_family']]:
      all_font[item['font_family']].append(str(item['weight']))
  for key, val in all_font.items():
    all_font[key] = ','.join(val)
  return all_font


if __name__ == '__main__':
  # 字体原始文件路径
  fontdir = path.join(path.abspath('.'), 'font')
  nrdir = path.join(fontdir, 'small')
  splitdir = path.join(fontdir, 'split')
  # 字体输入文件路径
  output = OUTPUT_FONT_CHUNKS
  output_vfdir = path.join(output, 'vf')
  output_nrdir = path.join(output, 'small')
  output_splitdir = path.join(output, 'split')
  # 支持的的字体格式
  SUPPORT_FONT_FORMAT = ['ttf', 'otf']
  
  for dir in [output, output_vfdir, output_nrdir, output_splitdir, fontdir, nrdir, splitdir]:
    checkMakeDir(dir)

  nrfontlist = getFontList(nrdir)
  splitfontlist = getFontList(splitdir)

  # 同个一个字体不同字重可能, 字体名字不一样
  # 这里规定一个字体文件夹就为同一个字体, 取最短的字体名字
  DIR_FONT_FAMILY_MAP = dict()
  

  metadata = getFontMetadata()

 # 输出字体元信息
  with open(METADATA_PATH, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

  rules = fetchSplitRules()

  with open(RULES_PATH, 'w', encoding='utf-8') as f:
    json.dump(rules, f, ensure_ascii=False, indent=2)

  with open(DIR_FONT_FAMILY_PATH, 'w', encoding='utf-8') as f:
    json.dump(DIR_FONT_FAMILY_MAP, f, ensure_ascii=False, indent=2)

  all_font = getAllFont()
  with open('FONT_DETAIL.json', 'w', encoding='utf-8') as f:
    json.dump(all_font, f, ensure_ascii=False, indent=2)
  
  complete_task_keys = getCompleleTaskKey()

  tasks = []

  for item in metadata:
    dir = 'split'
    if item['type'] == 'normal':
      dir = 'normal'
      tasks.append([
        item['fp'],
        '--flavor=woff2',
        '--unicodes=*',
        f"--output-file={path.join(output_nrdir, item['font_family'], str(item['weight']), 'all.woff2')}"
      ])
      checkMakeDir(path.join(output_nrdir, item['font_family'], str(item['weight'])))
      continue
    if item['isVf']:
      dir = 'vf'
    for key, val in rules.items():
      # unicode中不能存在空格
      val = val.replace(' ', '')
      keypath = f"{dir}/{item['font_family']}/{item['weight']}/{key}.woff2"
      # 过滤已完成的任务
      if keypath in complete_task_keys:
        continue
      checkMakeDir(path.join(output, f"{dir}/{item['font_family']}/{item['weight']}"))
      tasks.append([
        item['fp'],
        '--flavor=woff2',
        f'--unicodes={val}',
        f'--output-file={path.join(output, keypath)}'
      ])

  
  CPU_NUM = os.cpu_count()

  # 使用进度条
  with Progress(TextColumn("[progress.description]{task.description}"),
      BarColumn(),
      TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
      TimeRemainingColumn(),
      TimeElapsedColumn()) as progress:
    
    p = progress.add_task(description="正在切分字体:", total=len(tasks))

    with ProcessPoolExecutor(max_workers=CPU_NUM) as executor:
      futures = [executor.submit(splitFont, task) for task in tasks]
      for future in as_completed(futures):
        progress.advance(p, advance=1)
    
  
  print('字体切分完成,准备启动Web服务器')
  from server import app
  print(f'服务器已启动测试访问: http://localhost:{PORT}')
  serve(app, host=HOST, port=PORT)

        


