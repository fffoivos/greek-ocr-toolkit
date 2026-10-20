import json,sys
items=[json.loads(x) for x in open('items.jsonl')]
p='zoom/choices.json'
try: choices=json.load(open(p))
except FileNotFoundError: choices=[]
for s in sys.argv[1:]:
 b,a,*c=s.split('/')
 choices.append((b,a,c[0] if c else 'high'))
json.dump(choices,open(p,'w'))
with open('answers.jsonl','w') as f:
 for it,(b,a,c) in zip(items,choices):
  f.write(json.dumps(dict(item_id=it['item_id'],breathing=next(k for k,v in it['breathing_options'].items() if v==b),accent=next(k for k,v in it['accent_options'].items() if v==a),confidence=c,note=''))+'\n')
print(len(choices))
