"""Recover the owner's 153ff82e letter slots from isolated temporary code.

Both old modules are imported from a package outside greekocr. No git writes.
"""
from greekocr.ops.data_root import input_path as _data_input
import importlib, json, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image
from greekocr.labelfix.owner_slots import overlap_slots

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/records/labelfix/spellcheck'
REV='153ff82e'


def main():
    notes=[json.loads(x) for x in (OUT/'owner_notes_db_20261016.jsonl').read_text().splitlines()]
    expectations=[json.loads(x) for x in (OUT/'owner_slot_expectations.jsonl').read_text().splitlines()]
    import gzip
    with gzip.open(_data_input(OUT/'S2_lines.jsonl.gz'),'rt') as f:
        lines={l['line_id']:l for x in f if (l:=json.loads(x))}
    recovered={}
    with tempfile.TemporaryDirectory(prefix='spellcheck-v8-') as tmp:
        pkg=Path(tmp)/'owner_v8'
        for sub in ('','glyphs','labelfix'):
            p=pkg/sub;p.mkdir(exist_ok=True);(p/'__init__.py').write_text('')
        for rel in ('glyphs/components.py','labelfix/ink.py'):
            (pkg/rel).write_bytes(subprocess.check_output(['git','show',f'{REV}:greekocr/{rel}'],cwd=ROOT))
        sys.path.insert(0,tmp)
        old=importlib.import_module('owner_v8.labelfix.ink')
        for n in notes:
            l=lines[n['line_id']]
            with Image.open(l['crop']) as im:
                ci=old.analyse(im)
            letters=sorted((c for c in ci.components if c.role=='letter'),key=lambda c:c.x0)
            recovered[l['line_id']]=[dict(slot=i+1,bbox=[c.x0,c.y0,c.x1,c.y1]) for i,c in enumerate(letters)]
        sys.path.remove(tmp)
    for e in expectations:
        lid=e['line_id']; slots=recovered[lid]
        # Explicit owner numbers stay literal. Four notes identify a glyph/sign
        # rather than a number; their old physical target is recovered by overlap.
        if 'v8_slot' not in e:
            slot=e['slot']
            if e.get('slot_resolution') or lid in ('8b6b0de9-p000007-l0030','2793d64c-p000048-l0004'):
                b=lines[lid]['slots'][slot-1]['bbox']
                slot,_=overlap_slots(b[0],b[2],slots)
            e['v8_slot']=slot
        s=next((s for s in slots if s['slot']==e['v8_slot']),None)
        e.update(slot=e['v8_slot'],v8_revision=REV,v8_x0=s['bbox'][0] if s else None,v8_x1=s['bbox'][2] if s else None)
        e['mapped_slot'],e['overlapping_slots']=overlap_slots(e['v8_x0'],e['v8_x1'],lines[lid]['slots']) if s else (None,[])
    (OUT/'owner_v8_slots.json').write_text(json.dumps(dict(revision=REV,lines=recovered),ensure_ascii=False,indent=2)+'\n')
    (OUT/'owner_slot_expectations.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in expectations))
    print('Pinned',len(expectations),'expectations;',sum(e['mapped_slot']!=e['v8_slot'] for e in expectations),'renumbered;',sum(e['mapped_slot'] is None for e in expectations),'unresolved')


if __name__=='__main__':main()
