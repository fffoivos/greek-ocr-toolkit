"""S8a frozen CPU baseline and blind print-truth cards, saved readers only.

Default: prepare baseline, census, controls review, cards when controls verified.
--masked: incorporate the sourcing handoff without any reader inference.
Audit all 48 released L1M lines, using their locally saved original/masked evidence.
"""
import os
import sys
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[name]='1'
os.environ.update(PYTHONDONTWRITEBYTECODE='1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',GIT_OPTIONAL_LOCKS='0')
sys.dont_write_bytecode=True
import argparse
from collections import Counter,defaultdict
from copy import deepcopy
import csv
import gzip
import hashlib
import html
import json
import math
from pathlib import Path
import random
import re
import socket
import subprocess
import time
import unicodedata as U
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from greekocr.labelfix import reading,ink,release_gate as gate,case,markshape
from greekocr.labelfix.ctc_align import Alignment,Recognizer
from greekocr.labelfix.candidates import align_chars
from greekocr.labelfix.text import nfd,nfc,clusters,ELISION,word_final_elision
from scripts.labelfix.clariden.l1_common import overlay

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/labelfix/spellcheck/S8_DEV'
E=OUT/'evidence'
L1=ROOT.parent/'greek-ocr-toolkit-spellcheck-l1/docs/labelfix/spellcheck/L1M_evidence'
MASK=ROOT.parent/'collect-v3-data/v2_masked/s8_dev'
FROZEN='c6064650fa5451cbc3bd13197d7a31c0d3bbf33d'
SEED='S8a-20261017'
METRICS=('localisation_unknown','segmentation_uncertain','clipped_top','clipped_bottom','unnamed')
MODES=('ENSEMBLE_AB','PRESENCE')
WAVES=('parliament','vouli','round1','round2','mixed')

def forbidden(*a,**kw):raise RuntimeError('S8a prohibits inference and network in preparation')
Recognizer.__init__=forbidden
Recognizer.align_batch=forbidden
socket.socket.connect=forbidden

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def dump(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def rows(p):
    with (gzip.open if str(p).endswith('.gz') else open)(p,'rt') as f:
        return [json.loads(s) for s in f if s.strip()]
def write(p,data):
    p=Path(p)
    if str(p).endswith('.gz'):
        raw=''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in data).encode()
        if not p.exists() or gzip.decompress(p.read_bytes())!=raw:p.write_bytes(gzip.compress(raw,mtime=0))
    else:
        with p.open('w') as f:
            for r in data:f.write(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n')
def bare(s):return ''.join(c for c in nfd(s) if not U.category(c).startswith('M'))
def literal(s):
    return ''.join(t if t in ('\u0374','\u0384') else nfc(t) for t in re.split('([\u0374\u0384])',s))

def elision_policy(forms):
    """Scoring metadata only: preserve all non-elision marks and printed keraia."""
    def without_elision(s):
        out=[]
        for t in re.split('([\u0374\u0384])',s):
            if t in ('\u0374','\u0384'):out.append(t);continue
            cs=clusters(nfd(t))
            out.append(''.join(c.base+c.marks for i,c in enumerate(cs) if not word_final_elision(cs,i)))
        return ''.join(out)
    differs=len(set(forms.values()))>1
    alias_only=differs and len({canon(v) for v in forms.values()})==1
    only=differs and len({without_elision(v) for v in forms.values()})==1
    return dict(elision_alias_only=only,alias_only=alias_only,
        elision_presence_only=only and not alias_only,
        scoring_policy='alias_only' if alias_only else 'elision_presence_only' if only else 'ordinary')

def canon(s):
    # NFC aliases U+0374 to U+02B9 and U+0384 to U+1FFD: protect printed keraia.
    chunks=re.split('([\u0374\u0384])',s)
    for j,t in enumerate(chunks):
        if t in ('\u0374','\u0384'):continue
        cs=clusters(nfd(t))
        chunks[j]=nfc(''.join('’' if word_final_elision(cs,i) else c.base+c.marks for i,c in enumerate(cs)))
    return ''.join(chunks)

def binding(extra_paths=()):
    assert gate.POLICY=='sf4-release-v1'
    paths={Path(m.__file__).resolve() for m in list(sys.modules.values())
        if getattr(m,'__file__',None) and str(m.__file__).endswith('.py')
        and str(Path(m.__file__).resolve()).startswith(str(ROOT/'greekocr')+'/')}
    paths.update((ROOT/'greekocr/labelfix').glob('*.py'))
    paths.update(ROOT/p for p in extra_paths)
    paths.update(ROOT/p for p in gate.policy_binding()['sources'])
    paths.update(ROOT/'docs/labelfix'/p for p in ('markshape_model_S4.json','case_model_S5.json'))
    hashes={}
    for p in sorted(paths):
        rel=str(p.relative_to(ROOT)); committed=subprocess.check_output(['git','--no-optional-locks','show',FROZEN+':'+rel],cwd=ROOT)
        assert p.read_bytes()==committed,('frozen source differs',rel)
        hashes[rel]=sha(p)
    return dict(commit=FROZEN,policy=gate.policy_binding(),sources=hashes,python=sys.version,executable=sys.executable)

def metrics(serial):
    c=Counter({k:0 for k in METRICS});hist=Counter()
    for s in serial['slots']:
        c['letters']+=1;n=len(s.get('component_ids',[]));hist[n]+=1;c['component_assignments']+=n
        for k in METRICS:c[k]+=int(bool(s.get('evidence',{}).get(k) if k.startswith('clipped_') else s.get(k)))
        c['unnamed_blobs']+=len(s.get('unnamed',[]))
    return dict(c,components_per_letter_histogram=dict(sorted(hist.items())))

def baseline(sources,remote,ids,use_masked):
    initial=binding();dump(E/'frozen_binding.json',initial)
    case.configure_model(ROOT/'docs/labelfix/case_model_S5.json')
    model=markshape.load_model(ROOT/'docs/labelfix/markshape_model_S4.json')
    bp=dict(detector='s6',r1_sha256='719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636',policy_sha256=initial['policy']['sha256'])
    staged={};mask_receipt=None
    if use_masked and (MASK/'receipt.json').exists():
        mr=load(MASK/'receipt.json');mp=MASK/'lines.jsonl';assert sha(mp)==mr['lines_sha256']
        staged={r['id']:r for r in rows(mp)}
        assert set(staged)<={k for k in ids if sources[k]['wave']!='parliament'}
        assert mr.get('status')=='completed' and mr['completed_pages']==mr['selected_pages']
        mask_receipt=dict(path=str(MASK/'receipt.json'),sha256=sha(MASK/'receipt.json'),receipt=mr,lines_sha256=sha(mp))
    result=[];start=time.monotonic()
    for i,k in enumerate(ids,1):
        src=sources[k];saved=remote['runtime'][k];al=Alignment.from_record(remote['alignments'][k]['alignment'])
        assert saved['historical_A_verified'] and nfd(saved['recogniser_text'])==al.prediction
        original=Path(src['original_path']);variants={'original':original}
        if k in staged:
            sr=staged[k];mp=MASK/sr['masked_path']
            assert sha(original)==sr['original_crop_sha256'] and sha(mp)==sr['masked_sha256']
            map_name=next((sr[a] for a in ('ownership_path','label_map_path','ownership_label_map','ownership_map_path','ownership_labels_path','ownership_label_map_path') if sr.get(a)),None)
            assert map_name,('missing 0-5 ownership map path',k)
            op=MASK/map_name
            if op.suffix=='.npy':labels=np.load(op,allow_pickle=False)
            elif op.suffix=='.npz':
                with np.load(op,allow_pickle=False) as z:
                    assert len(z.files)==1,('ambiguous ownership npz',op)
                    labels=z[z.files[0]]
            else:
                with Image.open(op) as im:labels=np.asarray(im)
            with Image.open(original) as oi,Image.open(mp) as mi:
                assert oi.size==mi.size and labels.shape==(oi.height,oi.width),(k,'masked/map dimensions differ')
            assert set(np.unique(labels))<=set(range(6)),(k,'ownership labels outside 0-5')
            for field in ('ownership_sha256','label_map_sha256','ownership_map_sha256','ownership_labels_sha256'):
                if field in sr:assert sha(op)==sr[field],(k,'ownership map hash differs')
            mask_receipt.setdefault('ownership_maps',{})[k]=dict(path=str(op),sha256=sha(op))
            variants['masked']=mp
        for name,p in variants.items():
            cache=E/'baseline'/name/(k+'.json.gz');crop_hash=sha(p)
            if cache.exists():
                record=json.loads(gzip.decompress(cache.read_bytes()))
                assert record['crop_sha256']==crop_hash and record['binding_sha256']==digest(initial)
                result.append(record);continue
            with Image.open(p) as im:ci=ink.analyse(im)
            serial=gate.serialize(reading.read_ink(ci,al.prediction,al,model,filtered=False))
            runtime={key:deepcopy(v) for key,v in saved.items() if key not in ('evidence_sha256','modes','historical_A_verified')}
            runtime['detector']=serial
            modes={mode:gate.compose_runtime(runtime,mode) for mode in MODES}
            decisions={mode:overlay(src,runtime,mode,bp) for mode in MODES}
            parity={}
            if name=='original' and k in remote.get('decisions',{}).get('ENSEMBLE_AB',{}):
                for mode in MODES:
                    old=remote['decisions'][mode][k];new=decisions[mode]
                    proj=lambda x:{a:x.get(a) for a in ('status','label','hold_slots')}
                    parity[mode]=digest(proj(old))==digest(proj(new))
            record=dict(id=k,wave=src['wave'],variant=name,crop=str(p),crop_sha256=crop_hash,
                crop_size=[ci.width,ci.height],binding_sha256=digest(initial),metrics=metrics(serial),
                detector=serial,modes=modes,decisions=decisions,saved_sf4_decision_parity=parity,
                reader_inputs_sha256=digest({key:saved.get(key) for key in ('recogniser_text','recogniser_nfd','r1_predictions','coverage','peer_predictions','peer_coverage','k1_flags')}))
            cache.parent.mkdir(parents=True,exist_ok=True);cache.write_bytes(gzip.compress(json.dumps(record,ensure_ascii=False).encode()))
            result.append(record)
        if i%50==0:print(f'baseline {i}/600, {time.monotonic()-start:.1f}s',flush=True)
    assert binding()==initial
    dump(E/'masked_receipt.json',mask_receipt)
    write(E/'baseline_per_line.jsonl', [{k:v for k,v in r.items() if k not in ('detector','modes','decisions')}|
        dict(gate={m:dict(status=r['decisions'][m]['status'],label=r['decisions'][m].get('label'),
            proposal=r['modes'][m]['text'],holds=r['decisions'][m]['hold_slots']) for m in MODES}) for r in result])
    return {(r['id'],r['variant']):r for r in result}

def audit_inputs(sources):
    """Select only the 48 AB releases from the two completed L1M populations."""
    selected=[];details={};remote=dict(runtime={},alignments={},decisions={m:{} for m in MODES})
    custody={}
    for sample in ('200','vouli'):
        lines=rows(L1/sample/'lines.jsonl.gz')
        kept=[r for r in lines if r['status']['masked']['ENSEMBLE_AB'] in ('corrected','unchanged')]
        assert all(r['status']['original']['ENSEMBLE_AB']=='hold' for r in kept)
        wanted={r['id'] for r in kept}
        ds={r['id']:r for r in rows(L1/sample/'details.jsonl.gz') if r['id'] in wanted}
        src=load(L1/sample/'source_selected.json')
        rr=json.loads(gzip.decompress((L1/f'remote_{sample}.json.gz').read_bytes()))
        for r in kept:
            k=r['id'];s=r['source'];sources[k]=dict(src[k],original_path=s['original_path'])
            assert sha(s['original_path'])==s['original_crop_sha256']
            selected.append(dict(id=k,wave=r['wave'],sample=sample,AB_before='hold',
                AB_after=r['status']['masked']['ENSEMBLE_AB'],own_pixels_lost=s.get('own_pixels_lost'),
                original_crop_sha256=s['original_crop_sha256'],masked_crop_sha256=s['masked_sha256']))
            details[k]=ds[k];remote['runtime'][k]=rr['runtime'][k]
            if k in rr['alignments']:remote['alignments'][k]=rr['alignments'][k]
            for m in MODES:remote['decisions'][m][k]=ds[k]['overlays']['original'][m]
        for name in ('lines.jsonl.gz','details.jsonl.gz','source_selected.json','receipt.json'):
            custody[sample+'/'+name]=sha(L1/sample/name)
        custody['remote_'+sample+'.json.gz']=sha(L1/f'remote_{sample}.json.gz')
    wanted={r['id'] for r in selected}
    for r in rows(L1/'c1_selected_alignments.jsonl.gz'):
        if r['id'] in wanted:remote['alignments'][r['id']]=r
    assert len(selected)==len(wanted)==48
    assert Counter(r['AB_after'] for r in selected)=={'corrected':14,'unchanged':34}
    assert wanted==set(remote['runtime'])==set(remote['alignments'])==set(details)
    assert not wanted&set((OUT/'S8_DEV_ids.txt').read_text().split())
    for k in wanted:assert nfd(remote['runtime'][k]['recogniser_text'])==remote['alignments'][k]['alignment']['prediction']
    dump(E/'audit_selection.json',selected);dump(E/'audit_input_custody.json',custody)
    dump(E/'sources.json',sources)
    saved=E/'audit_remote_selected.json.gz'
    if not saved.exists() or json.loads(gzip.decompress(saved.read_bytes()))!=remote:
        saved.write_bytes(gzip.compress(json.dumps(remote,ensure_ascii=False).encode(),mtime=0))
    return selected,remote,details

def parity_audit(sources,remote,details,selected):
    """Re-run the exact original-crop projection on the 14 corrected witnesses."""
    case.configure_model(ROOT/'docs/labelfix/case_model_S5.json')
    model=markshape.load_model(ROOT/'docs/labelfix/markshape_model_S4.json')
    bp=dict(detector='s6',r1_sha256='719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636',policy_sha256=binding()['policy']['sha256'])
    result=[]
    for r in selected:
        if r['AB_after']!='corrected':continue
        k=r['id'];saved=remote['runtime'][k];al=Alignment.from_record(remote['alignments'][k]['alignment'])
        with Image.open(sources[k]['original_path']) as im:ci=ink.analyse(im)
        serial=gate.serialize(reading.read_ink(ci,al.prediction,al,model,filtered=False))
        runtime={key:deepcopy(v) for key,v in saved.items() if key not in ('evidence_sha256','modes','historical_A_verified')};runtime['detector']=serial
        proj=lambda x:{a:x.get(a) for a in ('status','label','hold_slots','changes','gate_decisions')}
        modes={m:gate.compose_runtime(runtime,m) for m in MODES}
        decisions={m:overlay(sources[k],runtime,m,bp) for m in MODES}
        eq={m:digest(proj(decisions[m]))==digest(proj(details[k]['overlays']['original'][m])) for m in MODES}
        modeeq={m:all(modes[m][f]==details[k]['modes']['original'][m][f] for f in ('text','hold_slots')) for m in MODES}
        result.append(dict(id=k,detector_equal=digest(serial)==digest(details[k]['detector']['original']),decision_parity=eq,mode_parity=modeeq))
    dump(E/'L1M_original_projection_parity.json',dict(lines=result,expected=14,
        all_equal=len(result)==14 and all(r['detector_equal'] and all(r['decision_parity'].values()) and all(r['mode_parity'].values()) for r in result)))
    assert load(E/'L1M_original_projection_parity.json')['all_equal'],'STOP: L1M projection parity failed'

def word_groups(anchor,sources,canonical=True,retain_raw=False):
    """R0 connected-word method generalized to every S8 source; no word dropped."""
    # Preserve keraia before NFD; they are candidate identities, not accent aliases.
    norm=lambda s:''.join(t if t in ('\u0374','\u0384') else nfd(t) for t in re.split('([\u0374\u0384])',s))
    alltext={'anchor':norm(anchor),**{k:norm(v) for k,v in sources.items()}}
    words={k:list(re.finditer(r'\S+',s)) for k,s in alltext.items()}
    parent={(k,i):(k,i) for k,ww in words.items() for i in range(len(ww))}
    def find(a):
        if parent[a]!=a:parent[a]=find(parent[a])
        return parent[a]
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:parent[b]=a
    def owned(k):
        chars=[];owners=[];ranges={p:i for i,w in enumerate(words[k]) for p in range(w.start(),w.end())}
        for p,ch in enumerate(alltext[k]):
            if U.category(ch).startswith('M'):continue
            chars.append(ch);owners.append(ranges.get(p))
        return ''.join(chars),owners
    a,ao=owned('anchor')
    for k in sources:
        s,so=owned(k);path=align_chars(a,s);linked=set()
        for i,j in path:
            if i is not None and j is not None and ao[i] is not None and so[j] is not None:
                union(('anchor',ao[i]),(k,so[j]));linked.add(so[j])
        for wi in range(len(words[k])):
            if wi in linked or not words['anchor']:continue
            at=next((p for p,(i,j) in enumerate(path) if j is not None and so[j]==wi),0)
            near=min((abs(p-at),ao[i]) for p,(i,j) in enumerate(path) if i is not None and ao[i] is not None)[1]
            union(('anchor',near),(k,wi))
    groups=defaultdict(list)
    for node in parent:groups[find(node)].append(node)
    out=[]
    for nodes in groups.values():
        ai=sorted(i for k,i in nodes if k=='anchor')
        assert ai,('no recogniser word for card',nodes)
        raw={k:literal(' '.join(words[k][i].group() for kk,i in sorted(nodes) if kk==k)) for k in sources}
        group=dict(start=words['anchor'][ai[0]].start(),end=words['anchor'][ai[-1]].end(),anchor_words=ai,
            forms={k:(canon if canonical else nfc)(v) for k,v in raw.items()})
        if retain_raw:group.update(raw_forms=raw,**elision_policy(raw))
        out.append(group)
    return sorted(out,key=lambda g:(g['start'],g['end']))

def r1_text(runtime,canonical=True):
    # Name only scored saved A positions; preserve unscored recogniser clusters.
    pred={p['start']:p for p in runtime['r1_predictions']}
    out=[]
    for c in clusters(runtime['recogniser_nfd']):
        p=pred.get(c.start)
        out.append(c.base+(''.join(reading.MARKS[q] for q in p['parts'] if q in reading.MARKS) if p is not None else c.marks))
    return (canon if canonical else literal)(''.join(out))

def kinds(forms):
    values=list(forms.values());out=[]
    if len({bare(v) for v in values})>1:out.append('letters_punctuation_or_boundary')
    if len({''.join(c for c in nfd(v) if U.category(c).startswith('M')) for v in values})>1:out.append('mark_form')
    if len(set(values))>1 and not out:out.append('mark_placement')
    return out

def census(sources,remote,ids,base):
    allwords=[];items=[];controls=[]
    for k in ids:
        src=sources[k];rr=remote['runtime'][k];orig=base[k,'original']
        forms=dict(google=src['label'],r1_A=r1_text(rr,canonical=False),detector_original=orig['detector']['text'],
            frozen_AB=orig['modes']['ENSEMBLE_AB']['text'])
        if (k,'masked') in base:forms['detector_masked']=base[k,'masked']['detector']['text']
        for g in word_groups(rr['recogniser_nfd'],forms,retain_raw=True):
            agree=len(set(g['forms'].values()))==1
            item=dict(g,line_id=k,wave=src['wave'],control=False,
                selection='all_agree_sample' if agree else 'disagreement',kinds=kinds(g['forms']),
                AB_status=orig['decisions']['ENSEMBLE_AB']['status'],masked_available=(k,'masked') in base)
            item['uid']=digest([k,g['start'],g['end']])[:20]
            allwords.append(item)
            answer=next(iter(g['forms'].values()))
            if agree and 2<=len(answer)<=10 and any(U.combining(c) for c in nfd(answer)) and all(c.isalpha() for c in answer):
                controls.append(dict(item,correct=answer))
            if not agree:items.append(item)
    # Exact ceil(5%) by wave; per-word inclusion probability retained for weighting.
    for wave in WAVES:
        pool=sorted([x for x in allwords if x['wave']==wave and x['selection']=='all_agree_sample'],key=lambda x:x['uid'])
        chosen=random.Random(SEED+wave).sample(pool,math.ceil(.05*len(pool)))
        chosen_ids={x['uid'] for x in chosen}
        for x in pool:x.update(selected=x['uid'] in chosen_ids,inclusion_probability=len(chosen)/len(pool) if pool else 0)
        items.extend(chosen)
    for x in allwords:
        if x['selection']=='disagreement':x.update(selected=True,inclusion_probability=1.)
    selected_ids={x['uid'] for x in items}
    controls=[x for x in controls if x['uid'] not in selected_ids]
    write(E/'word_census.jsonl',allwords);write(E/'dev_plan.jsonl',items)
    write(E/'control_candidates.jsonl',controls)
    source_names=sorted({k for x in allwords for k in x['forms']})
    summary=dict(words=len(allwords),disagreements=sum(x['selection']=='disagreement' for x in items),
        all_agree_words=sum(x['selection']=='all_agree_sample' for x in allwords),
        all_agree_sample=sum(x['selection']=='all_agree_sample' for x in items),cards=len(items),
        controls_required=math.ceil(len(items)*.08/.92),by_wave={w:dict(Counter(x['selection'] for x in items if x['wave']==w)) for w in WAVES},
        by_kind=dict(Counter(q for x in items for q in x['kinds'])),
        by_elision_policy=dict(Counter(x['scoring_policy'] for x in items)),
        by_wave_elision_policy={w:dict(Counter(x['scoring_policy'] for x in items if x['wave']==w)) for w in WAVES},
        census_elision_policy=dict(Counter(x['scoring_policy'] for x in allwords)),
        by_wave_kind={w:dict(Counter(q for x in items if x['wave']==w for q in x['kinds'])) for w in WAVES},
        by_wave_source_pattern={w:dict(Counter(' | '.join(sorted('='.join(sorted(k for k,v in x['forms'].items() if v==f)) for f in set(x['forms'].values())))
            for x in items if x['wave']==w and x['selection']=='disagreement')) for w in WAVES},
        by_source_pair={a+' != '+b:sum(x['forms'][a]!=x['forms'][b] for x in allwords if a in x['forms'] and b in x['forms'])
            for i,a in enumerate(source_names) for b in source_names[i+1:]})
    dump(E/'card_counts.json',summary)
    return items,controls,summary

def has_mark(s):
    return any(c in '\u0374\u0384' for c in s) or any(U.combining(c) or c in ELISION for c in nfd(s))

def audit_plan(sources,remote,audit_rows,details):
    wanted={r['id'] for r in audit_rows};assert len(wanted)<=48
    assert set(details)==wanted
    items=[];allwords=[];controls=[]
    for k in sorted(wanted):
        src=sources[k];d=details[k];ov=d['overlays']['masked']['ENSEMBLE_AB'];assert ov['status'] in ('corrected','unchanged')
        meta=dict(line_id=k,wave=src['wave'],control=False,audit_claim=ov['status'],
            audit_own_pixels_lost=next(r.get('own_pixels_lost') for r in audit_rows if r['id']==k))
        forms=dict(google=src['label'],r1_A=r1_text(remote['runtime'][k]),
            detector_original=d['detector']['original']['text'],detector_masked=d['detector']['masked']['text'])
        groups=word_groups(remote['runtime'][k]['recogniser_nfd'],forms)
        pool=[]
        for g in groups:
            if not any(has_mark(v) for v in g['forms'].values()):continue
            agree=len(set(g['forms'].values()))==1
            x=dict(g,**meta,uid=digest([k,g['start'],g['end']])[:20],kinds=kinds(g['forms']),
                selection='L1M_unchanged_undisputed_sample' if agree else 'L1M_unchanged_disputed',
                selected=False,inclusion_probability=0.)
            allwords.append(x)
            answer=next(iter(g['forms'].values()))
            if agree and 2<=len(answer)<=10 and all(c.isalpha() for c in answer) and any(U.combining(c) for c in nfd(answer)):
                controls.append(dict(x,correct=answer))
            if ov['status']=='unchanged':
                if agree:pool.append(x)
                else:x.update(selected=True,inclusion_probability=1.);items.append(x)
        if ov['status']=='unchanged':
            chosen=random.Random(SEED+'audit20'+k).sample(sorted(pool,key=lambda x:x['uid']),math.ceil(.2*len(pool)))
            chosen_ids={x['uid'] for x in chosen}
            for x in pool:x.update(selected=x['uid'] in chosen_ids,inclusion_probability=len(chosen)/len(pool))
            items.extend(chosen)
        else:
            for g in word_groups(remote['runtime'][k]['recogniser_nfd'],dict(google=src['label'],corrected=ov['label']),canonical=False):
                if len(set(g['forms'].values()))==1:continue
                items.append(dict(g,**meta,selection='L1M_changed_word',kinds=['audit_correction'],uid=digest([k,g['start'],g['end']])[:20],
                    inclusion_probability=1.,canonical_forms={s:canon(v) for s,v in g['forms'].items()}))
    assert {x['line_id'] for x in items}==wanted
    write(E/'audit_plan.jsonl',items)
    write(E/'audit_word_census.jsonl',allwords);write(E/'audit_control_candidates.jsonl',controls)
    # Only selected saved L1M rows are copied; original and masked evidence retained.
    write(E/'audit_saved_details.jsonl.gz',[details[k] for k in sorted(wanted)])
    dump(E/'audit_counts.json',dict(lines=len(wanted),line_claims=dict(Counter(r['AB_after'] for r in audit_rows)),
        cards=len(items),controls_required=math.ceil(len(items)*.08/.92),
        by_selection=dict(Counter(x['selection'] for x in items)),by_wave=dict(Counter(x['wave'] for x in items)),
        by_kind=dict(Counter(q for x in items for q in x['kinds'])),
        by_line={k:dict(Counter(x['selection'] for x in items if x['line_id']==k)) for k in sorted(wanted)}))
    return items,controls

def word_box(it,sources,remote):
    k=it['line_id'];al=Alignment.from_record(remote['alignments'][k]['alignment']);x0,x1=al.window(it['start'],it['end'])
    with Image.open(sources[k]['original_path']) as im:w,h=im.size
    return [max(0,int(x0-.6*h)),0,min(w,max(int(x0+1),math.ceil(x1+.6*h))),h]

def control_preview(controls,sources,remote,tag=''):
    # Stable wave-balanced queue, independently pixel-verified before planting.
    pool=[]
    for w in WAVES:
        cs=sorted([c for c in controls if c['wave']==w],key=lambda c:c['uid'])
        random.Random(SEED+'controls'+w).shuffle(cs);pool.append(cs)
    queue=[x for row in __import__('itertools').zip_longest(*pool) for x in row if x is not None][:240]
    write(E/(tag+'control_review_queue.jsonl'),queue)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
    for page in range(math.ceil(len(queue)/40)):
        canvas=Image.new('RGB',(1600,1200),'#eeeeee');draw=ImageDraw.Draw(canvas)
        for j,it in enumerate(queue[page*40:page*40+40]):
            x=(j%4)*400;y=(j//4)*120;box=word_box(it,sources,remote)
            with Image.open(sources[it['line_id']]['original_path']) as im:c=im.crop(box).convert('RGB')
            sc=min(3.,390/c.width,83/c.height);c=c.resize((round(c.width*sc),round(c.height*sc)),Image.Resampling.LANCZOS)
            canvas.paste(c,(x,y+30));draw.text((x+3,y+3),f'{page*40+j:03d} {it["correct"]}',font=font,fill='black')
        canvas.save(E/f'{tag}control_review_{page:02d}.png')
    return queue

def planted(verified,number,tag):
    assert len(verified)>=number,('need pixel-verified controls',len(verified),number)
    out=[]
    rng=random.Random(SEED+'plant'+tag);pool=verified[:];rng.shuffle(pool)
    for i,c in enumerate(pool[:number]):
        s=nfd(c['correct']);positions=[j for j,ch in enumerate(s) if U.combining(ch)];assert positions
        at=positions[i%len(positions)]
        fake=canon(s[:at]+({'́':'̀','̀':'́'}.get(s[at],'') if i%2 else '')+s[at+1:])
        assert fake!=c['correct']
        out.append(dict(c,control=True,known_answer=c['correct'],selection='planted_control',kinds=['planted_control'],
            forms=dict(pixel_verified=c['correct'],planted_wrong=fake),uid=digest([tag,c['uid'],'control'])[:20]))
    return out

def cards(items,verified,tag,sources,remote):
    required=math.ceil(len(items)*.08/.92);controls=planted(verified,required,tag)
    pool=items+controls;random.Random(SEED+tag).shuffle(pool)
    dest=OUT/tag;(dest/'img').mkdir(parents=True,exist_ok=True)
    blind=[];key=[];line_paths={}
    for it in pool:
        ident='item_'+digest([tag,it['uid']])[:16];k=it['line_id'];forms=list(dict.fromkeys(it['forms'].values()))
        random.Random(SEED+ident).shuffle(forms);assert len(forms)>=1
        if k not in line_paths:
            p='img/line_'+digest([tag,k])[:16]+'.png'
            with Image.open(sources[k]['original_path']) as im:im.convert('RGB').save(dest/p)
            line_paths[k]=p
        box=word_box(it,sources,remote)
        with Image.open(sources[k]['original_path']) as im:c=im.crop(box).convert('RGB')
        scale=min(3.,900/max(1,c.width));sz=[max(1,round(c.width*scale)),max(1,round(c.height*scale))]
        c.resize(sz,Image.Resampling.LANCZOS).save(dest/'img'/(ident+'.png'))
        options={chr(65+j):v or '∅' for j,v in enumerate(forms)}
        b=dict(id=ident,img='img/'+ident+'.png',line_img=line_paths[k],options=options,other_options=['none of these','unreadable'])
        blind.append(b);entry=dict(b,**it);entry.update(crop_box=box,zoom_scale=scale,
            source_crop_sha256=sha(sources[k]['original_path']),candidate_sources={choice:[s for s,v in it['forms'].items() if (v or '∅')==form] for choice,form in options.items()},
            expected_choice=next((a for a,v in options.items() if v==it.get('known_answer')),None));key.append(entry)
    dump(dest/'items_blind.json',blind);dump(OUT/'private'/tag/'items_key.json',key)
    dump(dest/'answers_blank.json',[dict(id=b['id'],choice=None,transcription=None,uncertain=None,note=None) for b in blind])
    (dest/'README.md').write_text('Read the ink literally, including misprints. Choose a form, none of these (transcribe), or unreadable. Elision apostrophe is U+2019; numeral keraia remains U+0374/U+0384 as printed. Do not regularise spelling or accentuation. View the full line and word zoom (at most 3x, uniform scale). Record ambiguous word boundaries or clipping. Two readers work independently. Only this folder goes to readers; the private key and other evidence stay with the coordinator. Answers are pending; this is training-wave DEV, never a locked test.\n')
    template='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Print truth cards</title><style>body{font:18px Georgia;max-width:1200px;margin:24px auto;padding:12px;background:#eee}section{background:white;padding:20px;margin:24px 0;break-inside:avoid}img{max-width:100%;height:auto;display:block;margin:16px 0}li{font-size:26px;margin:12px}.line{border:1px solid #aaa}</style><p>Read the ink, misprints included. U+2019 for elision; preserve printed numeral keraia. Choose a candidate, none of these / transcribe, or unreadable.</p>'''
    for b in blind:
        template+='<section><h2>'+b['id']+'</h2><img src="'+b['img']+'"><img class="line" src="'+b['line_img']+'"><ul>'+''.join('<li>'+a+': '+html.escape(v)+'</li>' for a,v in b['options'].items())+'</ul><p>none of these / unreadable</p></section>'
    (dest/'index.html').write_text(template)
    dump(E/(tag+'_receipt.json'),dict(cards=len(items),controls=required,total=len(blind),control_fraction=required/len(blind),
        blind_sha256=sha(dest/'items_blind.json'),key_sha256=sha(OUT/'private'/tag/'items_key.json'),max_zoom=3,
        source_labels_hidden=True,control_flags_hidden=True,truth='PENDING independent print adjudication'))
    return len(items),required

def aggregate(base):
    out=[]
    for variant in ('original','masked'):
        for wave in WAVES+('ALL',):
            rr=[r for r in base.values() if r['variant']==variant and (wave=='ALL' or r['wave']==wave)]
            if not rr:continue
            c=Counter();hist=Counter()
            for r in rr:
                c.update({k:v for k,v in r['metrics'].items() if k!='components_per_letter_histogram'})
                hist.update({int(k):v for k,v in r['metrics']['components_per_letter_histogram'].items()})
            out.append(dict(variant=variant,wave=wave,lines=len(rr),**c,
                components_per_letter=c['component_assignments']/c['letters'] if c['letters'] else None,
                components_per_letter_histogram=dict(sorted(hist.items())),
                rates_percent={k:100*c[k]/c['letters'] for k in METRICS},
                affected_lines={k:sum(bool(r['metrics'][k]) for r in rr) for k in METRICS},
                gate={m:dict(Counter(r['decisions'][m]['status'] for r in rr)) for m in MODES},
                saved_sf4_parity={m:sum(r['saved_sf4_decision_parity'].get(m,False) for r in rr) for m in MODES}))
    dump(E/'baseline_by_wave.json',out);return out

def report(summary,agg,base,audit_items,rendered):
    from scripts.labelfix.s8_report import write_report
    write_report(summary,agg,base,audit_items,rendered)

def subsample_proposal(summary):
    n=1800;ctrl=math.ceil(n*.08/.92)
    obj=dict(seed=SEED+'subsample',cards=n,controls=ctrl,total=n+ctrl,
        strata='wave x disagreement/all-agree x detector mark-presence positive/negative; proportional quotas with minimum 20 per nonempty stratum; store actual inclusion probabilities',
        method='retain all-agree random sample; stratified random sample disagreements; inverse-probability weighted TP/FP/FN; line/document cluster bootstrap',
        ci='Nominal worst-case independent-binomial 95% half-width 1.96*sqrt(.25/n_eff): 2.31 pp for 1800, 3.27 pp for 900 predicted/true-positive units. Wave n=300: 5.66 pp. Actual presence denominators, weights and clustering may widen intervals; report effective n and bootstrap CI, no precision promise.')
    dump(E/'subsample_proposal.json',obj)
    return f'Propose {n} seeded, wave-stratified data cards plus {ctrl} controls ({n+ctrl} total). '+obj['ci']+' See `evidence/subsample_proposal.json`. No DEV cards rendered pending scope decision.'

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--masked',action='store_true')
    args=ap.parse_args()
    sources=load(E/'sources.json')
    ids=(OUT/'S8_DEV_ids.txt').read_text().split();assert len(ids)==len(set(ids))==600
    audit_rows,audit_remote,details=audit_inputs(sources)
    parity_audit(sources,audit_remote,details,audit_rows)
    if not (E/'remote.json.gz').exists():
        # The audit needs only permitted local L1M evidence; no remote access here.
        audit,audit_controls=audit_plan(sources,audit_remote,audit_rows,details)
        control_preview(audit_controls,sources,audit_remote,'audit_')
        verified=load(E/'audit_controls_verified.json')
        assert all(x['uid'] in {q['uid'] for q in audit_controls} and x.get('pixel_verified') for x in verified)
        rendered={'audit':cards(audit,verified,'audit',sources,audit_remote)}
        dump(E/'frozen_binding.json',binding())
        from scripts.labelfix.s8_report import write_stopped_report
        write_stopped_report(rendered)
        dump(E/'receipt.json',dict(schema='s8a2-preparation-v1',DEV_lines=600,audit_lines=48,
            audit_cards=len(audit),audit_controls=rendered['audit'][1],baseline_complete=False,
            cards_rendered=rendered,DEV_cards_rendered=0,masked_lines=0,masked_pending=True,
            remote_access_stopped=True,missing_stage_summary_sha256=sha(E/'missing_stage_summary.json'),
            reader_runs=0,DEV_detector_runs=0,projection_parity_witnesses=14,git_writes=0,
            preparation_network=False,frozen_binding_sha256=sha(E/'frozen_binding.json'),
            audit_original_crops_unchanged=all(sha(sources[r['id']]['original_path'])==r['original_crop_sha256'] for r in audit_rows),
            adjudication='PENDING',status='STOP_missing_DEV_saved_evidence'))
        print('STOP: DEV evidence missing; completed audit 48 lines, 114 cards + 10 controls. No SSH or DEV detector run.')
        return
    from scripts.labelfix.s8_verify_evidence import verify
    remote=verify()
    assert remote['complete'] and set(remote['runtime'])==set(remote['alignments'])==set(ids)
    base=baseline(sources,remote,ids,args.masked);agg=aggregate(base)
    items,controls,summary=census(sources,remote,ids,base)
    audit,audit_controls=audit_plan(sources,audit_remote,audit_rows,details)
    control_preview(audit_controls,sources,audit_remote,'audit_')
    if summary['cards']+summary['controls_required']<=2000:control_preview(controls,sources,remote)
    rendered={}
    for tag,plan,pool,rr,verified_name in (
        ('audit',audit,audit_controls,audit_remote,'audit_controls_verified.json'),
        ('cards',items,controls,remote,'controls_verified.json')):
        if tag=='cards' and summary['cards']+summary['controls_required']>2000:continue
        verified=load(E/verified_name) if (E/verified_name).exists() else []
        assert all(x['uid'] in {q['uid'] for q in pool} and x.get('pixel_verified') for x in verified)
        current={x['uid']:x for x in pool}
        assert all(all(x[field]==current[x['uid']][field] for field in ('correct','forms','line_id','start','end')) for x in verified)
        assert all(not x.get('source_crop_sha256') or x['source_crop_sha256']==sha(sources[x['line_id']]['original_path']) for x in verified)
        if len(verified)>=math.ceil(len(plan)*.08/.92):rendered[tag]=cards(plan,verified,tag,sources,rr)
    report(summary,agg,base,audit,rendered)
    dump(E/'receipt.json',dict(schema='s8a4-preparation-v1',DEV_lines=600,audit_lines=len(audit_rows),
        masked_lines=sum(r['variant']=='masked' for r in base.values()),baseline_complete=True,
        cards_rendered=rendered,DEV_render_blocked_over_cap=summary['cards']+summary['controls_required']>2000,
        reader_runs=0,git_writes=0,preparation_network=False,
        remote_sha256=sha(E/'remote.json.gz'),frozen_binding_sha256=sha(E/'frozen_binding.json'),
        evidence_acceptance_sha256=sha(E/'S8a4_evidence_acceptance.json'),
        DEV_s6_records=sum(r['variant']=='original' for r in base.values()),projection_parity_witnesses=14,
        DEV_controls_reviewed=len(load(E/'controls_verified.json')) if (E/'controls_verified.json').exists() else 0,
        audit_original_crops_unchanged=all(sha(sources[r['id']]['original_path'])==r['original_crop_sha256'] for r in audit_rows),
        original_crops_unchanged=all(sha(r['crop'])==r['crop_sha256'] for r in base.values()),
        adjudication='PENDING',masked_pending=sum(r['variant']=='masked' for r in base.values())<450))
    print(json.dumps(dict(summary=summary,rendered=rendered),ensure_ascii=False),flush=True)

if __name__=='__main__':main()
