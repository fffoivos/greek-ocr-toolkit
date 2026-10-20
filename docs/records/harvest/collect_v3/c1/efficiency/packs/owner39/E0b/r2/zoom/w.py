import json,sys
N=lambda i:{"index":i,"breathing":"none","accent":"none","diaeresis":"none","subscript":"none"}
def H(b,a,d="none",s="none"): return {"breathing":b,"accent":a,"diaeresis":d,"subscript":s}
U={"input_tokens":0,"output_tokens":0}
rows=[
dict(card_id="75bf9ba00994af5cc93d40b3",choice="literal",transcription="ἂνδρα",anchor_heads=H("psili","grave"),letter_heads=[N(i) for i in range(1,5)],readability="readable",ownership_ok=True,confidence="low",note="merged blob mark; head top-left comma, right stroke widens down-right (grave-like); psili/grave from ink, low certainty"),
dict(card_id="b976c5ed91d8c8f39e9dce12",choice="literal",transcription="εἰς",anchor_heads=H("psili","none"),letter_heads=[N(0),N(2)],readability="partial",ownership_ok=True,confidence="medium",note="bottom cut; single comma-shaped mark (head top, tail down-left) touching iota; no accent visible"),
dict(card_id="2cde036c0566d23eca89f515",choice="literal",transcription="ᾔνεον,",anchor_heads=H("psili","acute","none","present"),letter_heads=[N(i) for i in range(1,5)],readability="readable",ownership_ok=True,confidence="medium",note="psili+acute above eta; separate iota-shaped stroke below eta read as iota subscript"),
dict(card_id="7aa08f1ceee853024955a82f",choice="literal",transcription="ἂν",anchor_heads=H("psili","grave"),letter_heads=[N(1)],readability="readable",ownership_ok=True,confidence="medium",note="blobby breathing+accent, same glyph as on ἢ in line; right stroke descends rightward (grave); not the flat tilde used for circumflex in this line"),
dict(card_id="fd5f8607ad7985bc169a9fa1",choice="C",anchor_heads=H("none","grave"),letter_heads=[N(0)],readability="partial",ownership_ok=True,confidence="medium",note="degraded scan; wedge thick top-left tapering to bottom-right = grave"),
dict(card_id="dbe936f8cae1d0d4d4c60af5",choice="C",anchor_heads=H("none","none"),letter_heads=[N(i) for i in range(1,9)],readability="readable",ownership_ok=None,confidence="medium",note="all caps, area above letters blank though crop is tight"),
dict(card_id="fa4490efe944a7e2730e5c64",choice="literal",transcription="εἷλκον",anchor_heads=H("dasia","circumflex"),letter_heads=[N(0)]+[N(i) for i in range(2,6)],readability="readable",ownership_ok=True,confidence="medium",note="circumflex arc over breathing; breathing is reversed-comma (tail on left), unlike the ')' psili on εὐναίας in same line -> dasia"),
]
with open('answers.jsonl','w') as f:
    for r in rows:
        r.setdefault("transcription",None); r["usage"]=U
        f.write(json.dumps(r,ensure_ascii=False)+"\n")
