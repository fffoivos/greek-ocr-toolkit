"""R0a3: offline, crop-bound clean Wikisource (i-b), without runtime changes.

Use the project Python with PYTHONPATH=$PWD and PYTHONDONTWRITEBYTECODE=1.
Stages deliberately freeze the draw before any inference. The existing R0a
letter generator, native span census and card renderer are reused unchanged.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import subprocess
import sys
import time
import unicodedata as U

os.environ.update(PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1',
                  TRANSFORMERS_OFFLINE='1', HF_DATASETS_OFFLINE='1',
                  GIT_OPTIONAL_LOCKS='0', TOKENIZERS_PARALLELISM='false')
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'docs/records/labelfix/spellcheck'
WORK = OUT/'R0_evidence/ib'
HARVEST = ROOT.parent/'greek-ocr-toolkit-sol-wsr0/docs/harvest/wikisource_r0'
CACHE = ROOT/'.cache/labelfix/r0/align_locked_ib.jsonl'
EXTRACTION = CACHE.parent/'ib_r1_extraction'
PRIVATE = OUT/'R0_adjudication_private/ib'
BOOKS = {'45855dfb', 'e90ad4c2', 'bf4f6c1b', 'df94dc99', 'a3114593'}
EXPECTED_R1 = '719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636'
PROTECTED = [OUT/x for x in ('R0_cards', 'R0_cards_ia', 'R0_expected_truth.json',
    'R0_expected_truth_ia.json', 'R0_locked_set.jsonl', 'R0_locked_ia_ids.txt')]


def audit(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo', 'socket.sendto'):
        raise RuntimeError('R0a3 network OFF')
    if event != 'open' or isinstance(args[0], int):
        return
    path, mode, flags = args
    p = Path(os.fsdecode(path)).absolute()
    writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
    if writing:
        resolved = p.resolve()
        if '.git' in resolved.parts or any(p == q or q in p.parents for q in PROTECTED):
            raise RuntimeError(f'Protected output: {p}')
        if not (resolved == Path(os.devnull) or resolved.is_relative_to(ROOT)
                or resolved.is_relative_to(Path('/private/tmp'))
                or resolved.is_relative_to(Path('/private/var/folders'))):
            raise RuntimeError(f'No writes outside workspace: {p} -> {resolved}')
    old_private = OUT/'R0_adjudication_private'
    if (p == old_private or old_private in p.parents) and not p.is_relative_to(PRIVATE):
        raise RuntimeError('Other adjudication keys/readers are out of scope')


sys.addaudithook(audit)
from scripts.labelfix import r0_prepare as r0
from PIL import Image, ImageDraw, ImageFont


def binding():
    paths = ['greekocr/labelfix/ctc_align.py', 'greekocr/labelfix/ink.py',
        'greekocr/labelfix/segmentation.py', 'greekocr/labelfix/reading.py',
        'greekocr/labelfix/case.py', 'greekocr/labelfix/markshape.py',
        'docs/records/labelfix/markshape_model_S4.json', 'scripts/labelfix/r0_prepare.py',
        '.cache/labelfix/align_s0.jsonl', '.cache/labelfix/m2/align_s0.jsonl']
    paths += [f'scripts/labelfix/clariden/r1_{s}.py' for s in ('extract','pixels','model','train','common')]
    return dict(head=subprocess.check_output(['git','--no-optional-locks','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
        branch=subprocess.check_output(['git','--no-optional-locks','branch','--show-current'],cwd=ROOT).decode().strip(),
        files={p:r0.sha(ROOT/p) for p in paths},
        checkpoint=str(r0.CKPT[0]), checkpoint_sha256=r0.sha(r0.CKPT[0]),
        harvest_files={p:r0.sha(HARVEST/p) for p in ('lines.jsonl','pages.jsonl','books.jsonl','RECEIPT.md')},
        original_ia_receipt_sha256=r0.sha(OUT/'R0_locked_set_receipt.json'),
        network=False, device='cpu', seed=r0.SEED)


def normalize(lid):
    return re.sub(r'(?:--n?\d+|-p\d+)-l\d+$', '', lid.removeprefix('r0-ws-'))


def intersection(rows, pool):
    own_ids = {r['line_id'] for r in rows}
    own_docs = {r['doc'] for r in rows}
    ids = {r.get('line_id',r.get('id','')) for r in pool}
    docs = {r.get('doc',r.get('document_id','')) for r in pool}
    fields = ids | docs
    hits = sorted(h for h in BOOKS if any(h in s for s in fields))
    result = dict(comparison_rows=len(pool), line_ids=sorted(own_ids & ids),
        documents=sorted(own_docs & docs), normalized_line_ids=sorted(
            {s.removeprefix('r0-ws-') for s in own_ids} & {s.removeprefix('r0-ws-') for s in ids}),
        normalized_document_ids=sorted(BOOKS & ({normalize(s) for s in ids} |
            {s.split(':',1)[-1] for s in docs})), bare_book_hashes=hits,
        matching_rows=sum(any(h in r.get('id',r.get('line_id','')) or h in r.get('doc',r.get('document_id',''))
            for h in BOOKS) for r in pool))
    assert not any(result[k] for k in ('line_ids','documents','normalized_line_ids','normalized_document_ids','bare_book_hashes','matching_rows')), result
    return result


def freeze():
    WORK.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'R0_locked_ib.jsonl').exists(), 'Frozen draw is write-once'
    bind = binding()
    books = {r['index_url']:r for r in r0.read(HARVEST/'books.jsonl')}
    pages = {r['page_id']:r for r in r0.read(HARVEST/'pages.jsonl')}
    source = r0.read(HARVEST/'lines.jsonl')
    assert len(source)==1246 and len(pages)==116 and {r['book_key'] for r in source}==BOOKS
    candidates=[]; rejects=[]
    for r in source:
        h = r0.nfd(r['human_label_literal'].lstrip(':').strip())
        al = r['alignment']; crop = HARVEST.parents[2]/r['crop_path']
        reasons=[]
        if not h: reasons.append('empty_human')
        if al['alignment']!='aligned' or al['alignment_reason']!='one_to_one' or len(al['human_line_indices'])!=1:
            reasons.append('not_one_to_one_aligned')
        if books[r['index_url']]['lang']!='el' or not any(c in h for c in r0.POLY):
            reasons.append('no_polytonic_evidence')
        if not crop.is_file(): reasons.append('missing_complete_crop')
        if reasons:
            rejects.append(dict(line_id=r['line_id'],reasons=reasons)); continue
        assert r0.sha(crop)==r['crop_sha256']
        with Image.open(crop) as im: assert list(im.size)==r['crop_size']
        gp = pages[r['page_id']]['geometry']['lines'][al['google_line_index']]
        assert gp['bbox']==r['google_line_bbox'] and gp['text']==al['google_text']
        candidates.append(dict(line_id=r['line_id'],doc=r['document_id'],book=r['book_key'],
            book_title=books[r['index_url']]['title'],crop=str(crop),crop_sha256=r['crop_sha256'],
            google=r0.nfd(gp['text'].strip()),human=h,human_literal=r['human_label_literal'],
            human_nfc=r['human_label_nfc'],human_status='Wikisource reference; not pixel-adjudicated print truth',
            script_class='greek_poly',source='wikisource_el',stratum='wikisource_ib',stratum_label='clean locked Wikisource stratum',
            human_line_indices=al['human_line_indices'],human_alignment=al['alignment'],
            alignment_evidence=al,source_url=r['source_url'],page_id=r['page_id'],
            crop_bbox=r['crop_bbox'],google_line_bbox=r['google_line_bbox'],
            selection_role='never_tune_locked_test',train_pool_eligible=False,training_release_allowed=False))
    chosen, quotas = r0.stratified(candidates,400,lambda r:r['doc'])
    assert chosen==r0.stratified(candidates,400,lambda r:r['doc'])[0]
    assert len(chosen)==400 and len(quotas)==5 and max(quotas.values())<=160
    pools = dict(continuity_666=r0.read(OUT/'R0_evidence/continuity_666.jsonl'),
        DEV=r0.read(OUT/'R0_evidence/dev_598.jsonl'),
        L1_input_documents=[dict(doc=d) for d in (OUT/'R0_evidence/L1_input_documents.txt').read_text().splitlines()],
        stratum_ii=r0.read(OUT/'R0_newsource_locked.jsonl'),
        stratum_ii_development=r0.read(OUT/'R0_newsource_dev.jsonl'),
        stratum_ia=r0.read(OUT/'R0_locked_set.jsonl'))
    local = [r for r in json.loads((ROOT/'docs/records/harvest/wikisource/holdout_books.json').read_text()) if r['lang']=='el']
    assert len(local)==20
    assert {r['book_key'] for r in local}=={r['key'] for r in json.loads((HARVEST/'exclusions/local20_books.json').read_text())}
    pools['local20_books']=[dict(doc='wikisource:'+r['book_key']) for r in local]
    checks={}
    for name,pool in pools.items():
        checks[name]=intersection(chosen,pool)
        print('ZERO_INTERSECTION',name,json.dumps(checks[name]),flush=True)
    # Stream every split, explicitly checking both id and doc against bare hashes.
    v2={}
    for split in ('train','dev','test'):
        path=ROOT/f'docs/records/harvest/collection/v2/import_real_v2_{split}.jsonl'
        count=0; hits=[]
        with path.open() as f:
            for line in f:
                if not line.strip():continue
                r=json.loads(line);count+=1
                if any(h in r.get('id','') or h in r.get('doc','') for h in BOOKS):
                    hits.append(dict(id=r.get('id'),doc=r.get('doc')))
        assert not hits,(split,hits)
        v2[split]=dict(path=str(path.relative_to(ROOT)),sha256=r0.sha(path),comparison_rows=count,
            matching_rows=0,intersection=hits,fields=['id','doc'],bare_book_hashes=sorted(BOOKS))
        print('ZERO_INTERSECTION collection_v2_'+split,json.dumps(v2[split]),flush=True)
    checks['collection_v2_val']=v2['dev']
    crop_checks={}; own={r['crop_sha256'] for r in chosen}
    for name,pool in pools.items():
        if not pool or 'crop' not in pool[0]:continue
        hashes={r0.sha(r['crop']) for r in pool}
        hits=sorted(own&hashes);assert not hits
        crop_checks[name]=dict(comparison_crops=len(pool),intersection=hits,count=0)
    r0.write(OUT/'R0_locked_ib.jsonl',chosen)
    (OUT/'R0_locked_ib_ids.txt').write_text(''.join(r['line_id']+'\n' for r in chosen))
    r0.write(WORK/'admission_rejections.jsonl',rejects)
    r0.write(WORK/'admitted_inventory.jsonl',candidates)
    r0.dump(WORK/'input_binding.json',bind)
    r0.dump(WORK/'original_ia_receipt.json',json.loads((OUT/'R0_locked_set_receipt.json').read_text()))
    comparisons=[OUT/'R0_evidence/continuity_666.jsonl',OUT/'R0_evidence/dev_598.jsonl',
        OUT/'R0_evidence/L1_input_documents.txt',OUT/'R0_newsource_locked.jsonl',
        OUT/'R0_newsource_dev.jsonl',OUT/'R0_locked_set.jsonl',ROOT/'docs/records/harvest/wikisource/holdout_books.json']
    receipt=dict(schema='r0-locked-ib-v1',status='FROZEN_IB',label='clean locked Wikisource stratum',stratum='i-b',
        seed=r0.SEED,lines=len(chosen),books=5,book_counts=dict(sorted(Counter(r['book'] for r in chosen).items())),
        eligible_by_book=dict(sorted(Counter(r['book'] for r in candidates).items())),
        harvest_lines=len(source),harvest_pages=len(pages),eligible_lines=len(candidates),rejected_lines=len(rejects),
        max_book_fraction=max(quotas.values())/len(chosen),
        admission='R0a: Greek book; admitted existing whole crop; nonempty human; one-to-one aligned; NFD POLY evidence. Complete crop and hash checked. No recogniser/reader output or accuracy in admission.',
        selection='400; proportional largest-remainder quotas; stable line-id sort; random.Random(20261017).sample; repeated draw identical; maximum share <=40%.',
        zero_intersections=checks,collection_v2_all_splits=v2,exact_crop_zero_intersections=crop_checks,
        comparison_manifest_sha256={str(p.relative_to(ROOT)):r0.sha(p) for p in comparisons},
        google_source='pages.jsonl geometry.lines[alignment.google_line_index].text; asserted exact equality to lines.jsonl alignment.google_text and Google bbox; outer whitespace stripped, NFD for processing.',
        human_source='lines.jsonl human_label_literal; literal and NFC retained unchanged; R0a outer whitespace/leading colon processing only for NFD human.',
        never_tune='Clean locked Wikisource stratum (i-b): never use for training, policy/checkpoint/threshold selection or tuning. It judges L1 and wave 1c; the 666 are continuity only. Keep selection-exposed (i-a) separate.',
        truth_status='Human reference is not print truth. Letter and mark cards await two independent readers and pixel tiebreak; agreement is a proxy only.',
        release_exclusion='All 1246 harvest IDs are already locked_eval_ib_wikisource per sourcing handoff; this task does not change the release manifest; selected rows also explicitly forbid training.',
        identity_scope='Exact IDs, prefix-normalized line IDs, normalized document IDs, and bare book hashes in id/doc. Known crop sets additionally checked byte-for-byte. Undocumented editions/copies are not excluded by identifiers.',
        manifest_sha256=r0.sha(OUT/'R0_locked_ib.jsonl'),ids_sha256=r0.sha(OUT/'R0_locked_ib_ids.txt'),execution=bind)
    r0.dump(WORK/'locked_receipt.json',receipt)
    combined=json.loads((OUT/'R0_locked_set_receipt.json').read_text())
    assert 'stratum_ib' not in combined
    combined['stratum_ib']=receipt
    # Preserve the established one-space receipt formatting for existing IA.
    (OUT/'R0_locked_set_receipt.json').write_text(json.dumps(combined,ensure_ascii=False,indent=1,allow_nan=False)+'\n')
    assert CACHE.parent.resolve().is_relative_to(ROOT)
    CACHE.parent.mkdir(parents=True,exist_ok=True)
    print('FROZEN_IB',len(chosen),receipt['book_counts'],flush=True)


def locked():
    receipt=json.loads((WORK/'locked_receipt.json').read_text())
    assert r0.sha(OUT/'R0_locked_ib.jsonl')==receipt['manifest_sha256']
    rows=r0.read(OUT/'R0_locked_ib.jsonl')
    assert len(rows)==400 and {r['book'] for r in rows}==BOOKS
    for r in rows:assert r0.sha(r['crop'])==r['crop_sha256']
    return rows,receipt


def align():
    rows,receipt=locked();ckhash=receipt['execution']['checkpoint_sha256']
    assert r0.sha(r0.CKPT[0])==ckhash
    have={r['line_id']:r for r in r0.read(CACHE)} if CACHE.exists() else {}
    assert set(have)<={r['line_id'] for r in rows}
    for r in rows:
        if r['line_id'] in have:
            assert have[r['line_id']]['crop_sha256']==r['crop_sha256'] and have[r['line_id']]['checkpoint_sha256']==ckhash
    missing=[r for r in rows if r['line_id'] not in have];started=time.monotonic()
    if missing:
        rec=r0.Recognizer(r0.CKPT[0],device='cpu',threads=4)
        # Persist each batch so restarting does not re-forward completed crops.
        for start in range(0,len(missing),16):
            batch=missing[start:start+16]
            als=rec.align_paths([r['crop'] for r in batch],bs=16,log=lambda s:None)
            for r in batch:
                have[r['line_id']]=dict(crop=r['crop'],line_id=r['line_id'],crop_sha256=r['crop_sha256'],
                    checkpoint_sha256=ckhash,alignment=als[r['crop']].to_record(),origin='R0a3_CPU_forward',stratum='wikisource_ib')
            r0.write(CACHE,[have[r['line_id']] for r in rows if r['line_id'] in have])
            print('CTC aligned',len(have),'/',len(rows),flush=True)
    result=dict(schema='r0-ib-align-v1',locked_crops=len(rows),new_forward_crops=len(missing),
        total_R0a3_forward_crops=len(rows),reused_ib_cache_crops=len(rows)-len(missing),
        checkpoint=str(r0.CKPT[0]),checkpoint_sha256=ckhash,model='E3 full_s0',cpu_only=True,
        device='cpu',threads=4,batch_size=16,network=False,only_frozen_ib_forward=True,
        code_path='Recognizer.align_paths -> align_batch -> masked_forward -> frames_to_spans; unchanged R0a/666 code',
        code_sha256=r0.sha(ROOT/'greekocr/labelfix/ctc_align.py'),elapsed_seconds=time.monotonic()-started,
        frozen_manifest_sha256=receipt['manifest_sha256'],cache=str(CACHE.relative_to(ROOT)),sha256=r0.sha(CACHE))
    r0.dump(CACHE.with_suffix('.receipt.json'),result)


def aligned():
    rows,_=locked();cache=r0.read(CACHE)
    assert [r['line_id'] for r in cache]==[r['line_id'] for r in rows]
    als={r['line_id']:r0.Alignment.from_record(r['alignment']) for r in cache}
    for r in rows:r['model']=als[r['line_id']].prediction
    return rows,als


def extract():
    from scripts.labelfix.clariden.r1_extract import extract as run
    rows,_=aligned()
    path=WORK/'r1_selection.jsonl'
    r0.write(path,[dict(id=r['line_id'],doc=r['doc'],crop=r['crop'],recogniser_text=r['model'],label=r['google']) for r in rows])
    # crop_path deliberately canonicalizes absolute roots; pass the read-only
    # harvest root so the unchanged extractor resolves these external inputs.
    run(path,CACHE,EXTRACTION,HARVEST.parents[2],mode='heldout',workers=1)
    (WORK/'r1_extraction').mkdir(exist_ok=True)
    (WORK/'r1_extraction/extraction_receipt.json').write_bytes((EXTRACTION/'extraction_receipt.json').read_bytes())


def predict(checkpoint):
    import torch
    from scripts.labelfix.clariden.r1_train import Shards, predict as run
    from scripts.labelfix.clariden.r1_common import verify_receipt
    from scripts.labelfix.clariden.r1_model import MarkReader
    assert checkpoint and checkpoint.is_file(), 'Pass the trained R1-A checkpoint with --r1-checkpoint'
    assert r0.sha(checkpoint)==EXPECTED_R1, 'R1-A production checkpoint binding mismatch'
    verify_receipt(EXTRACTION)
    torch.set_num_threads(4)
    saved=torch.load(checkpoint,map_location='cpu',weights_only=False)
    model=MarkReader(embedding=True)
    model.load_state_dict(saved['model']);model.eval()
    started=time.monotonic()
    run(model,Shards(EXTRACTION,'A'),WORK/'r1_A_predictions.jsonl',torch.device('cpu'),128,0,checkpoint,'A')
    r0.dump(WORK/'r1_inference_receipt.json',dict(checkpoint=str(checkpoint),checkpoint_sha256=r0.sha(checkpoint),
        arm='A',device='cpu',threads=4,elapsed_seconds=time.monotonic()-started,training=False,
        extraction_unchanged=True,ctc_forward_passes=0,lines=400))


def detector():
    from greekocr.labelfix.reading import read_ink
    from greekocr.labelfix import ink,markshape
    from scripts.labelfix.s6_validate import detected
    rows,als=aligned();model=markshape.load_model(ROOT/'docs/records/labelfix/markshape_model_S4.json')
    output=[]
    for i,r in enumerate(rows):
        with Image.open(r['crop']) as im:reading=read_ink(ink.analyse(im),r['model'],als[r['line_id']],model,filtered=False,substitutions=frozenset())
        output.append(dict(line_id=r['line_id'],text=reading.text,slots=[dict(start=s['start'],base=s['base'],
            parts=s['parts'],apostrophe=s.get('apostrophe',False),unnamed=s.get('unnamed',False),
            localisation_unknown=s.get('localisation_unknown',False),detected=detected(dict(s,evidence=s['evidence'].to_record()))) for s in reading.slots]))
        if i%100==0:print('S6 detector',i,'/',len(rows),flush=True)
    r0.write(WORK/'s6_detector.jsonl',output)
    r0.dump(WORK/'s6_receipt.json',dict(lines=len(rows),model='markshape_model_S4.json',filtered=False,
        output='print',substitutions=[],constraints=False,ctc_forward_passes=0,
        function='read_ink; S6 raw detector contract (no label input)',sha256=r0.sha(WORK/'s6_detector.jsonl')))


def marked_form(text, predictions, detector_slots=None):
    """Compose only observed head/detector marks on native recogniser bases.

    Missing R1 windows remain UNKNOWN, never implicitly voted as no mark.
    The recogniser's combining marks are not candidates in the MARK deck.
    """
    from scripts.labelfix.clariden.r1_common import LETTERS, MARKS
    out=[];unknown=[]
    for c in r0.clusters(text):
        if c.base in "'’ʼ᾽᾿":
            # Neither instrument inherits an elision reading from CTC.
            # S6 appends only independently detected apostrophes below; R1
            # has no apostrophe head, so it never votes in that domain.
            continue
        if detector_slots is not None:
            s=detector_slots.get(c.start)
            if not c.base.isalpha():out.append(c.base);continue
            if s is None or s['localisation_unknown'] or s['unnamed']:
                unknown.append(dict(start=c.start,reason='S6_unnamed_or_unlocalised'))
            parts=s['parts'] if s else []
            out.append(c.base+''.join(MARKS[p] for p in parts if p in MARKS))
            if s and s['apostrophe']:out.append('’')
        else:
            s=predictions.get(c.start)
            if c.base in LETTERS and s is None:
                unknown.append(dict(start=c.start,reason='R1_window_not_scored'))
            out.append(c.base+''.join(MARKS[p] for p in (s['cls'].split('+') if s else []) if p in MARKS))
    return r0.nfc(''.join(out)),unknown


def mark_signature(form, anchor):
    """Sparse per-letter mark sets aligned to model-word base positions.

    A plain letter disagreement alone does not create a mark disagreement.
    Inserted marked letters and elision signs have explicit positions.
    """
    ac=[c for c in r0.clusters(anchor) if c.base.isalpha()]
    fc=[c for c in r0.clusters(form) if c.base.isalpha()]
    path=r0.align_chars(''.join(c.base for c in fc),''.join(c.base for c in ac))
    pos={i:j for i,j in path if i is not None}
    marks=[]
    for i,c in enumerate(fc):
        if c.marks:marks.append((str(pos.get(i)) if pos.get(i) is not None else 'insert:'+str(i),''.join(sorted(set(c.marks)))))
    # S2 treats an elision apostrophe as a separate mark kind.
    for i,c in enumerate(r0.clusters(form)):
        if c.base in "'’ʼ᾽᾿":
            before=sum(q.base.isalpha() for q in r0.clusters(form)[:i])-1
            marks.append(('apostrophe:'+str(pos.get(before,before)),'apostrophe'))
    return sorted(marks)


def plan():
    rows,als=aligned()
    letters,letter_controls,lmap,_=r0.planned_cards(rows,als,work=WORK)
    for c in letters:c['kind']='LETTER'
    predictions=defaultdict(dict)
    for p in r0.read(WORK/'r1_A_predictions.jsonl'):predictions[p['line_id']][p['start']]=p
    s6={r['line_id']:r for r in r0.read(WORK/'s6_detector.jsonl')}
    marks=[];mark_controls=[];census=[];word_count=0
    for l in rows:
        ds={s['start']:s for s in s6[l['line_id']]['slots']}
        for gi,g in enumerate(r0.word_groups(l)):
            word_count+=1
            a,b=g['start'],g['end'];native=l['model'][a:b]
            # Offsets of both independent instruments remain native CTC offsets.
            rp={p-a:v for p,v in predictions[l['line_id']].items() if a<=p<b}
            sp={p-a:v for p,v in ds.items() if a<=p<b}
            rf,ru=marked_form(native,rp)
            sf,su=marked_form(native,{},sp)
            forms={k:r0.nfc(v) for k,v in g['forms'].items() if k in ('google','human')}
            # Keep incomplete instruments in the census but never invent a vote.
            if not ru:forms['R1-A']=rf
            if not su:forms['S6']=sf
            unknown=ru+su
            word_id=l['line_id']+'|'+str(gi)
            elision="'’ʼ᾽᾿"
            # Combining marks: all four sources, with elision signs removed from
            # every candidate. Elision: only the three instruments that observe
            # it. No CTC punctuation can become a MARK vote or candidate.
            domains=[('diacritics',{k:''.join(c for c in v if c not in elision) for k,v in forms.items()})]
            apostrophe_forms={k:v for k,v in forms.items() if k!='R1-A'}
            if any(any(c in elision for c in v) for v in apostrophe_forms.values()):
                domains.append(('apostrophe',apostrophe_forms))
            for domain,domain_forms in domains:
                signatures={k:[p for p in mark_signature(v,native) if domain!='apostrophe' or p[0].startswith('apostrophe:')]
                    for k,v in domain_forms.items()}
                diff=len({json.dumps(v,ensure_ascii=False) for v in signatures.values()})>1
                # Unnamed/localisation failures also require a print review.
                domain_unknown=unknown if domain=='diacritics' else su
                needs=diff or bool(domain_unknown)
                group_id=word_id+'|'+domain
                census.append(dict(group_id=group_id,word_group_id=word_id,mark_domain=domain,line_id=l['line_id'],start=a,end=b,model_words=g['model_words'],
                    forms=domain_forms,mark_signatures=signatures,mark_disagreement=diff,instrument_unknown=domain_unknown,
                    R1_partial_form=rf if ru else None,S6_partial_form=sf if su else None,needs_card=needs))
                if needs:
                    distinct=list(dict.fromkeys(domain_forms.values()))
                    # A second panel retains a fourth distinct form while every
                    # card stays within the original A/B/C candidate contract.
                    panels=[distinct[:3]]
                    if len(distinct)>3:panels.append([distinct[0]]+distinct[3:])
                    for pi,values in enumerate(panels):
                        marks.append(dict(line_id=l['line_id'],start=a,end=b,kind='MARK',mark_domain=domain,
                            kinds=['mark_word_disagreement' if diff else 'mark_instrument_unknown'],
                            group_id=group_id,word_group_id=word_id,panel=pi+1,panels=len(panels),model_words=g['model_words'],
                            forms={k:v for k,v in domain_forms.items() if v in values},control=False,instrument_unknown=domain_unknown))
            if not unknown and len(forms)==4 and len(set(forms.values()))==1:
                answer=next(iter(forms.values()))
                if len(r0.letters(answer))>=3 and any(U.category(c).startswith('M') for c in r0.nfd(answer)):
                    mark_controls.append(dict(line_id=l['line_id'],start=a,end=b,model_words=g['model_words'],
                        correct=answer,kind='MARK',agreement_sources=sorted(forms)))
    for c in letter_controls:c['kind']='LETTER'
    r0.write(WORK/'mark_word_census.jsonl',census)
    r0.write(WORK/'mark_card_plan.jsonl',marks)
    r0.write(WORK/'combined_card_plan.jsonl',letters+marks)
    r0.write(WORK/'mark_control_candidates.jsonl',mark_controls)
    r0.dump(WORK/'combined_plan_receipt.json',dict(letter_cards=len(letters),mark_cards=len(marks),
        mark_disagreement_words=len({c['word_group_id'] for c in census if c['mark_disagreement']}),
        mark_unknown_words=len({c['word_group_id'] for c in census if c['instrument_unknown']}),
        words_requiring_mark_review=len({c['word_group_id'] for c in census if c['needs_card']}),total_word_groups=word_count,
        domain_groups=len(census),cards_by_domain=dict(Counter(c['mark_domain'] for c in marks)),
        multi_panel_words=len({c['group_id'] for c in marks if c['panels']>1}),
        letter_controls_needed=math.ceil(len(letters)*.08/.92),mark_controls_needed=math.ceil(len(marks)*.08/.92),
        letter_controls_available=len(letter_controls),mark_controls_available=len(mark_controls),
        mark_sources=['Google','human','R1-A','S6'],recogniser_marks_used_as_candidate=False,
        recogniser_punctuation_used_as_mark_candidate=False,R1_apostrophe_head=False,
        mark_contract='Combining marks: Google/human/R1-A/S6, elision removed from all candidates. Elision: Google/human/S6 only; R1 has no such head. Sparse NFD mark sets base-aligned to native model word. Unnamed/unlocalised S6 and missing R1 windows are UNKNOWN and always reviewed. Four distinct forms use two panels, each <=3.',
        plan_sha256=r0.sha(WORK/'combined_card_plan.jsonl')))
    print(json.dumps(json.loads((WORK/'combined_plan_receipt.json').read_text())),flush=True)


def preview():
    rows,als=aligned();lmap={r['line_id']:r for r in rows}
    summary=json.loads((WORK/'combined_plan_receipt.json').read_text())
    rng=random.Random(r0.SEED);queue=[]
    for kind,path in [('LETTER','control_candidates.jsonl'),('MARK','mark_control_candidates.jsonl')]:
        candidates=r0.read(WORK/path);rng.shuffle(candidates)
        required=summary[kind.lower()+'_controls_needed']
        chosen=candidates[:required+min(12,max(0,len(candidates)-required))]
        for i,c in enumerate(chosen):
            queue.append(dict(c,control_id=kind.lower()+f'{i:03d}',kind=kind))
    r0.write(WORK/'control_review_queue.jsonl',queue)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',20)
    for start in range(0,len(queue),12):
        sheet=Image.new('RGB',(1700,12*145),'#eeeeee');draw=ImageDraw.Draw(sheet)
        for j,c in enumerate(queue[start:start+12]):
            l=lmap[c['line_id']]
            with Image.open(l['crop']) as im:
                x0,x1=als[c['line_id']].window(c['start'],c['end']);pad=.2*im.height
                zoom=im.crop((max(0,int(x0-pad)),0,min(im.width,math.ceil(x1+pad)),im.height)).convert('RGB')
            scale=min(2,1100/zoom.width,120/zoom.height)
            zoom=zoom.resize((round(zoom.width*scale),round(zoom.height*scale)))
            sheet.paste(zoom,(550,j*145+15))
            draw.text((8,j*145+10),c['control_id']+' '+c['correct'],font=font,fill='black')
        sheet.save(WORK/f'control_review_{start//12:02d}.png')
    print('Review queue',len(queue),'required',summary['letter_controls_needed'],summary['mark_controls_needed'],flush=True)


def cards():
    rows,als=aligned();lmap={r['line_id']:r for r in rows}
    items=r0.read(WORK/'combined_card_plan.jsonl')
    summary=json.loads((WORK/'combined_plan_receipt.json').read_text())
    verified=r0.read(WORK/'controls_pixel_verified.jsonl')
    queue={r['control_id']:r for r in r0.read(WORK/'control_review_queue.jsonl')}
    for kind in ('LETTER','MARK'):
        controls=[c for c in verified if c['kind']==kind]
        assert len(controls)>=summary[kind.lower()+'_controls_needed']
        for ci,c in enumerate(controls[:summary[kind.lower()+'_controls_needed']]):
            assert all(c[k]==v for k,v in queue[c['control_id']].items())
            assert c['pixel_verified'] and c['correct']
            answer=r0.nfc(c['correct'])
            if kind=='LETTER':
                positions=[i for i,v in enumerate(answer) if v.isalpha()];at=positions[ci%len(positions)]
                confusable={'α':'ο','ο':'σ','σ':'ο','ς':'σ','ν':'υ','υ':'ν','η':'π','π':'η',
                    'ε':'ο','ρ':'β','β':'ρ','τ':'γ','γ':'τ','χ':'κ','κ':'χ','ι':'η',
                    'ξ':'ζ','ζ':'ξ','δ':'θ','θ':'δ','λ':'μ','μ':'λ','ω':'ο'}
                replacement=answer[at].swapcase() if ci%3==0 else confusable.get(answer[at].lower(),'β')
                if answer[at].isupper() and ci%3:replacement=replacement.upper()
                fake=answer[:at]+replacement+answer[at+1:]
            else:
                text=r0.nfd(answer);at=next(i for i,v in enumerate(text) if U.category(v).startswith('M'))
                replacement={'\u0313':'\u0314','\u0314':'\u0313','\u0301':'\u0300','\u0300':'\u0301',
                    '\u0342':'\u0301','\u0345':'','\u0308':''}.get(text[at],'')
                fake=r0.nfc(text[:at]+replacement+text[at+1:])
            assert answer!=fake
            items.append(dict(c,kinds=['planted_'+kind.lower()+'_control'],control=True,
                forms=dict(pixel_verified=answer,planted_wrong=fake),known_answer=answer))
    rng=random.Random(r0.SEED);rng.shuffle(items)
    card_dir=OUT/'R0_cards_ib';(card_dir/'img').mkdir(parents=True,exist_ok=True)
    assert not (PRIVATE/'items_key.json').exists(), 'Private key is write-once'
    blind=[];key=[];truth=[];line_images={}
    for i,it in enumerate(items):
        ident=f'ib_item{i:05d}';l=lmap[it['line_id']]
        if it['line_id'] not in line_images:
            p=f'img/line{len(line_images):04d}.png'
            with Image.open(l['crop']) as im:im.save(card_dir/p)
            line_images[it['line_id']]=p
        box=r0.card_window(it,l,als[it['line_id']])
        with Image.open(l['crop']) as im:crop=im.crop(box).convert('RGB')
        scale=min(3.,900/max(1,crop.width))
        crop=crop.resize((max(1,round(crop.width*scale)),max(1,round(crop.height*scale))),Image.Resampling.LANCZOS)
        zoom='img/'+ident+'.png';crop.save(card_dir/zoom)
        forms=list(dict.fromkeys(r0.nfc(f) for f in it['forms'].values()))
        assert 1<=len(forms)<=3,(it,forms)
        rng.shuffle(forms)
        b=dict(id=ident,img=zoom,line_img=line_images[it['line_id']],**{chr(65+j):v or '∅' for j,v in enumerate(forms)})
        blind.append(b)
        key.append(dict(b,**it,zoom_scale=scale,crop_box=list(box),source_crop_sha256=l['crop_sha256'],
            candidate_sources={chr(65+j):[s for s,v in it['forms'].items() if r0.nfc(v)==f] for j,f in enumerate(forms)},
            expected_choice=(chr(65+forms.index(it['known_answer'])) if it['control'] else None)))
        truth.append(dict(id=ident,reader_1=dict(choice=None,transcription=None,full_line_letters=None,full_line_marks=None,uncertain=None,note=None),
            reader_2=dict(choice=None,transcription=None,full_line_letters=None,full_line_marks=None,uncertain=None,note=None),
            adjudicated=dict(choice=None,transcription=None,status='PENDING_R0b',evidence=None)))
    r0.dump(card_dir/'items_blind.json',blind)
    PRIVATE.mkdir(parents=True,exist_ok=True)
    key_bytes=(json.dumps(key,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    with (PRIVATE/'items_key.json').open('xb') as f:f.write(key_bytes)
    r0.dump(OUT/'R0_expected_truth_ib.json',truth)
    r0.write(OUT/'R0_line_truth_placeholders_ib.jsonl',[dict(line_id=l['line_id'],doc=l['doc'],stratum=l['stratum'],
        full_line_letter_truth=None,full_line_mark_truth=None,case_folded_truth=None,apostrophe_quote_truth=None,status='PENDING_R0b',
        unresolved_card_ids=[r['id'] for r in key if r['line_id']==l['line_id'] and not r['control']],
        caution='Agreement and adjudicating only differences do not establish full-line print truth.') for l in rows])
    # R0a's offline layout, candidate/answer schema, export and local notes flow.
    viewer='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>R0 blind cards</title><style>body{font:18px Georgia;margin:20px;background:#f5f3ed}article{background:white;padding:16px;margin:18px 0;overflow:auto}img{display:block;max-width:100%;height:auto;margin:10px 0}button{font:24px Georgia;margin:6px;padding:8px}textarea{display:block;width:95%;height:60px}.full{max-width:none}details{overflow:auto}</style>
<h1>R0 blind cards</h1><p>Read the zoom and full line. Select the literal printed form; write a correction or uncertainty when needed. For marked forms, read every printed mark. For plain letter forms, preserve case and script. Notes save locally in this browser.</p>
<button id="export">Export answers</button><main id="cards"></main><script>
const items=ITEMS;const answers=JSON.parse(localStorage.getItem('r0-blind-ib-v1')||'{}');
function save(){localStorage.setItem('r0-blind-ib-v1',JSON.stringify(answers))}for(const it of items){let a=document.createElement('article');let h=document.createElement('h2');h.textContent=it.id;a.append(h);for(const src of [it.img,it.line_img]){let im=document.createElement('img');im.loading='lazy';im.src=src;im.alt=src===it.img?'Target crop':'Full line';if(src===it.line_img){im.className='full';let d=document.createElement('details'),s=document.createElement('summary');d.open=true;s.textContent='Full line';d.append(s,im);a.append(d)}else a.append(im)}for(const k of ['A','B','C'])if(it[k]!==undefined){let b=document.createElement('button');b.textContent=k+': '+it[k];b.onclick=()=>{answers[it.id]={...(answers[it.id]||{}),choice:k};save();a.dataset.choice=k;a.style.border='2px solid #276'};a.append(b)}let t=document.createElement('textarea');t.placeholder='Literal correction / uncertainty / note';t.value=answers[it.id]?.note||'';t.oninput=()=>{answers[it.id]={...(answers[it.id]||{}),note:t.value};save()};a.append(t);document.querySelector('main').append(a)}document.querySelector('#export').onclick=()=>{let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(answers,null,2)],{type:'application/json'}));a.download='R0_ib_reader_answers.json';a.click()};</script>'''
    (card_dir/'index.html').write_text(viewer.replace('ITEMS',json.dumps(blind,ensure_ascii=False).replace('</','<\\/')))
    (card_dir/'README.md').write_text('''# R0b blind adjudication: IB

Give each independent reader only R0_cards_ib/ and a blank R0_expected_truth_ib.json.
Keep the private key, report, original identifiers and other evidence away from readers.
Read both zoom (at most 3x native) and full line for every item. Choose the literal
printed form, or transcribe a correction when all candidates fail; ∅ means no text/sign.
Marked candidates: include every printed accent, breathing, dialytika, subscript and
elision apostrophe. Plain letter candidates: ignore diacritics, retain case, script,
word boundaries and punctuation. A one-option item still requires a pixel reading:
an instrument could not name/localise a mark; the offered form is not presumed true.
Report clipping, overruns, ligatures/editorial expansion and uncertainty explicitly.
Do not infer truth from label agreement or majority. Two readers work independently;
the track lead privately scores controls and resolves disagreements against pixels.
Full-line letter and mark truth stays pending until explicitly established. Do not
use this locked comparison set for training or any policy/checkpoint/threshold tuning.
''')
    counts=Counter(r['kind'] for r in key if not r['control']);controls=Counter(r['kind'] for r in key if r['control'])
    receipt=dict(blind_items=len(blind),adjudication_cards=sum(counts.values()),controls=sum(controls.values()),
        by_kind=dict(counts),controls_by_kind=dict(controls),control_fraction=sum(controls.values())/len(blind),
        seed=r0.SEED,source_labels_hidden=True,control_flags_hidden=True,max_zoom=3,
        blind_sha256=r0.sha(card_dir/'items_blind.json'),key_sha256=hashlib.sha256(key_bytes).hexdigest(),
        private_key='../R0_adjudication_private/ib/items_key.json',
        lines_with_cards=len(line_images),truth_status='PENDING_R0b; no print outcomes inferred')
    assert receipt['control_fraction']>=.08
    r0.dump(WORK/'cards_receipt.json',receipt)
    print(json.dumps(receipt),flush=True)


def finish():
    from PIL import ImageChops
    rows,locked_receipt=locked()
    cr=json.loads((WORK/'cards_receipt.json').read_text())
    spans=json.loads((WORK/'span_summary.json').read_text())
    binding_record=json.loads((WORK/'input_binding.json').read_text())
    for p,h in binding_record['files'].items():assert r0.sha(ROOT/p)==h,p
    assert r0.sha(r0.CKPT[0])==binding_record['checkpoint_sha256']
    for p,h in binding_record['harvest_files'].items():assert r0.sha(HARVEST/p)==h,p
    combined=json.loads((OUT/'R0_locked_set_receipt.json').read_text())
    assert {k:v for k,v in combined.items() if k!='stratum_ib'}==json.loads((WORK/'original_ia_receipt.json').read_text())
    assert combined['stratum_ib']==locked_receipt
    assert r0.sha(OUT/'R0_locked_set.jsonl')==combined['locked_set_sha256']
    assert r0.sha(OUT/'R0_locked_ia_ids.txt')==combined['release_exclusion_ids_sha256']
    ar=json.loads(CACHE.with_suffix('.receipt.json').read_text())
    assert r0.sha(CACHE)==ar['sha256'] and ar['total_R0a3_forward_crops']==400
    cached=r0.read(CACHE);lmap={r['line_id']:r for r in rows}
    for c in cached:
        assert c['checkpoint_sha256']==binding_record['checkpoint_sha256']
        assert c['crop_sha256']==lmap[c['line_id']]['crop_sha256']
    extraction=json.loads((EXTRACTION/'extraction_receipt.json').read_text())
    assert r0.sha(EXTRACTION/'extraction_receipt.json')==r0.sha(WORK/'r1_extraction/extraction_receipt.json')
    predictions=r0.read(WORK/'r1_A_predictions.jsonl')
    assert len(predictions)==extraction['samples']==len({r['sample_id'] for r in predictions})
    assert {r['line_id'] for r in predictions}<=set(lmap)
    assert {r['id'] for r in r0.read(EXTRACTION/'lines.jsonl.gz')}==set(lmap)
    assert r0.sha(CACHE.parent/'r1_A_best.pt')==EXPECTED_R1
    blind=json.loads((OUT/'R0_cards_ib/items_blind.json').read_text())
    key=json.loads((PRIVATE/'items_key.json').read_text())
    assert r0.sha(PRIVATE/'items_key.json')==cr['key_sha256']
    assert r0.sha(OUT/'R0_cards_ib/items_blind.json')==cr['blind_sha256']
    assert len(blind)==len(key)==cr['blind_items']
    for b,k in zip(blind,key):
        assert b['id']==k['id']
        assert set(b)<={'id','img','line_img','A','B','C'}
        assert 1<=sum(c in b for c in 'ABC')<=3 and k['zoom_scale']<=3
        if k['control']:assert b[k['expected_choice']]==k['known_answer']
        for name in ('img','line_img'):
            with Image.open(OUT/'R0_cards_ib'/b[name]) as im:im.verify()
    for image_path,lid in {r['line_img']:r['line_id'] for r in key}.items():
        with Image.open(OUT/'R0_cards_ib'/image_path) as a,Image.open(lmap[lid]['crop']) as b:
            assert a.size==b.size and ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox() is None
    census=r0.read(WORK/'mark_word_census.jsonl');planrows=r0.read(WORK/'mark_card_plan.jsonl')
    for c in planrows:
        assert 'model' not in c['forms']
        if c['mark_domain']=='apostrophe':assert 'R1-A' not in c['forms']
        else:assert all(not any(ch in "'’ʼ᾽᾿" for ch in v) for v in c['forms'].values())
    assert {r['group_id'] for r in census if r['needs_card']}=={r['group_id'] for r in planrows}
    for c in census:
        if c['needs_card']:
            covered={v for r in planrows if r['group_id']==c['group_id'] for v in r['forms'].values()}
            assert covered==set(c['forms'].values())
    assert len(r0.read(WORK/'span_line_census.jsonl'))==400
    assert len(r0.read(WORK/'span_slots.jsonl.gz'))==spans['pooled']['all_alphabetic_slots']
    qa=json.loads((WORK/'visual_qa.json').read_text())
    assert qa['control_zooms_inspected']>=cr['controls']
    dom=json.loads((WORK/'viewer_dom_validation.json').read_text())
    assert dom['complete'] and dom['cards']==len(blind)
    validation=dict(complete=True,lines=400,books=5,all_requested_intersections_zero=True,
        collection_v2_all_three_splits_zero=True,manifest_and_crop_hashes_valid=True,
        unchanged_runtime_and_shared_caches=True,unchanged_ia_artifacts_and_receipt_fields=True,
        all_blind_images_decode=True,all_mark_disagreement_and_unknown_groups_covered=True,
        all_distinct_mark_candidates_covered=True,source_and_control_labels_hidden=True,
        full_line_images_native_pixel_identical=True,R1_no_apostrophe_vote_or_candidate=True,
        offline_viewer_dom_checks=dom,
        control_fraction=cr['control_fraction'],visual_qa=qa,network=False,
        full_line_print_truth='PENDING two-reader adjudication; no scores produced')
    r0.dump(WORK/'validation.json',validation)
    plan_summary=json.loads((WORK/'combined_plan_receipt.json').read_text())
    ex=json.loads((WORK/'r1_extraction/extraction_receipt.json').read_text())
    inf=json.loads((WORK/'r1_inference_receipt.json').read_text())
    p=spans['pooled']
    counts=', '.join(f'{k} {v}' for k,v in locked_receipt['book_counts'].items())
    ready=(f'R0a3 READY: stratum (i-b) 400 lines / 5 books ({counts}); zero overlap with 666, DEV, L1 input, (ii), (i-a), local books, v2 val; '
        f"cards {cr['adjudication_cards']} (+controls {cr['controls']}); spans outside blob {p['outside_pct']:.4f}%")
    section='\n\n## R0a3 — clean locked Wikisource stratum (i-b)\n\n'
    section+=f"Frozen **400 complete polytonic lines / 5 books**, seed 20261017. Eligible pool: {locked_receipt['eligible_lines']} / 1,246 harvest lines; "
    section+='the R0a one-to-one human alignment, whole-crop and NFD polytonic admission rules are unchanged. Proportional largest-remainder quotas, stable line-ID order and seeded sampling were reproduced; no model output influenced admission.\n\n'
    section+='| Book hash | Eligible | Drawn |\n|---|---:|---:|\n'
    for book,n in locked_receipt['book_counts'].items():section+=f"| {book} | {locked_receipt['eligible_by_book'][book]} | {n} |\n"
    section+='\nMaximum share **39.5%**. [Frozen lines](R0_locked_ib.jsonl), [IDs](R0_locked_ib_ids.txt), [receipt](R0_locked_set_receipt.json), [input bindings](R0_evidence/ib/input_binding.json). Existing (i-a) receipt fields and its selection-exposed v2-val warning are preserved.\n\n'
    section+='| Intersection against | Comparison rows | Matching rows / books |\n|---|---:|---:|\n'
    for name,v in locked_receipt['zero_intersections'].items():section+=f"| {name} | {v['comparison_rows']} | 0 |\n"
    for split in ('train','test'):section+=f"| collection_v2_{split} | {locked_receipt['collection_v2_all_splits'][split]['comparison_rows']} | 0 |\n"
    section+='\nChecks use exact and prefix-normalized line IDs, document IDs, and the bare book hashes in **both `id` and `doc`**; all three v2 files were independently streamed. Crop hashes are also disjoint from 666, DEV, (ii), (ii)-development and (i-a). L1 input and local20 are document/book inventories; no crop-equivalence claim is made for them or v2. These checks cannot identify undocumented copies/editions. [Full intersection receipts](R0_evidence/ib/locked_receipt.json).\n\n'
    section+='**Never tune:** (i-b) judges L1 and wave 1c; never use it for training or policy/checkpoint/threshold selection. Keep selection-exposed (i-a) separate. The 666 remain the continuity instrument. All 1,246 harvest rows remain subject to the sourcing lead’s release exclusion; this task does not alter that manifest.\n\n'
    section+='Google labels come from the harvest `pages.jsonl` Google geometry line text, indexed by the recorded Google line index and checked against `alignment.google_text` and the Google bbox. Human labels come from `lines.jsonl`; literal and NFC fields are retained, with NFD used for processing. Human reference wording is not established print truth.\n\n'
    section+=f"**400 E3 full_s0 CPU forwards**, only on the frozen crops, unchanged `Recognizer.align_paths`/`masked_forward`; four threads, batches of 16. [Alignment receipt](../../../.cache/labelfix/r0/align_locked_ib.receipt.json). "
    section+=f"Native span census: **{p['outside']} / {p['clean_slots']} clean one-blob/one-character alphabetic slots = {p['outside_pct']:.4f}% outside blob**; {p['all_alphabetic_slots']} alphabetic slots censused in total. "
    section+='The clean-slot rate is a geometry diagnostic using runtime CTC-overlap ownership, not independent glyph identity or a letter error rate. Nonclean slots, marks, spaces and punctuation remain explicitly counted. [Summary by script, size and book](R0_evidence/ib/span_summary.json), [all slots](R0_evidence/ib/span_slots.jsonl.gz), [line census](R0_evidence/ib/span_line_census.jsonl).\n\n'
    section+=f"R1-A production checkpoint `{inf['checkpoint_sha256']}` ran on CPU with the **unchanged R1 full-height extraction**: {ex['samples']} / {ex['counts']['vowel_rho_slots']} vowel/rho windows ({100*ex['coverage']:.2f}% coverage), no training or extra CTC. "
    section+='Unscored windows stay UNKNOWN. S6 uses the unchanged raw `read_ink` detector, S4 markshape asset, no filtering/constraints or geometry substitutions, and no Google/human input. [Extraction](R0_evidence/ib/r1_extraction/extraction_receipt.json), [R1 inference](R0_evidence/ib/r1_inference_receipt.json), [S6 receipt](R0_evidence/ib/s6_receipt.json).\n\n'
    section+=f"The [mixed blind deck](R0_cards_ib/index.html) contains **{cr['by_kind']['LETTER']} LETTER + {cr['by_kind']['MARK']} MARK adjudication cards**, plus **{cr['controls_by_kind']['LETTER']} letter + {cr['controls_by_kind']['MARK']} mark planted controls** ({100*cr['control_fraction']:.2f}% overall). "
    section+=f"Mark coverage includes all {plan_summary['mark_disagreement_words']} differing word groups and {plan_summary['mark_unknown_words']} groups with unnamed/unlocalised detector marks or unscored R1 windows; groups can overlap. "
    multi=plan_summary['multi_panel_words']
    section+=f"{multi} word group{'s' if multi!=1 else ''} require{'s' if multi==1 else ''} two panels to cover all four distinct source forms without exceeding three candidates per card. "
    section+='The recogniser locates MARK windows only; its marks never vote or supply mark candidates. Combining-mark forms use all four sources with elision signs removed from every candidate; separate elision cards use Google/human/S6 only because R1-A has no apostrophe head. Candidate order and item order are seeded and shuffled, source/control labels and kinds stay in the private IB key, zooms are at most 3x, and every card includes the full native line. Controls were read against pixels before planting a single letter or mark change. [Plan/coverage receipt](R0_evidence/ib/combined_plan_receipt.json), [card receipt](R0_evidence/ib/cards_receipt.json), [validation](R0_evidence/ib/validation.json).\n\n'
    section+='**Print truth remains PENDING:** two independent readers and pixel tiebreak are required. Difference cards alone do not establish full-line truth or eliminate shared errors; no mark/letter accuracy is claimed here. Blank [reader slots](R0_expected_truth_ib.json) and [line truth placeholders](R0_line_truth_placeholders_ib.jsonl) are supplied. Runtime, checkpoints, shared alignment caches, harvest inputs and existing IA receipt fields were verified unchanged. Network stayed off; no Git mutation was used. Representative final zooms/full lines and every planted control were visually inspected; all full-line images are native-pixel identical. Viewer JavaScript syntax and DOM interactions were checked locally. Browser render QA was unavailable (empty browser inventory; in-app browser unavailable), so no browser-render claim is made.\n\n'
    section+=ready+'\n'
    report=OUT/'R0_REPORT.md';text=report.read_text();marker='\n\n## R0a3 — clean locked Wikisource stratum (i-b)'
    report.write_text(text.split(marker)[0]+section)
    (WORK/'READY.txt').write_text(ready+'\n')
    print(ready,flush=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stage',choices=['freeze','align','spans','extract','predict','detector','plan','preview','cards','finish'])
    ap.add_argument('--r1-checkpoint',type=Path)
    a=ap.parse_args()
    if a.stage=='spans':
        rows,als=aligned();r0.audit_spans(rows,als,work=WORK)
    elif a.stage=='predict':predict(a.r1_checkpoint)
    else:globals()[a.stage]()


if __name__=='__main__':main()
