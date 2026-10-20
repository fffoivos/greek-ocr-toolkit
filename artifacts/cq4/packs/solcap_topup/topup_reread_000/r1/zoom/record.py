import json,sys
items=[json.loads(l) for l in open('items.jsonl')]
try: answers=[json.loads(l) for l in open('answers.jsonl')]
except FileNotFoundError: answers=[]
for token in sys.argv[1:]:
 b,a=token.split(','); low='?' in token;b=b.replace('?','');a=a.replace('?','')
 names={'s':'smooth','r':'rough','n':'none','u':'unreadable','a':'acute','g':'grave','c':'circumflex'}
 it=items[len(answers)]
 answers.append(dict(item_id=it['item_id'],breathing=next(k for k,v in it['breathing_options'].items() if v==names[b]),accent=next(k for k,v in it['accent_options'].items() if v==names[a]),confidence='low' if low else 'high',note=''))
with open('answers.jsonl','w') as f:
 for a in answers:f.write(json.dumps(a)+'\n')
print(len(answers))
