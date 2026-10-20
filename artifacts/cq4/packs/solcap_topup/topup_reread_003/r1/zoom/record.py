import json,sys
items=[json.loads(l) for l in open('items.jsonl')]
p='zoom/decisions.json'
try:d=json.load(open(p))
except FileNotFoundError:d=[]
for s in sys.argv[1:]:
 b,a,*c=s.split('/')
 d.append([b,a,c[0] if c else 'high'])
json.dump(d,open(p,'w'))
with open('answers.jsonl','w') as f:
 for x,(b,a,c) in zip(items,d):
  bo=next(k for k,v in x['breathing_options'].items() if v==b);ao=next(k for k,v in x['accent_options'].items() if v==a)
  f.write(json.dumps(dict(item_id=x['item_id'],breathing=bo,accent=ao,confidence=c,note=''))+'\n')
print(len(d))
