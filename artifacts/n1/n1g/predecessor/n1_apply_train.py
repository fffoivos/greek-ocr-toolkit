"""Gate-protected complete collection-v2 numeric overlay. Never run before gate.

Exact digit localization is optional via a crop/parent-bound geometry sidecar
(or a row's DocAI document). Missing localization yields unsure, never a guess.
All measurements are recomputed from the crop with the existing renderer.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from greekocr.numerics.ink_rule import load_rule,decide,sha
from greekocr.numerics.line_complete import enumerate_slots
from n1r_fit import jsonl,write
from n1t_packs import rows


def label_sha(text):return hashlib.sha256(text.encode()).hexdigest()


def authorize_gate(gate,rule):
    if (gate.get('schema')!='n1-locked-gate-v1' or not gate.get('passed') or
        gate.get('rule_hash')!=rule['rule_hash'] or gate.get('unresolved') or
        gate.get('raised_predicted',0)<=0 or gate.get('raised_truth',0)<=0 or
        gate.get('raised_precision',0) is None or gate['raised_precision']<.99 or
        gate.get('false_range_edits')!=0):
        raise ValueError('matching non-vacuous locked gate must pass before training application')


def apply_rows(data,rule,gate,crop_root,geometry=None):
    """Pure result assembly; only temporary renders. Registry is written by run()."""
    authorize_gate(gate,rule)
    from PIL import Image
    from greekocr.glyphs.components import line_glyphs
    from greekocr.numerics.slots_geom import locate_slot
    from greekocr.numerics.dash import digit_widths,measure_dash
    from greekocr.numerics.tokens import tokenize
    from n1_render import render
    geometry=geometry or {};results=[];records=[];seen=set()
    with tempfile.TemporaryDirectory(prefix='n1-train-render-') as tmp:
        for row in data:
            lid=row['id']
            if lid in seen:raise ValueError('duplicate training id')
            seen.add(lid)
            if row.get('split','train')!='train':raise ValueError('non-training row')
            text=row['label'];slots=enumerate_slots(dict(id=lid,text=text,label=text))
            line_decisions=[]
            if slots:
                path=Path(row['crop']);path=path if path.is_absolute() else Path(crop_root)/path
                digest=sha(path)
                if row.get('crop_sha256') and row['crop_sha256']!=digest:raise ValueError('crop custody mismatch')
                with Image.open(path) as im:glyphs=line_glyphs(im)
                side=geometry.get(lid)
                if side and (side.get('crop_sha256')!=digest or side.get('parent_label_sha256')!=label_sha(text)):
                    raise ValueError('geometry custody mismatch')
                gs={s['slot_id']:s for s in side['slots']} if side else {}
                if side and (len(gs)!=len(side['slots']) or set(gs)!={s['slot_id'] for s in slots}):raise ValueError('geometry must be line complete')
                doc=row.get('docai_document');widths={}
                if doc:
                    widths={i:digit_widths(dict(row,text=text),t,doc) for i,t in enumerate(tokenize(text))}
                for s in slots:
                    if side:
                        old=gs[s['slot_id']]
                        if any(old[k]!=s[k] for k in ('start','end','glyph')):raise ValueError('geometry offsets differ')
                        s['geometry']=old['geometry'];s['dash']=old.get('digit_widths',{})
                    elif doc:
                        s['geometry']=locate_slot(dict(row,text=text),s,doc,exact_boundary=True)
                        s['dash']=widths[s['token_index']]
                    else:s['geometry']=dict(geom_status='missing',reason='exact_digit_localization_unavailable')
                    if s['geometry']['geom_status']=='ok':
                        g=s['geometry']
                        if g['digit_height']<=0 or g['gap_width']!=g['gap'][1]-g['gap'][0]:raise ValueError('invalid side geometry')
                        s.update(render(path,g,tmp,glyphs=glyphs))
                        s['dash']=measure_dash(s['measurements'],s['dash'])
                    d=decide(s,rule,text)
                    d.update(crop_sha256=digest,parent_label_sha256=label_sha(text))
                    line_decisions.append(d)
            edits=[d['edit'] for d in line_decisions if d['edit']]
            ordered=sorted(edits,key=lambda e:e['start'])
            if any(a['end']>b['start'] for a,b in zip(ordered,ordered[1:])):raise ValueError('overlapping edits')
            label=text
            for e in reversed(ordered):
                if label[e['start']:e['end']]!=e['original']:raise ValueError('edit custody mismatch')
                label=label[:e['start']]+e['replacement']+label[e['end']:]
            tags=[dict(slot_id=d['slot_id'],tag=t) for d in line_decisions for t in d['tags']]
            results.append(dict(id=lid,label=label,parent_label=text,new_label=label,edits=ordered,tags=tags,
                decision_records_ref='n1_v1_train_decisions.jsonl#'+lid,rule_hash=rule['rule_hash']))
            records.extend(line_decisions)
    return results,records


def run(source,output,registry,rule,gate,crop_root,geometry=None):
    authorize_gate(gate,rule)  # before reading crops or creating any outputs
    output=Path(output);registry=Path(registry);source=Path(source)
    decisionpath=output.with_name('n1_v1_train_decisions.jsonl');manifestpath=output.with_name('n1_v1_train_manifest.json')
    if any(p.exists() for p in (output,decisionpath,manifestpath)):raise ValueError('refusing to overwrite train outputs')
    obj=json.loads(registry.read_text());versions=obj['versions']
    if 'n1_v1_train' in versions:raise ValueError('n1_v1_train already registered')
    parent='collection_v2_train';digest=sha(source)
    if parent in versions and (versions[parent]['sha256']!=digest or versions[parent]['path']!=str(source)):
        raise ValueError('registered parent differs')
    data=rows(source)
    results,records=apply_rows(data,rule,gate,crop_root,geometry)
    parent_entry=dict(path=str(source),sha256=digest,parent=None,text_field='label',id_field='id',status='local',
                      population=dict(rows=len(data),definition='complete collection-v2 training labels'))
    output.parent.mkdir(parents=True,exist_ok=True)
    jsonl(output,results);jsonl(decisionpath,records)
    manifest=dict(version='n1_v1_train',rule_hash=rule['rule_hash'],parent=parent_entry,
                  output=dict(path=str(output),sha256=sha(output),rows=len(results)),
                  decisions=dict(path=str(decisionpath),sha256=sha(decisionpath),slots=len(records)),
                  gate=gate,classes=dict(Counter(d['class'] for d in records)),
                  edits=sum(len(r['edits']) for r in results),
                  localization='exact bound geometry or DocAI symbols; unavailable slots retain labels with unsure tag')
    write(manifestpath,manifest)
    versions[parent]=parent_entry
    versions['n1_v1_train']=dict(path=str(output),sha256=sha(output),parent=parent,text_field='label',id_field='id',
        status='local',rule_hash=rule['rule_hash'],manifest=str(manifestpath),
        population=dict(rows=len(results),definition='complete collection-v2 train; numeric ink-rule edits, other labels inherited'))
    # Atomic registry replacement after all artifacts exist; preserve unrelated entries.
    temp=registry.with_name(registry.name+'.n1.tmp')
    with temp.open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
    temp.replace(registry)
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=Path.home()/'Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl')
    p.add_argument('--output',type=Path,default=ROOT/'artifacts/n1/n1_v1_train.jsonl')
    p.add_argument('--registry',type=Path,default=ROOT/'docs/labelfix/lqb/versions.json')
    p.add_argument('--rule',type=Path,default=ROOT/'artifacts/n1/n1r/rule.json')
    p.add_argument('--locked-out',type=Path,default=ROOT/'artifacts/n1/n1e');p.add_argument('--lead',type=Path)
    p.add_argument('--geometry',type=Path);p.add_argument('--crop-root',type=Path,default=Path.home()/'Projects/greek-ocr-toolkit')
    a=p.parse_args();rule=load_rule(a.rule)
    # Recompute the real gate from original packs/answers; never trust a passed flag.
    from n1_gate import score_locked
    gate=score_locked(a.locked_out,a.rule,a.lead);authorize_gate(gate,rule)
    held=json.loads((a.rule.parent/'held_metrics.json').read_text())
    if held['raised_precision'] is None or held['raised_precision']<.99 or not held['raised_predicted']:
        raise ValueError('held-out development precision is not qualified')
    side={r['line_id']:r for r in rows(a.geometry)} if a.geometry else None
    print(json.dumps(run(a.source,a.output,a.registry,rule,gate,a.crop_root,side),ensure_ascii=False))
if __name__=='__main__':main()
