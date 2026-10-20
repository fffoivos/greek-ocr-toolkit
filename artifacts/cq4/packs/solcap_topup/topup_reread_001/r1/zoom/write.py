import json,sys
items=[json.loads(x) for x in open('items.jsonl')]
p='zoom/decisions.json'
try: ds=json.load(open(p))
except FileNotFoundError: ds=[]
for s in sys.argv[1:]:
 b,a,*c=s.split('/')
 ds.append((b,a,c[0] if c else 'high'))
json.dump(ds,open(p,'w'))
with open('answers.jsonl','w') as f:
 for x,(b,a,c) in zip(items,ds):
  f.write(json.dumps(dict(item_id=x['item_id'],breathing=next(k for k,v in x['breathing_options'].items() if v==b),accent=next(k for k,v in x['accent_options'].items() if v==a),confidence=c,note=''))+'\n')
print(len(ds))
