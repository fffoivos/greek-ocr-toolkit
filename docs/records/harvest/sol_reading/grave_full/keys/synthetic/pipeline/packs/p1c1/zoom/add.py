import json,sys
items=[json.loads(x) for x in open('items.jsonl')]
a=[json.loads(x) for x in open('answers.jsonl')]
for label in sys.argv[1].split():
 accent={'g':'grave','a':'acute','c':'circumflex','n':'none','u':'unreadable'}[label.rstrip('?')]
 a.append(dict(item_id=items[len(a)]['item_id'],accent=accent,confidence='low' if label.endswith('?') else 'high',note=''))
with open('answers.jsonl','w') as f:
 for t in a:f.write(json.dumps(t)+'\n')
print(len(a))
