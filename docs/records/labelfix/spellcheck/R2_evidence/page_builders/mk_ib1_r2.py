import json,sys
d={x['id']:x for x in json.load(open(sys.argv[1]))}
AP="comma-shaped elision mark; glyph identical to psili/koronis, transcribed as U+2019"
R={
0:("A","h",""),1:("C","m",AP),2:("C","m",AP),3:("A","m","space before !, dots letterspaced uniformly"),
4:("B","h","space before !"),5:("B","h","acute on epsilon"),6:("C","m",AP),7:("A","h",""),8:("A","m",AP),
9:("A","h",""),10:("C","m",AP),11:("A","h",""),12:("A","m",AP),13:("A","h",""),14:("B","m",AP),
15:("A","h",""),16:("A","m","three separate periods"),17:("B","h","rough breathing only, no circumflex"),
18:("A","h","acute"),19:("C","m",AP),20:("B","h","space before !"),
21:("other","m","space then long em dash; no candidate has space+em dash","ψηλα —"),
22:("B","h","νἆναι"),23:("A","m",AP),24:("C","m",AP),25:("B","m",AP),26:("A","m","apostrophe printed before δῶ"),
27:("A","h",""),28:("A","m","kappa faded/broken but present"),29:("C","m",AP),30:("A","h","acute"),
31:("B","m",AP),32:("B","h","breathing on rho, no circumflex"),33:("C","m",AP),34:("B","h",""),35:("B","h",""),
36:("A","m",AP),37:("A","m",AP),38:("B","m",AP),39:("C","m","breathing on omicron, diaeresis on iota, no breathing on iota"),
40:("A","m","three periods, letterspaced"),
41:("other","m","second glyph is epsilon-shaped with stray horizontal bar above; sits on baseline with no xi descender","θεαματα"),
42:("A","h",""),43:("A","m",AP),44:("C","m",AP),45:("B","h",""),
46:("B","m","small iota-subscript-like tick printed under alpha"),47:("A","m","stray stroke above is from line above"),
48:("B","m",AP),49:("A","h","comma + em dash, no space"),50:("B","m","γγ; visible gap before !"),51:("A","h",""),
52:("C","m",AP),53:("A","m",AP),54:("A","m","faded ink, letters traceable"),55:("A","h",""),
56:("C","m","bar above epsilon is a stray mark, not a diacritic; letter is epsilon (no descender)"),
57:("A","h",""),58:("A","h",""),59:("C","m",AP+"; initial breathing on Alpha ignored for letters"),60:("A","m",AP),
61:("uncertain","l","vowel between tau and nu faded; faint descender hints eta but cannot be confirmed","στὴν"),
62:("A","m","upsilon not printed; floating accent in its place, no word space"),63:("A","h",""),64:("B","m",AP),
65:("B","h","space before !"),66:("A","m",AP),67:("B","h",""),68:("B","m","comma-shaped, not straight; no U+2019 option"),
69:("B","h","smooth breathing + acute"),70:("B","m",AP),71:("B","m","comma-shaped, not straight; no U+2019 option"),
72:("B","h",""),73:("C","m",AP),74:("A","m",AP),75:("A","h",""),76:("C","m",AP),77:("A","h",""),78:("B","m",AP),
79:("B","m",AP),80:("A","h",""),81:("A","h",""),82:("A","m","space before !, two letterspaced dots"),
83:("A","m","thin space before !"),84:("B","h","mark before A is breathing+accent, not a quote"),85:("A","m",AP),
86:("B","h","breathing printed before capital Alpha"),87:("A","m","eta partly faded"),88:("C","m","comma-shaped; no U+2019 option"),
89:("other","m","space then long em dash","καθαροτερη —"),90:("B","m",AP),91:("B","h",""),92:("B","h","lowercase omicron"),
93:("A","h",""),94:("B","m",AP),95:("B","h","grave"),96:("B","h",""),97:("B","h","space before !"),98:("A","m",AP),
99:("C","m",AP),100:("B","m",AP),101:("A","h",""),102:("B","h",""),103:("A","m",AP),104:("A","h","space before ;"),
105:("A","h","space before !"),106:("A","m","space before !"),107:("A","h",""),108:("A","h",""),109:("A","h",""),
110:("B","m",AP),111:("A","h","space before ;"),112:("A","h",""),113:("C","m",AP),114:("A","m","omicron and iota partly faded"),
115:("A","h",""),116:("A","h",""),117:("A","m","thin space before !"),
118:("other","m","space before ; then em dash","ραχη ;—"),119:("A","m",AP),120:("A","m",AP),121:("C","m",AP),
122:("A","m","first letter is epsilon with breathing, not omicron (misprint)"),123:("B","m",AP),124:("B","h",""),125:("A","m",AP),
126:("B","m",AP),127:("A","m",AP),128:("B","h","space before !"),129:("C","h",""),130:("A","m",AP),131:("B","h",""),
132:("uncertain","l","first glyph faded: visible narrow stroke reads like iota, but omicron also lost its left half, so likely alpha with faded bowl","αποσταμενη"),
133:("B","m",AP),134:("A","h","no dash before word on this line"),135:("B","h","space before !"),
136:("A","h",""),137:("other","m","space then long em dash","βλεπω —"),
138:("other","m","printed apostrophe + final sigma, no epsilon","’ς"),139:("A","m","three periods"),140:("A","h",""),
141:("B","h",""),142:("A","m",AP),143:("other","m","space, em dash, comma","φορα —,"),144:("A","h","space before !"),
145:("B","m","three periods"),146:("B","m","whole word letterspaced; no word break inside ἔλατο (gap before ; also letterspacing)"),
147:("B","h",""),148:("other","m","comma, space, em dash","αγαπη, —"),149:("other","m","printed apostrophe + final sigma","’ς"),
150:("A","m",AP),151:("A","h",""),152:("A","h",""),153:("B","m",AP),154:("A","m","final sigma broken but present"),
155:("uncertain","l","vowel faded; faint descender hints eta but cannot be confirmed","στην"),
156:("B","h","no space before !"),157:("A","h",""),158:("A","m","smooth breathing; note a space is printed before ;"),
159:("B","m",AP),160:("C","m",AP),161:("B","m",AP),162:("A","h",""),163:("B","h","space before ;"),
164:("A","m","iota subscript visible under eta"),165:("B","h","space before ;"),166:("A","h","acute"),167:("A","h",""),
}
C={"h":"high","m":"medium","l":"low"}
assert len(R)==len(d)==168
out=open(sys.argv[2],"w")
for i in range(168):
    k=f"ib_item{i:05d}"; x=d[k]; r=R[i]; ans=r[0]
    printed = r[3] if len(r)>3 else x[ans]
    out.write(json.dumps({"id":k,"answer":ans,"printed":printed,"confidence":C[r[1]],"note":r[2]},ensure_ascii=False)+"\n")
from collections import Counter
print(Counter(v[0] for v in R.values()))
