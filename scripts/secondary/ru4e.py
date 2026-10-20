"""RU4E preparation, offline adjudication, and explicit later reading driver.

Import labels are RAW Google text in these input files. Never consult a convention
label stream. All offsets address the exact import string, without normalization.
"""
import argparse
from collections import Counter, defaultdict
import copy
import fcntl
import hashlib
import html
import json
import math
from pathlib import Path
import random
import secrets
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[1]
BOUND = HERE/'ru4e_bound'
sys.path.insert(0, str(BOUND))
from common import rows, dump, jsonl, sha, SCRATCH
from ru1_census import positions, mask
import scan_packs
import scan_rollout
from ru1_map_answers import map_records, score_controls
from ru2t_coverage import coverage
from ledger import weekly, record, append

ART = WORK/'artifacts/ru1/ru4e'
PACK = SCRATCH/'sol_packs/ru4e'
COLLECTION = Path.home()/'Projects/greek-ocr-toolkit/docs/harvest/collection/v2'
SOURCES = {s: COLLECTION/f'import_real_v2_{s}.jsonl' for s in ('test', 'dev')}
BOOKS = WORK/'artifacts/ru1/ru2t/build.json'
REGISTRY = WORK/'docs/records/labelfix/lqb/versions.json'
SCANNER_SHA = 'dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547'
SEED = 'RU4E:20261018:exact-nine-books:final-only'


def external(pack):
    for p in (Path(pack).absolute(), Path(pack).resolve()):
        for a in (p, *p.parents):
            if (a/'.git').exists() or (a/'.git').is_symlink():
                raise ValueError('pack root must be outside every git worktree')


def scanner_check():
    if sha(BOUND/'scan_rollout.py') != SCANNER_SHA or scan_rollout.VERSION != 'v4.4-canonical':
        raise ValueError('canonical v4.4 scanner changed')


def stem(ctx, reader):
    return ctx + ('.'+reader if reader != 'r1' else '')


def bid(r):
    return r['source']+':'+r['doc']


def inventory(sources, books, selected_ids=None):
    selected = []
    candidates = []
    counts = []
    inputs = {}
    ids = set()
    for split, path in sources.items():
        inputs[str(path.resolve())] = sha(path)
        data = rows(path)
        if len({r['id'] for r in data}) != len(data):
            raise ValueError('duplicate source ids')
        for r in data:
            if bid(r) not in books:
                continue
            if selected_ids is not None and r['id'] not in selected_ids:
                continue
            if r['id'] in ids:
                raise ValueError('cross-split duplicate id')
            ids.add(r['id'])
            selected.append(dict(r, ru4e_split=split))
            candidates.extend(dict(p, row_id=r['id'], source_id=r['id'],
                                   split=split, book=bid(r), prior='unknown', control=False)
                              for p in positions(r['label'])
                              if p['google'] == 'ь' and p['kind'] == 'final')
        for b in sorted(books):
            rr = [r for r in selected if r['ru4e_split'] == split and bid(r) == b]
            pp = [p for p in candidates if p['split'] == split and p['book'] == b]
            counts.append(dict(split=split, book=b, rows=len(rr),
                               candidate_positions=len(pp), candidate_lines=len({p['row_id'] for p in pp})))
    return selected, candidates, counts, inputs


def controls():
    root = WORK/'artifacts/ru1'
    inv = json.loads((root/'keys/control_inventory.json').read_text())
    saved = {m['adjudication_id']: m for p in sorted((root/'keys').glob('ctx*.json'))
             for m in json.loads(p.read_text())['items'].values() if m['control']}
    pool = []
    for c in inv:
        if not c['slots']:
            continue
        m = saved[c['adjudication_id']]
        if c['slots'] != m['slots']:
            raise ValueError('control adjudication differs')
        image = SCRATCH/'ru1_cache/crops'/(m['source_crop_sha256']+'.png')
        if sha(image) != m['source_crop_sha256']:
            raise ValueError('control crop differs')
        pool.append(dict(c, image=str(image), source_crop_sha256=m['source_crop_sha256']))
    if len(pool) != 31 or sum(len(c['slots']) for c in pool) != 65:
        raise ValueError('65-position controls incomplete')
    return pool


def assignment(dest, art, ctx, reader, order, used):
    external(dest)
    if dest.exists():
        raise ValueError('refuse assignment overwrite')
    dest.mkdir(parents=True)
    public, private = [], {}
    for m in order:
        iid = 'k'+secrets.token_hex(5)
        while iid in used:
            iid = 'k'+secrets.token_hex(5)
        used.add(iid)
        digest = m['source_crop_sha256']
        rel = 'crops/'+digest+'.png'
        target = dest/rel
        target.parent.mkdir(exist_ok=True)
        if not target.exists():
            shutil.copyfile(m['image'], target)
        if sha(target) != digest:
            raise ValueError('copy differs')
        public.append(dict(item_id=iid, crop=rel, masked_text=m['masked_text'], slots=len(m['slots'])))
        private[iid] = {k: v for k, v in m.items() if k not in {'image', 'masked_text'}}
    jsonl(dest/'items.jsonl', public)
    dump(art/f'keys/{stem(ctx, reader)}.json',
         dict(context=ctx, readers={reader: [p['item_id'] for p in public]}, items=private))


def closure(pack, art, runtime=False, replacement=False):
    external(pack)
    scan_packs.ROOT = art
    results = []
    if not pack.exists():
        raise ValueError('missing pack root')
    for ctx in sorted(pack.iterdir()):
        if ctx.is_symlink() or not ctx.is_dir() or not __import__('re').fullmatch(r'ctx\d{2,}', ctx.name):
            raise ValueError('unexpected pack entry '+str(ctx))
        readers = ('r3',) if replacement else ('r1', 'r2')
        allowed = set(readers) | {'MANIFEST.'+r+'.json' for r in readers}
        if any(p.name not in allowed or p.is_symlink() for p in ctx.iterdir()):
            raise ValueError('unexpected context entry')
        for reader in readers:
            rd = ctx/reader
            if not rd.is_dir() or rd.is_symlink():
                raise ValueError('missing reader assignment')
            if not 1 <= len(rows(rd/'items.jsonl')) <= 100:
                raise ValueError('context must contain 1..100 items')
            result = scan_packs.scan(rd, 'yer', write_manifest=not runtime, allow_runtime=runtime)
            results.append(result)
    if any(not r['ok'] for r in results):
        raise ValueError('pack closure failed: '+str(results))
    return results


def bindings(paths):
    return {str(p.resolve()): sha(p) for p in paths if p.is_file()}


def build(sources=SOURCES, books_path=BOOKS, art=ART, pack=PACK, control_pool=None,
          selected_ids=None, prepare_crop=None):
    external(pack)
    scanner_check()
    if (pack.exists() and any(pack.iterdir())) or (art/'build.json').exists():
        raise ValueError('refuse build overwrite')
    books = json.loads(books_path.read_text())['books']
    if selected_ids is None and len(books) != 9:
        raise ValueError('expected exactly nine RU2T identities')
    selected, pp, counts, inputs = inventory(sources, books, selected_ids)
    inputs.update(bindings([books_path]))
    art.mkdir(parents=True, exist_ok=True)
    pack.mkdir(parents=True, exist_ok=True)
    jsonl(art/'census_by_split_book.jsonl', counts)
    jsonl(art/'candidate_positions.full.jsonl', pp)
    candidate_ids = {p['row_id'] for p in pp}
    lines = [dict(row_id=r['id'], split=r['ru4e_split'], book=bid(r), crop=r['crop'])
             for r in selected if r['id'] in candidate_ids]
    jsonl(art/'candidate_lines.full.jsonl', lines)
    jsonl(art/'selected_lines.jsonl', lines)
    pool = controls() if control_pool is None else control_pool
    dump(art/'control_inventory.json', [{k: v for k, v in c.items() if k != 'image'} for c in pool])
    if control_pool is None:
        inputs.update(bindings((WORK/'artifacts/ru1/keys').glob('*.json')))
    bed = []
    for r in selected:
        if r['id'] not in candidate_ids:
            continue
        path = Path(r['crop']).expanduser()
        if not path.is_absolute():
            path = sources[r['ru4e_split']].parents[4]/path
        digest = sha(path)
        inputs[str(path.resolve())] = digest
        crop_provenance = {}
        if prepare_crop is not None:
            path, crop_provenance = prepare_crop(path)
            digest = sha(path)
            inputs[str(path.resolve())] = digest
        masked, slots = mask(r['label'])  # Mask hard and pre-hyphen signs too: no Google hints.
        for slot in slots:
            slot.update(prior='unknown', control_truth=None)
        bed.append(dict(control=False, row_id=r['id'], source_id=r['id'],
                        split=r['ru4e_split'], book=bid(r), slots=slots,
                        masked_text=masked, image=str(path), source_crop_sha256=digest,
                        **crop_provenance))
    rng = random.Random(SEED)
    rng.shuffle(bed)
    pool = list(pool)
    rng.shuffle(pool)
    contexts = []
    used = set()
    cursor = 0
    nctx = math.ceil(len(bed)/90)
    for j in range(nctx):
        ctx = f'ctx{j+1:02d}'
        batch = bed[j*len(bed)//nctx:(j+1)*len(bed)//nctx]
        nc = math.ceil(len(batch)*.1)
        if not pool:
            raise ValueError('no controls')
        order = batch+[pool[(cursor+k) % len(pool)] for k in range(nc)]
        cursor += nc
        rng.shuffle(order)
        for c in order:
            inputs[str(Path(c['image']).resolve())] = sha(c['image'])
        for reader, seq in [('r1', order), ('r2', list(reversed(order)))]:
            assignment(pack/ctx/reader, art, ctx, reader, seq, used)
        contexts.append(dict(context=ctx, bed_lines=len(batch), control_lines=nc, items=len(order)))
    scans = closure(pack, art)
    dump(art/'closure.json', dict(ok=True, packs=scans, empty_scope=not bool(pp)))
    inputs.update(bindings([Path(__file__), WORK/'greekocr/labelfix/lqb.py', HERE/'run_ru4e_all.sh', HERE/'ru4e_finalize.sh',
                            *BOUND.glob('*')]))
    info = dict(schema='RU4E-v1', status='READY_FOR_READINGS' if pp else 'EMPTY_SCOPE',
                parent='google_raw_v2_import', text_field='label',
                parent_semantics='Exact RAW Google import label; no convention stream or normalization',
                sources={s: str(p.resolve()) for s, p in sources.items()}, books=books,
                rows={s: sum(r['ru4e_split'] == s for r in selected) for s in sources},
                candidate_positions=len(pp), candidate_lines=len(lines), counts=counts,
                contexts=contexts, inputs=inputs, pack=str(pack.resolve()),
                pack_inputs=bindings([*pack.rglob('*'), *(art/'keys').glob('*.json'),
                                      art/'candidate_positions.full.jsonl', art/'candidate_lines.full.jsonl',
                                      art/'selected_lines.jsonl', art/'census_by_split_book.jsonl',
                                      art/'control_inventory.json']),
                budget=dict(points_per_100_reads=.2, item_reads=2*sum(c['items'] for c in contexts),
                            points=round(.004*sum(c['items'] for c in contexts), 3)),
                scope='lowercase word-final ь, kind final only; pre_hyphen excluded; Google ъ never a candidate',
                scanner_sha256=SCANNER_SHA, network=False, reader_runs=0, git_writes=False)
    for p, h in inputs.items():
        if sha(p) != h:
            raise ValueError('input changed during build')
    dump(art/'build.json', info)
    return info


def validate(art=ART, pack=PACK):
    external(pack)
    scanner_check()
    info = json.loads((art/'build.json').read_text())
    if str(pack.resolve()) != info['pack']:
        raise ValueError('wrong pack root')
    for p, h in {**info['inputs'], **info['pack_inputs']}.items():
        if sha(p) != h:
            raise ValueError('bound input changed: '+p)
    actual = {p.name for p in pack.iterdir()}
    if actual != {c['context'] for c in info['contexts']}:
        raise ValueError('pack context coverage differs')
    closure(pack, art, runtime=True)
    return info


def collect(art, pack, ctx, reader, seen):
    ans = art/'answers'/stem(ctx, reader)
    runpath = Path(str(ans)+'.run.json')
    run = json.loads(runpath.read_text())
    if run['rc'] != 0 or run['model'] != 'gpt-6.1-sol':
        raise ValueError('failed reader/model')
    rollout = Path(run['rollout'])
    digest = sha(rollout)
    if digest in seen:
        raise ValueError('rollout reused across independent reads')
    seen.add(digest)
    metadata = [r.get('payload', {}) for r in rows(rollout) if r.get('type') in {'session_meta', 'turn_context'}]
    models = {r['model'] for r in metadata if r.get('model')}
    efforts = {r.get('effort', r.get('reasoning_effort')) for r in metadata
               if r.get('effort', r.get('reasoning_effort'))}
    if models != {'gpt-6.1-sol'} or efforts != {'medium'}:
        raise ValueError('rollout model/effort mismatch')
    rd = pack/ctx/reader
    scan = scan_rollout.inspect(rollout, rd)
    dump(Path(str(ans)+'.scan.json'), scan)
    if not scan['ok'] or scan['scanner_version'] != 'v4.4-canonical':
        raise ValueError('unclean canonical scan')
    items = rows(rd/'items.jsonl')
    cov = coverage(scan, rollout, rd, items)
    dump(Path(str(ans)+'.coverage.json'), cov)
    answerpath = rd/'answers.jsonl'
    keypath = art/f'keys/{stem(ctx, reader)}.json'
    mapped, _ = map_records(rows(answerpath), json.loads(keypath.read_text()), items, reader)
    mapped = [p for p in mapped if p['item_id'] not in set(cov['dropped_items'])]
    gate = score_controls(mapped, ctx)
    if not gate['correct']:
        gate.update(status='VOID', reason='no_usable_correct_controls')
    for p in mapped:
        p['context_void'] = gate['status'] == 'VOID'
        p['edit_proposal'] = None  # Only final combined, lead-checked decisions can edit.
    jsonl(Path(str(ans)+'.mapped.jsonl'), mapped)
    dump(Path(str(ans)+'.controls.json'), gate)
    evidence = bindings([runpath, rollout, answerpath, keypath,
                         *[Path(str(ans)+s) for s in ('.scan.json', '.coverage.json', '.mapped.jsonl', '.controls.json')]])
    return mapped, gate, cov, evidence


def combine(p, votes):
    calls = [v['call'] for v in votes]
    decision, reason = 'hold', 'missing_independent_reads'
    if (len(votes) == 2 and {v['logical_reader'] for v in votes} == {'r1', 'r2'}
            and all(v['gate_status'] == 'VALID' for v in votes)):
        if calls == ['ъ', 'ъ']:
            decision, reason = 'edit_hard', 'two_valid_hard'
        elif calls == ['ь', 'ь']:
            decision, reason = 'keep_soft', 'two_valid_soft'
        else:
            reason = 'reader_disagreement' if set(calls) == {'ь', 'ъ'} else 'uncertain_read'
    return dict(p, decision=decision, reason=reason, reads=votes)


def replacement(art, pack, ctx, reader):
    """One isolated r3 assignment per VOID reading, even if both roles are VOID."""
    rp = pack.parent/'ru4e_r3'/(ctx+'-'+reader)
    ra = art/'r3_replacements'/(ctx+'-'+reader)
    receipt = ra/'replacement.json'
    if receipt.exists():
        obj = json.loads(receipt.read_text())
        if any(obj.get(k) != v for k, v in dict(art=str(ra), pack=str(rp), context='ctx01',
                  reader='r3', logical_reader=reader, replaces=ctx+'/'+reader,
                  identity=ctx+'/'+reader+'/r3', seed=SEED+':'+ctx+':'+reader+':r3').items()):
            raise ValueError('replacement identity differs')
        for p, h in obj['bindings'].items():
            if sha(p) != h:
                raise ValueError('replacement binding changed')
        closure(rp, ra, runtime=True, replacement=True)
        original = rows(pack/ctx/reader/'items.jsonl')
        random.Random(obj['seed']).shuffle(original)
        fresh = rows(rp/'ctx01/r3/items.jsonl')
        strip = lambda seq: [{k: v for k, v in i.items() if k != 'item_id'} for i in seq]
        oldkey = json.loads((art/f'keys/{stem(ctx, reader)}.json').read_text())
        newkey = json.loads((ra/'keys/ctx01.r3.json').read_text())
        if strip(original) != strip(fresh) or [oldkey['items'][i['item_id']] for i in original] != [newkey['items'][i['item_id']] for i in fresh]:
            raise ValueError('replacement assignment differs from VOID original')
        return obj
    if rp.exists() or ra.exists():
        raise ValueError('partial replacement exists; refuse overwrite')
    key = json.loads((art/f'keys/{stem(ctx, reader)}.json').read_text())
    public = rows(pack/ctx/reader/'items.jsonl')
    seed = SEED+':'+ctx+':'+reader+':r3'
    random.Random(seed).shuffle(public)
    order = [dict(key['items'][i['item_id']], masked_text=i['masked_text'],
                  image=str(pack/ctx/reader/i['crop'])) for i in public]
    used = {i for p in (art/'keys').glob('*.json') for i in json.loads(p.read_text())['items']}
    # Include every earlier replacement's IDs in the global freshness check.
    for kp in (art/'r3_replacements').glob('*/keys/*.json'):
        used.update(json.loads(kp.read_text())['items'])
    assignment(rp/'ctx01/r3', ra, 'ctx01', 'r3', order, used)
    closure(rp, ra, replacement=True)
    obj = dict(identity=ctx+'/'+reader+'/r3', logical_reader=reader, replaces=ctx+'/'+reader,
               art=str(ra), pack=str(rp), context='ctx01', reader='r3', seed=seed,
               bindings=bindings([*rp.rglob('*'), *(ra/'keys').glob('*.json')]),
               status='READY_FOR_READING', no_reader_run=True)
    dump(receipt, obj)
    return obj


def lead_sheets(art, pack, decisions):
    """Full-line native PNGs and 4x nearest-neighbour HTML; no guessed glyph box."""
    hard = [d for d in decisions if d['decision'] == 'edit_hard']
    soft = [d for d in decisions if d['decision'] == 'keep_soft']
    rng = random.Random(SEED+':audit')
    audit = rng.sample(hard, min(20, len(hard)))+rng.sample(soft, min(10, len(soft)))
    auditkeys = {(d['row_id'], d['offset']) for d in audit}
    disagreements = [d for d in decisions if d['reason'] == 'reader_disagreement']
    needed = {(d['row_id'], d['offset']): d for d in hard+audit+disagreements}
    index = {}
    for ctx in sorted(pack.glob('ctx*')):
        key = json.loads((art/f'keys/{ctx.name}.json').read_text())
        for i in rows(ctx/'r1/items.jsonl'):
            m = key['items'][i['item_id']]
            if not m['control']:
                index[m['row_id']] = (ctx/'r1'/i['crop'], i, m)
    review = art/'lead'
    review.mkdir(exist_ok=True)
    entries = []
    page = ['<!doctype html><meta charset="utf-8"><title>RU4E lead pixel checks</title>',
            '<style>body{font:16px sans-serif}article{border-bottom:1px solid;padding:16px;overflow:auto}img{image-rendering:pixelated}code{white-space:pre-wrap}</style>',
            '<h1>RU4E lead pixel checks</h1><p>Read the saved native pixels. Offset is a Unicode code point in exact RAW Google text. No inferred glyph boxes. Every proposed edit needs a pixel check; audit items additionally require confirmation.</p>']
    from PIL import Image
    for n, (k, d) in enumerate(sorted(needed.items()), 1):
        source, item, meta = index[d['row_id']]
        dest = review/'crops'/source.name
        dest.parent.mkdir(exist_ok=True)
        if not dest.exists():
            shutil.copyfile(source, dest)
        if sha(dest) != meta['source_crop_sha256']:
            raise ValueError('lead image changed')
        text = item['masked_text']
        for j, slot in enumerate(meta['slots'], 1):
            text = text.replace(f'⟦{j}⟧', slot['google'])
        with Image.open(dest) as im:
            width = im.width
        marked = text[:d['offset']]+'【'+text[d['offset']]+'】'+text[d['offset']+1:]
        entry = dict(row_id=d['row_id'], split=d['split'], offset=d['offset'],
                     proposed=d['decision'], audit=k in auditkeys,
                     genuine_disagreement=d['reason'] == 'reader_disagreement',
                     crop=str(dest.resolve()), crop_sha256=sha(dest),
                     call=None, pixel_checked=False, reviewer=None, note=None)
        entries.append(entry)
        page.append(f'<article id="p{n}"><p>{html.escape(d["row_id"])} / {d["split"]} / offset {d["offset"]} / {d["decision"]} / audit {entry["audit"]}</p><code>{html.escape(marked)}</code><p>Native:</p><img src="crops/{dest.name}"><p>4× nearest neighbour:</p><img width="{width*4}" src="crops/{dest.name}"></article>')
    (review/'sheets.html').write_text('\n'.join(page))
    jsonl(review/'template.jsonl', entries)
    info = dict(edit_checks=len(hard), audit_edit_hard=min(20, len(hard)),
                audit_keep_soft=min(10, len(soft)), genuine_disagreements=len(disagreements),
                required=len(entries), sheets_sha256=sha(review/'sheets.html'),
                template_sha256=sha(review/'template.jsonl'))
    dump(review/'manifest.json', info)
    return entries, info


def apply_overlay(data, decisions, lead):
    """Exact sparse raw overlay; requires two admitted hard votes AND lead pixels."""
    originals = {r['id']: r for r in data}
    if len(originals) != len(data):
        raise ValueError('duplicate parent ids')
    grouped = defaultdict(list)
    seen = set()
    for d in decisions:
        k = d['row_id'], d['offset']
        if k in seen:
            raise ValueError('duplicate decision')
        seen.add(k)
        r = originals[d['row_id']]
        candidates = {p['offset'] for p in positions(r['label']) if p['google'] == 'ь' and p['kind'] == 'final'}
        if d['offset'] not in candidates or d['split'] != r['ru4e_split']:
            raise ValueError('not an exact final RAW soft-sign candidate')
        outcome = d['decision']
        check = lead.get(k)
        if outcome == 'edit_hard':
            votes = d['reads']
            if len(votes) != 2 or {v['logical_reader'] for v in votes} != {'r1', 'r2'} or any(v['call'] != 'ъ' or v['gate_status'] != 'VALID' for v in votes):
                raise ValueError('edit requires two valid agreeing reads')
            if not check or not check['pixel_checked'] or check['call'] not in {'ъ', 'ь', 'hold'} or not check['reviewer']:
                raise ValueError('edit lacks lead pixel check')
            outcome = {'ъ': 'edit_hard', 'ь': 'keep_soft', 'hold': 'hold'}[check['call']]
        elif check:
            # A lead cannot promote a disagreement/soft decision to an edit.
            if check['call'] == 'ъ':
                raise ValueError('lead cannot create edit without two hard reads')
            outcome = 'keep_soft' if check['call'] == 'ь' else 'hold'
        grouped[d['row_id']].append(dict(d, decision=outcome, lead=check))
    result = []
    for r in data:
        ds = grouped[r['id']]
        edits = [d for d in ds if d['decision'] == 'edit_hard']
        holds = [d for d in ds if d['decision'] == 'hold']
        if not edits and not holds:
            continue
        raw = r['label']
        chars = list(raw)
        for d in edits:
            chars[d['offset']] = 'ъ'
        text = ''.join(chars)
        changed = {i for i, (a, b) in enumerate(zip(raw, text)) if a != b}
        if len(raw) != len(text) or changed != {d['offset'] for d in edits}:
            raise ValueError('unlisted change')
        restored = list(text)
        for i in changed:
            if (raw[i], text[i]) != ('ь', 'ъ'):
                raise ValueError('non-yer edit')
            restored[i] = 'ь'
        if ''.join(restored).encode() != raw.encode():
            raise ValueError('raw bytes not recovered')
        result.append(dict(id=r['id'], split=r['ru4e_split'], label=text, label_parent=raw,
                           parent_utf8_sha256=hashlib.sha256(raw.encode()).hexdigest(),
                           status='hold' if holds else 'ok', edits=edits, holds=holds))
    return result


def finalize(art=ART, pack=PACK, apply_lead=None, registry=REGISTRY, output=None):
    info = validate(art, pack)
    expected = rows(art/'candidate_positions.full.jsonl')
    votes = defaultdict(list)
    contexts, coverages, evidence = {}, {}, {}
    replacements = []
    seen = set()
    for c in info['contexts']:
        ctx = c['context']
        for reader in ('r1', 'r2'):
            identity = ctx+'/'+reader
            run = art/'answers'/(stem(ctx, reader)+'.run.json')
            if not run.exists():
                contexts[identity] = dict(status='PENDING')
                continue
            try:
                mapped, gate, cov, ev = collect(art, pack, ctx, reader, seen)
                evidence.update(ev)
                coverages[identity] = cov
                contexts[identity] = dict(status=gate['status'], gate=gate)
                if gate['status'] == 'VOID':
                    repl = replacement(art, pack, ctx, reader)
                    replacements.append(repl)
                    ra, rp = Path(repl['art']), Path(repl['pack'])
                    if not (ra/'answers/ctx01.r3.run.json').exists():
                        continue
                    mapped, gate, cov, ev = collect(ra, rp, 'ctx01', 'r3', seen)
                    evidence.update(ev)
                    coverages[repl['identity']] = cov
                    contexts[repl['identity']] = dict(status=gate['status'], gate=gate)
                    if gate['status'] != 'VALID':
                        continue
                    identity = repl['identity']
                for p in mapped:
                    if p['control'] or p['google'] != 'ь' or p['kind'] != 'final':
                        continue
                    k = p['row_id'], p['offset']
                    if any(v['logical_reader'] == reader for v in votes[k]):
                        raise ValueError('duplicate role vote')
                    votes[k].append(dict(logical_reader=reader, context=identity, call=p['call'],
                                         gate_status='VALID', confidence=p['confidence'],
                                         item_id=p['item_id'], evidence=ev))
            except (OSError, ValueError, KeyError, TypeError) as exc:
                contexts[identity] = dict(status='FAILED', reason=str(exc))
    expected_keys = {(p['row_id'], p['offset']) for p in expected}
    if set(votes)-expected_keys:
        raise ValueError('votes outside census')
    decisions = [combine(p, votes[p['row_id'], p['offset']]) for p in expected]
    jsonl(art/'decisions.jsonl', decisions)
    jsonl(art/'r3_to_run.jsonl', replacements)
    entries, leadinfo = lead_sheets(art, pack, decisions)
    report = dict(status='EMPTY_SCOPE' if not expected else 'AWAITING_LEAD', contexts=contexts,
                  coverage=coverages, evidence=evidence, lead=leadinfo,
                  counts=dict(Counter(d['decision'] for d in decisions)),
                  replacements=replacements, decisions_sha256=sha(art/'decisions.jsonl'))
    if any(len(votes[p['row_id'], p['offset']]) != 2 for p in expected):
        report['status'] = 'PENDING_READS'
    dump(art/'finalize.json', report)
    if not apply_lead:
        return report
    if report['status'] != 'AWAITING_LEAD':
        raise ValueError('cannot apply: '+report['status'])
    supplied = rows(apply_lead)
    checks = {(r['row_id'], r['offset']): r for r in supplied}
    if len(checks) != len(supplied) or set(checks) != {(r['row_id'], r['offset']) for r in entries}:
        raise ValueError('lead coverage differs')
    for entry in entries:
        check = checks[entry['row_id'], entry['offset']]
        if any(check.get(k) != entry[k] for k in ('split', 'proposed', 'audit', 'genuine_disagreement', 'crop', 'crop_sha256')):
            raise ValueError('lead entry binding differs')
        if sha(entry['crop']) != entry['crop_sha256'] or check.get('pixel_checked') is not True or not isinstance(check.get('reviewer'), str) or not check['reviewer'].strip() or check.get('call') not in {'ъ', 'ь', 'hold'}:
            raise ValueError('incomplete lead pixel check')
    data = [dict(r, ru4e_split=s) for s, p in info['sources'].items() for r in rows(p)]
    result = apply_overlay(data, decisions, checks)
    output = output or WORK/'artifacts/ru1/ru1_v3_test_edits.jsonl'
    manifest_path = output.with_name(output.stem+'_manifest.json')
    if output.exists() or manifest_path.exists():
        raise ValueError('refuse issued overlay overwrite')
    obj = json.loads(registry.read_text())
    if 'ru1_v3_test_edits' in obj['versions']:
        raise ValueError('version already registered')
    # Existing train parent remains intact; add exact split paths under that RAW family.
    parent = obj['versions'].get('google_raw_v2_import')
    if not parent or parent.get('text_field') != 'label' or parent.get('parent') is not None:
        raise ValueError('RAW parent registration missing or incompatible')
    parent = copy.deepcopy(parent)
    split_sources = {s: dict(path=p, sha256=sha(p), text_field='label', id_field='id')
                     for s, p in info['sources'].items()}
    for s, spec in split_sources.items():
        old = parent.setdefault('splits', {}).get(s)
        if old and old != spec:
            raise ValueError('RAW split registration differs')
        parent['splits'][s] = spec
    jsonl(output, result)
    manifest = dict(version='ru1_v3_test_edits', parent=dict(version='google_raw_v2_import', splits=split_sources),
                    output=dict(path=str(output), sha256=sha(output), rows=len(result)),
                    counts=dict(edited_rows=sum(bool(r['edits']) for r in result),
                                edits=sum(len(r['edits']) for r in result),
                                hold_rows=sum(bool(r['holds']) for r in result)),
                    offset_unit='zero-based Unicode code point in exact RAW import label',
                    inheritance='Sparse id overlay; omitted ids inherit exact RAW text from recorded split',
                    evidence=evidence, inputs=info['inputs'],
                    provenance=bindings([art/'build.json', art/'decisions.jsonl', Path(apply_lead),
                                         art/'lead/manifest.json', art/'lead/sheets.html']))
    dump(manifest_path, manifest)
    output.with_suffix('.sha256').write_text(sha(output)+'  '+output.name+'\n')
    obj['versions']['google_raw_v2_import'] = parent
    obj['versions']['ru1_v3_test_edits'] = dict(path=str(output), sha256=sha(output),
        parent='google_raw_v2_import', overlay=True, text_field='label', id_field='id',
        parent_splits=list(split_sources),
        split_field='split', status='local', manifest=str(manifest_path),
        sources=split_sources, read='Exact id overlay; otherwise exact RAW Google import label in recorded split')
    dump(registry, obj)
    return manifest


def tasks(info, art, pack):
    todo = [dict(identity=c['context']+'/'+r, context=c['context'], reader=r,
                 art=str(art), pack=str(pack)) for r in ('r1', 'r2') for c in info['contexts']]
    pending = art/'r3_to_run.jsonl'
    if pending.exists():
        todo.extend(rows(pending))
    return todo


def attempted(task):
    a, p = Path(task['art']), Path(task['pack'])
    name = stem(task['context'], task['reader'])
    return any((a/'answers').glob(name+'.*')) or (p/task['context']/task['reader']/'answers.jsonl').exists()


def drive(art=ART, pack=PACK, dry_run=False, runner=subprocess.run, prober=subprocess.check_output):
    info = validate(art, pack)
    plan = tasks(info, art, pack)
    if dry_run:
        result = dict(dry_run=True, status=info['status'], contexts=len(plan),
                      todo=[t for t in plan if not attempted(t)], model='gpt-6.1-sol',
                      effort='medium', network=False, closure='ok', probes=0, reads=0)
        return result
    with (art/'driver.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        stop = art/'STOPPED_AT_70.json'
        if stop.exists():
            return dict(status='STOPPED_AT_70')
        for task in plan:
            if attempted(task):
                continue
            validate(art, pack)
            a, p = Path(task['art']), Path(task['pack'])
            ctx, reader = task['context'], task['reader']
            if reader == 'r3':
                for path, h in task['bindings'].items():
                    if sha(path) != h:
                        raise ValueError('replacement changed')
                closure(p, a, runtime=True, replacement=True)
            probe = prober(['bash', str(BOUND/'limit_probe.sh'), 'before:RU4E/'+task['identity']], text=True).strip().splitlines()[-1]
            used = weekly(probe)
            if used >= 70:
                dump(stop, dict(weekly_used_percent=used, probe=probe, next_context=task['identity'], threshold=70))
                return dict(status='STOPPED_AT_70')
            name = stem(ctx, reader)
            ans = a/'answers'/name
            ans.parent.mkdir(parents=True, exist_ok=True)
            claim = Path(str(ans)+'.attempt.json')
            with claim.open('x') as f:
                json.dump(dict(task=task, probe=probe, status='CLAIMED'), f)
            # Owned helper accepts output root through a bound argument, never a shared mutation.
            cmd = ['bash', str(BOUND/'run_read.sh'), 'RU4E-'+task['identity'].replace('/', '-'),
                   str(p/ctx/reader), str(BOUND/'yer.md'), 'medium']
            run = runner(cmd, text=True, capture_output=True)
            Path(str(ans)+'.launcher.log').write_text(run.stdout+run.stderr)
            try:
                payload = json.loads(run.stdout.strip().splitlines()[-1])
                dump(Path(str(ans)+'.run.json'), payload)
            except (ValueError, IndexError):
                dump(claim, dict(status='FAILED', rc=run.returncode))
                continue
            after = prober(['bash', str(BOUND/'limit_probe.sh'), 'after:RU4E/'+task['identity']], text=True).strip().splitlines()[-1]
            append(art/'usage_ledger.json', record(payload, probe, after, 'ru4e/'+task['identity'], reader,
                                                 len(rows(p/ctx/reader/'items.jsonl'))))
            dump(claim, dict(status='DONE' if run.returncode == 0 and payload['rc'] == 0 else 'FAILED',
                             rc=run.returncode, probe=probe, after=after))
            if weekly(after) >= 70:
                dump(stop, dict(weekly_used_percent=weekly(after), probe=after, threshold=70))
                return dict(status='STOPPED_AT_70')
    return dict(status='COMPLETE', contexts=len(plan))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['build', 'drive', 'finalize'])
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--apply-lead', type=Path)
    args = p.parse_args()
    if args.action == 'build':
        result = build()
    elif args.action == 'drive':
        result = drive(dry_run=args.dry_run)
    else:
        result = finalize(apply_lead=args.apply_lead)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
