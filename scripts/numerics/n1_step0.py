"""Offline N1S0 text census and unrendered slot frame. Run from repo root."""
from collections import Counter, defaultdict
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import random
import re
import sys
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from greekocr.numerics.tokens import tokenize

ROOT = Path(__file__).resolve().parents[2]
PROJECTS = Path.home() / 'Projects'
OUT = ROOT / 'artifacts/n1'
SEED = 20261017
INPUTS = {}


def read_bytes(path):
    data = path.read_bytes()
    INPUTS[str(path)] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    return data


def rows(path):
    return [json.loads(x) for x in read_bytes(path).splitlines() if x.strip()]


def bucket(r):
    source = r['source']
    year = r.get('year')
    if source == 'gazette_modern' and isinstance(year, int):
        if 1982 <= year <= 1985:
            return 'gazette_1982_1985'
        if 1986 <= year <= 1990:
            return 'gazette_1986_1990'
    return source


def glyph_key(g):
    if not g:
        return 'NONE_TEXT'
    return '+'.join(f'U+{ord(c):04X}' for c in g)


def blank():
    return dict(lines=0, numeric_lines=0, tokens=0, slots=0, inner_slots=0,
                boundary_slots=0, inner_hyphen_occurrences=0, hyphen_in_4plus_digit_tokens=0,
                tokens_with_hyphen_4plus_digits=0, glyph_by_position={},
                years={}, raised_dot_between_digits=0)


def add(stats, r, text, tokens):
    stats['lines'] += 1
    stats['years'][str(r.get('year'))] = stats['years'].get(str(r.get('year')), 0) + 1
    stats['numeric_lines'] += bool(tokens)
    stats['tokens'] += len(tokens)
    for t in tokens:
        stats['slots'] += len(t.slots)
        stats['inner_slots'] += len(t.slots)-2
        stats['boundary_slots'] += 2
        hs = sum(s.glyph.count('-') for s in t.slots if s.boundary is None)
        stats['inner_hyphen_occurrences'] += hs
        stats['hyphen_in_4plus_digit_tokens'] += hs if t.digit_count >= 4 else 0
        stats['tokens_with_hyphen_4plus_digits'] += bool(hs and t.digit_count >= 4)
        stats['raised_dot_between_digits'] += sum(s.glyph.count('·') + s.glyph.count('·') for s in t.slots if s.boundary is None)
        for s in t.slots:
            g = glyph_key(s.glyph)
            table = stats['glyph_by_position'].setdefault(g, {})
            table[s.position] = table.get(s.position, 0) + 1


def dot_census(records):
    result = {}
    for ch in ('·', '·'):
        examples = []
        numeric_examples = []
        spaced_examples = []
        spaced_between = 0
        total = lines = between = 0
        for r in records:
            text = r['label']
            n = text.count(ch)
            for m in re.finditer(r'(?<=[0-9]) *'+re.escape(ch)+r' *(?=[0-9])', text):
                spaced_between += 1
                if len(spaced_examples) < 20:
                    spaced_examples.append({'id':r['id'], 'offset':m.start(), 'context':text[max(0,m.start()-20):m.end()+20], 'raw_label':r.get('raw_label',text)})
            total += n
            lines += bool(n)
            for i, c in enumerate(text):
                if c == ch:
                    numeric = i > 0 and i+1 < len(text) and text[i-1].isascii() and text[i-1].isdigit() and text[i+1].isascii() and text[i+1].isdigit()
                    between += numeric
                    if numeric and len(numeric_examples) < 20:
                        numeric_examples.append({'id': r['id'], 'offset': i, 'context': text[max(0,i-20):i+21], 'raw_label': r.get('raw_label', text)})
                    if len(examples) < 8:
                        examples.append({'id': r['id'], 'offset': i, 'context': text[max(0,i-20):i+21], 'between_digits': numeric})
        result[f'U+{ord(ch):04X}'] = dict(occurrences=total, lines=lines, between_digits=between, examples=examples, numeric_examples=numeric_examples, between_digits_allowing_spaces=spaced_between, spaced_numeric_examples=spaced_examples)
    return result


def balanced_sample(pool, count, rng):
    """Round-robin equal allocation to source × primary grammar × glyph cells."""
    cells = defaultdict(list)
    for r in pool:
        cells[(r['source_era'], r['position'], glyph_key(r['glyph']))].append(r)
    keys = sorted(cells)
    for key in keys:
        rng.shuffle(cells[key])
    rng.shuffle(keys)
    chosen = []
    while keys and len(chosen) < count:
        for key in keys[:]:
            chosen.append(cells[key].pop())
            if not cells[key]:
                keys.remove(key)
            if len(chosen) == count:
                break
    return chosen


def summarize_frame(frame):
    return dict(Counter(f"{r['partition']} | {r['source_era']} | {r['position']} | {glyph_key(r['glyph'])}" for r in frame))


def main():
    OUT.mkdir(exist_ok=True)
    w1path = PROJECTS/'collect-v3-data/run/W1/features.jsonl'
    records = rows(w1path)
    c1root = PROJECTS/'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1'
    c1results = json.loads(read_bytes(c1root/'c1_results.json'))
    separators = {k: v['separator'] for k,v in c1results.items() if v.get('separator')}
    verdict_count = sum(len(rows(f)) for f in sorted((c1root/'verdicts').glob('*.jsonl')))
    excluded = set()
    keyroot = PROJECTS/'collect-v3-data/run/W1/c1'
    for f in sorted(keyroot.glob('*_key.json')):
        key = json.loads(read_bytes(f))
        excluded.update(v['line_id'] for v in key.values() if isinstance(v, dict) and 'line_id' in v)
    assert excluded
    stats = defaultdict(blank)
    total = blank()
    candidates = []
    for r in records:
        text = r['text']  # Google stream, not corrected/convention labels
        ts = tokenize(text)
        b = bucket(r)
        add(stats[b], r, text, ts)
        add(total, r, text, ts)
        if r['id'] in excluded:
            continue
        for ti, t in enumerate(ts):
            for s in t.slots:
                candidates.append(dict(line_id=r['id'], document=f"{r['source']}:{r['item']}",
                    source=r['source'], source_era=b, year=r['year'], page=r['page'],
                    crop=r['crop'], crop_sha256=r['crop_sha256'],
                    token_index=ti, token_start=t.start, token_end=t.end,
                    digit_count=t.digit_count, **asdict(s),
                    slot_id=f"{r['id']}:t{ti}:s{s.index}",
                    suspected_hyphen=(s.boundary is None and '-' in s.glyph and t.digit_count>=4)))
    reported = {k:v for k,v in stats.items() if k.startswith('gazette_') or k=='elstat' or v['tokens']>=100}
    candidates = [r for r in candidates if r['source_era'] in reported]
    # Whole documents locked before development sampling; never tune on any of their lines.
    rng = random.Random(SEED)
    locked_docs = set()
    locked = []
    targets = ['elstat','gazette_1982_1985','gazette_1986_1990']
    for b in targets:
        eligible = [r for r in candidates if r['source_era']==b]
        docs = sorted({r['document'] for r in eligible})
        rng.shuffle(docs)
        # A quarter of documents; at least two. Expand only if 100 slots unavailable.
        selected = set(docs[:max(2, (len(docs)+3)//4)])
        while sum(r['document'] in selected for r in eligible) < 100:
            selected.add(docs[len(selected)])
        locked_docs.update(selected)
        epool = [r for r in eligible if r['document'] in selected]
        # Prefer actual separator candidates, retaining boundaries/none as controls.
        marks = [r for r in epool if r['glyph'] or r['position']=='table_boundary']
        chosen = balanced_sample(marks, 90, rng)
        used = {r['slot_id'] for r in chosen}
        chosen += balanced_sample([r for r in epool if r['slot_id'] not in used], 100-len(chosen), rng)
        locked.extend(chosen)
    devpool = [r for r in candidates if r['document'] not in locked_docs]
    # 40% explicitly targets the suspected class, across source/grammar/glyph cells.
    suspect = balanced_sample([r for r in devpool if r['suspected_hyphen']], 240, rng)
    dev = list(suspect)
    used = {r['slot_id'] for r in dev}
    # 300 more observed separator/table slots, balanced across all source-era cells.
    dev += balanced_sample([r for r in devpool if r['slot_id'] not in used and (r['glyph'] or r['position']=='table_boundary')], 540-len(dev), rng)
    used = {r['slot_id'] for r in dev}
    dev += balanced_sample([r for r in devpool if r['slot_id'] not in used], 600-len(dev), rng)
    assert len(dev)==600 and len(locked)==300
    for partition, selected in [('step1', dev), ('locked_eval', locked)]:
        for r in selected:
            r['partition'] = partition
            r['seed'] = SEED
            r['truth'] = None
            r['rendered'] = False
    frame = dev + locked
    assert len({r['slot_id'] for r in frame}) == 900
    assert not ({r['document'] for r in dev} & locked_docs)
    assert not ({r['line_id'] for r in frame} & excluded)
    trainroot = PROJECTS/'greek-ocr-toolkit/docs/harvest/collection/v2'
    codecpaths = [PROJECTS/'greek-ocr-toolkit/greekocr/_vendor/codec/v1.json', PROJECTS/'greek-ocr-toolkit/greekocr/_vendor/codec/v2.json', PROJECTS/'greek-page-ocr/codec/v2.json']
    codecs = {}
    atoms = set()
    for path in codecpaths:
        if path.exists():
            codec = json.loads(read_bytes(path))
            chars = {a['ch'] for a in codec['atoms']}
            codecs[str(path)] = {'policy':codec['policy'], 'raised_dot_atoms': [a for a in codec['atoms'] if a['ch'] in '··']}
            if path.name=='v1.json':
                atoms = chars
    rustpath = PROJECTS/'greek-page-ocr/factory/src/codec.rs'
    rust = read_bytes(rustpath).decode()
    block = re.search(r'let c = match c \{(.*?)other => other,', rust, re.S)[1]
    folds = {}
    for line in block.splitlines():
        if '=>' not in line:
            continue
        left, right = line.split('=>', 1)
        src = re.findall(r"'\\u\{([0-9a-fA-F]+)\}'", left)
        dest = re.search(r"'\\u\{([0-9a-fA-F]+)\}'", right)
        assert src and (dest or 'continue' in right)
        for h in src:
            folds[chr(int(h,16))] = chr(int(dest[1],16)) if dest else ''
    training = {}
    for split in ('train','dev','test'):
        path = trainroot/f'import_real_v2_{split}.jsonl'
        data = rows(path)
        allstats = blank()
        bysource = defaultdict(blank)
        codecstats = blank()
        rejected = 0
        normalized_records = []
        normalized_by_source = defaultdict(blank)
        for r in data:
            text = r['label']
            ts = tokenize(text)
            add(allstats, r, text, ts)
            add(bysource[bucket(r)], r, text, ts)
            normalized = ' '.join(''.join(folds.get(ch,ch) for ch in unicodedata.normalize('NFD',text)).split())
            if set(normalized) <= atoms:
                nts = tokenize(normalized)
                add(codecstats, r, normalized, nts)
                add(normalized_by_source[bucket(r)], r, normalized, nts)
                normalized_records.append(dict(r, label=normalized, raw_label=text))
            else:
                rejected += 1
        training[split] = dict(path=str(path), total=allstats, by_source_era=dict(bysource),
            unicode=dot_census(data), codec_v1_normalized_eligible=codecstats, codec_v1_rejected_lines=rejected,
            codec_v1_normalized_unicode=dot_census(normalized_records),
            codec_v1_normalized_by_source_era=dict(normalized_by_source))
    result = dict(schema_version=1, seed=SEED, google_text_field='text',
        counting={'slots':'digit_count + 1 per token; includes empty inner gaps and both boundaries',
                  'hyphen_in_4plus_digit_tokens':'U+002D occurrences in inner slots of tokens with >=4 total digits; ranges included',
                  'grammar':'primary label only in tables; alternatives retained in tokenizer/frame',
                  'table_boundary':'text proxy: multiple spaces or explicit pipe/tab; not visual truth'},
        w1=dict(total=total, by_source_era=reported,
                omitted_below_100={k:v for k,v in stats.items() if k not in reported}),
        collection_v2=training, codecs=codecs,
        c1=dict(excluded_lines=len(excluded), verdicts=verdict_count, separator_entries=separators),
        sampling=dict(step1=len(dev), locked=len(locked), suspect_quota_target=240,
            suspect_selected=len(suspect), candidate_slots=len(candidates),
            stratum_counts=summarize_frame(frame), development_documents=sorted({r['document'] for r in dev}),
            locked_documents=sorted(locked_docs)), inputs=INPUTS,
        training_scope='collection-v2 source labels and Rust-v1-fold normalized codec-eligible rows; not a checkpoint consumed-row manifest',
        missing_codec_paths=[str(p) for p in codecpaths if not p.exists()],
        convention_recommendation='U+00B7', convention_status='recommendation; lead ruling pending')
    (OUT/'census.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (OUT/'frame_step1.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in frame))
    (OUT/'locked_eval_docs.json').write_text(json.dumps(dict(seed=SEED,
        document_identity='source:item (all pages and lines)',
        development_documents=sorted({r['document'] for r in dev}),
        locked_documents=sorted(locked_docs), locked_slot_ids=[r['slot_id'] for r in locked],
        excluded_c1_line_ids=sorted(excluded),
        scope='N1 document-disjoint lock; previous C1 exposure is not erased'),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'W1': {k:(v['tokens'],v['slots'],v['hyphen_in_4plus_digit_tokens']) for k,v in reported.items()},
        'total':(total['tokens'],total['slots']), 'train':training['train']['unicode'],
        'codec_train_lines':training['train']['codec_v1_normalized_eligible']['lines'],
        'suspect_selected':len(suspect),'docs':(len({r['document'] for r in dev}),len(locked_docs))},ensure_ascii=False))


if __name__ == '__main__':
    main()
