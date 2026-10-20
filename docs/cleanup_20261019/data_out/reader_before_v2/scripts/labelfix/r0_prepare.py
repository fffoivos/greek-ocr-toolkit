"""R0a only: offline inventories, frozen splits, cached-span audit and blind cards.

Never scores letters against Google. Never changes runtime code or shared caches.
Run stages explicitly; new CTC inference requires an already frozen local list.
"""
from __future__ import annotations
import argparse
import base64
from collections import Counter, defaultdict
import gzip
import hashlib
import html
import io
import json
import math
import os
from pathlib import Path
import random
import re
import subprocess
import unicodedata as U

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['GIT_OPTIONAL_LOCKS'] = '0'
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[name] = '1'
from PIL import Image
from greekocr.labelfix.ctc_align import Alignment, Recognizer
from greekocr.labelfix.sheet import load_alignments, crop_key
from greekocr.labelfix.validate import load_three_way, DEV_BOOKS, CKPT
from greekocr.labelfix.text import nfd, nfc, clusters
from greekocr.labelfix.candidates import align_chars

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'docs/labelfix/spellcheck'
WORK = OUT/'R0_evidence'
SEED = 20261017
L1 = ROOT.parent/'greek-ocr-toolkit-spellcheck-l1'
M2_BASE = ROOT.parent/'greek-ocr-toolkit-sol-funnel-gr/docs/harvest/blind_checks_v1'
POLY = '\u0313\u0314\u0342\u0345\u0300'
QUOTES = "'’ʼ᾽‘“”«»„\"‟‹›`´"

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def read(path):
    with (gzip.open if str(path).endswith('.gz') else open)(path, 'rt') as f:
        return [json.loads(s) for s in f if s.strip()]

def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n')

def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with (gzip.open if str(path).endswith('.gz') else open)(path, 'wt') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False, allow_nan=False)+'\n')

def bare(text):
    return ''.join(c for c in nfd(text) if not U.category(c).startswith('M'))

def letters(text):
    return ''.join(c for c in bare(text) if c.isalpha())

def docstem(lid):
    return re.sub(r'(?:--n?\d+|-p\d+)-l\d+$', '', lid)

def line_sources():
    return load_three_way(0)

def stratified(rows, n, key):
    """Proportional largest-remainder allocation; stable sort before seeded draw."""
    groups = defaultdict(list)
    for r in rows: groups[key(r)].append(r)
    quotas = {k: int(n*len(v)/len(rows)) for k,v in groups.items()}
    order = sorted(groups, key=lambda k: (-(n*len(groups[k])/len(rows)-quotas[k]), k))
    for k in order[:n-sum(quotas.values())]: quotas[k] += 1
    rng = random.Random(SEED)
    chosen = []
    for k in sorted(groups):
        pool = sorted(groups[k], key=lambda r: r.get('line_id', r.get('id')))
        chosen.extend(rng.sample(pool, quotas[k]))
    return sorted(chosen, key=lambda r: r.get('line_id',r.get('id'))), quotas

def overlap_receipt(rows, other):
    ids = {r['line_id'] for r in rows}
    docs = {r['doc'] for r in rows}
    stems = {docstem(r['line_id']) for r in rows}
    checks = {}
    for name, pool in other.items():
        if name == 'L1_input':
            odocs = set(pool); oids = set(); ostems = {x.split(':',1)[-1] for x in pool}
        else:
            oids = {r['line_id'] for r in pool}; odocs = {r['doc'] for r in pool}
            ostems = {docstem(r['line_id']) for r in pool}
        checks[name] = dict(line_ids=sorted(ids & oids), documents=sorted(docs & odocs),
                            normalized_document_ids=sorted(stems & ostems))
        if name=='development':
            assert not checks[name]['line_ids']
        else:assert not any(checks[name].values()), (name, checks[name])
    return checks

def fresh_wiki_inventory(exclusions):
    """R0a eligibility, independently reusable without touching another deck."""
    records = read(ROOT/'docs/harvest/wikisource/records.jsonl')
    admitted = {r['id']:r for r in read(ROOT/'docs/harvest/wikisource/admitted.jsonl')}
    books = {b['book_key']:b for b in json.loads((ROOT/'docs/harvest/wikisource/holdout_books.json').read_text())}
    inventory_rows = []; pools = {}
    for k,b in books.items():
        rr = [r for r in records if r['book_key']==k]
        if b['lang'] != 'el' or 'wikisource:'+k in exclusions: continue
        eligible = []
        for r in rr:
            a = admitted.get(r['id'])
            if not a or not r.get('human_label') or r['alignment'] != 'aligned': continue
            crop = ROOT/a['crop_path']
            h = nfd(r['human_label'].lstrip(':').strip())
            # Complete crop, one-to-one human line, Greek polytonic evidence;
            # no recogniser agreement or accuracy participates in eligibility.
            if not crop.exists() or not any(c in h for c in POLY): continue
            eligible.append(dict(line_id=r['id'],doc='wikisource:'+k,book_title=b['title'],
                crop=str(crop),crop_sha256=sha(crop),google=nfd(a['label']),human=h,
                human_status='Wikisource reference; not yet pixel-adjudicated',
                script_class='greek_poly',source='wikisource_el',stratum='wikisource',
                human_line_indices=r['human_line_indices'],human_alignment=r['alignment'],
                source_split=b['split'],source_url=r['source_url']))
        inventory_rows.append(dict(book=k,title=b['title'],source_split=b['split'],
            raw_lines=len(rr),human_aligned_lines=sum(bool(r.get('human_label')) for r in rr),
            eligible_lines=len(eligible)))
        pools[k] = eligible
    return inventory_rows, pools

def inventory():
    WORK.mkdir(parents=True, exist_ok=True)
    ls = line_sources(); held = [r for r in ls if r['doc'] not in DEV_BOOKS]
    dev = [r for r in ls if r['doc'] in DEV_BOOKS]
    assert len(held) == 666 and len({r['doc'] for r in held}) == 14
    rel = 'docs/labelfix/spellcheck/clariden/L1_input_documents.txt'
    committed = subprocess.check_output(['git','-C',str(L1),'show','6b91ebaa:'+rel])
    actual = (L1/rel).read_bytes()
    assert actual == committed, 'L1 working manifest differs from requested commit'
    (WORK/'L1_input_documents.txt').write_bytes(committed)
    l1 = set(committed.decode().splitlines())
    inventory_rows, pools = fresh_wiki_inventory({r['doc'] for r in ls} | l1)
    for k, eligible in pools.items():
        write(WORK/f'fresh_candidates_{k}.jsonl',eligible)
    write(WORK/'continuity_666.jsonl',held)
    write(WORK/'dev_598.jsonl',dev)
    source_files = ['greekocr/labelfix/ctc_align.py','greekocr/labelfix/ink.py',
                    'greekocr/labelfix/segmentation.py','greekocr/labelfix/reading.py',
                    'greekocr/labelfix/case.py','docs/labelfix/case_model_S5.json',
                    'docs/labelfix/markshape_model_S4.json','docs/harvest/wikisource/records.jsonl',
                    'docs/harvest/wikisource/admitted.jsonl','docs/harvest/wikisource/holdout_books.json',
                    '.cache/labelfix/align_s0.jsonl','.cache/labelfix/m2/align_s0.jsonl',
                    'docs/labelfix/spellcheck/M2_lines.jsonl.gz','docs/labelfix/spellcheck/S5_lines.jsonl.gz',
                    'docs/labelfix/spellcheck/S5_capital_truth.jsonl']
    dump(WORK/'input_binding.json',dict(head=subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),
        requested_head='fabcd6d4',seed=SEED,network=False,device='cpu',
        l1_commit='6b91ebaa',l1_manifest_sha256=sha(WORK/'L1_input_documents.txt'),
        files={p:sha(ROOT/p) for p in source_files},checkpoint=str(CKPT[0]),checkpoint_sha256=sha(CKPT[0])))
    dump(WORK/'fresh_pool_inventory.json',dict(books=inventory_rows,
        target=dict(lines=[300,500],min_books=5),
        status='INSUFFICIENT_FRESH_BOOKS',
        explanation='Only three Greek books outside all 17 instrument books exist in the specified local harvest. Ten other fresh books are Russian.',
        existing_heldout_books=sorted({r['doc'] for r in held}),existing_dev_books=list(DEV_BOOKS)))
    print(json.dumps(inventory_rows,ensure_ascii=False),flush=True)

def freeze_newsource():
    ls=read(WORK/'continuity_666.jsonl'); dev=read(WORK/'dev_598.jsonl')
    l1=(WORK/'L1_input_documents.txt').read_text().splitlines()
    all_m2=read(OUT/'M2_lines.jsonl.gz')
    measured=[r for r in all_m2 if r['status']=='ok'];assert len(measured)==473
    eligible=[r for r in measured if r['source'] not in ('gazette_modern','ia_russian')
        and any(c in nfd(r['google_label']+r['recogniser_text']) for c in POLY)
        and not any('CYRILLIC' in U.name(c,'') for c in r['google_label']+r['recogniser_text'])]
    chosen,quotas=stratified(eligible,200,lambda r:r['source'])
    locked_ids={r['id'] for r in chosen}
    rest=[r for r in measured if r['id'] not in locked_ids]
    def convert(r, locked):
        phase,source,cid=r['id'].split('/')
        source_dir=M2_BASE/phase/source
        card=next(x for x in read(source_dir/'cards.jsonl') if x['card_id']==cid)
        source_key=json.loads((source_dir.parent/(source+'_key.json')).read_text())[cid]
        assert source_key['line_id']==r['line_id']
        assert nfd(card['google_text'])==nfd(r['google_label'])
        assert sha(source_dir/card['crop'])==sha(r['crop'])
        # Reference is explicitly not a transcription or new print truth.
        return dict(line_id=r['line_id'],card_id=r['id'],doc='newsource:'+docstem(r['line_id']),
            source=r['source'],stratum='newsource',crop=r['crop'],crop_sha256=sha(r['crop']),
            model=nfd(r['recogniser_text']),google=nfd(r['google_label']),human=None,
            existing_blind_verdict=r['verdict'],existing_key=r['key'],
            human_status='PENDING_R0b; existing verdict is reference only',
            script_class='greek_latin_cs' if r['source'] in ('ia_greek_latin','bsb_mixed') else
                         'greek_mono' if r['source']=='gazette_modern' else 'greek_poly',
            selection_role='never_tune_locked_test' if locked else 'development_only')
    locked=[convert(r,True) for r in chosen]; remainder=[convert(r,False) for r in rest]
    assert len(locked)==len({r['line_id'] for r in locked})==200
    write(OUT/'R0_newsource_locked.jsonl',locked);write(OUT/'R0_newsource_dev.jsonl',remainder)
    (OUT/'R0_newsource_exclusion_ids.txt').write_text(''.join(x+'\n' for x in sorted(r['line_id'] for r in locked)))
    (OUT/'R0_newsource_dev_ids.txt').write_text(''.join(x+'\n' for x in sorted(r['line_id'] for r in remainder)))
    overlap=overlap_receipt(locked,dict(continuity_666=ls,DEV=dev,L1_input=l1,development=remainder))
    # Cross-source aliases are additionally checked by exact crop content.
    old_hashes={sha(r['crop']) for r in ls+dev}
    assert not old_hashes & {r['crop_sha256'] for r in locked}
    assert not {r['crop_sha256'] for r in locked} & {r['crop_sha256'] for r in remainder}
    l1_urls={}
    for r in read(ROOT/'docs/harvest/collection/v2/import_real_v2_train.jsonl'):
        if r['doc'] in l1 and r.get('source_url'):l1_urls.setdefault(r['doc'],r['source_url'])
    l1_anemi={}
    for d,u in l1_urls.items():
        m=re.search(r'metadata-[\w-]+\.tkl',u)
        if m:l1_anemi[m.group()]=d
    canonical_hits=[]
    for r in locked:
        m=re.search(r'metadata-[\w-]+\.tkl',r['line_id'])
        if m and m.group() in l1_anemi:canonical_hits.append(dict(line_id=r['line_id'],L1_doc=l1_anemi[m.group()]))
    assert not canonical_hits,canonical_hits
    receipt=dict(schema='r0-newsource-split-v1',seed=SEED,measured_m2_cards=473,
        eligible_polytonic_cards=len(eligible),locked_lines=len(locked),locked_sources=quotas,
        dev_lines=len(remainder),dev_sources=dict(Counter(r['source'] for r in remainder)),
        unmeasured_excluded_cards=len(all_m2)-len(measured),
        rule='Select 200 by proportional largest-remainder source quotas and random.Random(20261017).sample over stable line-id order. All remaining 273 measured cards are DEV, including modern and uncertain-script cards. No Cyrillic enters locked or DEV measured pool.',
        half_note='200/409 eligible polytonic cards = 48.9%; 200 is the requested maximum.',
        never_tune='Stratum (ii) must never again be used for selection or tuning and must never enter a training release. It judges L1 and wave 1c from now on.',
        prior_exposure='All 473 measured M2 cards were S7 qualification targets; this split prevents future reuse but cannot undo prior exposure. This is not a previously untouched test.',
        truth='Existing blind verdicts are references only, pending fresh pixel adjudication.',
        zero_intersections=overlap,exact_crop_overlap_with_666_DEV=0,
        canonical_anemi_check=dict(L1_documents_with_urls=len(l1_urls),L1_Anemi_metadata_ids=len(l1_anemi),locked_hits=canonical_hits),
        document_identity_note='Documents use harvest line-id stem, with wave namespace; normalized stems also compared. This does not prove absence of unrecorded cross-archive editions.',
        files={p.name:sha(p) for p in [OUT/'R0_newsource_locked.jsonl',OUT/'R0_newsource_dev.jsonl',OUT/'R0_newsource_exclusion_ids.txt',OUT/'R0_newsource_dev_ids.txt']})
    dump(OUT/'R0_newsource_split_receipt.json',receipt)
    print('ZERO INTERSECTION newsource: '+json.dumps({k:v for k,v in overlap.items() if k!='development'}),flush=True)

def freeze_wiki(allow_shortfall=False):
    candidates=[]
    for p in sorted(WORK.glob('fresh_candidates_*.jsonl')):candidates.extend(read(p))
    if len({r['doc'] for r in candidates})<5 and not allow_shortfall:
        ns=json.loads((OUT/'R0_newsource_split_receipt.json').read_text())
        dump(OUT/'R0_locked_set_receipt.json',dict(status='PENDING_SCOPE_DECISION',seed=SEED,
            stratum_i_lines=0,stratum_i_books=0,available_lines=len(candidates),
            available_books=sorted({r['doc'] for r in candidates}),
            never_tune='Any eventual R0 locked set is never for tuning; it judges L1 and wave 1c. The 666 remain the continuity instrument.',
            reason='Requested >=5 fresh Greek books unavailable offline. No noncompliant set frozen and no CTC forward pass authorized on candidates.',
            newsource_lines=ns['locked_lines'],newsource_sources=len(ns['locked_sources']),newsource_dev_lines=ns['dev_lines'],
            newsource_manifest_sha256=sha(OUT/'R0_newsource_locked.jsonl'),newsource_receipt_sha256=sha(OUT/'R0_newsource_split_receipt.json'),
            cross_stratum_intersection_status='PENDING_NONEMPTY_STRATUM_I'))
        write(OUT/'R0_locked_set.jsonl',[])
        r=json.loads((OUT/'R0_locked_set_receipt.json').read_text());r['locked_set_sha256']=sha(OUT/'R0_locked_set.jsonl');dump(OUT/'R0_locked_set_receipt.json',r)
        return
    chosen,quotas=stratified(candidates,min(400,len(candidates)),lambda r:r['doc'])
    write(OUT/'R0_locked_set.jsonl',chosen)
    checks=overlap_receipt(chosen,dict(continuity_666=read(WORK/'continuity_666.jsonl'),DEV=read(WORK/'dev_598.jsonl'),
        L1_input=(WORK/'L1_input_documents.txt').read_text().splitlines(),newsource=read(OUT/'R0_newsource_locked.jsonl')))
    dump(OUT/'R0_locked_set_receipt.json',dict(status='LOCKED_WITH_EXPLICIT_SIZE_EXCEPTION' if len(quotas)<5 else 'LOCKED',
        seed=SEED,stratum_i_lines=len(chosen),stratum_i_books=len(quotas),books=quotas,
        zero_intersections=checks,sha256=sha(OUT/'R0_locked_set.jsonl'),
        never_tune='Never use for tuning or selection. Judges L1 and wave 1c; 666 are continuity only.',
        exception='Owner/coordinator explicitly allowed available three-book set.' if len(quotas)<5 else None))
    print('ZERO INTERSECTION Wikisource: '+json.dumps(checks),flush=True)

def align_locked():
    ls=read(OUT/'R0_locked_set.jsonl')+read(OUT/'R0_newsource_locked.jsonl')
    assert len(ls)<=600 and len({r['crop'] for r in ls})==len(ls)
    original_cache=read(ROOT/'.cache/labelfix/m2/align_s0.jsonl')
    existing=load_alignments(ROOT/'.cache/labelfix/m2/align_s0.jsonl')
    cache_bindings={crop_key(r['crop']):r for r in original_cache}
    cache=WORK/'align_locked_s0.jsonl'
    have={r['crop']:r for r in read(cache)} if cache.exists() else {}
    missing=[]
    for l in ls:
        if l['crop'] in have:continue
        key=crop_key(l['crop'])
        if key in existing:
            assert cache_bindings[key]['crop_sha256']==sha(l['crop'])
            assert cache_bindings[key]['checkpoint_sha256']==sha(CKPT[0])
            have[l['crop']]=dict(crop=l['crop'],line_id=l['line_id'],crop_sha256=sha(l['crop']),
                checkpoint_sha256=sha(CKPT[0]),alignment=existing[key].to_record(),origin='existing_M2_cache')
        else:missing.append(l)
    if missing:
        rec=Recognizer(CKPT[0],device='cpu',threads=4)
        al=rec.align_paths([l['crop'] for l in missing],bs=8,log=print)
        for l in missing:
            have[l['crop']]=dict(crop=l['crop'],line_id=l['line_id'],crop_sha256=sha(l['crop']),
                checkpoint_sha256=sha(CKPT[0]),alignment=al[l['crop']].to_record(),origin='R0a_CPU_forward')
    write(cache,[have[l['crop']] for l in ls])
    dump(WORK/'alignment_receipt.json',dict(locked_crops=len(ls),new_forward_crops=len(missing),
        cached_M2=sum(have[l['crop']]['origin']=='existing_M2_cache' for l in ls),
        total_R0_forward_crops=sum(have[l['crop']]['origin']=='R0a_CPU_forward' for l in ls),
        cpu_only=True,network=False,never_forward_on_666=True,sha256=sha(cache)))

def all_locked():
    ls=read(OUT/'R0_locked_set.jsonl')+read(OUT/'R0_newsource_locked.jsonl')
    als={r['line_id']:Alignment.from_record(r['alignment']) for r in read(WORK/'align_locked_s0.jsonl')}
    for l in ls:
        l['recorded_model']=l.get('model');l['model']=als[l['line_id']].prediction
    return ls,als

def audit_spans(lines=None, alignments=None, work=None):
    from greekocr.labelfix import ink
    from greekocr.labelfix.case import estimate_font, prepare
    from greekocr.labelfix.segmentation import recogniser_slots
    work = WORK if work is None else work
    if lines is None:
        old=read(WORK/'continuity_666.jsonl');locked,la=all_locked()
        lines=old+locked
        cache=load_alignments(ROOT/'.cache/labelfix/align_s0.jsonl')
        alignments={l['line_id']:la.get(l['line_id']) or cache[crop_key(l['crop'])] for l in lines}
    rows=[];line_stats=[]
    for k,l in enumerate(lines):
        al=alignments[l['line_id']]
        # Audit actual emitted characters/spans. Transferred spans are never
        # mistaken for native CTC positions; saved-text drift is recorded.
        with Image.open(l['crop']) as im:ci=ink.analyse(im)
        estimate_font(ci)
        slots=recogniser_slots(ci,al.prediction,al)
        prepare(ci,slots)
        components={c.index:c for c in ci.components if c.role=='letter'}
        owners=Counter(q for s in slots for q in s['component_ids'])
        stratum=l.get('stratum','continuity_666')
        for s in slots:
            ids=s['component_ids'];valid=[q for q in ids if q in components]
            clean=(len(valid)==1 and owners[valid[0]]==1 and not s['fused'] and not s['split_union'] and not s['localisation_unknown'])
            if clean:status='clean_one_blob_one_character'
            elif s['localisation_unknown']:status='no_letter_blob'
            elif s['fused']:status='fused_multi_character_blob'
            elif s['split_union']:status='split_character_multi_blob'
            else:status='ambiguous_ownership'
            bbox=([components[valid[0]].x0,components[valid[0]].y0,components[valid[0]].x1,components[valid[0]].y1] if clean else None)
            xh=float(ci.word_bands.get(valid[0],{}).get('xh',ci.xh)) if valid else float(ci.xh)
            name=U.name(s['base'],'')
            script='Latin' if 'LATIN' in name else 'greek_poly' if 'GREEK' in name and l['script_class']!='greek_mono' else 'modern' if 'GREEK' in name else 'other'
            centre=sum(s['locator_span'])/2
            rows.append(dict(line_id=l['line_id'],doc=l['doc'],stratum=stratum,slot=s['start'],
                base=s['base'],script_class=script,line_script_class=l['script_class'],
                xheight_px=xh,size_bucket='<20px' if xh<20 else '20-34px' if xh<35 else '>=35px',
                status=status,component_ids=ids,ctc_span=s['locator_span'],ctc_centre=centre,
                blob_bbox=bbox,outside_blob=(not (bbox[0]<=centre<bbox[2])) if clean else None,
                reference='native detector connected-component bbox; half-open x interval',
                native_ctc=True,recorded_text_differs=nfd(l['model'])!=al.prediction))
        line_stats.append(dict(line_id=l['line_id'],stratum=stratum,doc=l['doc'],xh=ci.xh,
            alphabetic_slots=len(slots),all_ctc_atoms=len(al.spans),
            spaces=sum(s.char.isspace() for s in al.spans),
            combining_marks=sum(U.category(s.char).startswith('M') for s in al.spans),
            other_nonletters=sum(not s.char.isalpha() and not s.char.isspace() and not U.category(s.char).startswith('M') for s in al.spans),
            recorded_text_differs=nfd(l['model'])!=al.prediction))
        if k%100==0:print('span lines',k,'/',len(lines),flush=True)
    write(work/'span_slots.jsonl.gz',rows);write(work/'span_line_census.jsonl',line_stats)
    def stat(rr):
        clean=[r for r in rr if r['outside_blob'] is not None];outside=sum(r['outside_blob'] for r in clean)
        return dict(all_alphabetic_slots=len(rr),statuses=dict(Counter(r['status'] for r in rr)),
            clean_slots=len(clean),outside=outside,outside_pct=100*outside/len(clean) if clean else None)
    summary=dict(pooled=stat(rows),by_stratum={s:stat([r for r in rows if r['stratum']==s]) for s in sorted({r['stratum'] for r in rows})},
        by_script={s:stat([r for r in rows if r['script_class']==s]) for s in ('greek_poly','modern','Latin','other')},
        by_size={s:stat([r for r in rows if r['size_bucket']==s]) for s in ('<20px','20-34px','>=35px')},
        by_script_size={s+' / '+b:stat([r for r in rows if r['script_class']==s and r['size_bucket']==b]) for s in ('greek_poly','modern','Latin','other') for b in ('<20px','20-34px','>=35px')},
        by_book={d:stat([r for r in rows if r['doc']==d]) for d in sorted({r['doc'] for r in rows})},
        caveat='CTC-overlap-based component assignment is the runtime mapping, not independent glyph identity truth. Outside-blob is a geometry diagnostic, not letter error. All alphabetic slots are censused; only clean slots enter the rate. Combining marks, spaces and punctuation are atom-censused separately.',
        native_cached_prediction_drift_lines=[r['line_id'] for r in line_stats if r['recorded_text_differs']])
    dump(work/'span_summary.json',summary)
    print(json.dumps(summary['pooled']),flush=True)
    return summary

def audit_r1():
    frozen=read(OUT/'S4_lines.jsonl.gz')
    frozen={l['line_id']:l for l in frozen if not l['dev']}
    metadata=ROOT.parent/'greek-ocr-toolkit-spellcheck-r1/artifacts/labelfix_r1/heldout_font/lines.jsonl.gz'
    md={l['id']:l for l in read(metadata)}
    records=[];scored=0;mapped=0
    for lid,l in frozen.items():
        rs={r['start']:r for r in l['recogniser_slots']}
        primary_owners=defaultdict(list)
        for r in l['recogniser_slots']:
            if r.get('primary') is not None:primary_owners[r['primary']].append(r['start'])
        for c in md[lid]['coverage']:
            if not c['scored']:continue
            scored+=1;r=rs.get(c['start'])
            if r and r.get('component_slot') is not None:
                mapped+=1;continue
            if r is None:reason='no_frozen_recogniser_slot_at_start'
            elif r.get('fused'):reason='fused_region_no_unique_frozen_blob'
            elif r.get('split_union'):reason='split_union_no_single_frozen_blob'
            elif r.get('localisation_unknown') and r.get('primary') is None:reason='frozen_no_overlapping_primary_letter_blob'
            elif r.get('localisation_unknown') and len(primary_owners[r['primary']])>1:reason='frozen_shared_primary_blob_rejected'
            elif r.get('localisation_unknown'):reason='frozen_localisation_unknown_other'
            elif r.get('bbox'):
                exact=[s for s in l['slots'] if s['bbox']==r['bbox']]
                reason='region_bbox_differs_from_all_frozen_blobs' if not exact else 'frozen_component_slot_not_assigned'
            else:reason='frozen_recogniser_slot_has_no_component_bbox'
            span=r.get('locator_span') if r else c.get('locator_span')
            hits=[dict(slot=s['slot'],bbox=s['bbox']) for s in l['slots'] if span and min(span[1],s['bbox'][2])>max(span[0],s['bbox'][0])]
            records.append(dict(line_id=lid,slot=c['start'],base=c['base'],reason=reason,
                mapping_detail=('R1_shared_component_frozen_mapper_unlocated' if c.get('fused') else
                    'R1_no_component_owners_frozen_mapper_unlocated' if not c.get('component_owners') else
                    'R1_single_owner_component_frozen_mapper_unlocated'),
                frozen_overlap_count=len(hits),
                frozen_primary_owner_starts=primary_owners.get(r.get('primary'),[]) if r else [],
                frozen_recogniser_slot=r,coverage=c,overlapping_frozen_blobs=hits,
                interpretation='mapping/evaluation availability, not adjudicated letter failure'))
    assert scored==11329 and mapped==10614 and len(records)==715,(scored,mapped,len(records))
    assert Counter(r['reason'] for r in records)==Counter(frozen_no_overlapping_primary_letter_blob=17,frozen_shared_primary_blob_rejected=698)
    write(WORK/'R1_unmapped_715.jsonl',records)
    dump(WORK/'R1_unmapped_summary.json',dict(scored=scored,mapped=mapped,unmapped=len(records),
        reasons=dict(Counter(r['reason'] for r in records)),
        mapping_details=dict(Counter(r['mapping_detail'] for r in records)),
        frozen_overlap_counts=dict(Counter(r['frozen_overlap_count'] for r in records)),
        detail_examples={t:sorted({r['line_id'] for r in records if r['mapping_detail']==t})[:3] for t in sorted({r['mapping_detail'] for r in records})},
        examples={t:sorted({r['line_id'] for r in records if r['reason']==t})[:3] for t in sorted({r['reason'] for r in records})},
        frozen='S4 original physical-slot mapping, preserving the R1 reported denominator',
        source=str(metadata),source_sha256=sha(metadata)))
    historical=subprocess.check_output(['git','show','afe67823:greekocr/labelfix/reading.py'],cwd=ROOT)
    (WORK/'historical_S4_reading.py.txt').write_bytes(historical)

def label_frequencies():
    p=ROOT/'docs/harvest/collection/v2/import_real_v2_train.jsonl'
    counts=Counter();line_counts=Counter();byclass=defaultdict(Counter);n=0
    for r in read(p):
        s=nfd(r['label']);n+=1
        counts.update(s);line_counts.update(set(s));byclass[r['script_class']].update(s)
    symbols=sorted(set(QUOTES+'\u0313\u0314\u0342\u0345')|{c for c in counts if c.isupper()})
    dump(WORK/'training_label_frequencies.json',dict(path=str(p),sha256=sha(p),lines=n,
        symbols=[dict(symbol=c,codepoint=f'U+{ord(c):04X}',name=U.name(c,''),occurrences=counts[c],lines=line_counts[c],
                    by_script={k:v[c] for k,v in byclass.items()}) for c in symbols],
        interpretation='Frequency is label evidence only; presence or scarcity does not prove label correctness or DATA/MODEL causation.'))

def word_groups(l):
    """Connected word correspondences through mark-stripped character alignment.

    Many-to-one word joins stay together; inserted reference-only words are
    attached to their nearest alignment context, never silently dropped.
    """
    sources={k:nfd(l[k]) for k in ('model','google','human') if l.get(k) is not None}
    words={k:list(re.finditer(r'\S+',s)) for k,s in sources.items()}
    parent={(k,i):(k,i) for k,ww in words.items() for i in range(len(ww))}
    def find(a):
        if parent[a]!=a:parent[a]=find(parent[a])
        return parent[a]
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:parent[b]=a
    def char_words(k):
        chars=[];owner=[]
        for pos,ch in enumerate(sources[k]):
            if U.category(ch).startswith('M'):continue
            chars.append(ch);owner.append(next((i for i,w in enumerate(words[k]) if w.start()<=pos<w.end()),None))
        return ''.join(chars),owner
    mt,mo=char_words('model')
    for k in sources:
        if k=='model':continue
        tt,to=char_words(k);path=align_chars(mt,tt);linked=set()
        for i,j in path:
            if i is not None and j is not None and mo[i] is not None and to[j] is not None:
                union(('model',mo[i]),(k,to[j]));linked.add(to[j])
        for wi in range(len(words[k])):
            if wi in linked or not words['model']:continue
            at=next((pi for pi,(i,j) in enumerate(path) if j is not None and to[j]==wi),0)
            near=min((abs(pi-at),mo[i]) for pi,(i,j) in enumerate(path) if i is not None and mo[i] is not None)[1]
            union(('model',near),(k,wi))
    groups=defaultdict(list)
    for node in parent:groups[find(node)].append(node)
    result=[]
    for nodes in groups.values():
        forms={k:' '.join(words[k][i].group() for kk,i in sorted(nodes) if kk==k) for k in sources}
        model_ids=sorted(i for k,i in nodes if k=='model')
        if model_ids:a=words['model'][model_ids[0]].start();b=words['model'][model_ids[-1]].end()
        else:a=0;b=len(sources['model'])
        result.append(dict(forms=forms,start=a,end=b,model_words=model_ids))
    return sorted(result,key=lambda r:(r['start'],r['end']))

def planned_cards(lines=None, alignments=None, work=None):
    separate = lines is not None
    work = WORK if work is None else work
    if not separate:
        held=read(WORK/'continuity_666.jsonl');locked,la=all_locked()
        cache=load_alignments(ROOT/'.cache/labelfix/align_s0.jsonl')
        lines=held+locked
        alignments={l['line_id']:la.get(l['line_id']) or cache[crop_key(l['crop'])] for l in lines}
    lmap={l['line_id']:l for l in lines}
    als=alignments
    items=[];controls=[];word_census=[]
    for l in lines:
        for g in word_groups(l):
            raw=g['forms']; forms={k:bare(v) for k,v in raw.items()}
            letter_forms={k:' '.join(letters(t) for t in v.split()) for k,v in raw.items()}
            letter_diff=len(set(letter_forms.values()))>1
            quote_forms={k:''.join(c for c in v if c in QUOTES+'…′″') for k,v in raw.items()}
            quote_diff=len(set(quote_forms.values()))>1
            if letter_diff or quote_diff:
                types=[]
                if letter_diff:types.append('letter_word_disagreement')
                if quote_diff:types.append('apostrophe_quote_disagreement')
                items.append(dict(line_id=l['line_id'],start=g['start'],end=g['end'],
                    kinds=types,forms=forms,control=False,model_words=g['model_words']))
            elif len(raw)==3 and len(set(forms.values()))==1:
                correct=forms['model']
                if len(correct)>=4 and all(c.isalpha() for c in correct):
                    controls.append(dict(line_id=l['line_id'],start=g['start'],end=g['end'],
                        correct=correct,model_words=g['model_words']))
            word_census.append(dict(line_id=l['line_id'],start=g['start'],end=g['end'],
                model_words=g['model_words'],reference_forms=forms,letter_disagreement=letter_diff,
                quote_disagreement=quote_diff))
    if separate:
        write(work/'word_disagreement_census.jsonl',word_census)
        write(work/'card_plan.jsonl',items)
        write(work/'control_candidates.jsonl',controls)
        dump(work/'card_plan_summary.json',dict(items=len(items),
            by_kind=dict(Counter(t for r in items for t in r['kinds'])),
            minimum_controls=math.ceil(len(items)*.08/.92),controls_available=len(controls),
            locked_lines=len(lines),full_pixel_letter_truth_lines=0,full_pixel_letter_truth_slots=0,
            supplement_note='Fresh Wikisource has no historical S4/S5/M2 cohorts; use the unchanged three-way word/quote generator.'))
        return items,controls,lmap,als
    # Owner's explicit Latin-a witness is in detector DEV, outside the 666.
    # Supplementary card only: never add it to either locked-set denominator.
    for l in line_sources():
        if 'ξa' not in nfc(l['model']) or l['line_id'] in lmap:continue
        l=dict(l,stratum='owner_DEV_supplement')
        lmap[l['line_id']]=l;als[l['line_id']]=cache[crop_key(l['crop'])]
        for g in word_groups(l):
            if 'ξa' not in nfc(g['forms']['model']):continue
            items.append(dict(line_id=l['line_id'],start=g['start'],end=g['end'],
                kinds=['owner_Latin_a_witness'],forms={k:bare(v) for k,v in g['forms'].items()},
                control=False,model_words=g['model_words'],owner_reference='Explicit ξaνὰ witness from the R0 brief; not full-line truth.'))
    # The ten cached forward predictions differ from the stored E3 instrument.
    # Adjudicate new native-cache variants too, without merging the two streams.
    drift=[]
    for l in held:
        al=als[l['line_id']]
        if al.prediction==nfd(l['model']):continue
        def offsets(text):
            return [(i,c) for i,c in enumerate(nfd(text)) if not U.category(c).startswith('M')]
        aa,bb=offsets(al.prediction),offsets(l['model'])
        changed=set();path=align_chars(''.join(c for i,c in aa),''.join(c for i,c in bb))
        for pi,(i,j) in enumerate(path):
            if i is not None and (j is None or aa[i][1]!=bb[j][1]):changed.add(aa[i][0])
            elif i is None:
                near=next((ii for ii,jj in path[pi+1:] if ii is not None),len(aa)-1)
                if aa:changed.add(aa[near][0])
        drift.append(dict(line_id=l['line_id'],recorded_model=l['model'],native_cached=al.prediction,
            base_letters_differ=letters(l['model'])!=letters(al.prediction),changed_native_offsets=sorted(changed)))
        if not changed:continue
        native=dict(l,model=al.prediction)
        for g in word_groups(native):
            if not any(g['start']<=i<g['end'] for i in changed):continue
            forms={k:bare(v) for k,v in g['forms'].items()}
            if len(set(forms.values()))<2:continue
            items.append(dict(line_id=l['line_id'],start=g['start'],end=g['end'],
                kinds=['native_cached_prediction_variant'],forms=forms,control=False,
                model_words=g['model_words'],model_variant='native_cached',locator_text=al.prediction))
    write(WORK/'cached_prediction_drift_10.jsonl',drift)
    # Exact requested S5 cohort, sampled by book with at least one per book.
    s5={l['line_id']:l for l in read(OUT/'S5_lines.jsonl.gz')}
    case=[r for r in read(OUT/'S5_capital_truth.jsonl') if r.get('case_disagreement') is True]
    assert len(case)==753
    for r in case:r['doc']=lmap[r['line_id']]['doc']
    grouped=defaultdict(list)
    for r in case:grouped[r['doc']].append(r)
    rng=random.Random(SEED);sample=[]
    for d,rr in sorted(grouped.items()):sample.extend(rng.sample(sorted(rr,key=lambda r:(r['line_id'],r['slot'])),1))
    selected={(r['line_id'],r['slot']) for r in sample}
    rest=[r for r in case if (r['line_id'],r['slot']) not in selected]
    more,_=stratified(rest,160-len(sample),lambda r:r['doc']);sample+=more
    for r in sample:
        l=s5[r['line_id']];s=next(s for s in l['slots'] if s['slot']==r['slot'])
        base=bare(s['base']);rec=base.upper() if r['recogniser_upper'] else base.lower()
        px=base.upper() if r['pixel'] else base.lower()
        if rec==px:raise ValueError('case candidate pair did not disagree')
        items.append(dict(line_id=r['line_id'],start=s.get('recogniser_start',0),
            end=s.get('recogniser_start',0)+1,bbox=s['bbox'],kinds=['case_disagreement'],
            forms=dict(recogniser=rec,S5_pixel=px),control=False,frozen_slot=r['slot'],
            case_reference=r))
    write(WORK/'case_sample_160.jsonl',sample)
    dump(WORK/'case_sampling_receipt.json',dict(seed=SEED,population=753,sample=160,
        population_by_book=dict(Counter(r['doc'] for r in case)),sample_by_book=dict(Counter(r['doc'] for r in sample)),
        estimator='In R0c use sum_h N_h * (recogniser_right_h / n_h); divide by 753. Do not use an unweighted pooled percentage. Reader ties/unknowns stay explicit; intervals must respect book strata.',
        recogniser_right=None,extrapolated_count=None,status='PENDING_R0b'))
    # S4 punctuation candidates are reference proposals, never new print truth.
    for l in read(OUT/'S4_lines.jsonl.gz'):
        if l['line_id'] not in lmap:continue
        for s in l['slots']:
            if not (s.get('apostrophe') or s.get('evidence',{}).get('apostrophes') or any(t[0]=='apostrophe' for t in s.get('truth') or [])):continue
            b=bare(s['base'])
            items.append(dict(line_id=l['line_id'],start=s.get('recogniser_start',0),
                end=s.get('recogniser_start',0)+1,bbox=s['bbox'],kinds=['S4_apostrophe_candidate'],
                forms=dict(no_sign=b,with_sign=b+'’'),control=False,frozen_slot=s['slot'],
                evidence=s.get('evidence',{}).get('apostrophes',[])))
        for q in l.get('opening_quotes',[]):
            if not q.get('bbox'):continue
            items.append(dict(line_id=l['line_id'],start=0,end=1,bbox=q['bbox'],
                kinds=['S4_opening_quote_candidate'],forms=dict(no_sign='',quote='“',apostrophe='’'),
                control=False,evidence=q))
    # Existing M2 verdict pairs supply additional candidates, never answers.
    m2={r['line_id']:r for r in read(OUT/'M2_lines.jsonl.gz')}
    for l in locked:
        if l['stratum']!='newsource':continue
        for s in m2[l['line_id']]['detector']['slots']:
            if not (s.get('apostrophe') or s.get('evidence',{}).get('apostrophes')):continue
            b=bare(s['base'])
            items.append(dict(line_id=l['line_id'],start=s['start'],end=s['end'],
                bbox=s.get('bbox'),kinds=['M2_apostrophe_candidate'],
                forms=dict(no_sign=b,with_sign=b+'’'),control=False,
                evidence=s.get('evidence',{}).get('apostrophes',[])))
        detail=m2[l['line_id']]['verdict'].get('detail','')
        for segment in detail.split(';'):
            if '→' not in segment:continue
            a,b=segment.split('→',1)
            a=re.sub(r'\([^)]*\)','',a).strip();b=re.sub(r'\([^)]*\)','',b).strip()
            if not a or not b or bare(a)==bare(b):continue
            pos=nfc(l['google']).find(nfc(b))
            if pos<0:continue
            # This form can span words; the entire line is retained for context.
            model=nfc(l['model']);win=next((g for g in word_groups(l) if b in nfc(g['forms'].get('google',''))),None)
            items.append(dict(line_id=l['line_id'],start=win['start'] if win else 0,
                end=win['end'] if win else len(l['model']),kinds=['existing_blind_reference_disagreement'],
                forms=dict(existing_blind_reference=bare(a),google=bare(b)),control=False,
                existing_verdict_reference=detail))
    # Owner evidence is retained verbatim in a separate ledger. DEV examples
    # use only their existing cached CTC alignment, never a new forward pass.
    notes=[]
    for p in sorted(OUT.glob('owner_notes*20261016.jsonl')):
        for r in read(p):
            if re.search(r'misread|classif|ξa|quote|ellipsis',r.get('note',''),re.I):
                notes.append(dict(line_id=r['line_id'],note=r['note'],source=p.name,
                    truth_scope='partial owner observation; not full-line letter truth'))
    for l in lmap.values():
        if l.get('stratum')=='owner_DEV_supplement':
            notes.append(dict(line_id=l['line_id'],note='R0 brief explicitly identifies ξaνὰ with Latin a',
                source='docs/briefs/R0_recogniser_audit.md',recorded_model=nfc(l['model']),
                truth_scope='partial owner observation; not full-line letter truth'))
    write(WORK/'owner_letter_punctuation_evidence.jsonl',notes)
    write(WORK/'word_disagreement_census.jsonl',word_census)
    write(WORK/'card_plan.jsonl',items)
    write(WORK/'control_candidates.jsonl',controls)
    dump(WORK/'card_plan_summary.json',dict(items=len(items),by_kind=dict(Counter(t for r in items for t in r['kinds'])),
        minimum_controls=math.ceil(len(items)*.08/.92),controls_available=len(controls),
        continuity_lines=666,locked_lines=len(locked),full_pixel_letter_truth_lines=0,
        full_pixel_letter_truth_slots=0,case_disagreement_population=753,case_sample=160))
    return items,controls,lmap,als

def card_window(it,l,al):
    if it.get('bbox'):
        x0,_,x1,_=it['bbox']
    else:
        # Text transfer is only a card locator, never span-placement evidence.
        from greekocr.labelfix.ctc_align import transfer_alignment
        al=transfer_alignment(nfd(it.get('locator_text',l['model'])),al)
        x0,x1=al.window(it['start'],it['end'])
    with Image.open(l['crop']) as im:
        w,h=im.size;pad=.6*h
        return max(0,int(x0-pad)),0,min(w,max(int(x0+1),math.ceil(x1+pad))),h

def preview_controls():
    from PIL import ImageDraw, ImageFont
    _,controls,lmap,als=planned_cards()
    # Random, stable control sample across books, manually checked before use.
    rng=random.Random(SEED);rng.shuffle(controls)
    controls=controls[:120]
    for i,c in enumerate(controls):c['control_id']=f'ctrl{i:03d}'
    write(WORK/'control_review_queue.jsonl',controls)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
    for start in range(0,len(controls),20):
        canvas=Image.new('RGB',(1500,20*95),'#eeeeee');d=ImageDraw.Draw(canvas)
        for j,c in enumerate(controls[start:start+20]):
            l=lmap[c['line_id']]
            with Image.open(l['crop']) as im:
                # Tight actual word centre plus smaller context on either side.
                box=card_window(c,l,als[c['line_id']]);crop=im.crop(box).convert('RGB')
            crop.thumbnail((980,68));canvas.paste(crop,(470,j*95+24))
            d.text((8,j*95+10),c['control_id']+' '+c['correct'],fill='black',font=font)
        canvas.save(WORK/f'control_review_{start//20:02d}.png')
    print(json.loads((WORK/'card_plan_summary.json').read_text()),flush=True)

def build_cards(plan=None, verified=None, tag=None, work=None):
    work = WORK if work is None else work
    items,_,lmap,als=planned_cards() if plan is None else plan
    items=list(items)
    verified=read(work/'controls_pixel_verified.jsonl') if verified is None else verified
    suffix='_'+tag if tag else ''
    required=math.ceil(len(items)*.08/.92)
    assert len(verified)>=required,(len(verified),required)
    for ci,c in enumerate(verified[:required]):
        answer=c['correct'];at=next(i for i,v in enumerate(answer) if v.isalpha())
        positions=[i for i,v in enumerate(answer) if v.isalpha()]
        at=positions[ci%len(positions)]
        confusable={'α':'ο','ο':'σ','σ':'ο','ς':'σ','ν':'υ','υ':'ν','η':'π','π':'η',
                    'ε':'ο','ρ':'β','β':'ρ','τ':'γ','γ':'τ','χ':'κ','κ':'χ','ι':'η',
                    'ξ':'ζ','ζ':'ξ','δ':'θ','θ':'δ','λ':'μ','μ':'λ','ω':'ο'}
        replacement=answer[at].swapcase() if ci%3==0 else confusable.get(answer[at].lower(),'β')
        if answer[at].isupper() and ci%3:replacement=replacement.upper()
        fake=answer[:at]+replacement+answer[at+1:]
        items.append(dict(c,line_id=c['line_id'],kinds=['planted_control'],control=True,
            forms=dict(pixel_verified=answer,planted_wrong=fake),known_answer=answer))
    rng=random.Random(SEED);rng.shuffle(items)
    card_dir=OUT/('R0_cards'+suffix);(card_dir/'img').mkdir(parents=True,exist_ok=True)
    blind=[];key=[];truth=[];line_images={}
    for i,it in enumerate(items):
        ident=(tag+'_' if tag else '')+f'item{i:05d}';l=lmap[it['line_id']]
        if it['line_id'] not in line_images:
            p=f'img/line{len(line_images):04d}.png'
            with Image.open(l['crop']) as im:im.save(card_dir/p)
            line_images[it['line_id']]=p
        box=card_window(it,l,als[it['line_id']])
        with Image.open(l['crop']) as im:crop=im.crop(box).convert('RGB')
        scale=min(3.,900/max(1,crop.width))
        crop=crop.resize((max(1,round(crop.width*scale)),max(1,round(crop.height*scale))),Image.Resampling.LANCZOS)
        zoom='img/'+ident+'.png';crop.save(card_dir/zoom)
        forms=list(dict.fromkeys(it['forms'].values()))
        assert 2<=len(forms)<=3,(it,forms)
        rng.shuffle(forms)
        b=dict(id=ident,img=zoom,line_img=line_images[it['line_id']],
               **{chr(65+j):v or '∅' for j,v in enumerate(forms)})
        blind.append(b)
        key.append(dict(b,**it,zoom_scale=scale,crop_box=list(box),source_crop_sha256=sha(l['crop']),
            candidate_sources={chr(65+j):[s for s,v in it['forms'].items() if v==f] for j,f in enumerate(forms)},
            expected_choice=(chr(65+forms.index(it['known_answer'])) if it['control'] else None)))
        truth.append(dict(id=ident,reader_1=dict(choice=None,transcription=None,full_line_letters=None,uncertain=None,note=None),
            reader_2=dict(choice=None,transcription=None,full_line_letters=None,uncertain=None,note=None),
            adjudicated=dict(choice=None,transcription=None,status='PENDING_R0b',evidence=None)))
    dump(card_dir/'items_blind.json',blind)
    private=OUT/'R0_adjudication_private'
    if tag:private=private/tag
    private.mkdir(parents=True,exist_ok=True)
    key_bytes=(json.dumps(key,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    # A separate run must never overwrite or read an existing private key.
    with (private/'items_key.json').open('xb' if tag else 'wb') as f:f.write(key_bytes)
    dump(OUT/('R0_expected_truth'+suffix+'.json'),truth)
    write(OUT/('R0_line_truth_placeholders'+suffix+'.jsonl'),[dict(line_id=l['line_id'],doc=l['doc'],
        stratum=l.get('stratum','continuity_666'),full_line_letter_truth=None,case_folded_truth=None,
        apostrophe_quote_truth=None,status='PENDING_R0b',
        unresolved_card_ids=[r['id'] for r in key if r['line_id']==l['line_id'] and not r['control']],
        caution='Three-way agreement and existing mark truth do not establish full print letter truth.') for l in lmap.values()])
    receipt=dict(blind_items=len(blind),adjudication_cards=len(blind)-required,
        controls=required,control_fraction=required/len(blind),
        by_kind=dict(Counter(t for r in key if not r['control'] for t in r['kinds'])),
        by_stratum=dict(Counter(lmap[r['line_id']].get('stratum','continuity_666') for r in key if not r['control'])),
        seed=SEED,source_labels_hidden=True,control_flags_hidden=True,max_zoom=3,
        private_key='../R0_adjudication_private/'+(tag+'/' if tag else '')+'items_key.json',
        blind_sha256=sha(card_dir/'items_blind.json'),key_sha256=hashlib.sha256(key_bytes).hexdigest())
    dump(work/'cards_receipt.json',receipt)
    instructions='''# R0b blind adjudication

Give each independent reader only `R0_cards/` and a blank copy of `R0_expected_truth.json`.
Keep `R0_adjudication_private/`, the report, original identifiers and other evidence away from readers.
Open both the zoom (at most 3x native) and full line for every item. Read the pixels literally.
Choose A/B/C, or write the correct form when all candidates fail. `∅` means no text/sign at this position.
Ignore combining diacritics when comparing letter forms; preserve case, script and word boundaries.
For punctuation choose the printed apostrophe/quote form; identify elision versus quotation versus breathing.
Greek/Latin homoglyph identity cannot always be established by pixels: mark it uncertain and explain.
Record crop clipping, overrun, ligature/editorial expansion or ambiguous placement, without guessing.
No majority-label inference. Two readers work independently, without the key or each other's answers.
The track lead scores planted controls privately, resolves disagreements against pixels, and supplies final truth.
Do not use these locked cards or their outcomes for policy, checkpoint or threshold selection.
R0c must establish full-line truth explicitly; adjudicating disagreement words alone leaves shared-error risk.
'''
    if tag:
        instructions=instructions.replace('R0_cards/','R0_cards'+suffix+'/').replace('R0_expected_truth.json','R0_expected_truth'+suffix+'.json')
    (card_dir/'README.md').write_text(instructions)
    # Fully offline blind viewer; key is neither embedded nor fetched.
    viewer='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>R0 blind cards</title><style>body{font:18px Georgia;margin:20px;background:#f5f3ed}article{background:white;padding:16px;margin:18px 0;overflow:auto}img{display:block;max-width:100%;height:auto;margin:10px 0}button{font:24px Georgia;margin:6px;padding:8px}textarea{display:block;width:95%;height:60px}.full{max-width:none}details{overflow:auto}</style>
<h1>R0 blind cards</h1><p>Read the zoom and full line. Select the literal printed form; write a correction or uncertainty when needed. Letters ignore diacritics; case and script are preserved. Notes save locally in this browser.</p>
<button id="export">Export answers</button><main id="cards"></main><script>
const items=ITEMS;const answers=JSON.parse(localStorage.getItem('r0-blind-v1')||'{}');
function save(){localStorage.setItem('r0-blind-v1',JSON.stringify(answers))}for(const it of items){let a=document.createElement('article');let h=document.createElement('h2');h.textContent=it.id;a.append(h);for(const src of [it.img,it.line_img]){let im=document.createElement('img');im.loading='lazy';im.src=src;im.alt=src===it.img?'Target crop':'Full line';if(src===it.line_img){im.className='full';let d=document.createElement('details'),s=document.createElement('summary');d.open=true;s.textContent='Full line';d.append(s,im);a.append(d)}else a.append(im)}for(const k of ['A','B','C'])if(it[k]!==undefined){let b=document.createElement('button');b.textContent=k+': '+it[k];b.onclick=()=>{answers[it.id]={...(answers[it.id]||{}),choice:k};save();a.dataset.choice=k;a.style.border='2px solid #276'};a.append(b)}let t=document.createElement('textarea');t.placeholder='Literal correction / uncertainty / note';t.value=answers[it.id]?.note||'';t.oninput=()=>{answers[it.id]={...(answers[it.id]||{}),note:t.value};save()};a.append(t);document.querySelector('main').append(a)}document.querySelector('#export').onclick=()=>{let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(answers,null,2)],{type:'application/json'}));a.download='R0_reader_answers.json';a.click()};</script>'''
    if tag:
        viewer=viewer.replace('r0-blind-v1','r0-blind-'+tag+'-v1').replace('R0_reader_answers.json','R0_'+tag+'_reader_answers.json')
    (card_dir/'index.html').write_text(viewer.replace('ITEMS',json.dumps(blind,ensure_ascii=False).replace('</','<\\/')))
    print(receipt,flush=True)
    return receipt,blind,key

def main():
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['inventory','newsource','wiki','align','spans','r1','frequencies','preview','cards'])
    ap.add_argument('--allow-shortfall',action='store_true');a=ap.parse_args()
    if a.stage=='wiki':freeze_wiki(a.allow_shortfall)
    else:globals()[dict(inventory='inventory',newsource='freeze_newsource',align='align_locked',
        spans='audit_spans',r1='audit_r1',frequencies='label_frequencies',preview='preview_controls',cards='build_cards')[a.stage]]()

if __name__=='__main__':main()
