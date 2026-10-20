"""R2C saved-data preparation. No OCR imports, services, model calls or git writes.

Card conventions copied in spirit from S8 l1a2_cards.py: full-height word
context, uniform <=3x zoom, native line, separate private joins and controls.
"""
import sys
sys.dont_write_bytecode = True
import argparse
from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
import html
import io
import gzip
import json
import math
from pathlib import Path
import random
import re
import socket
import unicodedata as U

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
PROJECTS = ROOT.parent
HARVEST = PROJECTS / 'greek-ocr-toolkit'
RUN = PROJECTS / 'collect-v3-data/run'
S8 = PROJECTS / 'greek-ocr-toolkit-spellcheck-s8'
EX = PROJECTS / 'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions'
OUT = ROOT / 'docs/labelfix/spellcheck/R2'
SEED = 'R2:2026-10-17:'
INPUTS = {}


def forbidden(*a, **kw):
    raise RuntimeError('R2C is offline, saved geometry only')


socket.socket.connect = forbidden
socket.create_connection = forbidden


@lru_cache(maxsize=16384)
def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def bind(path):
    path = Path(path)
    INPUTS[str(path)] = sha(path)
    return path


def load(path):
    return json.loads(bind(path).read_text())


def rows(path):
    with bind(path).open() as f:
        return [json.loads(s) for s in f if s.strip()]


def dump(path, data):
    path = Path(path)
    assert path.resolve().is_relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def jsonl(path, data):
    path = Path(path)
    assert path.resolve().is_relative_to(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(r, ensure_ascii=False, allow_nan=False) + '\n' for r in data))


def digest(s):
    return hashlib.sha256(s.encode()).hexdigest()


def alias(doc):
    return doc.split(':')[-1]


def line_doc(ident):
    return re.split(r'--n\d+|-p\d+|-l\d+', ident)[0]


def allocate(documents):
    """Largest-remainder allocation across source/era, then hash order per cell.

    Global targets avoid rounding every singleton cell up to a whole reserve.
    Witness = 20% of post-reserve (minimum 20); calibration = 15% of
    post-reserve. Exact rounding and tie break are persisted before mining.
    """
    groups = defaultdict(list)
    for d, r in documents.items():
        groups[(r['source'], r['era'])].append(d)
    for ds in groups.values():
        ds.sort(key=lambda d: digest(SEED + d))
    n = len(documents)
    targets = [('validation', round(n * .10)),
               ('witness', min(max(20, round((n-round(n*.10))*.20)), n-round(n*.10))),
               ('calibration', round((n-round(n*.10))*.15))]
    for role, target in targets:
        total = sum(map(len, groups.values()))
        quotas = {g: len(ds) * target / total for g, ds in groups.items()} if total else {}
        counts = {g: math.floor(q) for g, q in quotas.items()}
        for g in sorted(groups, key=lambda g: (-(quotas[g]-counts[g]), g))[:target-sum(counts.values())]:
            counts[g] += 1
        for g, ds in groups.items():
            k = counts[g]
            for d in ds[:k]:
                documents[d]['role'] = role
            groups[g] = ds[k:]
    for ds in groups.values():
        for d in ds:
            documents[d]['role'] = 'supervision'
    return documents


def inventory():
    w1 = rows(RUN/'W1/candidates.jsonl')
    v2base = HARVEST/'docs/harvest/collection/v2'
    train = rows(v2base/'import_real_v2_train.jsonl')
    devtest = rows(v2base/'import_real_v2_dev.jsonl') + rows(v2base/'import_real_v2_test.jsonl')
    c1path = S8/'.cache/labelfix/clariden/C1_selection.jsonl'
    c1 = rows(c1path)
    c1docs = {alias(r['doc']) for r in c1}
    assert len(c1docs) == 316
    ids = {}
    ids['S8_DEV'] = set(bind(S8/'docs/labelfix/spellcheck/S8_DEV/S8_DEV_ids.txt').read_text().split())
    audit = S8/'docs/labelfix/spellcheck/clariden/L1R3_evidence/production_3680729_3680730/audit100_ids.jsonl'
    ids['audit100'] = {r['line_id'] for r in rows(audit)}
    # This is exactly the saved-ID join in load_three_way(0), without importing
    # its recogniser/model dependency tree or writing import caches elsewhere.
    pred = PROJECTS/'greek-page-ocr/out/e3b/predictions'
    humans = rows(pred/'full_s0_wikisource_human.jsonl')
    vpred = {r['line_id'] for r in rows(pred/'full_s0_v2_test.jsonl')}
    ids['heldout666'] = {r['line_id'][:-6] for r in humans if r['source_dataset']=='wikisource_el'}
    assert len(ids['heldout666']) >= 666 and ids['heldout666'] <= vpred
    ids['v2_dev_test'] = {r['id'] for r in devtest}
    release = load(EX/'release_exclusions.json')
    alias_books={}
    for name, spec in release['classes'].items():
        p = EX/spec['file']
        # Owner directory contains a historical swapped-word filename. Accept
        # only the exact declared content hash, never an inferred replacement.
        if not p.exists():
            matches = [q for q in EX.glob('*.txt') if sha(q)==spec['sha256']]
            assert len(matches)==1, (name, 'missing exclusion input')
            p = matches[0]
        assert sha(p)==spec['sha256'], p
        ids['release_'+name] = set(bind(p).read_text().split())
        if spec.get('books'):
            alias_books['release_'+name]=set(spec['books'])
    allrows = train + devtest
    lookup = {r['id']: alias(r['doc']) for r in allrows}
    lookup.update({r['id']:r['item'] for r in w1})
    exclusion_docs = {k: {lookup.get(i, line_doc(i)) for i in s} for k,s in ids.items()}
    for name,books in alias_books.items():
        exclusion_docs[name].update(books)
    exclusion_docs['C1_316'] = c1docs
    strata = load(EX/'unchecked_strata.json')['strata']
    passed = {(s['tranche'],s['source'],s['primary_class'],s['gazette_stratum']) for s in strata if s['status']=='c1_pass'}
    allowed = {('bsb_poly1850','poly1850'),('ia_poly1850','poly1850'),('nlg','greek_poly'),('nlg','poly1850'),('nlg','poly1900')}
    count = Counter()
    overlap = Counter()
    eligible = []
    for pool, records in [('W1',w1),('v2',train)]:
        count[pool+'_input'] = len(records)
        for r in records:
            d = r['item'] if pool=='W1' else r['doc']
            reasons=[]
            if pool=='W1':
                if (r['source'],r['primary_class']) not in allowed:
                    reasons.append('not_requested_Greek_stratum')
                if (r['tranche'],r['source'],r['primary_class'],r.get('gazette_stratum')) not in passed:
                    reasons.append('stratum_not_c1_pass')
                if not (r.get('usable_final') is True and r.get('candidate_usable') is True):
                    reasons.append('line_admission_failed')
            else:
                if r['script_class'] not in ('greek_mono','greek_poly'):
                    reasons.append('not_Greek_class')
                if r.get('split')!='train':
                    reasons.append('not_train')
            for name, ds in exclusion_docs.items():
                # Quality/admission exclusions are line-level classes. Only
                # evaluation cohorts additionally exclude whole documents.
                line_only=name in ('release_separator_ambiguous','release_rotated_crop')
                if (not line_only and alias(d) in ds) or r['id'] in ids.get(name,set()):
                    reasons.append(name)
            for reason in reasons:
                overlap[pool+':'+reason] += 1
            if reasons:
                count[pool+':'+reasons[0]] += 1
                continue
            rr = dict(r, pool=pool, document=d)
            eligible.append(rr)
            count[pool+'_eligible'] += 1
    docs = {}
    for r in eligible:
        year = r.get('year')
        era = str(int(year)//10*10)+'s' if str(year).isdigit() else 'unknown'
        source = r['source'] if r['pool']=='W1' else r['wave']+':'+r['source']
        meta = dict(source=source, era=era, line_count=0, pool=r['pool'])
        docs.setdefault(r['document'], meta)['line_count'] += 1
        assert docs[r['document']]['source']==source
    allocate(docs)
    rule = ('source x decade; v2 source = wave:source; sha256("R2:2026-10-17:"+doc) ascending within cells; '
            'global rounded 10% validation; 20% of remaining witness (minimum 20); 15% of post-validation calibration; '
            'largest remainder per role over remaining cells, fractional ties source/era lexical; rest supervision')
    result = dict(rule=rule, documents=docs, role_counts=dict(Counter(r['role'] for r in docs.values())),
                  input_sha256=INPUTS.copy(), exclusion_counts_sequential=dict(count),
                  exclusion_counts_overlapping=dict(overlap),
                  exclusion_set_sizes={k:dict(lines=len(v),documents=len(exclusion_docs[k])) for k,v in ids.items()},
                  c1_selection_fallback=str(c1path),
                  heldout_note='Current saved load_three_way(0) ID join has %d lines; conservatively excluded all, versus brief 666.' % len(ids['heldout666']),
                  reservation_before_geometry=True)
    path=OUT/'doc_roles.json'
    if path.exists():
        previous=json.loads(path.read_text())
        if previous!=result:
            changes={k:dict(previous=previous.get(k),current=result.get(k)) for k in set(previous)|set(result) if previous.get(k)!=result.get(k)}
            if set(changes)=={'exclusion_set_sizes'}:
                # Repair only the displayed line-set count: book aliases are
                # documents, never synthetic line IDs. Frozen roles/input
                # identities/line populations must remain byte-equivalent.
                dump(OUT/'receipts/exclusion_count_metadata_correction.json',dict(
                    reason='Resolve saved document aliases and legacy page prefixes; count book aliases as documents, never as lines',changes=changes,
                    frozen_documents_unchanged=True,old_sha256=sha(path)))
                dump(path,result)
            elif (set(changes)<={'input_sha256','exclusion_counts_overlapping','exclusion_set_sizes'} and
                  previous['documents']==result['documents'] and
                  previous['role_counts']==result['role_counts'] and
                  previous['exclusion_counts_sequential']==result['exclusion_counts_sequential']):
                # A live owner's class index may gain an out-of-universe class.
                # Refresh custody only when the entire eligible population and
                # every pre-draw document assignment are exactly unchanged.
                oldids={json.loads(s)['id'] for s in (OUT/'eligible_lines.jsonl').read_text().splitlines()}
                assert oldids=={r['id'] for r in eligible}, 'Eligible pool changed; require a new reviewed preparation'
                if not (OUT/'receipts/doc_roles_reservation_snapshot.json').exists():
                    dump(OUT/'receipts/doc_roles_reservation_snapshot.json',previous)
                dump(OUT/'receipts/live_exclusion_refresh.json',dict(changes=changes,
                    eligible_line_ids_unchanged=True,document_roles_unchanged=True,
                    note='New live rotated-crop class has zero eligible rows; quality classes remain line-level, not whole-document exclusions.'))
                dump(path,result)
            else:
                dump(OUT/'receipts/reservation_recheck_difference.json',changes)
                raise AssertionError('Reservation changed; refuse redraw')
    else:
        dump(path,result)
    jsonl(OUT/'eligible_lines.jsonl',eligible)
    print('Reserved',len(docs),'documents',result['role_counts'],dict(count),flush=True)
    return eligible,docs


def anchor_range(layout):
    ss = layout.get('textAnchor',{}).get('textSegments',[])
    if len(ss)!=1:
        raise ValueError('noncontiguous_text_anchor')
    return int(ss[0].get('startIndex',0)),int(ss[0]['endIndex'])


def literal_normalize(form,text):
    # Copied S8 convention: preserve printed keraia codepoints through Unicode
    # normalisation. U+0384 is not an accent head; U+0374 is not a letter slot.
    return ''.join(c if c in ('\u0374','\u0384') else U.normalize(form,c)
                   for c in re.split('([\u0374\u0384])',text))


def is_letter(c):
    return U.category(c) in ('Lu','Ll','Lt','Lo')


def skeleton(text):
    return ''.join(c for c in literal_normalize('NFD',text) if is_letter(c))


def clusters(text):
    out=[]
    for c in literal_normalize('NFD',text):
        if U.combining(c) and out:
            out[-1]+=c
        else:
            out.append(c)
    return out


def tuple_heads(cluster):
    return dict(breathing='dasia' if '\u0314' in cluster else 'psili' if '\u0313' in cluster else 'none',
                accent='acute' if '\u0301' in cluster else 'grave' if '\u0300' in cluster else 'circumflex' if '\u0342' in cluster else 'none',
                diaeresis='present' if '\u0308' in cluster else 'none',
                subscript='present' if '\u0345' in cluster else 'none')


def polygon_box(layout, size, native_normalized=False):
    poly=layout['boundingPoly']
    if native_normalized or not poly.get('vertices'):
        points=[(v.get('x',0)*size[0],v.get('y',0)*size[1]) for v in poly['normalizedVertices']]
    else:
        points=[(v.get('x',0),v.get('y',0)) for v in poly['vertices']]
    return [min(p[0] for p in points),min(p[1] for p in points),max(p[0] for p in points),max(p[1] for p in points)]


def v2_metadata(eligible):
    wanted={r['id'] for r in eligible if r['pool']=='v2'}
    admits={}; records={}
    for wave in sorted({r['wave'] for r in eligible if r['pool']=='v2'}):
        base=HARVEST/'docs/harvest'/wave
        p=base/'admitted.jsonl'
        if p.exists():
            admits.update({r['id']:r for r in rows(p) if r['id'] in wanted})
        candidates=[base/'records.jsonl']
        if wave=='round1':
            candidates=[base/'records_all.jsonl',base/'reads_d1/records.jsonl',base/'reads_rest/records.jsonl']
        for p in candidates:
            if p.exists():
                records.update({r['id']:r for r in rows(p) if r['id'] in wanted})
    return admits,records


@lru_cache(maxsize=8)
def response(path):
    j=load(path)
    return j.get('document',j)


@lru_cache(maxsize=8)
def saved_response(path,expected):
    path=Path(path)
    if path.exists():
        if sha(path)!=expected:
            raise ValueError('response_hash_mismatch')
        return response(str(path)),str(path),sha(path)
    compressed=Path(str(path)+'.dedup.gz')
    if not compressed.exists():
        raise ValueError('missing_saved_response')
    bind(compressed)
    j=json.loads(gzip.decompress(compressed.read_bytes()))
    if j.get('schema')!='t23-raw-dedup-1' or j['raw_sha256']!=expected:
        raise ValueError('dedup_response_identity_mismatch')
    return j['response']['document'],str(compressed),sha(compressed)


@lru_cache(maxsize=2)
def native_page(path):
    bind(path)
    with Image.open(path) as im:
        return im.convert('L')


def restore_crop(r):
    path=Path(r['crop'])
    if path.exists():
        return path
    # Reproduce the disposable W1 PNG byte for byte from the retained raster.
    # This is pixel cropping, not recognition; original file hash must match.
    image=native_page(r['crop_source_image']).crop(r['crop_bbox'])
    stream=io.BytesIO();image.save(stream,format='PNG',compress_level=3)
    payload=stream.getvalue()
    if hashlib.sha256(payload).hexdigest()!=r['crop_sha256']:
        raise ValueError('native_crop_reconstruction_hash_mismatch')
    path=OUT/'native_crops'/(r['crop_sha256']+'.png')
    path.parent.mkdir(exist_ok=True)
    if not path.exists():
        path.write_bytes(payload)
    return path


def locate(r, admits, records):
    """Use provider token anchors only; stored text is only a mining key.

    Refuse frame conversions without an explicit saved native-frame policy.
    No equal-width text slicing or estimated character locations.
    """
    if r['pool']=='W1':
        meta=load(RUN/'W1/pages'/(r['page_id']+'.json'))
        raw=Path(meta['response'])
        doc,raw,rawhash=saved_response(str(raw),meta['response_sha256'])
        idx=r['docai_line_index']; box=r['crop_bbox']
        crop=restore_crop(r)
        native_normalized=False
        # native_size in the discovery record can predate the saved downscale.
        # Token geometry is in the submitted retained raster's pixel frame.
        bind(r['crop_source_image'])
        with Image.open(r['crop_source_image']) as source_image:
            size=list(source_image.size)
    else:
        a=admits.get(r['id']); rec=records.get(r['id'])
        if not a or not rec:
            raise ValueError('missing_saved_line_metadata')
        crop=HARVEST/r['crop']
        if a['crop_path']!=r['crop']:
            raise ValueError('crop_identity_mismatch')
        box=a['crop_bbox'];idx=rec['docai_index']
        base=HARVEST/'docs/harvest/harvest_big'/r['wave']/'google/docai'
        matches=list(base.glob('*/'+rec['image_sha256']+'-*/cache.json'))
        # Round1 rescue has a separate response directory.
        if not matches:
            matches=list((HARVEST/'docs/harvest/harvest_big'/r['wave']).glob('**/docai/*/'+rec['image_sha256']+'-*/cache.json'))
        if len(matches)!=1:
            raise ValueError('missing_or_ambiguous_response')
        receipt=load(matches[0]);raw=Path(receipt['raw_json_path'])
        doc,raw,rawhash=saved_response(str(raw),receipt['raw_sha256'])
        native_normalized='docai_normalized_vertices_native_frame' in rec.get('flags',[])
        bind(HARVEST/rec['image'])
        with Image.open(HARVEST/rec['image']) as page:
            size=list(page.size)
    page=doc['pages'][0]
    dims=page['dimension']; reported=[int(dims['width']),int(dims['height'])]
    size=size or reported
    if page.get('transforms') and not native_normalized:
        # A transform must be explicitly inverted; unsupported frames stay out.
        raise ValueError('unqualified_page_transform')
    if list(size)!=reported and not native_normalized:
        raise ValueError('page_frame_mismatch')
    line=page['lines'][idx]['layout']; start,end=anchor_range(line)
    txt=doc['text']; original=txt[start:end]
    raw_words=list(re.finditer(r'\S+', original))
    keys=re.findall(r'\S+',r.get('label',r.get('text','')))
    if len(keys)!=len(raw_words) or any(skeleton(a)!=skeleton(b.group()) for a,b in zip(keys,raw_words)):
        raise ValueError('line_anchor_text_mismatch')
    image=Image.open(crop).convert('L')
    if image.size!=(box[2]-box[0],box[3]-box[1]):
        raise ValueError('crop_frame_mismatch')
    crop_hash=sha(crop)
    expected=r.get('crop_sha256') if r['pool']=='W1' else a.get('crop_sha256')
    if expected and crop_hash!=expected:
        raise ValueError('crop_hash_mismatch')
    INPUTS[str(crop)]=crop_hash
    ink=np.asarray(image)<180
    tokens=[]
    for token in page.get('tokens',[]):
        ts,te=anchor_range(token['layout'])
        if start<=ts and te<=end:
            tokens.append((ts,te,polygon_box(token['layout'],size,native_normalized)))
    words=[]
    for wi,(key,m) in enumerate(zip(keys,raw_words)):
        s,e=start+m.start(),start+m.end()
        tt=[t for t in tokens if t[0]<e and t[1]>s]
        if not tt or any(txt[max(t[0],s):min(t[1],e)].strip()=='' for t in tt):
            continue
        # Provider tokens may include a trailing space, but may not straddle words.
        if any(txt[t[0]:s].strip() if t[0]<s else False for t in tt):
            continue
        if any(txt[e:t[1]].strip() if t[1]>e else False for t in tt):
            continue
        b=[min(t[2][0] for t in tt)-box[0],min(t[2][1] for t in tt)-box[1],
           max(t[2][2] for t in tt)-box[0],max(t[2][3] for t in tt)-box[1]]
        h,w=ink.shape
        if b[0]<0 or b[1]<-1 or b[2]>w or b[3]>h+1:
            continue
        # Full crop height retains marks. Find clean vertical boundaries within
        # 0.25 line heights of the token edge. No foreground component is cut.
        x0=max(0,math.floor(b[0]));x1=min(w,math.ceil(b[2]))
        margin=max(2,round(.25*h))
        left=[x for x in range(max(0,x0-margin),x0+1) if x>0 and not ink[:,x-1:x+1].any()]
        right=[x for x in range(x1,min(w,x1+margin)+1) if x<w and not ink[:,x-1:x+1].any()]
        if not left or not right:
            continue
        lo=min(left);hi=max(right)
        if not ink[:,x0:x1].any():
            continue
        # Preserve all visible pixels; clipped native word pixels cannot qualify
        # as a trustworthy complete locator, including top/bottom mark fragments.
        if ink[0,lo:hi].any() or ink[-1,lo:hi].any():
            continue
        words.append(dict(uid=digest(crop_hash+':'+str(wi)),line_id=r['id'],doc=r['document'],
                          source=r['source'],pool=r['pool'],page=r.get('page_id',r['id'].rsplit('-l',1)[0]),
                          crop=str(crop),crop_sha256=crop_hash,word_index=wi,mining_key=key,
                          crop_letter_offset=sum(len(skeleton(k)) for k in keys[:wi]),
                          word_box=[lo,0,hi,h],token_box=b,geometry_response=str(raw),
                          geometry_response_sha256=rawhash,native_size=[w,h],
                          script_class=r.get('script_class',r.get('primary_class')),
                          neighbour_body_ink_xh=r.get('neighbour_body_ink_xh',0),
                          accent_ink_cut_fraction=r.get('accent_ink_cut_fraction',0)))
    return words


def geometry(eligible,docs):
    # Reservation is already persisted and hash-bound before entering here.
    assert (OUT/'doc_roles.json').is_file()
    admits,records=v2_metadata(eligible)
    coverage=defaultdict(Counter); candidates=[]
    for i,r in enumerate(eligible):
        source=r['source'];coverage[source]['eligible_lines']+=1
        if docs[r['document']]['role'] in ('validation','calibration'):
            coverage[source]['reserved_not_located']+=1
            continue
        coverage[source]['attempted_lines']+=1
        try:
            ww=locate(r,admits,records)
        except (ValueError,KeyError,IndexError,FileNotFoundError) as e:
            coverage[source][str(e) if isinstance(e,ValueError) else type(e).__name__]+=1
            continue
        if ww:
            coverage[source]['lines_with_safe_words']+=1
            coverage[source]['safe_words']+=len(ww)
            candidates.extend(ww)
        else:
            coverage[source]['no_safe_word_box']+=1
        if i%1000==0:
            print('Geometry',i,'/',len(eligible),'words',len(candidates),flush=True)
    dump(OUT/'geometry_coverage.json',coverage)
    jsonl(OUT/'located_words.jsonl',candidates)
    dump(OUT/'receipts/geometry_inputs.json',INPUTS)
    return candidates,coverage


def slice_candidates(word):
    cs=[c for c in clusters(word['mining_key']) if is_letter(c[0])]
    if not cs or not all('GREEK' in U.name(c[0],'') for c in cs):
        return []
    base=''.join(c[0] for c in cs); out=[]
    vowels=[i for i,c in enumerate(cs) if c[0].lower() in 'αεηιουω']
    def add(sl,i,head,marked):
        out.append(dict(slice=sl,anchor_index=i,target_head=head,mining_marked=bool(marked)))
    caps=[i for i,c in enumerate(cs) if c[0].isupper()]
    caps.sort(key=lambda i:(not any(v!='none' for v in tuple_heads(cs[i]).values()),i not in vowels,i))
    for i in caps[:1]:
        # All-caps words, lone vowels, initials/numerals; marked capitals may
        # also occur in ordinary titlecase words.
        marked=any(v!='none' for v in tuple_heads(cs[i]).values())
        if (len(base)>=2 and base.isupper()) or len(base)==1 or marked:
            add('capitals',i,'breathing' if tuple_heads(cs[i])['accent']=='none' else 'accent',marked)
    if not vowels:
        return out
    if base in ('ο','οι') or base.startswith('εξ') or cs[0][0].lower() in 'αεηιουω':
        if cs[0][0].islower():
            i=1 if base=='οι' else 0
            breathing=tuple_heads(cs[i])['breathing']
            mono=word['script_class']=='greek_mono'
            if base in ('ο','οι') or base.startswith('εξ') or mono or breathing!='none':
                add('omicron_monotonic',i,'breathing',breathing!='none')
    if cs[-1][0].lower() in 'αηω':
        add('subscript',len(cs)-1,'subscript','\u0345' in cs[-1])
    risk=(word['neighbour_body_ink_xh']>=1.0 or word['accent_ink_cut_fraction']>=.05 or
          word['token_box'][0]<word['native_size'][1]*.5 or
          word['native_size'][0]-word['token_box'][2]<word['native_size'][1]*.5)
    if risk:
        i=vowels[0]; heads=tuple_heads(cs[i]);marked=any(v!='none' for v in heads.values())
        head=next((h for h,v in heads.items() if v!='none'),'breathing')
        add('specks',i,head,marked)
    # Exact-name subtypes retain their own acquisition counts; no orthographic
    # validity is consulted, including mid-word breathings/coronis.
    exact=[]
    for i in vowels:
        hh=tuple_heads(cs[i])
        if hh['accent'] in ('grave','acute') and i==vowels[-1]:
            exact.append((i,'accent','final_accent'))
        if hh['accent']=='circumflex':
            exact.append((i,'accent','circumflex'))
        if hh['diaeresis']=='present':
            exact.append((i,'diaeresis','dialytika'))
        if hh['breathing']!='none':
            exact.append((i,'breathing','crasis' if i>1 or (i>0 and base[0].lower() not in 'αεηιουω') else 'psili_dasia'))
    for i,head,subtype in exact:
        out.append(dict(slice='exact_names',anchor_index=i,target_head=head,mining_marked=True,subtype=subtype))
    # T4 absent exact-name counterparts are independently sampled bare heads.
    i=vowels[0]
    if all(v=='none' for v in tuple_heads(cs[i]).values()):
        out.append(dict(slice='exact_names_absent',anchor_index=i,target_head='accent',mining_marked=False))
    add('random',vowels[0],'breathing',tuple_heads(cs[vowels[0]])['breathing']!='none')
    return out


def c1_priority(words):
    errors={}; byline={w['line_id']:w for w in words if w['pool']=='W1'}
    c1base=PROJECTS/'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts'
    counts=Counter()
    for name in ['bsb_poly1850__poly1850','ia_poly1850__poly1850','nlg__greek_poly','nlg__poly1850','nlg__poly1900']:
        keypath=RUN/'W1/c1'/(name+'_key.json')
        cardpath=RUN/'W1/c1'/name/'cards.jsonl'
        if not keypath.exists() or not cardpath.exists():
            continue
        keys=load(keypath); cards={r['card_id']:r for r in rows(cardpath)}
        for p in sorted(c1base.glob(name+'__*.jsonl')):
            for verdict in rows(p):
                if verdict.get('marks')!='n':
                    continue
                counts['mark_error_cards']+=1
                ident=keys[verdict['card_id']]['line_id']
                if ident not in byline:
                    continue
                source=byline[ident]
                cpath=cardpath.parent/cards[verdict['card_id']]['crop']
                bind(cpath)
                with Image.open(cpath) as a, Image.open(source['crop']) as b:
                    if a.size!=b.size or a.convert('L').tobytes()!=b.convert('L').tobytes():
                        counts['identity_join_refused']+=1
                        continue
                errors[ident]=dict(card_id=verdict['card_id'],verdict=str(p),crop_sha256=sha(cpath))
                counts['eligible_exact_crop_joins']+=1
    dump(OUT/'receipts/c1_priority.json',dict(counts=counts,joined_lines=errors))
    return errors


def options(base,anchor,head,seed):
    # No provider mark is copied. Only base letters and punctuation survive.
    spacing_names=('PSILI','DASIA','VARIA','OXIA','PERISPOMENI','DIALYTIKA','TONOS','KORONIS')
    cc=[c for c in literal_normalize('NFD',base) if not U.category(c).startswith('M') and
        not (c not in ('\u0374','\u0384') and not is_letter(c) and 'GREEK' in U.name(c,'') and
             any(s in U.name(c,'') for s in spacing_names))]
    positions=[i for i,c in enumerate(cc) if is_letter(c)]
    pos=positions[anchor]
    marks={'breathing':['','\u0313','\u0314'], 'accent':['','\u0301','\u0300','\u0342'],
           'diaeresis':['','\u0308'], 'subscript':['','\u0345']}[head]
    forms=[literal_normalize('NFC',''.join(cc[:pos+1])+m+''.join(cc[pos+1:])) for m in marks]
    random.Random(seed).shuffle(forms)
    return {chr(65+i):v for i,v in enumerate(forms)}


def select(words,docs,deck,priority):
    role='supervision' if deck=='T2' else 'witness'
    pool=[w for w in words if docs[w['doc']]['role']==role]
    buckets=defaultdict(list)
    for w in pool:
        for spec in slice_candidates(w):
            buckets[(spec['slice'],spec['mining_marked'])].append(dict(w,**spec))
    targets=({'capitals':260,'omicron_monotonic':160,'subscript':180,'specks':120,'exact_names':80} if deck=='T2'
             else {'capitals':100,'omicron_monotonic':100,'subscript':100,'exact_names':100,'random':200,'specks':200})
    selected=[]; used=set(); pages=Counter(); counts=Counter(); skips=Counter()
    document_counts=Counter()
    def draw(sl,marked,n):
        bucket='exact_names_absent' if sl=='exact_names' and not marked else sl
        pp=buckets[(bucket,marked)] if marked is not None else buckets[(bucket,False)]+buckets[(bucket,True)]
        # C1 mark-error line candidates come first, exact raster identity joined.
        # Within that priority, deterministic hash draws; round-robin documents
        # give every available witness document a chance before repeated draws.
        groups=defaultdict(list)
        for w in pp:
            groups[(0 if w['line_id'] in priority and deck=='T2' else 1,w['doc'])].append(w)
        for gg in groups.values():
            gg.sort(key=lambda w:digest(SEED+deck+sl+w['uid']+str(w['anchor_index'])))
        ordered=[]
        for rank in (0,1):
            gs={d:gg for (r,d),gg in groups.items() if r==rank}
            ds=sorted(gs,key=lambda d:digest(SEED+deck+sl+d))
            for i in range(max((len(gg) for gg in gs.values()),default=0)):
                ordered.extend(gs[d][i] for d in ds if i<len(gs[d]))
        if sl=='random':
            ordered=sorted(pp,key=lambda w:digest(SEED+deck+'uniform'+w['uid']))
        elif sl=='exact_names' and marked:
            sub=defaultdict(list)
            for w in ordered:
                sub[w['subtype']].append(w)
            ordered=[]
            for i in range(max(map(len,sub.values()),default=0)):
                ordered.extend(sub[t][i] for t in sorted(sub) if i<len(sub[t]))
        if deck=='T2':
            ordered.sort(key=lambda w:w['line_id'] not in priority)
        got=0
        for w in ordered:
            if got>=n:
                break
            if w['uid'] in used:
                skips['already_selected_word']+=1;continue
            if pages[w['page']]>=5:
                skips['page_cap']+=1;continue
            if document_counts[(sl,w['doc'])]>=targets[sl]//10:
                skips['document_slice_cap']+=1;continue
            selected.append(dict(w,slice=sl,control=False,c1_priority=priority.get(w['line_id'])))
            used.add(w['uid']);pages[w['page']]+=1;document_counts[(sl,w['doc'])]+=1
            counts[(sl,marked)]+=1;got+=1
        return got
    # Harder sparse slices first, with fixed limits and no quota backfill.
    for sl in ('capitals','subscript','omicron_monotonic','exact_names','specks','random'):
        if sl not in targets:
            continue
        n=targets[sl]
        if sl=='exact_names' and deck=='T2':
            draw(sl,True,n)
        elif sl=='random':
            draw(sl,None,n)
        else:
            draw(sl,False,n//2);draw(sl,True,n-n//2)
    # Proposed controls only. Their printed labels remain unverified until the
    # lead signs the private control key. No text is promoted to print truth.
    deckdocs={w['doc'] for w in selected}
    controls=[]
    for w in sorted(pool,key=lambda w:digest(SEED+deck+'control'+w['uid'])):
        if len(controls)>=80:
            break
        if w['uid'] in used or w['doc'] not in deckdocs or pages[w['page']]>=5:
            continue
        base=skeleton(w['mining_key'])
        if not 2<=len(base)<=9 or any(not ('GREEK' in U.name(c,'')) for c in base):
            continue
        specs=slice_candidates(w)
        if not specs:
            continue
        spec=specs[-1]
        controls.append(dict(w,**spec,control=True))
        used.add(w['uid']);pages[w['page']]+=1
    receipt=dict(targets=targets,drawn={sl:sum(w['slice']==sl for w in selected) for sl in targets},
                 candidates={f'{sl}:{"marked" if marked else "absent"}':len(v) for (sl,marked),v in sorted(buckets.items())},
                 drawn_polarity={f'{sl}:{marked}':n for (sl,marked),n in counts.items()},
                 caps_hit=dict(skips),documents=len(deckdocs),controls=len(controls),
                 max_cards_per_page=max(pages.values(),default=0),
                 max_document_per_slice={sl:max((v for (s,d),v in document_counts.items() if s==sl),default=0) for sl in targets},
                 c1_priority_drawn=sum(bool(w.get('c1_priority')) for w in selected),
                 exact_name_subtypes=dict(Counter(w.get('subtype','absent_counterpart') for w in selected if w['slice']=='exact_names')),
                 random_sampling='sha256 permutation of all vowel-bearing words, rejecting previously selected words and diversity cap violations',
                 shortfalls={sl:targets[sl]-sum(w['slice']==sl for w in selected) for sl in targets})
    return selected,controls,receipt


def save_pixels(path,image):
    data=io.BytesIO();image.save(data,format='PNG')
    raw=data.getvalue();name=hashlib.sha256(raw).hexdigest()+'.png'
    (path/name).write_bytes(raw)
    return name


def control_review(private):
    cp=json.loads((private/'controls_proposed.json').read_text())
    parts=['<!doctype html><meta charset="utf-8"><title>Proposed controls: lead pixel review</title><style>body{font:18px system-ui;margin:24px}article{margin:32px 0;padding:16px;border:1px solid #aaa}.pixels{overflow:auto}img{max-width:none;display:block}pre{white-space:pre-wrap;font:14px monospace}.form{font:30px serif}</style><h1>Proposed controls — lead pixel review required</h1><p>Check the complete printed word and every proposed letter tuple against the pixels. These are proposals, never accepted truth. Correct or replace defective controls, then set lead_verified only in controls_proposed.json after review. Readers must not start before all controls are verified.</p>']
    for c in cp['controls']:
        parts.append('<article><p>'+c['card_id']+'</p><p class="form">'+html.escape(c['expected_form'])+'</p><div class="pixels"><img src="'+c['word_image']+'"><img src="'+c['line_image']+'"></div><pre>'+html.escape(json.dumps(c['expected_letter_heads'],ensure_ascii=False))+'</pre></article>')
    (private/'controls_review.html').write_text('\n'.join(parts))


README='''# Printed word reading

Transcribe what is printed, including misprints. Do not normalise spelling.
Use word pixels and the full native line to decide mark ownership. The zoom
retains context on both sides; read the central word. Anchor indexes count
letters only, from zero; punctuation does not count.

Options are generated from base letters, varying one head at the anchor.
Other printed marks may be absent from the options: choose `literal` and
transcribe the COMPLETE word exactly whenever no option is exact. You may
always use literal transcription. Choose `unreadable` for an unreadable/cut word.

For the anchor give breathing (none/psili/dasia/unknown), accent
(none/acute/grave/circumflex/unknown), diaeresis and subscript
(none/present/unknown). Include `letter_heads` for every other letter you can
decide, with zero-based index and all four heads. Never infer an invisible head.
Use unknown for undecided heads; do not guess from spelling.
Give readability readable/partial/unreadable, ownership_ok true/false/null,
confidence high/medium/low, and a short note. Mark ownership means ink owned
by this letter, rather than another line, a neighbour, or a speck.

Use cards.jsonl in order for reader 1 and cards_reverse.jsonl for reader 2.
Readers work independently. Repeated views share witness_group and are ONE
source word, never independent statistical witnesses. Do not compare answers.
The coordinator must verify the private control key before any reader starts.
Answer files are JSONL, one answer per card, following answer_schema.json.
'''


def render_deck(deck,data,controls,receipt):
    base=OUT/'decks'/deck; blind=base/'blind';private=base/'private'
    blind.mkdir(parents=True,exist_ok=True);private.mkdir(parents=True,exist_ok=True)
    if (private/'controls_proposed.json').exists():
        old=json.loads((private/'controls_proposed.json').read_text())
        if any(c.get('lead_verified') for c in old['controls']):
            raise ValueError('Refuse to replace a deck with lead-verified controls')
    # These directories are generated artifacts owned exclusively by this
    # builder. Remove stale views before replacing a pre-reader draft.
    for directory in (blind,private):
        for path in directory.iterdir():
            assert path.is_file() and path.suffix in ('.png','.json','.jsonl','.html','.md')
            path.unlink()
    public=[];key=[];proposed=[]
    combined=data+controls
    combined.sort(key=lambda w:digest(SEED+deck+'order'+w['uid']))
    repeats=set(w['uid'] for w in sorted([w for w in data if w['slice']=='specks'],key=lambda w:digest(SEED+'views'+w['uid']))[:50]) if deck=='T4' else set()
    for w in combined:
        card_id=digest(SEED+deck+'card'+w['uid'])[:24]
        with Image.open(w['crop']) as im:
            line=im.convert('RGB')
        crop=line.crop(w['word_box']);scale=min(3.,1200/crop.width)
        # Integer uniform zoom guarantees identical scale on both axes.
        scale=max(1,min(3,math.floor(scale)))
        zoom=crop.resize((crop.width*scale,crop.height*scale),Image.Resampling.LANCZOS)
        linefile=save_pixels(blind,line);wordfile=save_pixels(blind,zoom)
        opts=options(w['mining_key'],w['anchor_index'],w['target_head'],SEED+card_id)
        pub=dict(card_id=card_id,word_image=wordfile,line_image=linefile,anchor_index=w['anchor_index'],
                 anchor_base=skeleton(w['mining_key'])[w['anchor_index']],options=opts,
                 extra_options={'literal':'none of these: transcribe the word exactly as printed','unreadable':'unreadable / cut'})
        views=[]
        if w['uid'] in repeats:
            # Keep every pixel. Span jitter expands left/right, never crops the
            # original word. Rotation expands the canvas; native line stays fixed.
            padded=Image.new('RGB',(crop.width+16,crop.height+16),'white');padded.paste(crop,(8,8))
            angle=1.5 if int(card_id,16)%2 else -1.5
            skew=padded.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True,fillcolor='white')
            lo,_,hi,h=w['word_box'];jitter=line.crop((max(0,lo-3),0,min(line.width,hi+5),h))
            for kind,im in [('padding',padded),('mild_skew',skew),('span_jitter',jitter)]:
                name=save_pixels(blind,im.resize((im.width*scale,im.height*scale),Image.Resampling.LANCZOS))
                views.append(dict(kind=kind,image=name))
            pub.update(witness_group=card_id,paired_views=views)
        public.append(pub)
        priv=dict(w,card_id=card_id,options=opts,public=pub,zoom_scale=scale,paired_views=views)
        key.append(priv)
        if w['control']:
            letters=[c for c in clusters(w['mining_key']) if is_letter(c[0])]
            cp=dict(card_id=card_id,expected_form=literal_normalize('NFC',w['mining_key']),
                    expected_letter_heads=[dict(index=i,**tuple_heads(c)) for i,c in enumerate(letters)],
                    word_image=wordfile,line_image=linefile,lead_verified=False,
                    expected_readability='readable',expected_ownership_ok=True,
                    status='proposed_from_selection_text_REQUIRES_PIXEL_VERIFICATION')
            proposed.append(cp)
            (private/wordfile).write_bytes((blind/wordfile).read_bytes())
            (private/linefile).write_bytes((blind/linefile).read_bytes())
    jsonl(blind/'cards.jsonl',public);jsonl(blind/'cards_reverse.jsonl',list(reversed(public)))
    jsonl(private/'key.jsonl',key)
    dump(private/'controls_proposed.json',dict(status='NOT_PIXEL_VERIFIED_DO_NOT_START_READERS',controls=proposed))
    control_review(private)
    # A deck-level private proposal index points to images beside the actual key.
    dump(base/'controls_proposed.json',dict(private_key='private/controls_proposed.json',controls=len(proposed),lead_verified=False))
    (blind/'README.md').write_text(README)
    schema=dict(card_id='required opaque ID',choice='option letter, literal, or unreadable',
                transcription='required for literal; complete word as printed',
                anchor_heads={'breathing':['none','psili','dasia','unknown'],'accent':['none','acute','grave','circumflex','unknown'],
                              'diaeresis':['none','present','unknown'],'subscript':['none','present','unknown']},
                letter_heads='list of {index,breathing,accent,diaeresis,subscript} for other decided letters',
                readability=['readable','partial','unreadable'],ownership_ok=[True,False,None],
                confidence=['high','medium','low'],note='short note',usage={'input_tokens':0,'output_tokens':0})
    dump(blind/'answer_schema.json',schema)
    for reverse,name in [(False,'index.html'),(True,'reverse.html')]:
        pp=list(reversed(public)) if reverse else public
        parts=['<!doctype html><meta charset="utf-8"><title>Word reading</title><style>body{font:18px system-ui;margin:24px}article{margin:40px 0;padding:16px;border:1px solid #ccc}.native{overflow:auto}img{display:block;max-width:none}li{font:24px serif}</style><h1>Word reading</h1><p>Read README.md and answer_schema.json first. Full lines scroll horizontally at native pixels.</p>']
        for p in pp:
            parts.append('<article id="'+p['card_id']+'"><p>'+p['card_id']+' · anchor letter '+str(p['anchor_index'])+' ('+p['anchor_base']+')</p><div class="native"><img src="'+p['word_image']+'"></div><div class="native"><img src="'+p['line_image']+'"></div><ul>')
            parts.extend('<li>'+k+': '+html.escape(v)+'</li>' for k,v in p['options'].items())
            parts.append('</ul><p>none of these: transcribe the word exactly as printed · unreadable / cut</p>')
            for view in p.get('paired_views',[]):
                parts.append('<p>Repeated view of this witness: '+view['kind']+'</p><div class="native"><img src="'+view['image']+'"></div>')
            parts.append('</article>')
        (blind/name).write_text('\n'.join(parts))
    receipt.update(paired_source_words=len(repeats),additional_views=len(repeats)*3,
                   data_cards=len(data),controls_proposed=len(controls),controls_pixel_verified=0,
                   state='PREPARED_PENDING_LEAD_CONTROL_AND_GEOMETRY_QA',
                   key_sha256=sha(private/'key.jsonl'))
    dump(private/'receipt.json',receipt)
    return receipt


def qa_strips(words):
    groups=defaultdict(list)
    for w in words:
        groups[w['source']].append(w)
    qa=OUT/'qa';qa.mkdir(exist_ok=True)
    manifest={}
    for source,ww in sorted(groups.items()):
        # Hash selection is a reproducible uniform random permutation.
        chosen=sorted(ww,key=lambda w:digest(SEED+'QA'+w['uid']))[:20]
        panels=[]
        for i,w in enumerate(chosen):
            with Image.open(w['crop']) as im:
                crop=im.convert('RGB')
            lo,_,hi,h=w['word_box']; view=crop.copy();draw=ImageDraw.Draw(view)
            draw.rectangle((lo,0,hi-1,h-1),outline='red',width=1)
            # Native line plus the unboxed zoom. Wrap wide native rows by
            # allocating enough sheet width, never compressing the line.
            zoom=crop.crop(w['word_box']).resize(((hi-lo)*2,h*2))
            panel=Image.new('RGB',(max(crop.width,zoom.width)+20,h+zoom.height+42),'white')
            ImageDraw.Draw(panel).text((10,4),str(i)+' '+w['uid'][:16],fill='black')
            panel.paste(zoom,(10,22));panel.paste(view,(10,30+zoom.height));panels.append(panel)
        sheet=Image.new('RGB',(max(p.width for p in panels),sum(p.height for p in panels)),'#ddd')
        y=0
        for p in panels:
            sheet.paste(p,(0,y));y+=p.height
        path=qa/(source+'.png');sheet.save(path)
        manifest[source]=dict(count=len(chosen),image=str(path.relative_to(OUT)),sha256=sha(path),words=chosen)
    dump(qa/'manifest.json',manifest)


def leak_scan():
    result={}
    for deck in ('T2','T4'):
        blind=OUT/'decks'/deck/'blind'; findings=[]
        key=[json.loads(s) for s in (blind.parent/'private/key.jsonl').read_text().splitlines()]
        needles={w[k] for w in key for k in ('doc','line_id','source','crop')}
        needles.update(['Google','google','confidence_scope','mining_key','crop_sha256','neighbour_body_ink_xh'])
        for p in sorted(blind.iterdir()):
            if p.suffix=='.png':
                if p.stem!=sha(p):
                    findings.append(dict(file=p.name,reason='not_content_hash'))
                with Image.open(p) as im:
                    if im.info:
                        findings.append(dict(file=p.name,reason='image_metadata',metadata=list(im.info)))
            else:
                text=p.read_text()
                for needle in sorted(needles):
                    if needle and needle in text:
                        findings.append(dict(file=p.name,reason='private_identifier',needle=needle))
        result[deck]=dict(files=len(list(blind.iterdir())),findings=findings,passed=not findings,
                          limits='Text/path/PNG metadata scan. Native printed line content may itself identify a text; intrinsic content is retained as required.')
    dump(OUT/'receipts/leak_scan.json',result)
    assert all(v['passed'] for v in result.values()),result
    return result


def decks(words,docs):
    priority=c1_priority(words)
    receipts={}
    for deck in ('T2','T4'):
        data,controls,receipt=select(words,docs,deck,priority)
        receipts[deck]=render_deck(deck,data,controls,receipt)
    qa_strips(words)
    leak_scan()
    dump(OUT/'receipts/deck_inputs.json',INPUTS)
    dump(OUT/'receipts/decks.json',receipts)
    print(json.dumps(receipts,ensure_ascii=False,indent=2),flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--geometry',action='store_true')
    parser.add_argument('--decks',action='store_true')
    args=parser.parse_args()
    if args.decks:
        docs=json.loads((OUT/'doc_roles.json').read_text())['documents']
        words=rows(OUT/'located_words.jsonl')
        offsets={}
        for line in rows(OUT/'eligible_lines.jsonl'):
            nn=0;oo=[]
            for key in re.findall(r'\S+',line['label']):
                oo.append(nn);nn+=len(skeleton(key))
            offsets[line['id']]=oo
        changed=False
        for w in words:
            offset=offsets[w['line_id']][w['word_index']]
            changed|=w.get('crop_letter_offset')!=offset
            w['crop_letter_offset']=offset
        if changed:
            jsonl(OUT/'located_words.jsonl',words)
        decks(words,docs)
    else:
        eligible,docs=inventory()
        if args.geometry:
            geometry(eligible,docs)
