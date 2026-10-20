import json,sys
# args: card_id choice transcription(or -) anchor(b,a,d,s) letterheads("i:b,a,d,s;...") readability ownership confidence note
cid,ch,tr,anc,lh,rd,own,conf,note=sys.argv[1:10]
b,a,d,s=anc.split(',')
L=[]
if lh!='-':
  for item in lh.split(';'):
    i,h=item.split(':'); hb,ha,hd,hs=h.split(',')
    L.append({"index":int(i),"breathing":hb,"accent":ha,"diaeresis":hd,"subscript":hs})
o={"card_id":cid,"choice":ch}
if ch=='literal': o["transcription"]=tr
o.update({"anchor_heads":{"breathing":b,"accent":a,"diaeresis":d,"subscript":s},"letter_heads":L,"readability":rd,
 "ownership_ok":{"true":True,"false":False,"null":None}[own],"confidence":conf,"note":note,"usage":{"input_tokens":0,"output_tokens":0}})
open('answers.jsonl','a').write(json.dumps(o,ensure_ascii=False)+'\n')
