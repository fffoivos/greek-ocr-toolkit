"""Offline OS2 specs, adapted by replaying the coordinator's exact selection.

Run from the checkout: PYTHONDONTWRITEBYTECODE=1 python -m scripts.review.build_owner_sheets_v2
No network, publishing, database access, or git writes. Coordinator snapshots make continuity reviewable alongside the live source replay.
"""
from __future__ import annotations
import ast
import collections
import copy
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.layout_paths import relocated
from greekocr.ops.data_root import input_path as _data_input
from greekocr.adjudicate.owner_sheet import render, image_path

ROOT = Path(__file__).resolve().parents[2]
PROJECTS = Path.home() / 'Projects'
BASE = PROJECTS / 'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3'
W = PROJECTS / 'collect-v3-data/run/W1'
T = PROJECTS / 'greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked'
DEST = relocated(ROOT / 'docs/owner_sheets')
OUT = ROOT / 'artifacts/owner_sheets/v2'
NAMES = ('failure_modes_per_class', 'segmentation_failures')

def read(p): return json.loads(_data_input(Path(p)).read_text())
def rows(p): return [json.loads(x) for x in _data_input(Path(p)).read_text().splitlines() if x.strip()]
def dump(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
def clean(text, google_text=''):
    # Preserve literal punctuation in Google/Printed. Only checker uncertainty
    # notation is expanded, with the original retained in provenance.
    return text if '?' in google_text else text.replace('?', '[uncertain]')

def recompute_labelmap():
    """Join actual C1 crop bytes to W1 hashes, never the sealed key ids."""
    byhash = {}; text = {}
    with (W/'features.jsonl').open() as stream:
        for line in stream:
            r = json.loads(line)
            byhash[r['crop_sha256']] = r['id']
            text[r['id']] = r.get('text') or ''
    cardmap = {}; gtext = {}; unmapped = []; empty = []
    for path in (W/'c1').glob('*/cards.jsonl'):
        for c in rows(path):
            key = path.parent.name + '|' + c['card_id']
            digest = hashlib.sha256((path.parent/c['crop']).read_bytes()).hexdigest()
            lid = byhash.get(digest)
            if lid is None:
                unmapped.append(key)
                continue
            cardmap[key] = lid
            label = c.get('google_text') or text[lid]
            gtext[lid] = label
            if not label.strip():
                empty.append(dict(card=key, line_id=lid))
    expected = read(DEST/'inputs/coordinator_labelmap.json')['cardmap']
    differences = dict(missing=sorted(expected.keys()-cardmap.keys()),
        extra=sorted(cardmap.keys()-expected.keys()),
        changed=[dict(card=k, recomputed=cardmap[k], coordinator=expected[k])
                 for k in sorted(cardmap.keys() & expected.keys()) if cardmap[k] != expected[k]])
    assert cardmap == expected and len(cardmap) == 5326, differences
    return dict(cardmap=cardmap, text=text, gtext=gtext), dict(
        map_pairs=len(cardmap), coordinator_equal=True, differences=differences,
        unmapped_cards=sorted(unmapped), empty_source_cards=empty)


def coordinator(labelmap=None):
    """Replay the patched coordinator, redirecting reads and capturing output."""
    path = DEST / 'inputs/coordinator_build_sheets_v2.py'
    tree = ast.parse(path.read_text())
    tree.body = [n for n in tree.body if not (
        isinstance(n, ast.ImportFrom) and n.module == 'greekocr.adjudicate.owner_sheet')]
    captured = []
    def capture(lines, spec):
        captured.append(copy.deepcopy(dict(spec, lines=lines)))
        return ''
    def local_open(path, mode='r', *args, **kwargs):
        import io
        if 'w' in mode:
            return io.StringIO()
        p = Path(path)
        if p.name == 'labelmap.json':
            return io.StringIO(json.dumps(labelmap if labelmap is not None else
                                          read(DEST/'inputs/coordinator_labelmap.json')))
        return p.open(mode, *args, **kwargs) if p.is_absolute() else (BASE/'c1'/p).open(mode, *args, **kwargs)
    import glob
    import fnmatch
    cache_index = OUT/'recovered_crops/index.json'
    cached_paths = read(cache_index) if cache_index.exists() else {}
    class LocalGlob:
        @staticmethod
        def glob(pattern):
            p = Path(pattern)
            pattern = str(p if p.is_absolute() else BASE/'c1'/p)
            return sorted(set(glob.glob(pattern)) | {p for p in cached_paths if fnmatch.fnmatch(p, pattern)})
    tree.body = [n for n in tree.body if not (isinstance(n, ast.Import) and any(a.name == 'glob' for a in n.names))]
    class CachedImages(ast.NodeTransformer):
        def visit_Call(self, node):
            self.generic_visit(node)
            if ast.unparse(node.func) == 'os.path.exists':
                node.func = ast.Name(id='asset_exists', ctx=ast.Load())
            elif ast.unparse(node.func) == 'Image.open':
                node.args[0] = ast.Call(func=ast.Name(id='image_path', ctx=ast.Load()), args=[node.args[0]], keywords=[])
            return node
    tree = ast.fix_missing_locations(CachedImages().visit(tree))
    ns = dict(render=capture, open=local_open, glob=LocalGlob, json=json,
              os=__import__('os'), collections=collections, sys=__import__('sys'),
              asset_exists=lambda p: image_path(p).exists(), image_path=image_path)
    exec(compile(tree, str(path), 'exec'), ns)
    assert [len(s['lines']) for s in captured] == [133, 42]
    assert len(captured[0]['sections']) == 14
    return captured, ns['CLASS'], ns['fault']


def evidence(labelmap=None):
    if labelmap is None:
        labelmap, _ = recompute_labelmap()
    records = []
    crop_hashes = {r['id']:r['crop_sha256'] for r in rows(W/'features.jsonl')}
    for stage, folder in [('C1', BASE/'c1/verdicts'), ('T6b', T/'checks/verdicts')]:
        for vp in sorted(folder.glob('*__[ab].jsonl')):
            bed = vp.stem.rsplit('__', 1)[0]
            if stage == 'T6b' and bed not in ('kosmopolis', 'lekythos', 'gazette_modern'):
                continue
            kp = W/'c1'/f'{bed}_key.json' if stage == 'C1' else T/'cards'/f'{bed}_key.json'
            keys = read(kp)
            cardfile = (W/'c1'/bed if stage == 'C1' else T/'cards'/bed)/'cards.jsonl'
            cards = {r['card_id']: r for r in rows(cardfile)}
            for v in rows(vp):
                k = keys[v['card_id']]; c = cards[v['card_id']]
                lid = labelmap['cardmap'][bed+'|'+v['card_id']] if stage == 'C1' else k['line_id']
                label = (c.get('google_text') or labelmap['text'].get(lid, ''))
                if not label.strip(): continue
                records.append(dict(v, line_id=lid, bed=bed, stage=stage,
                    verdict_path=str(vp), key_path=str(kp), card_path=str(cardfile),
                    google=label,
                    image=str(cardfile.parent/c['crop']) if 'crop' in c else str(W/'crops'/f"{k['line_id']}.png"),
                    key=k))
                if stage == 'C1' and lid != k['line_id']:
                    # Coordinator result entries retain explicit key ids even
                    # when duplicate native crops hash to another feature id.
                    # Bind evidence to both only with byte-identical rasters.
                    original_crop = W/'crops'/f"{k['line_id']}.png"
                    original_hash = (hashlib.sha256(original_crop.read_bytes()).hexdigest()
                                     if original_crop.exists() else crop_hashes[k['line_id']])
                    assert original_hash == hashlib.sha256((cardfile.parent/c['crop']).read_bytes()).hexdigest()
                    records.append(dict(records[-1], line_id=k['line_id'],
                        crop_hash_alias=lid))
    return records


def print_from_verdict(r, google):
    for key in ('printed', 'printed_text', 'adjudicated_print'):
        if r.get(key):
            return r[key], dict(path=r['verdict_path'], card_id=r['card_id'], method=key)
    detail = r.get('detail', '')
    if re.search(r'low confidence|uncertain|barely|handwritten',detail,re.I):
        return '', None
    context = re.fullmatch(r'· → - \(twice: (.+) → (.+)\)',detail)
    if context and context[2] == google:
        return context[1],dict(path=r['verdict_path'],card_id=r['card_id'],method='explicit full-label substitution in checker context',detail=detail)
    original_detail=detail
    # Parentheses that only describe glyph identity are metadata, not ink.
    # Unknown parentheses, alternatives, and uncertainty are deliberately kept
    # and rejected below rather than silently inventing a reading.
    detail=re.sub(r'\s*\((?:mid-height dots|em dash(?:es)?|en dash|hyphen|Greek|Latin(?: siglum)?|circumflex|superscript[^()]*|rough breathing[^()]*|breathing on[^()]*|printed[^()]*|inverted-breve accent[^()]*)\)', '', detail)
    # Adjudicated substitutions are useful only when the whole detail consists
    # of unambiguous ink -> Google replacements. Never infer omitted spans.
    if not detail or any(ch in detail for ch in '()/[]'):
        return '', None
    text = google
    replacements=[]
    for clause in detail.split(';'):
        if clause.count(' → ') != 1:
            return '', None
        ink, label = map(str.strip, clause.split(' → '))
        if not ink or not label or google.count(label) != 1:
            return '', None
        replacements.append((ink,label))
    for ink,label in sorted(replacements,key=lambda pair:-len(pair[1])):
        if text.count(label)==1:text=text.replace(label,ink,1)
        elif ink not in text:return '',None
    return text, dict(path=r['verdict_path'], card_id=r['card_id'],
        method='exact unique substitutions from every adjudicated checker clause; descriptive glyph qualifiers excluded', detail=original_detail)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    labelmap, audit = recompute_labelmap()
    dump(OUT/'os3_recomputed_cardmap.json', labelmap['cardmap'])
    baseline, classes, fault = coordinator(labelmap)
    reference, _, _ = coordinator()
    assert baseline == reference, 'Recomputed labels differ from coordinator current build'
    for name, s in zip(NAMES, reference):
        dump(DEST/'inputs'/f'coordinator_v2_{name}.json', s)
    a, b = copy.deepcopy(baseline)
    records = evidence(labelmap)
    byline = collections.defaultdict(list)
    for r in records: byline[r['line_id']].append(r)
    needed = set(byline) | {c['line_id'] for s in baseline for c in s['lines']}
    features = {}
    for r in rows(W/'features.jsonl'):
        if r['id'] in needed: features[r['id']] = r
    def crop(lid):
        p = W/'crops'/f'{lid}.png'
        if image_path(p).is_file(): return str(p)
        f = features[lid]; p = OUT/'crops'/f'{lid}.png'; p.parent.mkdir(exist_ok=True)
        with Image.open(f['crop_source_image']) as im: im.convert('RGB').crop(f['crop_bbox']).save(p)
        return str(p)
    def google(r):
        return r['google'] or features[r['line_id']]['text']
    def newcard(r, group):
        image = r['image'] if r['stage'] == 'T6b' else crop(r['line_id'])
        if r['stage'] == 'T6b':
            assert hashlib.sha256(Path(image).read_bytes()).hexdigest() == r['key']['card_crop_sha256']
        return dict(line_id=r['line_id'], doc_id=r['line_id'], label=r['line_id'], image=image,
                    group=group, rows=[dict(name='Google', text=google(r))], tags=[], printed='')
    def annotate(c, selected=None):
        evs = byline.get(c['line_id'], [])
        if not c['rows'][0]['text']:
            primary = selected or next((r for r in evs if r['stage']=='C1'), None)
            c['rows'][0]['text'] = google(primary) if primary else features[c['line_id']]['text']
        # Retain checker codes and individual C1/T6b verdicts for audit.
        errors = sorted({e for r in evs for e in r.get('errors', [])})
        c['fault_codes'] = errors
        c['evidence'] = [{k:r[k] for k in ('stage','bed','card_id','verdict_path','key_path','errors','detail')} for r in evs]
        existing = {t['text'] for t in c['tags']}
        c['tags'] += [dict(text=e) for e in errors if e not in existing]
        if selected:
            c['display_evidence'] = dict(stage=selected['stage'], path=selected['verdict_path'], card_id=selected['card_id'])
            c['tags'] += [dict(text=selected['stage'])]
        # Match print adjudication to the displayed Google row, never transplant
        # a masked-card reading to a different original label.
        text = c['rows'][0]['text']
        candidates = [r for r in evs if google(r) == text]
        prefills = []
        for r in candidates:
            printed, source = print_from_verdict(r, text)
            if printed: prefills.append((printed, source))
        c['printed'] = ''; c['printed_source'] = None
        if prefills and len({p for p, _ in prefills}) == 1:
            c['printed'], c['printed_source'] = prefills[0]
        elif prefills:
            c['printed_conflicts'] = [dict(text=p, source=s) for p,s in prefills]
        details = list(dict.fromkeys(f"{r['stage']} {r['card_id']}: {clean(r.get('detail',''),google(r))}" for r in evs if r.get('detail')))
        c['rows'] = c['rows'][:1] + ([dict(name='Checker', text='; '.join(details))] if details else [])
        # The note stays empty so the owner retains a clean editable field.
        c['note'] = ''
        c['image_size'] = list(Image.open(image_path(c['image'])).size)
    for s in (a,b):
        for c in s['lines']:
            c['rows'][0]['text'] = labelmap['gtext'].get(c['line_id']) or labelmap['text'].get(c['line_id'], '')
            if s is a:
                # Replace the heuristic fault pill with authoritative codes.
                # Its Cyrillic 'р' shortcut even called dialogue dashes yers.
                c['tags']=[c['tags'][0],*c['tags'][2:]]
            annotate(c)
    section_for = {s['heading']:s['id'] for s in a['sections']}
    def section(r):
        bed = r['bed']
        if r['stage'] == 'T6b':
            bed = dict(kosmopolis='kosmopolis__poly1900',lekythos='lekythos__poly1900',gazette_modern='gazette_modern__modern_scanned__measured_1986_1990')[bed]
        return section_for[classes[bed]]
    existing = {c['doc_id']:c for c in a['lines']}
    # Top up the coordinator's small C1 subsections from the same checker
    # classification, without moving any existing card or duplicating ids.
    for g in a['groups']:
        title = re.sub(r'\s*\(\d+ cards found; showing \d+\)$', '', g['heading'])
        candidates = [r for r in records if r['stage']=='C1'
                      and section(r)==g['section'] and fault(r['errors'],r.get('detail',''))==title]
        g['candidate_count'] = len({r['line_id'] for r in candidates})
        for r in candidates:
            if sum(c['group']==g['id'] for c in a['lines'])>=3: break
            if r['line_id'] in existing: continue
            c=newcard(r,g['id']);annotate(c,r);a['lines'].append(c);existing[c['doc_id']]=c
    # Extend the existing Russian subsection (or add one) with adjudicated yers.
    yerpath = BASE/'c1/yer_adjudication/table.json'; yerkeypath = yerpath.with_name('key.json')
    yerkey = read(yerkeypath)
    ys = [y for y in read(yerpath) if y['set']=='c1' and y['google_yer_errors'] > 0]
    yg = dict(id='s7_yer',section='s7',heading='Adjudicated yer: hard sign ъ read as ь',candidate_count=len(ys))
    a['groups'].append(yg)
    for y in ys:
        r = next(r for r in records if r['stage']=='C1' and r['bed']=='ia_russian__cyrillic' and r['card_id']==y['card_id'])
        if r['line_id'] not in existing and sum(c['group']==yg['id'] for c in a['lines']) < 6:
            c=newcard(r, yg['id']); annotate(c,r);a['lines'].append(c);existing[c['doc_id']]=c
        c=existing.get(r['line_id'])
        if c:
            key=yerkey[y['item_id']]; text=key['google_text']
            slots=[re.fullmatch(r'(\d+):g=(.) ink=(.) prior=.*',s) for s in y['slots']]
            positions=[i for i,ch in enumerate(text) if ch in 'ъь']
            if c['rows'][0]['text']==text and len(positions)==len(slots) and all(slots):
                chars=list(text)
                for m in slots:
                    i=positions[int(m[1])-1];assert chars[i]==m[2];chars[i]=m[3]
                # Preserve independent non-yer corrections from C1 if available.
                base=c['printed'] or text
                assert len([ch for ch in base if ch in 'ъь'])==len(positions)
                if base!=text and base!=''.join(chars):
                    pos=[i for i,ch in enumerate(base) if ch in 'ъь'];chars=list(base)
                    for m in slots: chars[pos[int(m[1])-1]]=m[3]
                c['printed']=''.join(chars)
                c['printed_source']=dict(path=str(yerpath),item_id=y['item_id'],card_id=y['card_id'],key_path=str(yerkeypath),
                    method='adjudicated yer slots in the full Google label',slots=y['slots'],other_corrections=c.get('printed_source'))
            c['yer_adjudication']=y
            c['tags'] += [dict(text='hard_sign_to_soft_sign'),dict(text='yer adjudicated')]
    # T6b: 3 witnesses per code, unioned across codes to keep one DB document
    # per line. All three held sources remain in their established classes.
    tgroups=[]
    for source in ('kosmopolis','lekythos','gazette_modern'):
        pool=[r for r in records if r['stage']=='T6b' and r['bed']==source]
        # A/B files partition the card ids; both are required for coverage.
        for code in sorted({e for r in pool for e in r.get('errors',[])}):
            candidates=[r for r in pool if code in r.get('errors',[])]
            shown=[c for c in a['lines'] if any(e['stage']=='T6b' and e['bed']==source and code in e['errors'] for e in c['evidence'])]
            added=[]
            for r in candidates:
                if len(shown)+len(added)>=3:break
                if r['line_id'] in existing:continue
                gid=f"{section(r)}_t6b_{code}"
                c=newcard(r,gid);annotate(c,r);a['lines'].append(c);existing[c['doc_id']]=c;added.append(c)
            if added:
                tgroups.append(dict(id=added[0]['group'],section=section(candidates[0]),heading=f'T6b masked cards: {code}',fault_code=code))
    a['groups'] += tgroups
    for g in a['groups']:
        if g['id']=='s7g0':
            g['heading']='Cyrillic faults: yer and dialogue punctuation (original coordinator group)'
    # Keep the 14 classes in exactly the coordinator order, and each original
    # group in its original relative order inside its original section.
    a['groups'].sort(key=lambda g: int(g['section'][1:]))
    for g in a['groups']:
        count=sum(c['group']==g['id'] for c in a['lines'])
        g['shown_count']=count
        g['heading']=re.sub(r'\s*\(\d+ cards found; showing \d+\)$','',g['heading'])+f' ({count} cards shown)'
        if count<3:
            g['gap']=f"fewer than 3 cards in this subsection ({count}); additional matching ids already shown elsewhere or unavailable"
    # Report per-code availability and represented counts, including cards
    # already present under another fault type instead of duplicating DB ids.
    a['fault_coverage']=[]
    for sid in [s['id'] for s in a['sections']]:
        pool=[r for r in records if section(r)==sid]
        for stage in ('C1','T6b'):
            for code in sorted({e for r in pool if r['stage']==stage for e in r.get('errors',[])}):
                candidates={r['line_id'] for r in pool if r['stage']==stage and code in r.get('errors',[])}
                shown=sorted(candidates & set(existing))
                a['fault_coverage'].append(dict(section=sid,stage=stage,code=code,available=len(candidates),shown_ids=shown))
    a['intro'] += ' Explicit tags retain checker error codes from both passes. T6b cards use the checked masked raster; existing cards retain their original raster and identity. Printed prefills name their adjudication source in the spec. Counts describe selected witnesses.'
    # Add source-specific coverage counts to section headers, including genuine
    # shortfalls, so all fault codes remain visible even when another subgroup
    # owns the single note document for a multi-fault card.
    for s in a['sections']:
        cov=[x for x in a['fault_coverage'] if x['section']==s['id']]
        s['header']='; '.join(f"{x['stage']} {x['code']}: {len(x['shown_ids'])} shown / {x['available']} available" + (' (fewer than 3 available)' if x['available']<3 else '') for x in cov)
    # Existing C1 cards can also witness T6b. Show the actual checked masked
    # raster and label alongside them, retaining the original main crop.
    for c in a['lines']:
        if c.get('display_evidence',{}).get('stage')=='T6b': continue
        masked=next((r for r in byline[c['line_id']] if r['stage']=='T6b' and r['errors']),None)
        if masked:
            assert hashlib.sha256(Path(masked['image']).read_bytes()).hexdigest()==masked['key']['card_crop_sha256']
            c.setdefault('zooms',[]).append(dict(image=masked['image'],alt='T6b checked masked crop'))
            c['rows'].append(dict(name='Google (T6b masked card)',text=google(masked)))
            c['tags'].append(dict(text='T6b masked evidence'))
    # Segmentation keeps all 34 original groups/ids and adds SG2 afterwards.
    for c in b['lines']:
        if c['group']=='g_rotated':
            c['fault_codes']=['rotated_vertical_line']
            c['tags'].append(dict(text='rotated_vertical_line'))
            c['evidence'].append(dict(stage='geometry',path=str(W/'features.jsonl'),line_id=c['line_id'],criterion='native crop height exceeds width'))
        if not c.get('zooms'):
            f=features[c['line_id']]; box=f['crop_bbox']
            with Image.open(f['crop_source_image']) as im:
                bounds=[max(0,box[0]-60),max(0,box[1]-100),min(im.width,box[2]+60),min(im.height,box[3]+100)]
                strip=im.convert('RGB').crop(bounds)
            ImageDraw.Draw(strip).rectangle([box[0]-bounds[0],box[1]-bounds[1],box[2]-bounds[0],box[3]-bounds[1]],outline='red',width=2)
            p=OUT/'strips'/f"{c['line_id']}.png";p.parent.mkdir(exist_ok=True);strip.save(p)
            c['zooms']=[dict(image=str(p),alt='Page strip; red box is the Google crop')]
    sg=BASE/'segmentation_gallery'
    b['groups'].append(dict(id='g_missing_box',heading='SG2: printed rows with no admitted box (3 strip witnesses)',
        header='Blue: admitted boxes; cyan: other raw Google boxes; red: no admitted box. These witnesses have raw boxes.'))
    for g in b['groups']:
        n=sum(c['group']==g['id'] for c in b['lines'])
        if g['id']!='g_missing_box' and n<3:g['gap']=f'fewer than 3 cards ({n})'
    for e in rows(sg/'examples.jsonl'):
        if not e['id'].startswith('sg2-'):continue
        missed=e['missed_rows'][0];lid=missed['id'];bounds=missed['locator_bbox']
        assignment=Path(e['assignment_path'])
        data=json.loads(gzip.open(assignment,'rt').read() if assignment.suffix=='.gz' else assignment.read_text())
        r=next(r for r in data['records'] if r['id']==lid)
        p=OUT/'crops'/f'{lid}.png';p.parent.mkdir(exist_ok=True)
        with Image.open(e['page_raster']) as im:im.convert('RGB').crop(bounds).save(p)
        c=dict(line_id=lid,doc_id=lid,label=lid,image=str(p),group='g_missing_box',
            rows=[dict(name='Google',text=r.get('docai_text') or r.get('label') or ''),dict(name='Checker',text=e['classification_note'])],
            printed='',printed_source=None,note='',fault_codes=['missing_admitted_box'],
            tags=[dict(text=t) for t in ['SG2','missing_admitted_box','raw_google_box_present',e['source']]],
            zooms=[dict(image=str(sg/e['image_paths']['page_strip']),alt='SG2 strip: blue admitted, cyan other raw boxes, red missing admitted boxes')],
            evidence=[dict(stage='SG2',path=str(sg/'examples.jsonl'),id=e['id'],notes_path=str(sg/'SG2.md'),validation_path=str(sg/'sg2_validation.json'),
                assignment_path=str(assignment),page=e['page_raster'],bbox=bounds,box_scope=e['box_scope'],raw_google_box_present=True)],image_size=list(Image.open(p).size))
        b['lines'].append(c)
    b['intro']=b['intro'].replace('(rows with no box: strips pending)', '(SG2 strips below show admission loss; raw Google boxes exist on these witnesses)')
    # R0 and print-truth contain span/word truth in other line-id namespaces.
    # Inventory exact joins; never put a word or reference-only line in Printed.
    truth=ROOT/'docs/records/labelfix/spellcheck'
    truth_paths=[truth/'R0_expected_truth.json',truth/'R0_locked_ib.jsonl',truth/'R0_newsource_dev.jsonl',truth/'print_truth_s0.json',truth/'print_truth/key_SEALED.json']
    truth_ids=set()
    for p in truth_paths:
        values=rows(p) if p.suffix=='.jsonl' else read(p)
        values=values.values() if isinstance(values,dict) else values
        truth_ids.update(v['line_id'] for v in values if isinstance(v,dict) and 'line_id' in v)
    for s in (a,b):
        s['truth_inventory']=dict(paths=list(map(str,truth_paths)),exact_line_id_matches=sorted({c['line_id'] for c in s['lines']} & truth_ids),
            policy='No namespace guessing or word/span truth substituted for a complete line; reference-only R0 human fields are not print adjudications.')
        for c in s['lines']:
            c['clean_image']=c['image']
            c['zooms']=c.get('zooms',[])
        s['schema']='OS2-v2'
    audit['excluded_sheet_cards'] = []
    audit['continuity'] = []
    for name, prev, s in zip(NAMES, baseline, (a,b)):
        kept = []
        for c in s['lines']:
            if not c['rows'][0]['text'].strip():
                audit['excluded_sheet_cards'].append(dict(sheet=name, doc_id=c['doc_id']))
            else: kept.append(c)
        s['lines'] = kept
        assert all(r['text'].strip() for c in kept for r in c['rows'] if r['name'].startswith('Google'))
        after = {c['line_id']:c for c in kept}
        assert all(c['line_id'] in after and after[c['line_id']]['doc_id'] == c['doc_id']
                   and after[c['line_id']]['group'] == c['group'] for c in prev['lines'])
        audit['continuity'].append(dict(sheet=name, coordinator_cards=len(prev['lines']),
                                      cards=len(kept), doc_ids_identical=True))
    audit['empty_google_rows'] = 0
    dump(OUT/'os3_mapping_audit.json', audit)
    for name,s in zip(NAMES,(a,b)):
        dump(DEST/name/'spec.json',s)
        (OUT/f'{name}.html').write_text(render(s['lines'],s))
    report(baseline,[a,b])
    with (DEST/'OS2_REPORT.md').open('a') as stream:
        stream.write('\n## OS3: Google-row mapping and current coordinator continuity\n\n'
            'Recomputed C1 crop SHA-256 joins against W1 `features.jsonl` `crop_sha256`: '
            f"{audit['map_pairs']:,} pairs, exactly equal to the coordinator map. Missing / extra / changed pairs: 0 / 0 / 0.\n\n"
            'The builder replays `inputs/coordinator_build_sheets_v2.py` with the recomputed map and independently with the coordinator map; complete captured specs agree. '
            'Current coordinator continuity: A 133/133 and B 42/42, with identical document ids, original groups, and crops. '
            'Explicit coordinator result ids can alias the hash-selected id; checker evidence is attached to both only after verifying byte-identical native crops.\n\n'
            'Google text uses `google_text`, then W1 feature text. Blank source cards and excluded sheet cards are listed in '
            '`artifacts/owner_sheets/v2/os3_mapping_audit.json`; blank Google rows fail validation. '
            f"Empty source cards: {len(audit['empty_source_cards'])}; excluded sheet cards: {len(audit['excluded_sheet_cards'])}; empty rendered Google rows: 0. "
            f"Unmapped C1 cards: {len(audit['unmapped_cards'])}, listed in the same audit.\n\n"
            f"Re-rendered A {len(a['lines'])} cards and B {len(b['lines'])} cards, offline with no `.git` writes.\n")
    from scripts.review.retag_owner_sheets_os4 import main as retag_os4
    retag_os4()
    add_os5()


def report(old,new):
    out=['# OS2 compatible owner-sheet specs','',
        'Offline build from `inputs/coordinator_build_sheets_v2.py`; no publishing, network, database access, or `.git` writes. Replayed current baseline: 133 / 42 cards. The checked baseline specs are retained under `inputs/coordinator_*.json`.', '',
        'Renderer change: **kept**. Section headings are needed by the coordinator’s 14-class builder. Optional note initialization, intro line breaks, and gap labels are additive. Legacy re-emission tests are unchanged; a new test compares the legacy path and covers these optional features. CSS/JS and the note database identity protocol are unchanged.', '',
        f'T6b pointer: `{BASE}/segmentation_gallery/build_gallery.py`; verdicts: `{T}/checks/verdicts/{{kosmopolis,lekythos,gazette_modern}}__{{a,b}}.jsonl`; keys and checked masked rasters: `{T}/cards/`. New T6b cards display the masked raster whose SHA-256 matches the key. Existing cards retain the coordinator raster and original group. Evidence and codes from every matching A/B partition are retained per card. The A/B files partition card ids; they are not duplicate adjudications of each card.', '',
        'Counts below compare with the coordinator, not the superseded OS1 selection. Kept includes re-tagged. No removals. Each existing card stays in its original section and subgroup. Fault-code coverage counts include witnesses in other subsections, so a multi-fault line has one note document. Shortfalls are stated in section headers and subgroup labels. The six-card cap is per selected subsection; pre-existing cross-tagged witnesses can raise code coverage above six.', '']
    out += ['The coordinator used `label` / `text` / `google` to read C1 card labels, but those files store `google_text`. Empty Google rows are now filled from that exact field (and feature text for the four unsampled rotated cards). This fixes label display without changing ids, original crops, or groups. The old heuristic fault pill is replaced by exact checker codes. The original Russian group is renamed to include dialogue punctuation: its heuristic classified any Cyrillic р as a yer. Cards and group ids remain intact. Four rotated cards have no checker verdict; their explicit geometry tag is bound to the native crop and features, not invented checker codes. Literal question marks in Russian labels and their quoted corrections are preserved; uncertainty placeholders are expanded to `[uncertain]`, with raw detail retained in evidence.', '']
    totals=[]
    for name,prev,s in zip(NAMES,old,new):
        before={c['doc_id']:c for c in prev['lines']};after={c['doc_id']:c for c in s['lines']}
        added=set(after)-set(before);removed=set(before)-set(after)
        retagged={lid for lid in before.keys() & after.keys() if before[lid].get('tags')!=after[lid].get('tags')}
        totals.append(dict(old=len(before),new=len(after),added=len(added),retagged=len(retagged),removed=len(removed)))
        out += [f'## {name}', '', '| Section | Kept | Added | Re-tagged | Removed |','|---|---:|---:|---:|---:|']
        groups={g['id']:g.get('section',g['id']) for g in s['groups']}
        headings={x['id']:x['heading'] for x in s.get('sections',s['groups'])}
        for sid in dict.fromkeys(groups.values()):
            ids={c['doc_id'] for c in s['lines'] if groups[c['group']]==sid}
            out.append(f"| {headings[sid]} | {len(ids & set(before))} | {len(ids & added)} | {len(ids & retagged)} | 0 |")
        out += ['',f'Doc-id continuity: **{len(before.keys() & after.keys())}/{len(before)} kept**. Removed: none.', '',
            '### Complete old-id continuity ledger','', '| Old doc id | Original group / section | Result |','|---|---|---|']
        oldgroups={g['id']:g.get('section',g['id']) for g in prev['groups']}
        for lid,c in before.items():
            assert lid in after and c['group']==after[lid]['group']
            out.append(f"| `{lid}` | {c['group']} / {oldgroups[c['group']]} | kept{', re-tagged' if lid in retagged else ''} |")
        out += ['', '### Added ids','']+[f"- `{lid}` — {after[lid]['group']}" for lid in sorted(added)]
        out += ['', '### Printed prefills and sources','', '| Doc id | Printed | Source and method |','|---|---|---|']
        for c in s['lines']:
            if c['printed']:
                src=c['printed_source']; out.append(f"| `{c['doc_id']}` | {c['printed'].replace('|','&#124;')} | `{src['path']}`; {src['method']}; {src.get('card_id','')} |")
        out += ['', f"Prefilled: {sum(bool(c['printed']) for c in s['lines'])}. All other Printed fields are empty. Conflicting adjudications are left empty and recorded in `printed_conflicts`.", '',
            f"R0 / print-truth inventory: {len(s['truth_inventory']['exact_line_id_matches'])} exact line-id matches. These sets use other namespaces and include word/span truth or reference-only text; no inferred join or partial-line prefill.", '']
    out += ['## SG2 scope','',
        'Three cards, one per existing SG2 strip, follow all original segmentation groups. Each uses the first identified missed row’s actual id, a native crop at its saved locator bounds, the archived raw Google label, Printed, tags, note, and the supplied strip. All eight missed rows remain visible across the three strips; only the three crop rows get note documents. Raw boxes exist on these witnesses: this is missing **admitted** boxes, not zero raw Google detections. Red locators are saved raw extents, not independently fitted row truth.', '',
        f'Sources: `{BASE}/segmentation_gallery/SG2.md`, `examples.jsonl`, `sg2_validation.json`, `sg2_pilot_selection.json`, `sg2-source-page_adjudication.jsonl`, and `sg2-01-strip.png` through `sg2-03-strip.png`.', '',
        'The 501/2,624 (19.09%) pilot uses admitted boxes. The later 8.55% raw-box census uses another denominator and criterion. These are archived visual judgments, not new owner adjudication.', '',
        '## Validation','', 'Run `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/adjudicate -q`. The OS2 tests check exact rendering, baseline continuity, 14-class order, evidence tags, masked hashes, source-bound prefills, SG2 provenance, embedded image pixels and native ratios, no model names or uncertainty placeholders in owner-facing content, and offline operation. The superseded OS1 tests were replaced because they required the abandoned 10-class layout and a disabled SG2 group.']
    dump(OUT/'summary.json',dict(sheets=totals,prefilled=sum(bool(c['printed']) for s in new for c in s['lines']),sg2=3))
    (DEST/'OS2_REPORT.md').write_text('\n'.join(out)+'\n')

OS5_GROUP = 'r2a_not_adopted'
OS5_SELECTION = (
    (16, '384c3f89-p000053-l0021', 8, [0,0,0,0], [0,0,0,1], 'subscript invented'),
    (17, '177b717d-p000054-l0004', 4, [1,3,0,0], [1,3,0,1], 'subscript invented'),
    (17, '177b717d-p000017-l0012', 24, [0,3,0,0], [0,3,1,0], 'dialytika invented'),
    (18, '22fda82b-p000063-l0039', 10, [0,3,0,1], [0,3,0,0], 'subscript dropped'),
    (18, '602cc72e-p000167-l0027', 10, [0,2,0,0], [1,2,0,0], 'breathing added'),
)


def r2a_cards():
    """Read saved held-out geometry and paired tuples; no inference or source writes."""
    from greekocr.labelfix.candidates import pair_tokens
    from greekocr.labelfix.text import clusters, nfd, nfc, tokenize, strip_marks
    prep = PROJECTS/'greek-ocr-toolkit-spellcheck-r2prep'
    r1 = PROJECTS/'greek-ocr-toolkit-spellcheck-r1'
    source = prep/'docs/labelfix/spellcheck/R2/evidence/r2a'
    paired_path = source/'r2rb2_paired_slots.json'
    owner_path = source/'r2rb2_owner_regressions.json'
    paired, owner = read(paired_path), read(owner_path)
    # Read HEADS and MARKS as literal constants, avoiding runtime/model imports.
    common = prep/'scripts/labelfix/clariden/r1_common.py'
    constants = {}
    for node in ast.parse(common.read_text()).body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in ('HEADS', 'MARKS'):
                assert isinstance(node.value, ast.Call) and node.value.func.id == 'dict'
                constants[name] = {kw.arg: ast.literal_eval(kw.value) for kw in node.value.keywords}
    heads, marks = constants['HEADS'], constants['MARKS']
    assert list(heads) == ['breathing', 'accent', 'dialytika', 'subscript']
    mapped_path = r1/'artifacts/labelfix_r1/score_3678928_K1c_vsS6/A_mapped_lines.jsonl.gz'
    wanted = {s[1] for s in OS5_SELECTION}
    with gzip.open(mapped_path, 'rt') as stream:
        mapped = {r['line_id']:r for line in stream if (r := json.loads(line))['line_id'] in wanted}
    google_path = PROJECTS/'greek-page-ocr/out/e3b/predictions/full_s0_v2_test.jsonl'
    google = {r['line_id']:r['gt'] for r in rows(google_path) if r['line_id'] in wanted}
    truth_path = r1/'docs/labelfix/spellcheck/print_truth_s0.json'
    adjudicated = read(truth_path)
    def word_with(word, slot, values):
        token = tokenize(word)[0]
        cs = clusters(token.core)
        cl = cs[slot['char']]
        assert cl.base == slot['base'], (word, slot['base'], slot['char'])
        selected = {choices[i] for choices, i in zip(heads.values(), values) if i}
        # Match r1_common.compose: diaeresis precedes the accent on one letter.
        applied = ''.join(marks[name] for name in
                          ('psili', 'dasia', 'dialytika', 'acute', 'grave', 'circumflex', 'subscript')
                          if name in selected)
        return nfc(token.lead + token.core[:cl.start] + cl.base + applied + token.core[cl.end:] + token.trail)
    cards = []
    for seed, lid, number, truth, after, change in OS5_SELECTION:
        did = f'{lid}:s{number}'
        pair = next(r for r in paired[str(seed)]['heldout'] if r['id'] == did)
        assert (pair['truth'], pair['old'], pair['new']) == (truth, truth, after)
        owner_rows = [r for r in owner['regressions'][str(seed)] if r['id'] == did]
        for witness in owner_rows:
            assert all(witness[k] == pair[k] for k in ('truth', 'old', 'new'))
        is_owner = did == '602cc72e-p000167-l0027:s10'
        if is_owner:
            assert len(owner_rows) == 1 and owner_rows[0]['named_owner_slot']
        line = mapped[lid]
        assert not line['dev']
        slot = next(s for s in line['slots'] if s['slot'] == number)
        assert slot['base'] == pair['base']
        # Same Google-token index and saved geometry as build_r1a_errors.py.
        gtoken = tokenize(google[lid])[slot['word']]
        recogniser = {g.index:m for g,m in pair_tokens(google[lid], nfd(line['recogniser_text']))}[slot['word']]
        assert recogniser is not None and strip_marks(gtoken.core) == strip_marks(recogniser.core)
        printed_record = adjudicated.get(f"{lid}|{slot['word']}")
        truth_word = printed_record['printed'] if printed_record else gtoken.text
        printed = word_with(truth_word, slot, truth)
        crop_path = r1/Path(line['crop']).relative_to(PROJECTS/'greek-ocr-toolkit-spellcheck')
        with Image.open(crop_path) as im:
            image = im.convert('RGB')
        draw = ImageDraw.Draw(image)
        detections = [dict(slot=s['slot'], bbox=s['bbox'], evidence=s.get('evidence', {})) for s in line['slots']]
        for s in detections:
            for key, color in [('above', (30,140,60)), ('apostrophes', (30,140,60)),
                               ('below', (40,80,200)), ('attached', (120,120,120))]:
                for mark in s['evidence'].get(key, []):
                    draw.rectangle(mark['bbox'], outline=color, width=1)
        x0, _, x1, _ = slot['bbox']
        draw.rectangle([x0-2, 0, x1+2, image.height-1], outline=(200,40,40), width=2)
        path = OUT/'r2a'/f'{did}.png'
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)
        ev = dict(stage='R2a', path=str(paired_path), owner_path=str(owner_path), seed=seed,
                  id=did, truth=truth, before=pair['old'], after=after,
                  heads={key:list(choices) for key, choices in heads.items()},
                  heads_path=str(common), mapped_path=str(mapped_path), crop=str(crop_path),
                  crop_sha256=hashlib.sha256(crop_path.read_bytes()).hexdigest(),
                  bbox=slot['bbox'], word=slot['word'], char=slot['char'], base=slot['base'],
                  google_path=str(google_path), detections=detections)
        tags = [f'seed {seed}', change] + (['owner witness'] if is_owner else [])
        cards.append(dict(line_id=lid, slot=number, doc_id=did, label=f'{lid} · slot {number} ({slot["base"]})',
            group=OS5_GROUP, image=str(path), clean_image=str(crop_path), image_size=list(image.size),
            alt='Full line with saved detections; selected letter outlined in red', zooms=[],
            rows=[dict(name='Google', text=nfc(gtoken.text)),
                  dict(name='Before', text=word_with(printed, slot, pair['old'])),
                  dict(name=f'After (R2a, seed {seed})', text=word_with(printed, slot, after))],
            printed=printed, printed_source=dict(path=str(paired_path), id=did, seed=seed,
                truth_word_path=str(truth_path) if printed_record else str(google_path),
                method='R1 held-out truth word with the source-of-record slot truth tuple applied'),
            note='', tags=[dict(text=t) for t in tags], fault_codes=[change], evidence=[ev]))
    return cards


def add_os5():
    """Append OS5 to completed OS4 outputs; repeated renders replace only OS5."""
    path = DEST/NAMES[0]/'spec.json'
    spec = read(path)
    original = copy.deepcopy(spec)
    spec['lines'] = [c for c in spec['lines'] if c['group'] != OS5_GROUP]
    spec['groups'] = [g for g in spec['groups'] if g['id'] != OS5_GROUP]
    existing = copy.deepcopy(spec['lines'])
    cards = r2a_cards()
    assert not {c['doc_id'] for c in existing} & {c['doc_id'] for c in cards}
    spec['groups'].append(dict(id=OS5_GROUP, heading='What moved in R2a (not adopted)', shown_count=5))
    spec['lines'] += cards
    assert spec['lines'][:-5] == existing
    assert spec['groups'][:-1] == [g for g in original['groups'] if g['id'] != OS5_GROUP]
    dump(path, spec)
    html_path = OUT/f'{NAMES[0]}.html'
    html_path.write_text(render(spec['lines'], spec))
    sha_path = DEST/'v2_html_sha256.txt'
    sha_path.write_text(''.join(f"{hashlib.sha256((OUT/f'{name}.html').read_bytes()).hexdigest()}  artifacts/owner_sheets/v2/{name}.html\n" for name in NAMES))
    report_path = DEST/'OS2_REPORT.md'
    content = report_path.read_text().split('\n## OS5:', 1)[0]
    content += '\n## OS5: What moved in R2a (not adopted)\n\n'
    content += ('Added one final group with five held-out slot witnesses. All 180 existing cards, document ids, groups and sections are unchanged. '
                'The five new note ids use `line_id:sN`, preserving the reader-errors slot identity. '
                'No network calls, model runs, or `.git` writes.\n\n'
                'Tuples were verified against `greek-ocr-toolkit-spellcheck-r2prep/docs/labelfix/spellcheck/R2/evidence/r2a/r2rb2_paired_slots.json` '
                'and matching entries in `r2rb2_owner_regressions.json`; the last card is a named owner witness. '
                'Tuple order and indexes come from `r1_common.HEADS`: breathing, accent, dialytika, subscript.\n\n'
                'Native full-line crops and slot geometry come from the R1 `score_3678928_K1c_vsS6/A_mapped_lines.jsonl.gz`, '
                'following `R2_evidence/page_builders/build_r1a_errors.py`. Saved detections are outlined in green (above/apostrophe), '
                'blue (below), and grey (attached); the selected letter has a red full-height outline. '
                'Google words use the same archived seed-0 labels and token mapping. Printed uses the R1 truth word with the verified slot truth applied; '
                'Before and After change only that letter’s marks. All source paths, geometry, detections and tuples are retained per card.\n\n'
                '| Seed | Note document | Truth / before | After | Change |\n|---|---|---|---|---|\n')
    for seed, lid, slot, truth, after, change in OS5_SELECTION:
        content += f'| {seed} | `{lid}:s{slot}` | `{truth}` | `{after}` | {change}{"; owner witness" if lid.startswith("602cc72e") else ""} |\n'
    content += '\nRebuild OS5 only: `python -m scripts.review.build_owner_sheets_v2 --os5-only`. The full builder also appends OS5 after OS4.\n'
    content += ('\nLocal source availability: W1 crop files were missing during OS5. '
                '`scripts/review/recover_owner_sheet_crops.py` preserved the already embedded rasters under '
                '`artifacts/owner_sheets/v2/recovered_crops/`, with source-path and SHA-256 entries in `index.json`. '
                'The renderer uses these only when the original path is absent. Coordinator replay resolves the same cached paths; '
                'duplicate-crop evidence uses the archived feature crop SHA-256 when original PNG bytes are unavailable. '
                'Existing card records retain their source paths. The segmentation HTML checksum is unchanged.\n')
    report_path.write_text(content)


if __name__=='__main__':
    if '--os5-only' in sys.argv:
        add_os5()
    else:
        main()
