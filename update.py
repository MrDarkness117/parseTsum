import json

with open('{}.json', 'r+', encoding='utf-8') as t:
    info = json.load(t)
    json.dump(info, t, ensure_ascii=False, indent=4)
    t.close()
