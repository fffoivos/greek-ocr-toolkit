"""RU3T-D offline issuance from frozen decision ledgers; no glyph readers."""
import collections
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import unicodedata as ud

ROOT = Path(__file__).resolve().parents[2]
COORD = Path.home()/'Projects/greek-page-ocr-wave1c'
SOURCE = Path.home()/'Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl'
OUT = ROOT/'artifacts/ru1'
AUDIT = OUT/'ru3td'

def guard(event, args):
    if event.startswith('socket.') or event in {'subprocess.Popen', 'os.system'}:
        raise RuntimeError('RU3TD network/process launch disabled')
    if event == 'open':
        path, mode, flags = args
        writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (isinstance(flags, int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
        if writing and isinstance(path, (str, bytes, os.PathLike)) and '.git' in Path(os.fsdecode(path)).resolve().parts:
            raise RuntimeError('RU3TD .git writes disabled')
sys.addaudithook(guard)

def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rows(p):
    with open(p) as f:return [json.loads(line) for line in f if line.strip()]
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def jsonl(p,x):p.write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in x))

def main():
    AUDIT.mkdir(exist_ok=True)
    raw=rows(SOURCE); original={r['id']:r for r in raw}
    v2={r['id']:r for r in rows(OUT/'ru1_v2_train.jsonl')}
    v3={r['id']:r for r in rows(OUT/'ru1_v3_train.jsonl')}
    assert len(raw)==len(original)==214436 and original.keys()==v2.keys()==v3.keys()
    assert sha(SOURCE)=='5c5429a4736ba41d9ebd85d1da0c5eb49a92f64509e00797bda12b2458227ff3'
    assert sha(OUT/'ru1_v3_train.jsonl')=='e23fcab1a47893e3fd4d59d7fc5a398c770dbfb411e327bea6cffd29503907a2'
    grouped=collections.defaultdict(list); ds=[]
    for wave in ['ru2t','ru3t']:
        path=OUT/wave/'decisions.jsonl'
        for d in rows(path):
            ds.append((wave,d))
            if d['decision'] not in {'edit_hard','hold','hold_uncertain'}:continue
            # Both ledgers were indexed directly against SOURCE.label. Confirm;
            # no normalization or speculative alignment is necessary.
            assert original[d['row_id']]['label'][d['offset']]=='ь'
            grouped[d['row_id']].append(dict(d,provenance=dict(decision_file=str(path.relative_to(ROOT)),decision_file_sha256=sha(path),original_offset=d['offset'],offset_remapped=False)))
    assert len({(d['row_id'],d['offset']) for _,d in ds})==len(ds)
    result=[];verified=[]
    for source in raw:
        i=source['id']; decisions=grouped.get(i,[])
        if not decisions:continue
        edits=[d for d in decisions if d['decision']=='edit_hard']; holds=[d for d in decisions if d['decision'] in {'hold','hold_uncertain'}]
        parent=source['label']; chars=list(parent)
        for d in edits:chars[d['offset']]='ъ'
        text=''.join(chars)
        actual=[j for j,(a,b) in enumerate(zip(parent,text)) if a!=b]
        assert len(parent)==len(text) and set(actual)=={d['offset'] for d in edits}
        assert text==v3[i]['label'] and bool(holds)==(v3[i]['status']=='hold')
        assert all(parent[j]=='ь' and text[j]=='ъ' for j in actual)
        restored=list(text)
        for j in actual:restored[j]='ь'
        assert ''.join(restored).encode('utf-8')==parent.encode('utf-8')
        assert all(text[d['offset']]=='ь' for d in holds)
        result.append(dict(id=i,label=text,label_parent=parent,status='hold' if holds else 'ok',edits=edits,holds=holds))
        verified.append(dict(id=i,offsets=actual,holds=[d['offset'] for d in holds],parent_utf8_sha256=hashlib.sha256(parent.encode()).hexdigest()))
    # Verify all omitted rows inherit exactly, and no actual correction was omitted.
    included={r['id'] for r in result}
    assert all(v3[i]['label']==r['label'] for i,r in original.items() if i not in included)
    target=OUT/'ru1_v3_edits.jsonl';jsonl(target,result)
    assert rows(target)==result
    jsonl(AUDIT/'row_verification.jsonl',verified)
    bindpath=COORD/'out/e4/wave1c_reg/bind_final/substitution.json'
    bind=json.loads(bindpath.read_text());sub={r['row_id'] for r in bind['changes']};unmatched=set(bind['unmatched']['ru1_v3_train'])
    new=[d for wave,d in ds if wave=='ru3t' and d['decision']=='edit_hard']
    excluded=[d for d in new if d['row_id'] not in sub]
    assert all(d['row_id'] in unmatched for d in excluded)
    jsonl(AUDIT/'unmatched_ru3t_edits.jsonl',excluded)
    differences=rows(AUDIT/'bind_differences.jsonl');assert {r['id'] for r in differences}==sub
    rust=(COORD/'factory/src/codec.rs').read_text();block=re.search(r'let c = match c \{(.*?)other => other,',rust,re.S)[1];folds={}
    for line in block.splitlines():
        if '=>' not in line:continue
        left,right=line.split('=>',1);dest=re.search(r"'\\u\{([0-9a-fA-F]+)\}'",right)
        for h in re.findall(r"'\\u\{([0-9a-fA-F]+)\}'",left):folds[chr(int(h,16))]=chr(int(dest[1],16)) if dest else ''
    oldnorm=lambda t:' '.join(''.join(folds.get(c,c) for c in ud.normalize('NFD',t)).split())
    categories=collections.Counter();patterns=collections.Counter();newids={d['row_id'] for d in new}
    for r in differences:
        assert r['raw_import']==original[r['id']]['label']
        assert oldnorm(r['raw_import'])==r['control_decoded']
        if r['id'] in newids:continue
        kinds=set()
        for a,b in r['patterns']:
            kind='RU2T ь→ъ' if (a,b)==('ь','ъ') else 'apostrophe restoration' if set(a+b)<={"'",'᾽','᾿'} else 'spacing tonos restoration'
            kinds.add(kind);patterns[a,b]+=1
        categories[' + '.join(sorted(kinds))]+=1
    coordpath=COORD/'out/e4/wave1c_reg2/inputs/releases/ru1_v3_edits.jsonl'
    comparison=dict(path=str(coordpath),found=coordpath.is_file())
    if coordpath.is_file():
        cr=rows(coordpath);cm={r['id']:r for r in cr};ours={r['id']:r for r in result}
        comparison.update(sha256=sha(coordpath),byte_identical=sha(coordpath)==sha(target),rows=len(cr),common_ids=len(cm.keys()&ours.keys()),labels_equal_on_common_ids=all(cm[i]['label']==ours[i]['label'] for i in cm.keys()&ours.keys()),only_ours=sorted(ours.keys()-cm.keys()),only_coordinator=sorted(cm.keys()-ours.keys()),edited_row_ids_identical=set(cm)=={r['id'] for r in result if r['edits']})
        assert comparison['labels_equal_on_common_ids'] and comparison['edited_row_ids_identical']
    counts=dict(rows=len(result),edited_rows=sum(bool(r['edits']) for r in result),edits=sum(len(r['edits']) for r in result),hold_rows=sum(bool(r['holds']) for r in result),hold_positions=sum(len(r['holds']) for r in result),hold_only_rows=sum(bool(r['holds']) and not r['edits'] for r in result),edited_and_hold_rows=sum(bool(r['holds']) and bool(r['edits']) for r in result))
    manifest=dict(version='ru1_v3_edits',parent=dict(version='google_raw_v2_import',path=str(SOURCE),sha256=sha(SOURCE),text_field='label'),output=dict(path=str(target),sha256=sha(target)),counts=counts,offset_unit='zero-based Python Unicode code point index in exact import label',offsets_remapped=0,policy='Sparse exact-import overlay: only decided ь→ъ edits and explicit holds; all uncovered IDs inherit exact parent text.',inputs={str(p):sha(p) for p in [SOURCE,OUT/'ru1_v2_train.jsonl',OUT/'ru1_v3_train.jsonl',OUT/'ru2t/decisions.jsonl',OUT/'ru3t/decisions.jsonl',bindpath,AUDIT/'bind_differences.jsonl',COORD/'out/e4/wave1c_reg/pools_projection.json.gz',COORD/'codec/v2.json',COORD/'factory/src/codec.rs',Path(__file__)]})
    dump(OUT/'ru1_v3_edits_manifest.json',manifest);target.with_suffix('.sha256').write_text(sha(target)+'  '+target.name+'\n')
    regpath=ROOT/'docs/labelfix/lqb/versions.json';reg=json.loads(regpath.read_text());before=copy.deepcopy(reg)
    reg['versions']['google_raw_v2_import']=dict(path=str(SOURCE),sha256=sha(SOURCE),parent=None,text_field='label',id_field='id',status='local',population=dict(rows=len(raw)),read='Exact import label bytes, no normalization or field fallback')
    reg['versions']['ru1_v3_edits']=dict(path=str(target),sha256=sha(target),parent='google_raw_v2_import',overlay=True,text_field='label',id_field='id',status='local',population=dict(rows=len(raw),overlay_rows=len(result),**{k:v for k,v in counts.items() if k!='rows'}),read='Exact id overlay label; otherwise exact google_raw_v2_import.label; holds retain parent characters',manifest=str(OUT/'ru1_v3_edits_manifest.json'))
    reg['versions']['ru1_v3_train'].update(status='superseded',superseded_by='ru1_v3_edits',supersession_reason='Full inherited train stream replaces factory labels outside corrections; use exact-import sparse overlay.')
    if reg!=before:
        dump(AUDIT/'versions_before.json',before);dump(regpath,reg)
    receipt=dict(status='READY',counts=counts,sha256=sha(target),inherited_diffs=sum(categories.values()),inherited_by_kind=dict(categories),inherited_patterns=[dict(before=a,after=b,spans=n) for (a,b),n in patterns.items()],new_ru3t_edits=len(new),bind_ru3t_edits=len(new)-len(excluded),unmatched_ru3t_edits=len(excluded),unmatched_ru3t_rows=len({d['row_id'] for d in excluded}),coordinator=comparison,validation=dict(all_output_rows_diff_exactly_listed_edits=True,all_parent_utf8_bytes_recovered=True,all_omitted_rows_inherit_exact_import=True,all_hold_characters_unchanged=True,all_bind_controls_equal_v1_encoded_import=True,no_duplicate_decision_positions=True,lqb_registered=True),constraints=dict(network=False,new_readings=False,browser=False,computer_use=False,git_writes=False),registry_sha256=sha(regpath),manifest_sha256=sha(OUT/'ru1_v3_edits_manifest.json'))
    dump(AUDIT/'RU3TD_RECEIPT.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k not in {'coordinator','inherited_patterns'}},ensure_ascii=False))
if __name__=='__main__':main()
