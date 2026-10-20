import json,sys
# usage: ans.py idx choice transcription|- anchor(b,a,d,s) letters("i:b,a,d,s;...") readability ownership(true/false/null) confidence note
B={'n':'none','p':'psili','d':'dasia','u':'unknown'}
A={'n':'none','a':'acute','g':'grave','c':'circumflex','u':'unknown'}
D={'n':'none','p':'present','u':'unknown'}
def heads(s):
    b,a,d,sub=s
    return {'breathing':B[b],'accent':A[a],'diaeresis':D[d],'subscript':D[sub]}
idx,choice,tr,anc,lets,read,own,conf,note=sys.argv[1:10]
base='/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/efficiency/packs/owner39/E0a/r1'
cards=[json.loads(l) for l in open(base+'/cards.jsonl')]
c=cards[int(idx)]
lh=[]
if lets!='-':
    for p in lets.split(';'):
        i,h=p.split(':'); d=heads(h); d={'index':int(i),**d}; lh.append(d)
o={'card_id':c['card_id'],'choice':choice}
if choice=='literal': o['transcription']=tr
o.update({'anchor_heads':heads(anc),'letter_heads':lh,'readability':read,
 'ownership_ok':{'true':True,'false':False,'null':None}[own],'confidence':conf,'note':note,
 'usage':{'input_tokens':0,'output_tokens':0}})
n=sum(1 for _ in open(base+'/answers.jsonl')) if __import__('os').path.exists(base+'/answers.jsonl') else 0
assert n==int(idx), f'expected line {n}'
open(base+'/answers.jsonl','a').write(json.dumps(o,ensure_ascii=False)+'\n')
print(json.dumps(o,ensure_ascii=False))
