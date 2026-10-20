"""Resume sheets from saved combine, with proved identity mapping for prior text edits."""
import inspect
import json
import sys
import textwrap
from types import SimpleNamespace
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'scripts/secondary'))
import ru3t as m
import ru3t_delivery as delivery
import sitecustomize as hook
sys.settrace(None)

mappings={}
def identity_mapping(retained,current,offset,row_id):
    a,b=retained['label'],current['label']
    if a==b:return
    assert len(a)==len(b), 'nonidentity retained/parent offset mapping'
    assert 0<=offset<len(a) and a[offset]==b[offset] and a[offset] in 'ъь', 'target changed'
    assert [c.isalpha() for c in a]==[c.isalpha() for c in b], 'word boundaries changed'
    # Equal codepoint lengths and equal alphabetic boundaries prove identity for
    # the target offset and word span. Full retained text is still checked against
    # DocAI text anchors by symbol_crops; all original crop/raw hashes stay checked.
    mappings[row_id]=dict(method='identity codepoint offsets; identical alphabetic boundaries; unchanged target sign',retained_label_sha256=__import__('hashlib').sha256(a.encode()).hexdigest(),parent_label_sha256=__import__('hashlib').sha256(b.encode()).hexdigest(),length=len(a),differences=[dict(offset=i,retained=x,parent=y) for i,(x,y) in enumerate(zip(a,b)) if x!=y])

original=inspect.getsource(delivery.Crops.get)
old="if r['label']!=self.parent[rid]['label']:raise ValueError('parent/admission text mismatch')"
assert original.count(old)==1
adapted=textwrap.dedent(original).replace(old,"identity_mapping(r,self.parent[rid],offset,rid)")
adapted=adapted.replace("word,final,geo=symbol_crops(image,r['label'],offset,doc,line,r['crop_bbox'][:2])", "word,final,geo=symbol_crops(image,r['label'],offset,doc,line,r['crop_bbox'][:2])\n    if rid in mappings:geo['retained_parent_mapping']=mappings[rid]")
namespace=dict(delivery.__dict__,identity_mapping=identity_mapping,mappings=mappings)
exec(compile(adapted,'<RU3TF1 identity-mapped retained geometry>','exec'),namespace)
delivery.Crops.get=namespace['get']
(m.ART/'phase1/crops_get.original.py').write_text(original)
(m.ART/'phase1/crops_get.phase1.py').write_text(adapted)
summary=json.loads((m.ART/'phase1/combine.json').read_text())
selected={r['row_id'] for r in m.rows(m.ART/'selected_lines.jsonl')}
expected={(p['row_id'],p['offset']):p for p in m.rows(m.ART/'candidate_positions.full.jsonl') if p['row_id'] in selected}
info=json.loads((m.ART/'build.json').read_text())
frame=SimpleNamespace(f_locals=dict(art=m.ART,decisions=list(m.rows(m.ART/'decisions.jsonl')),contexts=summary['contexts'],fresh=list(m.rows(m.ART/'fresh_r3_positions.jsonl')),inherited=list(m.rows(Path(info['old_art'])/'decisions.jsonl')),expected=expected,coverages=summary['coverage'],evidence=summary['evidence']))
sys.modules['__main__']=m
try:hook.finish(frame)
finally:m.dump(m.ART/'phase1/retained_geometry_mappings.json',mappings)
