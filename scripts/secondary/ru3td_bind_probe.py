"""Read-only pool decoding and import comparison; writes local audit ledger only."""
from greekocr.ops.data_root import input_path as _data_input
from ru3td_edits import guard
import json,gzip,re,unicodedata as u,collections,difflib,pathlib
R=pathlib.Path('/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-wave1c')
a={r['id']:r for r in map(json.loads,open('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl'))}
b={r['id']:r for r in map(json.loads,open(_data_input('artifacts/ru1/ru1_v3_train.jsonl')))}
s=json.load(open(R/'out/e4/wave1c_reg/bind_final/substitution.json'));changed={r['row_id'] for r in s['changes']}
codec=json.load(open(R/'codec/v2.json'));atoms={x['id']:x['ch'] for x in codec['atoms']};added={x['ch'] for x in codec['atoms'][247:]}
source=(R/'factory/src/codec.rs').read_text();block=re.search(r'let c = match c \{(.*?)other => other,',source,re.S)[1];folds={}
for line in block.splitlines():
 if '=>' not in line:continue
 l,r=line.split('=>',1); dest=re.search(r"'\\u\{([0-9a-fA-F]+)\}'",r)
 for h in re.findall(r"'\\u\{([0-9a-fA-F]+)\}'",l):folds[chr(int(h,16))]=chr(int(dest[1],16)) if dest else ''
def norm(t):return ' '.join(''.join(c if c in added else folds.get(c,c) for c in u.normalize('NFD',t)).split())
p=json.load(gzip.open(R/'out/e4/wave1c_reg/pools_projection.json.gz','rt'))
counts=collections.Counter();patterns=collections.Counter();samples=[];ledger=[]
for group in p['groups']:
 for row in group:
  i=row.get('line_id')
  if i not in changed:continue
  raw=a[i]['label']; final=b[i]['label'];old=''.join(atoms[n] for n in row['label_ids']);new=norm(final)
  ds=[(old[j:k],new[l:m]) for op,j,k,l,m in difflib.SequenceMatcher(None,old,new,autojunk=False).get_opcodes() if op!='equal']
  if raw!=final:cat='RU2T correction' if all(x=='ь' and y=='ъ' for x,y in ds) else 'mixed correction'
  else:cat='apostrophe fold' if all((x,y)==('᾽',"'") for x,y in ds) else 'other inherited'
  counts[cat]+=1;patterns.update(ds)
  ledger.append(dict(id=i,kind=cat,raw_import=raw,control_decoded=old,overlay_encoded=new,patterns=ds,control_equals_encoded_import=old==norm(raw)))
print(counts);print(patterns.most_common(25));print('control==norm(raw)',collections.Counter(x['control_equals_encoded_import'] for x in ledger));print('samples',ledger[:1])
pathlib.Path('artifacts/ru1/ru3td').mkdir(exist_ok=True)
with open('artifacts/ru1/ru3td/bind_differences.jsonl','w') as f:
 for x in ledger:f.write(json.dumps(x,ensure_ascii=False)+'\n')
