"""Build RU1 owner cards from completed decisions and hash-bound saved pixels.
Run with the collect venv and PYTHONPATH pointing only at the cleanup worktree.
No inference, crop regeneration, publication, or writes outside artifacts/ru1.
"""
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from functools import lru_cache
sys.path.insert(0, str(Path(__file__).resolve().parent/'reading'))
from ru1_decide import accepted_contexts
from common import ROOT, PACK_ROOT, PROJECTS, rows, dump, sha

SEED = '20261017:RU1S'
ORDER = ['lead_review', 'edit_hard', 'keep_soft']
NAMES = ['Needs a look', 'Proposed ъ', 'Kept ь']
# 4x/8x exceeded the 15 MB cap (15,574,528 bytes); retain native pixels.
WORD_SCALE, FINAL_SCALE = 3, 6


@lru_cache(maxsize=512)
def character_alignment(label, google):
    """Exact matches shared by ALL minimum-edit (unit-cost) alignments.

    An equally optimal deletion or substitution makes a character unaligned.
    Prefix/suffix costs examine every optimal edge, avoiding tie-break guesses.
    """
    n, m = len(label), len(google)
    def costs(a, b):
        out = [list(range(len(b)+1))]
        for i, ca in enumerate(a, 1):
            row = [i]
            for j, cb in enumerate(b, 1):
                row.append(min(out[-1][j]+1, row[-1]+1, out[-1][j-1]+(ca != cb)))
            out.append(row)
        return out
    pre = costs(label, google)
    rev = costs(label[::-1], google[::-1])
    best = pre[n][m]
    mapping = []
    for i, char in enumerate(label):
        choices = set()
        for j in range(m+1):
            if pre[i][j]+1+rev[n-i-1][m-j] == best:
                choices.add(None)  # deletion
            if j < m and pre[i][j]+(char != google[j])+rev[n-i-1][m-j-1] == best:
                choices.add(j if char == google[j] else None)
        mapping.append(next(iter(choices)) if len(choices) == 1 else None)
    return tuple(mapping)


def google_offset(label, google, offset):
    """Require the complete alphabetic word and yer to match uniquely."""
    if not 0 <= offset < len(label) or label[offset] not in 'ьъ':
        raise ValueError('invalid yer offset')
    start, end = offset, offset+1
    while start and label[start-1].isalpha(): start -= 1
    while end < len(label) and label[end].isalpha(): end += 1
    mapped = character_alignment(label, google)[start:end]
    if any(i is None for i in mapped): return None
    a, b = mapped[0], mapped[-1]+1
    if mapped != tuple(range(a, b)) or label[start:end] != google[a:b]: return None
    if (a and google[a-1].isalpha()) or (b < len(google) and google[b].isalpha()): return None
    return mapped[offset-start]


def proposed(label, decisions):
    chars = list(label); seen = set()
    for d in decisions:
        off = d['offset']
        if off in seen or not 0 <= off < len(chars) or chars[off] != 'ь' or d['google'] != 'ь' or d['kind'] != 'final':
            raise ValueError('invalid or duplicate candidate offset')
        seen.add(off)
        if d['decision'] == 'edit_hard': chars[off] = 'ъ'
    return ''.join(chars)


def group_for(decisions):
    return min((d['decision'] for d in decisions), key=ORDER.index)


def select_lines(by_line):
    groups = {g: sorted(lid for lid, ds in by_line.items() if group_for(ds) == g) for g in ORDER}
    kept = groups['keep_soft']
    sample = sorted(random.Random(SEED).sample(kept, min(40, len(kept))))
    return groups, {**groups, 'keep_soft': sample}


def build():
    from PIL import Image
    from greekocr.adjudicate import owner_sheet
    from ru1_review import symbol_crops, unmask, segments
    cleanup = PROJECTS/'greek-ocr-toolkit-cleanup'
    if Path(owner_sheet.__file__).resolve() != cleanup/'greekocr/adjudicate/owner_sheet.py':
        raise ValueError('wrong owner-sheet renderer')
    inputs = {}
    def bind(path):
        path = Path(path); inputs[str(path.resolve())] = sha(path); return path
    work = ROOT.parents[1]
    for path in [Path(__file__), work/'scripts/secondary/ru1_review.py',
                 work/'scripts/secondary/reading/common.py', work/'scripts/secondary/reading/ru1_map_answers.py',
                 work/'scripts/secondary/ru1_decide.py', work/'docs/records/labelfix/secondary/PLAN.md',
                 work/'docs/records/labelfix/secondary/RU1_CONTROL_REVIEW.md', cleanup/'docs/CLEANUP_STEP4_REPORT.md',
                 cleanup/'greekocr/adjudicate/owner_sheet.py', cleanup/'greekocr/adjudicate/owner_sheet.css',
                 cleanup/'greekocr/adjudicate/owner_sheet.js', ROOT/'decisions.summary.json']:
        bind(path)
    summary = json.loads((ROOT/'decisions.summary.json').read_text())
    if summary['status'] != 'complete': raise ValueError('requires complete two-reader decisions')
    by_line = defaultdict(list)
    for d in rows(bind(ROOT/'decisions.jsonl')): by_line[d['row_id']].append(d)
    all_groups, selected = select_lines(by_line)
    features = PROJECTS/'collect-v3-data/run/W1/features.jsonl'
    w1 = {r['id']: r for r in rows(bind(features)) if r['id'] in by_line}
    lookup = {}
    for ctx, reader, stem in accepted_contexts():
        key = json.loads(bind(ROOT/f'keys/{stem}.json').read_text())
        for suffix in ['jsonl','mapped.jsonl','controls.json','scan.json']:
            bind(ROOT/f'answers/{stem}.{suffix}')
        items = rows(bind(PACK_ROOT/ctx/reader/'items.jsonl'))
        bind(PACK_ROOT/ctx/f'MANIFEST.{reader}.json')
        if reader == 'r1':
            for item in items:
                meta = key['items'][item['item_id']]
                if not meta['control']: lookup[meta['row_id']] = (ctx,item,meta)
    population_alignment = Counter(aligned=0, unaligned=0)
    population_alignment.update(
        'aligned' if google_offset(w1[lid]['label'], w1[lid]['text'], d['offset']) is not None else 'unaligned'
        for lid, ds in by_line.items() for d in ds)
    cards = []; geometry = []
    for group in ORDER:
        for lid in selected[group]:
            ds = sorted(by_line[lid],key=lambda d:d['offset']); r = w1[lid]
            ctx,item,meta = lookup[lid]
            if meta['w1_id'] != lid or unmask(item,meta) != r['label']: raise ValueError('W1 pack mismatch')
            if not r['text']: raise ValueError('empty Google text')
            crop = bind(PACK_ROOT/ctx/'r1'/item['crop'])
            if sha(crop) != meta['source_crop_sha256'] or sha(crop) != r['crop_sha256']: raise ValueError('crop hash mismatch')
            with Image.open(crop) as im: image = im.copy()
            binding = json.loads(bind(features.parent/f"pages/{r['page_id']}.json").read_text())
            response = bind(binding['response'])
            if sha(response) != binding['response_sha256']: raise ValueError('response hash mismatch')
            doc = json.loads(response.read_text()); doc = doc.get('document',doc)
            line = doc['pages'][0]['lines'][r['docai_line_index']]
            google_text = ''.join(doc['text'][a:b] for a,b in segments(line['layout'])).rstrip('\r\n')
            if google_text != r['text']: raise ValueError('retained Google text mismatch')
            offsets = [google_offset(r['label'], google_text, d['offset']) for d in ds]
            zooms = []; reads = []
            card_aligned = all(off is not None for off in offsets)
            for n,d in enumerate(ds,1):
                geo = dict(label_offset=d['offset'],google_offset=offsets[n-1],
                           zoom='aligned' if card_aligned else 'unaligned',
                           reason=None if card_aligned else ('word_unaligned' if offsets[n-1] is None else 'card_has_unaligned_word'))
                if card_aligned:
                    word,final,boxes = symbol_crops(image,google_text,offsets[n-1],doc,line,r['crop_bbox'][:2])
                    geo.update(boxes,word_native_size=list(word.size),final_native_size=list(final.size),word_scale=WORD_SCALE,final_scale=FINAL_SCALE)
                    for name,native,scale in [('word',word,WORD_SCALE),('final',final,FINAL_SCALE)]:
                        zooms.append(dict(image=native.resize((native.width*scale,native.height*scale),Image.Resampling.NEAREST),alt=f'{name} {n}'))
                slot = next(s for s in meta['slots'] if s['offset'] == d['offset'])
                calls = ', '.join(f"{reader} {d['reads'][reader]['call']} ({d['reads'][reader]['context']}, {d['reads'][reader]['gate_status']})" for reader in d['reads'])
                klass = d['decision'] + (':'+d['reason'] if d['decision']=='lead_review' else '')
                reads.append(f"{n}: {slot['word']} — {calls}; {klass}; prior {d['prior']}")
                geometry.append(dict(line_id=lid,position=n,word=slot['word'],**geo))
            tags = sorted({d['decision']+(':'+d['reason'] if d['decision']=='lead_review' else '') for d in ds})
            cards.append(dict(line_id=lid,label=lid,image=image,alt='line crop',zooms=zooms,
                rows=[dict(name='Google',text=r['text']),dict(name='Proposed',text=proposed(r['label'],ds)),dict(name='Reads',text=' | '.join(reads))],
                tags=[dict(text=t) for t in tags+[meta['book'], 'zoom: aligned' if card_aligned else 'zoom: unaligned']],printed='',group=group))
    spec = dict(title='RU1 Hard Sign Decisions',intro=(
        'Google writes printed word-final ъ as ь in pre-1918 Russian; each position has two blind Sol reads. '
        'An edit requires two ъ reads with no ь, at least one valid context, and no conflicting prior. '
        "Google’s own ъ is never changed; please mark any wrong Proposed in the note or the Printed field. Proposed is built on the W1 label (the current label version)."),
        groups=[dict(id=g,heading=f'{name} — {len(all_groups[g])} lines, {sum(len(by_line[lid]) for lid in all_groups[g])} positions; showing {len(selected[g])} lines') for g,name in zip(ORDER,NAMES)])
    html = owner_sheet.render(cards,spec)
    size = len(html.encode('utf-8'))
    if size >= 15_000_000: raise ValueError(f'HTML too large: {size}; explicit zoom downscale needed')
    dest = ROOT/'owner_sheet'; dest.mkdir(exist_ok=True)
    path = dest/'ru1_sheet.html'; path.write_text(html)
    # Recheck all sources after rendering so hashes describe one stable build.
    if any(sha(p) != digest for p,digest in inputs.items()): raise ValueError('input drift during build')
    result = dict(schema='RU1F-owner-v1',cards=len(cards),candidate_lines=len(by_line),candidate_positions=sum(map(len,by_line.values())),
        groups={g:dict(total_lines=len(all_groups[g]),total_positions=sum(len(by_line[lid]) for lid in all_groups[g]),shown_lines=len(selected[g]),shown_positions=sum(len(by_line[lid]) for lid in selected[g]),line_ids=selected[g]) for g in ORDER},
        sample_seed=SEED,html=str(path.relative_to(work)),html_bytes=size,html_MB=size/1_000_000,html_sha256=sha(path),inputs=inputs,
        renderer=str(owner_sheet.__file__),python=sys.executable,printed_prefilled=False,zoom_downscaled=True,
        word_scale=WORD_SCALE,final_scale=FINAL_SCALE,geometry=geometry,
        zoom_counts={status:sum(g['zoom'] == status for g in geometry) for status in ['aligned','unaligned']},population_alignment_counts=dict(population_alignment),
        alignment_method='all optimal unit-cost character edit alignments; unchanged complete word required; any unaligned word suppresses all card zooms')
    dump(dest/'summary.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in {'inputs','geometry'}},ensure_ascii=False,indent=2))
    return result

if __name__ == '__main__': build()
