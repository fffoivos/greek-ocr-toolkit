#!/usr/bin/env python3
"""Offline BENCH02 draw, slim extraction and candidate readout (Python >=3.10)."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict, deque
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import random
import re
import sqlite3
import statistics
import subprocess
import tempfile
import sys

assert sys.version_info >= (3, 10), "BENCH02 requires Python >=3.10"
import unicodedata

HERE = Path(__file__).resolve().parent
QUOTAS = dict(zip(('monotonic','polytonic','poly_dictionary_journal','latin','greek_latin',
    'historical_russian','modern_cyrillic','numeric_cells','short','long','vertical_turned',
    'caps_headings','leaders_dashes','font_extremes','degraded','curved_skewed'),
    (240,360,160,160,160,120,160,200,120,160,100,120,100,100,100,100)))
# Physical/specialized strata precede script fallbacks; no row counts twice.
PRECEDENCE = ('vertical_turned','font_extremes','degraded','curved_skewed','numeric_cells',
    'caps_headings','leaders_dashes','short','long','greek_latin','historical_russian',
    'modern_cyrillic','latin','poly_dictionary_journal','polytonic','monotonic')
DEFAULT_EDITION_CAP = 50  # BENCH02I: evaluated by run_ruled_draw.py
DEGRADED_LABEL = 'degraded (relative: bottom 5% confidence within source)'
REASON = 'split_or_edition_identity_unresolved'
FEATURES = ('source','primary_class','confidence','confidence_scope','leader_runs',
    'emdash_label_count','cell_flag','A','turn_cw','source_width','source_height',
    'xheight_px','ink_density','degraded','language','languages','baseline_angle_deg',
    'curve_deviation_px','letter_spaced','dash_tag')

# Read-only git show sol/census-v2-serbian:greekocr/harvest/admission.py
# SERBIAN_DOCUMENTS; corroborated by census2_document_language.json.
SERBIAN_DOCUMENTS = frozenset(('cyrillic:7235f8d0', 'cyrillic:975289f3'))



def text_facets(d):
    """Sufficient statistics for the unchanged classifier; no text or word inventory."""
    text=d.get('final_text',''); inv=d.get('final_inventory',d.get('raw_inventory',{})); e=d.get('expectations',{})
    f={k:inv[k] for k in ('greek_letters','latin_letters','cyrillic_letters','letter_count') if k in inv}
    if 'scripts' in inv: f['observed_scripts']=inv['scripts']
    f.update(characters=inv.get('characters',len(text)),mixed_words=bool(inv.get('mixed_words',[])),
        numeric=sum(ch.isalnum() for ch in text)>1 and numeric_grammar(text),
        has_upper=any(ch.isupper() for ch in text),has_lower=any(ch.islower() for ch in text),
        punctuation_share=sum(not ch.isalpha() and not ch.isdigit() and not ch.isspace() for ch in text)/max(1,sum(not ch.isspace() for ch in text)),
        orthography=str(e.get('orthographies',{}).get('greek',e.get('orthography',''))).lower(),
        cyrillic_orthography=str(e.get('orthographies',{}).get('cyrillic',e.get('orthography',''))).lower(),
        scripts=e.get('scripts',[]),languages=e.get('languages',[]))
    return f



def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',',':'))


def sha(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()


def rows(path):
    path = Path(path)
    with (gzip.open(path,'rt') if path.suffix == '.gz' else path.open()) as f:
        for line in f:
            if line.strip(): yield json.loads(line)


def output(path, root=HERE):
    p = Path(path).resolve()
    if not Path(root).is_absolute(): raise ValueError('output-dir must be absolute')
    if not p.is_relative_to(Path(root).resolve()): raise ValueError('writes must stay inside output root')
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def dump(path, value, root=HERE):
    output(path, root).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n')


def key(d):
    b = d.get('binding', d)
    return b['parent_id'], b.get('id', b.get('row_id'))


def w12(parent):
    return bool(re.fullmatch(r'collect-v3-W[12]-.*', parent))


def census05_evidence(d, row):
    """Exact census_05 paths (line_pipeline.py gate 0.3 / census export).

    evaluation_diagnostics.row.crop_bbox -> crop_aspect: max(w,h)/min(w,h),
    cell_flag := A<=6. No standalone flag/universal A is emitted by the gate;
    decision.reasons[].A exists only for single_character_cell. numeric_cells
    .classify_cell.is_cell is a different small-image definition, not this gate.
    decision.raw_inventory.{scripts,*_letters,letter_count,mixed_words} is kept
    by text_facets when final_inventory is absent (final_text is still raw).
    row.confidence (fallback row.docai_confidence) is the line confidence.
    decision.routes.dashes.evidence.dashes is the pipeline's N1 dash tag.
    row.leader_runs / row.emdash_label_count are retained collector N1 fields.
    Ink density: absent in the inspected census_05 producer; no proxy invented.
    Serbian identity: row.doc or row.book_id, or decision.binding.book_id.
    """
    f = {k:v for k,v in row.items() if k in FEATURES}
    bbox = row.get('crop_bbox')
    if bbox is not None:
        w,h = bbox[2]-bbox[0], bbox[3]-bbox[1]
        if min(w,h)>0:
            f['A']=max(w,h)/min(w,h); f['cell_flag']=f['A']<=6
    if 'confidence' not in f and 'docai_confidence' in row:
        f['confidence']=row['docai_confidence']
    for doc in (row.get('doc'), row.get('book_id'), d.get('binding',{}).get('book_id')):
        if doc in SERBIAN_DOCUMENTS:
            f['languages']=['sr']; break
    dash=d.get('routes',{}).get('dashes',{}).get('evidence',{})
    if 'dashes' in dash: f['dash_tag']=bool(dash['dashes'])
    # Explicit null means absent, never zero or a guessed physical measurement.
    f.setdefault('confidence',None); f.setdefault('ink_density',None)
    return f


def density_percentiles(slimrows, features):
    """Linear interpolated p25, all census W1/W2 rows per source, before admission."""
    values=defaultdict(list)
    for r in slimrows:
        if not w12(r['parent_id']): continue
        f=dict(features.get(key(r),{})); f.update(r['evidence'])
        density=f.get('ink_density'); source=f.get('source')
        if density is not None and source is not None: values[source].append(density)
    result={}
    for source,v in sorted(values.items()):
        v.sort(); index=(len(v)-1)*.25; lo=math.floor(index); hi=math.ceil(index)
        result[source]=dict(p25=v[lo]+(v[hi]-v[lo])*(index-lo),rows=len(v))
    return result


def relative_degraded(slimrows, split_rows):
    """Admitted W1/W2 dev/test, including excluded rows; confidence is decision-bound."""
    populations=defaultdict(list)
    for r in slimrows:
        side=split_rows.get(key(r),{})
        side=side.get('split',side.get('proposed_split'))
        if r['admitted'] and w12(r['parent_id']) and side in ('dev','test'):
            populations[(side,r['evidence'].get('source','unavailable'))].append(r)
    flagged=set(); report={}
    for (side,source), population in sorted(populations.items()):
        ranked=[r for r in population if r['evidence'].get('confidence') is not None]
        ranked.sort(key=lambda r:(r['evidence']['confidence'],key(r)))
        selected=ranked[:math.ceil(.05*len(population))]
        flagged.update(key(r) for r in selected)
        report[side+'|'+source]=dict(population=len(population),ranked=len(ranked),
            missing_confidence=len(population)-len(ranked),flagged=len(selected))
    return flagged, dict(label=DEGRADED_LABEL,
        population='admitted W1/W2 rows per (dev/test split, source), before v2/locked exclusions',
        confidence_field='evidence.confidence',ranking='(confidence, (parent_id, row_id))',
        draw_order_key='(parent_id, row_id): existing sorted per-row key before seeded round-robin shuffle',
        selection='first ceil(0.05 * n); n = population size; n = 0 flags none',
        missing_confidence='not ranked; never degraded',populations=report,
        missing_confidence_count=sum(v['missing_confidence'] for v in report.values()),
        legacy='absolute confidence < 0.89 OR source density < p25 only for census_03 dry-run/upper-bound regressions')


def subgroup_quotas(split, cl):
    if cl=='font_extremes': return dict(small=50,large=50) if split=='test' else dict(small=13,large=12)
    if cl=='modern_cyrillic': return dict.fromkeys(('ru','sr','bg','uk'),40 if split=='test' else 10)
    return {}


def slim(d, feature=None):
    """Retain only decision-bound evidence; never use diagnostic decision as admission."""
    f = census05_evidence(d, feature or {})
    for s in d.get('stages', []):
        if s.get('stage') != 'segmentation': continue
        result = s.get('result', {})
        frame = result.get('frame', {})
        if 'normalization_cw' in frame: f['turn_cw'] = frame['normalization_cw']
        for k in ('source_width','source_height'): 
            if k in frame: f[k] = frame[k]
        ev = result.get('evidence', {})
        for k in ('xheight_px','baseline_angle_deg','curve_deviation_px','ink_density'):
            if k in ev: f[k] = ev[k]
        mains = [r for r in ev.get('detected_rows',[]) if r.get('side') == 'main']
        # Segmentation's mean/base curves provide physical measurements; no crop-height proxy.
        if len(mains) == 1:
            c = mains[0].get('curves', {}); base = c.get('base', []); mean = dict(c.get('mean', []))
            heights = [y-mean[x] for x,y in base if x in mean]
            if heights: f.setdefault('xheight_px', statistics.median(heights))
            if len(base)>1 and base[-1][0] != base[0][0]:
                x0,y0=base[0]; x1,y1=base[-1]; slope=(y1-y0)/(x1-x0)
                f.setdefault('baseline_angle_deg', math.degrees(math.atan(slope)))
                f.setdefault('curve_deviation_px', max(abs(y-y0-slope*(x-x0)) for x,y in base))
    # Leader payloads can contain text; the classifier consumes only their truth value.
    if 'leader_runs' in f: f['leader_runs']=bool(f['leader_runs'])
    result = dict(parent_id=d['binding']['parent_id'],row_id=d['binding']['id'],
        crop_sha256=d['binding'].get('crop_sha256'), admitted=d.get('admitted') is True,
        disposition=d.get('disposition'), reasons=[r.get('reason') if isinstance(r,dict) else r for r in d.get('reasons',[])],
        text_facets=text_facets(d), evidence=f)
    if 'split' in d['binding']: result['split']=d['binding']['split']
    elif 'split' in d: result['split']=d['split']
    return result


def numeric_grammar(text):
    """Frozen lexical grammar from greekocr/harvest/numeric_cells.py; no size heuristic."""
    separators = frozenset(".,:/-–—%()+'′§№")
    s=text.strip()
    token=s.strip(''.join(separators)+' \t\r\n\v\f')
    roman=unicodedata.normalize('NFKC',token.replace('Ι','I')).upper()
    glyphs=frozenset('IVXLCDMivxlcdmΙ'+''.join(chr(i) for i in range(0x2160,0x2180)))
    if token and all(c in glyphs for c in token) and re.fullmatch(r'M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})',roman):return True
    if any(unicodedata.category(c).startswith('L') for c in s):return False
    digits=sum(c.isdecimal() for c in s)
    return bool((digits and all(c.isdecimal() or c in separators or c.isspace() for c in s)) or
        (digits*2>len(s) and not any(c.isspace() for c in s) and all(c.isdecimal() or unicodedata.category(c)[0] in 'PS' for c in s)))


def tag(row, feature=None, density_p25=None, *, relative_flag=None):
    f = dict(feature or {}); f.update(row['evidence'])
    inv = row.get('text_facets')
    if inv is None: inv=text_facets(row) # compatibility with BENCH02D full tags
    e = inv
    g,l,c = (inv.get(k,0) for k in ('greek_letters','latin_letters','cyrillic_letters'))
    letters = inv.get('letter_count'); chars = inv['characters']
    orth = e['orthography']; src=f.get('source','unavailable')
    corth = e['cyrillic_orthography']
    tags = {k:False for k in QUOTAS}
    tags['monotonic'] = g>0 and not l and not c and orth in ('monotonic','modern')
    tags['polytonic'] = g>0 and not l and not c and orth=='polytonic'
    tags['poly_dictionary_journal'] = orth=='polytonic' and src in ('bsb_poly1850','ia_poly1850') and f.get('primary_class')=='poly1850'
    tags['latin'] = l>0 and not g and not c
    tags['greek_latin'] = g>0 and l>0 and not c and {'greek','latin'} <= set(e.get('scripts',[])) and not inv.get('mixed_words',[])
    langs=f.get('languages',f.get('language',e.get('languages',[])))
    if isinstance(langs,str): langs=[langs]
    names={'rus':'ru','srp':'sr','bul':'bg','ukr':'uk','ru':'ru','russian':'ru','modern russian':'ru','sr':'sr','serbian':'sr','bg':'bg','bulgarian':'bg','uk':'uk','ukrainian':'uk'}
    language=next((names[x.lower()] for x in langs if x.lower() in names), None)
    tags['historical_russian'] = bool(c and language=='ru' and corth in ('historical','historical_russian','russian_historical'))
    tags['modern_cyrillic'] = bool(c and not tags['historical_russian'] and language and corth in ('modern','monotonic','modern_cyrillic'))
    if c and language is None: tags['modern_cyrillic'] = 'unavailable'
    # Numeric grammar from numeric_cells._numeric_reason, plus programme's explicit cell flag/A.
    numeric = inv['numeric']
    cell=f.get('cell_flag'); a=f.get('A')
    tags['numeric_cells'] = (cell is True and a<=6) if numeric and cell is not None and a is not None else ('unavailable' if numeric else False)
    tags['cell_flag'] = cell if cell is not None else 'unavailable'
    tags['letter_spaced'] = f.get('letter_spaced','unavailable')
    tags['punctuation_heavy'] = inv['punctuation_share'] >= 1/3 or bool(f.get('leader_runs') or f.get('emdash_label_count',0)>0 or f.get('dash_tag'))
    tags['short'] = letters<=12 if letters is not None and cell is False else 'unavailable'
    tags['long'] = chars>=60
    turn=f.get('turn_cw'); h=f.get('source_height'); w=f.get('source_width')
    tags['vertical_turned'] = (h>w or turn%180==90) if turn is not None and h is not None and w is not None else 'unavailable'
    tags['caps_headings'] = f.get('primary_class')=='headings_caps' and ((inv['has_upper'] and not inv['has_lower']) or f.get('letter_spaced') is True)
    tags['leaders_dashes'] = bool(f.get('leader_runs') or f.get('emdash_label_count',0)>0 or f.get('dash_tag'))
    xh=f.get('xheight_px')
    tags['font_extremes'] = xh<=10 or xh>=30 if xh is not None else 'unavailable'
    confidence=f.get('confidence'); density=f.get('ink_density')
    low_confidence=confidence is not None and confidence<.89
    low_density=density is not None and density_p25 is not None and density<density_p25
    tags['degraded'] = bool(low_confidence or low_density) if confidence is not None or (density is not None and density_p25 is not None) else 'unavailable'
    if relative_flag is not None:
        tags['degraded'] = relative_flag
        tags['degraded_label'] = DEGRADED_LABEL
    angle=f.get('baseline_angle_deg'); curve=f.get('curve_deviation_px')
    tags['curved_skewed'] = abs(angle)>=2 or curve>=8 if angle is not None and curve is not None else 'unavailable'
    if any(k not in inv for k in ('greek_letters','latin_letters','cyrillic_letters')):
        for k in ('monotonic','polytonic','latin','greek_latin','historical_russian','modern_cyrillic'):
            tags[k] = 'unavailable'
    primary=next((k for k in PRECEDENCE if tags[k] is True),None)
    tags['font_size'] = ('small' if xh<=10 else 'large' if xh>=30 else 'ordinary') if xh is not None else 'unavailable'
    tags['cyrillic_language'] = language if c and language else ('unavailable' if c else 'not_applicable')
    return dict(tags=tags, primary_class=primary, source=src, language=language,
        font_size=('small' if xh<=10 else 'large' if xh>=30 else 'ordinary') if xh is not None else None,
        facets=dict(letter_count=letters,characters=chars,cell_flag=cell,xheight_px=xh,
            baseline_angle_deg=angle,curve_deviation_px=curve,confidence=f.get('confidence'),
            ink_density=density,punctuation_share=inv['punctuation_share'],
            collector_class=f.get('primary_class'),orthography=orth,expected_scripts=e.get('scripts',[])))


def extract(decisions, diagnostics, dest, output_dir=None):
    """Disk-backed keyed join: bounded memory even for multi-GB census evidence."""
    root=HERE if output_dir is None else Path(output_dir)
    dest=output(dest, root); stats=Counter(); inputs={str(p):sha(p) for p in decisions+diagnostics}
    with tempfile.TemporaryDirectory(dir=dest.parent, prefix='.extract-') as td:
        db=sqlite3.connect(str(Path(td)/'join.sqlite'))
        db.execute('CREATE TABLE diag (parent TEXT, rowid_text TEXT, feature TEXT, matched INTEGER DEFAULT 0, PRIMARY KEY(parent,rowid_text))')
        for p in diagnostics:
            for r in rows(p):
                d=r.get('decision',r); parent,rid=key(d)
                if not w12(parent): continue
                f=slim(d,r.get('row',{}))['evidence']
                db.execute('INSERT INTO diag(parent,rowid_text,feature) VALUES (?,?,?)',(parent,rid,canonical(f))); stats['diagnostics']+=1
        db.commit()
        db.execute('CREATE TABLE seen (parent TEXT, rid TEXT, PRIMARY KEY(parent,rid))')
        with dest.open('wb') as raw, gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz:
            for p in decisions:
                for d in rows(p):
                    parent,rid=key(d)
                    if not w12(parent): continue
                    db.execute('INSERT INTO seen VALUES (?,?)',(parent,rid))
                    stats['decisions']+=1
                    found=db.execute('SELECT feature FROM diag WHERE parent=? AND rowid_text=?',(parent,rid)).fetchone()
                    f=json.loads(found[0]) if found else {}
                    if found:
                        stats['joined']+=1; db.execute('UPDATE diag SET matched=1 WHERE parent=? AND rowid_text=?',(parent,rid))
                    r=slim(d,f); gz.write((canonical(r)+'\n').encode())
        stats['diagnostics_unmatched']=db.execute('SELECT count(*) FROM diag WHERE matched=0').fetchone()[0]
        db.close()
    receipt=dict(stats,decision_join_rate=stats['joined']/max(1,stats['decisions']),
        tags_sha256=sha(dest),tags_bytes=dest.stat().st_size,
        diagnostic_join_rate=stats['joined']/max(1,stats['diagnostics']),input_shas=inputs,code_sha=sha(__file__))
    dump(dest.with_suffix('.receipt.json'),receipt,root)
    return receipt


def edition_series(e):
    if e.get('gazette'): return None # issue is edition, never invent annual series
    if e.get('series') or e.get('book_series'): return e.get('series') or e['book_series']
    vals=set()
    for d in e.get('metadata',[]):
        for rec in d.get('records',[]):
            m=rec.get('metadata',{})
            v=m.get('series') or m.get('book_series') 
            if v: vals.add(str(v))
    return next(iter(vals)) if len(vals)==1 else None


def exclusions(editions, v2_paths, manifest, split_rows):
    # SPLIT1's edition-identity witnesses include acquisition-manifest title/URL matches.
    # Keep those witnesses and additionally apply direct document/row membership.
    docs=set(); ids=set(); inputs={str(p):sha(p) for p in v2_paths+[manifest]}
    for p in v2_paths:
        for r in rows(p): docs.add(r.get('doc')); ids.add(r.get('id'))
    ex=json.loads(Path(manifest).read_text()); locked=set()
    for name,v in ex['classes'].items():
        if not ('eval' in name or 'never trains' in v.get('rule','') or 'never admitted to training' in v.get('rule','')): continue
        p=Path(manifest).parent/v['file']; actual=sha(p)
        if actual!=v['sha256']: raise ValueError('locked ID checksum mismatch: '+str(p))
        inputs[str(p)]=actual; locked.update(p.read_text().splitlines())
    excluded_ids = ids | locked
    direct={r['edition_id'] for r in split_rows.values() if r['row_id'] in excluded_ids}
    blocked=set(direct)
    for eid,e in editions.items():
        if e.get('leakage_matches') or set(e.get('member_documents',[])) & docs: blocked.add(eid)
    return blocked,inputs


def diagnostic_locks(manifest, split_rows, editions):
    """Verified registered locked/eval IDs; forced memberships come from exact IDs."""
    classes=json.loads(Path(manifest).read_text())['classes']
    locked=set(); groups={'n1':set(), 'lqb':set()}
    for name,v in classes.items():
        if not ('eval' in name or 'never trains' in v.get('rule','') or 'never admitted to training' in v.get('rule','')):
            continue
        p=Path(manifest).parent/v['file']
        if sha(p)!=v['sha256']: raise ValueError('locked ID checksum mismatch: '+str(p))
        ids=set(p.read_text().splitlines()); locked.update(ids)
        group='n1' if name=='n1_locked_eval' else 'lqb' if name.startswith('lqb_truth_v1') else None
        if group:
            groups[group].update(r['edition_id'] for r in split_rows.values() if r['row_id'] in ids
                and r.get('split',r.get('proposed_split'))=='test' and editions[r['edition_id']].get('forced'))
    return locked,groups


def edition_cap_arg(value):
    if value=='unlimited': return None
    try: n=int(value)
    except ValueError: raise argparse.ArgumentTypeError('edition cap must be a positive integer or unlimited')
    if n<1: raise argparse.ArgumentTypeError('edition cap must be positive')
    return n


def round_robin(pool, split, cl, target, edcounts, sercounts, subgroup=None, edition_cap=DEFAULT_EDITION_CAP, series_cap=3*DEFAULT_EDITION_CAP):
    rng=random.Random(f'bench02:{split}:{cl}')
    groups=defaultdict(lambda:defaultdict(list))
    for r in pool: groups[r['source']][r['edition_id']].append(r)
    sources=sorted(groups); rng.shuffle(sources); queues={}
    for src in sources:
        es=sorted(groups[src]); rng.shuffle(es); queues[src]=deque(es)
        for eid in es:
            rr=sorted(groups[src][eid],key=lambda r:(r['parent_id'],r['row_id'])); rng.shuffle(rr)
            groups[src][eid]=deque(rr)
    selected=[]; subcounts=Counter()
    limits={k:math.ceil(v*1.2) for k,v in subgroup_quotas(split,cl).items()} if subgroup else {}
    while len(selected)<target:
        progress=False
        for src in sources:
            q=queues[src]; picked=None
            for _ in range(len(q)):
                eid=q.popleft(); rr=groups[src][eid]
                while rr:
                    r=rr.popleft(); series=r['series']; sub=r.get(subgroup) if subgroup else None
                    limit=limits.get(sub,0) if subgroup else None
                    if (edition_cap is not None and edcounts[(cl,eid)]>=edition_cap) or (series and series_cap is not None and sercounts[(cl,series)]>=series_cap): continue
                    if limit is not None and subcounts[sub]>=limit: continue
                    picked=r; break
                if rr:q.append(eid)
                if picked:break
            if picked:
                selected.append(picked); edcounts[(cl,picked['edition_id'])]+=1
                if picked['series']:sercounts[(cl,picked['series'])]+=1
                subcounts[picked.get(subgroup)]+=1; progress=True
                if len(selected)==target:break
        if not progress: break
    return selected


def fair_order(candidates):
    """Keep class selection/ranks; emit one row per edition/class/pass."""
    groups=defaultdict(lambda:defaultdict(deque))
    for r in candidates: groups[r['edition_id']][r['class']].append(r)
    editions=sorted(groups)
    while groups:
        for eid in editions:
            if eid not in groups: continue
            for cl in PRECEDENCE:
                q=groups[eid].get(cl)
                if q: yield q.popleft()
            if not any(groups[eid].values()): del groups[eid]


def verify_tags(tags_path, tags_sha256=None, require_receipt_sha=False):
    receipt=Path(tags_path).with_suffix('.receipt.json')
    rec=json.loads(receipt.read_text()) if receipt.exists() else {}
    expected=rec.get('tags_sha256')
    if require_receipt_sha and not expected: raise ValueError('tags receipt sha required')
    actual=sha(tags_path)
    for pinned in (expected,tags_sha256):
        if pinned and actual!=pinned: raise ValueError('tags SHA-256 mismatch')
    if 'tags_bytes' in rec and Path(tags_path).stat().st_size!=rec['tags_bytes']:
        raise ValueError('tags byte count mismatch')
    return dict(sha256=actual,bytes=Path(tags_path).stat().st_size,
        verified_against='receipt' if expected else 'argument' if tags_sha256 else 'unpinned legacy input')


def draw(tags_path, split_path, edition_paths, features, v2_paths, manifest, dest, dry_run=False, edition_cap=DEFAULT_EDITION_CAP, pool_include_forced='both', upper_bound=False, *, _cache=None, tags_sha256=None, require_receipt_sha=False):
    tags_verification=verify_tags(tags_path,tags_sha256,require_receipt_sha)
    dest=output(dest); dest.mkdir(exist_ok=True)
    if edition_cap is not None and (not isinstance(edition_cap,int) or edition_cap<1): raise ValueError('edition cap must be positive or None')
    if pool_include_forced not in ('none','n1','lqb','both'): raise ValueError('invalid forced pool')
    if upper_bound and dry_run: raise ValueError('upper bound and dry run are mutually exclusive')
    series_cap=None if edition_cap is None else 3*edition_cap
    # A sweep-local cache avoids re-reading and re-classifying the same frozen metadata.
    cache={} if _cache is None else _cache
    identity=tuple(map(str,[tags_path,split_path,*edition_paths,*features,*v2_paths,manifest]))
    if cache and cache['identity']!=identity: raise ValueError('draw cache input mismatch')
    if not cache:
        split_rows={key(r):r for r in rows(split_path)}
        editions={}
        for p in edition_paths:
            for e in rows(p): editions.setdefault(e['edition_id'],{}).update(e)
        blocked, exinputs=exclusions(editions,v2_paths,manifest,split_rows)
        slimrows=list(rows(tags_path)); needed={(r['parent_id'],r['row_id']) for r in slimrows}; fs={}
        for wave,p in enumerate(features,1):
            for f in rows(p):
                k=(f'collect-v3-W{wave}-20261018-0524',f['id'])
                if k in needed: fs[k]={x:f[x] for x in FEATURES if x in f}
        percentiles=density_percentiles(slimrows,fs)
        locked,forced_groups=diagnostic_locks(manifest,split_rows,editions)
        cache.update(identity=identity,split_rows=split_rows,editions=editions,blocked=blocked,
            exinputs=exinputs,slimrows=slimrows,fs=fs,percentiles=percentiles,locked=locked,forced_groups=forced_groups)
    else:
        split_rows=cache['split_rows']; editions=cache['editions']; blocked=cache['blocked']; exinputs=cache['exinputs']
        slimrows=cache['slimrows']; fs=cache['fs']; percentiles=cache['percentiles']; locked=cache['locked']; forced_groups=cache['forced_groups']
    relative = not (dry_run or upper_bound)
    flagged,degraded_plan=relative_degraded(slimrows,split_rows) if relative else (set(),None)
    allowed=set().union(*(forced_groups[g] for g in ('n1','lqb') if pool_include_forced in (g,'both')))
    added=Counter(); added_classified=Counter()
    supply=defaultdict(list); stats=Counter(); availability=defaultdict(Counter); raw_supply=Counter(); pre_supply=Counter(); pre_source_edition=Counter(); pre_facets=Counter()
    for r in slimrows:
        stats['rows']+=1; stats['admitted']+=r['admitted']
        eligible=w12(r['parent_id']) and (upper_bound or (r['reasons']==[REASON] if dry_run else r['admitted']))
        feature=fs.get((r['parent_id'],r['row_id']),{})
        source=r['evidence'].get('source',feature.get('source'))
        r.update(tag(r,feature,percentiles.get(source,{}).get('p25'),
            relative_flag=key(r) in flagged if relative else None))
        for k,v in r['tags'].items(): availability[k]['unavailable' if v=='unavailable' else 'available']+=1
        if not eligible:continue
        stats['pre_filter_supply']+=1
        pre_supply[r['primary_class'] or 'unclassified']+=1
        pre_facets.update(k for k,v in r['tags'].items() if v is True)
        s=split_rows.get((r['parent_id'],r['row_id']))
        if not s: stats['missing_split']+=1;continue
        eid=s['edition_id']; side=s.get('split',s.get('proposed_split'))
        pre_source_edition['|'.join((side,r['primary_class'] or 'unclassified',r['source'],eid))]+=1
        if r['row_id'] in locked or (eid in blocked and not (side=='test' and eid in allowed)):
            stats['excluded_rows']+=1; continue
        if side=='test' and eid in blocked and eid in allowed:
            for g in ('n1','lqb'):
                if eid in forced_groups[g]:
                    added[g]+=1
                    if r['primary_class']: added_classified[g]+=1
        if side not in ('test','dev'): stats['train_rows']+=1;continue
        e=editions[eid]; r.update(split=side,edition_id=eid,series=edition_series(e))
        if not r['series'] and not e.get('gazette'):stats['unknown_series_rows']+=1
        cl=r['primary_class']; raw_supply[f'{side}:{cl}']+=1
        if cl:supply[(side,cl)].append(r)
        else:stats['unclassified']+=1
    cache['tagged']=True
    candidates=[]; reports={}; edcounts=Counter(); sercounts=Counter()
    for side in ('test','dev'):
        for cl in PRECEDENCE:
            quota=QUOTAS[cl] if side=='test' else QUOTAS[cl]//4
            subs=subgroup_quotas(side,cl)
            subtargets={k:math.ceil(v*1.2) for k,v in subs.items()}
            target=sum(subtargets.values()) if subs else math.ceil(quota*1.2)
            pool=supply[(side,cl)]
            group='language' if cl=='modern_cyrillic' else 'font_size' if cl=='font_extremes' else None
            chosen=round_robin(pool,side,cl,target,edcounts,sercounts,group,edition_cap,series_cap)
            for rank,r in enumerate(chosen,1):
                candidates.append({k:r[k] for k in ('split','parent_id','row_id','edition_id','source','tags')} | dict(class_=cl,rank=rank))
                candidates[-1]['class']=candidates[-1].pop('class_')
                candidates[-1]['tags'] = dict(candidates[-1]['tags'], evidence_facets=r['facets'])
            reports[f'{side}:{cl}']=dict(quota=quota,overdraw_target=target,supply=len(pool),drawn=len(chosen),
                deficit=max(0,quota-len(chosen)),overdraw_deficit=target-len(chosen),
                sources=len({r['source'] for r in chosen}),editions=len({r['edition_id'] for r in chosen}),
                diversity_target='10 editions / 3 sources where supply allows',
                subgroups=dict(Counter(r.get(group) for r in chosen)) if group else {},
                subgroup_quotas=subs,subgroup_targets=subtargets,
                subgroup_deficits={k:max(0,v-sum(r.get(group)==k for r in chosen)) for k,v in subs.items()})
    candidates=list(fair_order(candidates))
    for k,v in reports.items():
        chosen=[r for r in candidates if r['split']+':'+r['class']==k]
        ec=Counter(r['edition_id'] for r in chosen)
        v.update(credited=min(v['drawn'],v['quota']),top_edition_share=max(ec.values(),default=0)/max(1,len(chosen)),
            diversity_pass=v['editions']>=10 and v['sources']>=3)
        languages={r.get('language') for r in supply[tuple(k.split(':'))]}
        v['label']='Serbian-only' if k.endswith(':modern_cyrillic') and languages=={'sr'} else DEGRADED_LABEL if relative and k.endswith(':degraded') else k.split(':')[1]
    with output(dest/'candidates.jsonl').open('w') as f:
        for r in candidates:f.write(canonical(r)+'\n')
    counts=dict(mode='UPPER BOUND (not admitted): all W1/W2 split rows' if upper_bound else 'mechanics dry run: sole split reason; NOT admitted or benchmark-qualified' if dry_run else 'admitted W1/W2',
        diagnostics=dict(stats),classes=reports,tag_availability=dict(availability),
        pre_filter_supply_per_class=dict(pre_supply),pre_filter_class_source_edition=dict(pre_source_edition),
        pre_filter_secondary_facets=dict(pre_facets),post_exclusion_split_supply=dict(raw_supply),
        excluded_editions=sorted(blocked-allowed),forced_test_editions_removed=sum(editions[e].get('forced',False) and editions[e].get('split',editions[e].get('proposed_split'))=='test' for e in blocked-allowed),
        class_source_edition=dict(Counter('|'.join((r['split'],r['class'],r['source'],r['edition_id'])) for r in candidates)),
        edition_counts={'|'.join(k):v for k,v in edcounts.items()},series_counts={'|'.join(k):v for k,v in sercounts.items()},
        edition_cap_hits=sorted('|'.join(e) for e,n in edcounts.items() if n==edition_cap),series_cap_hits=sorted('|'.join(s) for s,n in sercounts.items() if n==series_cap),
        secondary_facets=dict(Counter(k for r in candidates for k,v in r['tags'].items() if v is True)),
        classes_filled={s:sum(v['deficit']==0 for k,v in reports.items() if k.startswith(s+':')) for s in ('test','dev')})
    if edition_cap!=DEFAULT_EDITION_CAP or pool_include_forced!='both' or upper_bound:
        counts['mode']='DIAGNOSTIC ONLY; '+counts['mode']
        counts['diagnostic_options']=dict(edition_cap=edition_cap,series_cap=series_cap,pool_include_forced=pool_include_forced,
            added_rows={g:added[g] for g in ('n1','lqb')},added_classified_rows={g:added_classified[g] for g in ('n1','lqb')},
            included_forced_editions=len(allowed),locked_rows_never_drawable=True)
    counts['pool_options']=dict(pool_include_forced=pool_include_forced,added_rows=dict(added),
        included_forced_editions=len(allowed),locked_rows_never_drawable=True)
    paths=[tags_path,split_path,*edition_paths,*features]
    inputs=cache.get('input_shas') or {str(p):sha(p) for p in paths};inputs.update(exinputs)
    receipt=Path(tags_path).with_suffix('.receipt.json')
    if receipt.exists():
        inputs[str(receipt)]=sha(receipt)
        inputs.update(json.loads(receipt.read_text()).get('input_shas',{}))
    cache['input_shas']=inputs
    plan=dict(seed='bench02:<split>:<class>',order=list(PRECEDENCE),precedence_table=list(PRECEDENCE),
        caps=dict(edition=edition_cap,series=series_cap,scope='per class x edition, including overdraw; series per class'),quotas=QUOTAS,
        dev_quotas={k:v//4 for k,v in QUOTAS.items()},overdraw='ceil(1.2 * quota), per subgroup where specified',
        degraded=degraded_plan if relative else dict(confidence_below=.89,ink_density_field='absent in inspected census_05 producer',
            density_p25_by_source=percentiles,percentile_method='linear interpolation at (n-1)*0.25; all census W1/W2 rows per source before admission',
            density_branch='available' if percentiles else 'unavailable; confidence branch only'),
        punctuation_heavy='nonletter nondigit nonspace / nonspace >= 1/3 OR N1 leader/dash tag',
        serbian_documents=sorted(SERBIAN_DOCUMENTS),
        nominal_checks=3690,subgroup_rounded_checks=3691,p6_budget=3700,
        tags_verification=tags_verification,input_shas=inputs,code_sha=sha(__file__),
        numeric_grammar_source='frozen copy of greekocr/harvest/numeric_cells.py _numeric_reason; cell/A must be explicit',
        grouping='Selection independently per split/class: Random(bench02:<split>:<class>); shuffle sorted sources, then sorted editions per source, then rows sorted by (parent_id,row_id), using that RNG in sequence. One row/source/round; edition cursor persists; caps and subgroup limits include overdraw. Rank records this source -> edition selection order. Emission: repeat passes over lexicographically sorted edition IDs, classes in PRECEDENCE, emit at most one selected row per class/edition/pass, preserving selection order within each class/edition. No shared edition allowance across classes.',
        mode=counts['mode'],missing_series='null; cap enforced only for evidenced series; no invented series or extra exclusion',
        subquotas={side:{cl:subgroup_quotas(side,cl) for cl in ('modern_cyrillic','font_extremes')} for side in ('test','dev')})
    dump(dest/'draw_plan.json',plan);dump(dest/'counts.json',counts)
    lines=['# BENCH02D counts','',counts['mode'],'',f"Pre-filter supply: {stats['pre_filter_supply']}; admitted: {stats['admitted']}; forced-test editions excluded: {counts['forced_test_editions_removed']}.",'','| Split:class | Supply | Quota | Candidate target | Drawn | Deficit | Sources | Editions | Credit | Top-edition share | >=10 books / >=3 sources |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for k,v in reports.items():lines.append('| '+(k.split(':')[0]+':'+v['label'] if relative and k.endswith(':degraded') else k)+(' (Serbian-only)' if v['label']=='Serbian-only' else '')+' | '+' | '.join(str(v[x]) for x in ('supply','quota','overdraw_target','drawn','deficit','sources','editions','credited'))+f" | {v['top_edition_share']:.2%} | {v['diversity_pass']} |")
    lines+=['','Edition cap hits: '+str(len(counts['edition_cap_hits']))+'. Series cap hits: '+str(len(counts['series_cap_hits']))+'.','', 'Full class × source × edition counts, cap-hit IDs, secondary facets and tag availability are in counts.json. Books diagnostic counts edition IDs, including gazette issues; canonical works unverified. Polytonic census_03 awaits sf7; bg/uk and absent historical Russian remain deficits, with no quota transfer. Series cap is 3 x edition cap per class, unverifiable without series identity. Unknown series are diagnostic; no rows are excluded for missing series.']
    output(dest/'COUNTS.md').write_text('\n'.join(lines)+'\n')
    return counts


def readout(candidates, census_dir, output_dir):
    """Stream both census files; retain text/crop evidence for candidate keys only."""
    dest=output(Path(output_dir)/'candidates_readout.jsonl', output_dir)
    ordered=[key(r) for r in rows(candidates)]
    wanted=set(ordered)
    if len(wanted)!=len(ordered): raise ValueError('duplicate candidate ids')
    found={}; metadata={}
    for d in rows(Path(census_dir)/'decisions.jsonl'):
        k=key(d)
        if k not in wanted: continue
        if k in found: raise ValueError('duplicate candidate decision')
        found[k]=dict(parent_id=k[0],row_id=k[1],final_text=d['final_text'],
            raw_text_sha256=d['raw_text_sha256'],crop_sha256=d['binding']['crop_sha256'],edits=d['edits'])
    for diagnostic in rows(Path(census_dir)/'evaluation_diagnostics.jsonl'):
        k=key(diagnostic['decision'])
        if k not in wanted: continue
        if k in metadata: raise ValueError('duplicate candidate diagnostic')
        r=diagnostic['row']
        if key(r)!=k or r['crop_sha256']!=found.get(k,{}).get('crop_sha256'):
            raise ValueError('candidate crop binding mismatch')
        metadata[k]={x:r[x] for x in ('crop_source_image','crop_bbox')}
    if set(found)!=wanted or set(metadata)!=wanted:
        raise ValueError('candidate ids missing from census decisions or diagnostics')
    with dest.open('w') as f:
        for k in ordered: f.write(canonical(dict(found[k],**metadata[k]))+'\n')
    return len(ordered)


def absolute_dir(value):
    if not Path(value).is_absolute(): raise argparse.ArgumentTypeError('output-dir must be absolute')
    return Path(value)


def main():
    p=argparse.ArgumentParser(description=__doc__); subs=p.add_subparsers(dest='command',required=True)
    e=subs.add_parser('extract');e.add_argument('--decisions',nargs='+',required=True);e.add_argument('--diagnostics',nargs='+',required=True);e.add_argument('--output-dir',required=True,type=absolute_dir)
    r=subs.add_parser('readout');r.add_argument('--candidates',required=True);r.add_argument('--census-dir',required=True);r.add_argument('--output-dir',required=True,type=absolute_dir)
    d=subs.add_parser('draw');d.add_argument('--tags',required=True);d.add_argument('--split',required=True);d.add_argument('--editions',nargs='+',required=True)
    d.add_argument('--features',nargs=2,required=True,metavar=('W1','W2'));d.add_argument('--v2',nargs=3,required=True);d.add_argument('--exclusions',required=True);d.add_argument('--output',required=True);d.add_argument('--dry-run',action='store_true')
    d.add_argument('--edition-cap',type=edition_cap_arg,default=DEFAULT_EDITION_CAP,metavar='N|unlimited',help='per class x edition; series cap is 3*N per class')
    d.add_argument('--pool-include-forced',choices=('none','n1','lqb','both'),default='both',help='exact registered locked/eval rows stay excluded')
    d.add_argument('--upper-bound',action='store_true',help='diagnostic only: all W1/W2 split rows; UPPER BOUND, not admitted')
    d.add_argument('--tags-sha256',help='pinned tags checksum for a legacy receipt')
    d.add_argument('--require-receipt-sha',action='store_true')
    a=p.parse_args()
    if a.command=='extract':extract(a.decisions,a.diagnostics,a.output_dir/'tags.jsonl.gz',a.output_dir)
    elif a.command=='readout':readout(a.candidates,a.census_dir,a.output_dir)
    else:draw(a.tags,a.split,a.editions,a.features,a.v2,a.exclusions,a.output,a.dry_run,a.edition_cap,a.pool_include_forced,a.upper_bound,tags_sha256=a.tags_sha256,require_receipt_sha=a.require_receipt_sha)

if __name__=='__main__':main()
