import json,sys
items=[json.loads(x) for x in open('items.jsonl')]
try: rows=[json.loads(x) for x in open('answers.jsonl')]
except FileNotFoundError: rows=[]
for pair in sys.argv[1:]:
 b,a,*low=pair.split('/')
 it=items[len(rows)]
 rows.append(dict(item_id=it['item_id'],breathing=next(k for k,v in it['breathing_options'].items() if v==b),accent=next(k for k,v in it['accent_options'].items() if v==a),confidence='low' if low else 'high',note=''))
with open('answers.jsonl','w') as f:
 for r in rows:f.write(json.dumps(r)+'\n')
print(len(rows))
