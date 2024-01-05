from flask import Flask, request, make_response, send_file
from flask_cors import CORS
from run import OUTPUT_ROOT, METADATA_PATH, RULES_PATH, OUTPUT_FONT_CHUNKS, CSS_HOST_URI, checkMakeDir
from os import path
import json
import shutil

# clear cache
CACHE_DIR = path.join(OUTPUT_ROOT, 'cache')
checkMakeDir(CACHE_DIR)
shutil.rmtree(CACHE_DIR)
checkMakeDir(CACHE_DIR)

with open(METADATA_PATH, 'r', encoding='utf-8') as f:
  metadata = json.load(f)

with open(RULES_PATH, 'r', encoding='utf-8') as f:
  rules = json.load(f)

app = Flask(__name__)
CORS(app)

@app.route("/sayHello")
def hello_world():
    return "<p>Hello, World!</p>"

# https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@700&display=swap
# https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@200..700&display=swap
@app.route('/css', methods=['GET'])
def get_css():
  font_str = request.args.get('family')
  display_str = request.args.get('display')
  if not display_str:
    display_str = 'swap'

  try:
    font_arr = font_str.split(':wght@')
    font_family = None
    weight_str = None

    if len(font_arr) == 2:
      font_family = font_arr[0]
      weight_str = font_arr[1]
    elif len(font_arr) == 1:
      font_family = font_arr[0]
    else:
      return send_not_found()
    
    min_weight = 0
    max_weight = 20000
    
    if weight_str:
      weight_arr = weight_str.replace('..', ',').split(',')
      _min = 0
      _max = 0
      first = True
      for weight in weight_arr:
        weight = int(weight)
        if first:
          _min = weight
          _max = weight
          first = False
        if weight < _min:
          _min = weight
        if weight > _max:
          _max = weight
      min_weight = _min
      max_weight = _max

    filter_fonts = get_filter_font(font_family, min_weight, max_weight)

    if len(filter_fonts) == 0:
      return send_not_found()
    cache_css_path = path.join(CACHE_DIR, f'{font_family}_{min_weight}_{max_weight}_{display_str}.css')
    if path.exists(cache_css_path):
      with open(cache_css_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
      return send_css(''.join(lines))
    else:
      lines = gen_css(filter_fonts, cache_css_path, display_str)
      return send_css(''.join(lines))

  except Exception as err:
    print(err)
    # return send_not_found()
  return send_not_found()

@app.route('/transform/<path:filename>')
def handle_static(filename):
  try:
    # 使用 send_file 函数代理静态资源
    filename_uri = filename.replace('%20', ' ')
    return send_file(path.join(OUTPUT_FONT_CHUNKS, filename_uri), 'font/woff2')
  except Exception as e:
    print(filename_uri)
    return f"Error proxying static file: {e}", 500

def send_not_found():
  # not_found_path = path.join(OUTPUT_ROOT, 'cache', 'not_found.css')
  # if not path.exists(not_found_path):
  #   with open(not_found_path, 'w', encoding='utf-8') as f:
  #     f.write("""/* not found */ \n""")
  res = make_response("""/* not found */ \n""")
  res.headers['Content-Type'] = 'text/css;charset=utf-8'
  return res

def get_filter_font(font_family, min_weight, max_weight):
  global metadata
  fonts = []
  for item in metadata:
    if item['font_family'] == font_family and item['weight'] >= min_weight and item['weight'] <= max_weight:
      fonts.append(item)
  return fonts

def send_css(css: str):
  res = make_response(css)
  res.headers['Content-Type'] = 'text/css;charset=utf-8'
  return res

def gen_css(fonts, cache_css_path, display='swap'):
  global rules
  csses = []
  for font in fonts:
    dir = 'split'
    if font['type'] == 'normal':
      dir = 'small'
    if font['isVf']:
      dir = 'vf'

    keypath = f'{dir}/{font['font_family']}/{font['weight']}'
    url_keypath = keypath.replace(' ', '%20')

    if dir == 'small':
      rules2 = {
        'all': 'U+0000-U+FFFF'
      }

    else:
      rules2 = rules
    for key,val in rules2.items():

      css = f"""\
/* [{key}] */
""" + """\
@font-face {
  """ + f"""font-family: '{font['font_family']}';
  font-style: normal;
  font-weight: {font['weight']};
  src: url({CSS_HOST_URI}/{url_keypath}/{key}.woff2) format('woff2');
  unicode-range: {val};
  display: {display};
""" + "}\n"
      csses.append(css)
  with open(cache_css_path, 'w', encoding='utf-8') as f:
    f.writelines(csses)
  return csses

if __name__ == '__main__':
  # from waitress import serve
  # serve(app, host='0.0.0.0', port=3000)
  
  CSS_HOST_URI = 'http://localhost:3000/transform'

  app.run(host='0.0.0.0', port=3000, debug=True)