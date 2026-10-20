import json,sys
items=[json.loads(x) for x in open('items.jsonl')]
try: answers=[json.loads(x) for x in open('answers.jsonl')]
except FileNotFoundError: answers=[]
for token in sys.argv[1:]:
 b,a=token.split(','); low='?' in a or '?' in b;b=b.replace('?','');a=a.replace('?','')
 b={'n':'none','s':'smooth','r':'rough','u':'unreadable'}[b];a={'n':'none','a':'acute','g':'grave','c':'circumflex','u':'unreadable'}[a]
 it=items[len(answers)];answers.append(dict(item_id=it['item_id'],breathing=next(k for k,v in it['breathing_options'].items() if v==b),accent=next(k for k,v in it['accent_options'].items() if v==a),confidence='low' if low else 'high',note=''))
with open('answers.jsonl','w') as f:
 for x in answers:f.write(json.dumps(x)+'\n')
print(len(answers))
