import requests
import json
import re

def fetchSplitRules():
  headers = {
     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
  }
  res = requests.get('https://fonts.googleapis.com/css2?family=Ma%20Shan%20Zheng', headers=headers)

  execIndex = re.compile(r'\[(\d+)\]')
  execUnicode = re.compile('unicode-range: (.*?);')

  rules = {}
  
  if res.status_code == 200:
    idxs = execIndex.findall(res.text)
    unis = execUnicode.findall(res.text)
    # print(idxs)
    # print(len(idxs))
    # print(len(unis))
    for i in range(0, len(idxs)):
      rules[idxs[i]] = unis[i]
    
    rules['latin'] = unis[-1]
  
    # with open('./test.css', 'w', encoding='utf-8') as f:
    #   f.write(res.text)
    
    # with open('./rules.json', 'w', encoding='utf-8') as f:
    #   json.dump(rules, f, ensure_ascii=False, indent=2)
    
  return rules

if __name__ == '__main__':
  fetchSplitRules()
 