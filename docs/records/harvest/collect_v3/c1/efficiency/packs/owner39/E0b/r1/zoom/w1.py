import json,sys
D=sys.argv[1]
def H(b='none',a='none',d='none',s='none'): return {"breathing":b,"accent":a,"diaeresis":d,"subscript":s}
def LH(idxs, **kw): return [dict(index=i, **H()) for i in idxs]
U={"input_tokens":0,"output_tokens":0}
rows=[
 dict(card_id="13dea0c623ebe7ba71d72597",choice="literal",transcription="Ἐκ",anchor_heads=H(b="unknown",a="unknown"),letter_heads=LH([1]),readability="partial",ownership_ok=True,confidence="low",note="mark at top-left of E is cut by the line crop's left edge; shape not decidable (psili/dasia), accent area cut"),
 dict(card_id="0b78a61522cd2e4d03e0d14f",choice="literal",transcription="ἧχι",anchor_heads=H(b="dasia",a="circumflex",s="unknown"),letter_heads=LH([1,2]),readability="readable",ownership_ok=True,confidence="medium",note="dasia (c-shape) under circumflex; dot+stroke below left leg of eta may be subscript iota or ink from line below"),
 dict(card_id="745ee91d5d7378cfbb984bc3",choice="literal",transcription="ὦς",anchor_heads=H(b="psili",a="circumflex"),letter_heads=LH([1]),readability="readable",ownership_ok=True,confidence="medium",note="circumflex fused with breathing into '?' shape; breathing tail descends like the psili elsewhere in line"),
 dict(card_id="e1238dcd63e8514c3e56a178",choice="literal",transcription="εἶλεν",anchor_heads=H(b="psili",a="circumflex"),letter_heads=LH([0,2,3,4]),readability="readable",ownership_ok=True,confidence="medium",note="psili under circumflex on iota"),
 dict(card_id="74a1f3375c2fc3fae490f406",choice="A",anchor_heads=H(),letter_heads=LH([1]),readability="readable",ownership_ok=None,confidence="high",note="capitals, no marks"),
 dict(card_id="5bfb33b6ed179360e55f4a1d",choice="D",anchor_heads=H(),letter_heads=LH([1]),readability="readable",ownership_ok=None,confidence="medium",note="faint low-res capitals; no marks visible left of or above A"),
 dict(card_id="e38d2c80f7335e063c787535",choice="D",anchor_heads=H(),letter_heads=[],readability="readable",ownership_ok=None,confidence="high",note="capital H alone, no marks"),
 dict(card_id="15c133bf67c7e1c0516cf59f",choice="literal",transcription="ἆσσον",anchor_heads=H(b="psili",a="circumflex"),letter_heads=LH([1,2,3,4]),readability="readable",ownership_ok=True,confidence="medium",note="psili under circumflex; breathing tail descends right of its head as other psili in line"),
]
with open(D+'/answers.jsonl','w') as f:
  for r in rows:
    r.setdefault('transcription',None); r['usage']=U
    f.write(json.dumps(r,ensure_ascii=False)+'\n')
