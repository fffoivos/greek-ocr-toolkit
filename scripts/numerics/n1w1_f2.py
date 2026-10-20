"""Offline F2 materialisation after n1w1_r3_finalize.sh (never launches readers)."""
import json
from collections import Counter, defaultdict
from pathlib import Path
import n1w1 as m
from n1w1_sheets import font, paste_fit
from PIL import Image, ImageDraw


def category(d):
    valid = [r for r in d['reads'] if r['context_status'] == 'VALID' and r['read_status'] == 'ok']
    if len(valid) != 2:
        return 'still_missing'
    a, b = [r['meaning'] for r in valid]
    if a != b:
        return 'disagreements'
    return {'raised dot': 'agreed_raised', 'baseline dot': 'baseline',
            'hyphen': 'hyphen_dash', 'en dash': 'hyphen_dash', 'em dash': 'hyphen_dash'}.get(a, 'other')


def build():
    art = m.ART/'r3/finalization'
    ds = m.rows(art/'decisions.jsonl')
    review = json.loads((art/'review.json').read_text())
    slots = {s['slot_id']: s for s in m.rows(m.ART/'candidates.jsonl')}
    prior_path = m.REVIEW/'sheets/index.json'
    prior = json.loads(prior_path.read_text())
    confirmed = {c['slot_id']: c for sheet in prior['sheets'] for c in sheet['cells']}
    assert len(confirmed) == 22
    for sheet in prior['sheets']:
        assert m.sha(sheet['sheet']) == sheet['sha256']
    raised = {d['slot_id'] for d in ds if d['agreed_raised']}
    assert set(confirmed) <= raised
    for sid, cell in confirmed.items():
        assert cell['zoom_sha256'] == slots[sid]['zoom_sha256']
    new = [d for d in ds if d['slot_id'] in raised - set(confirmed)]
    outdir = m.REVIEW/'sheets2'
    outdir.mkdir(parents=True, exist_ok=True)
    controls = {c['slot_id']: c for c in m.rows(m.ART/'controls.jsonl')}
    refs = [controls[r['slot_id']] for r in prior['sheets'][0]['references']]
    for ref, old in zip(refs, prior['sheets'][0]['references']):
        assert m.sha(ref['zoom']) == old['zoom_sha256']
    sheets = []
    for offset in range(0, len(new), 6):
        canvas = Image.new('RGB', (2400, 3300), 'white'); draw = ImageDraw.Draw(canvas)
        draw.text((35, 20), f'N1W1 F2 new raised | sheet {offset//6+1}/{(len(new)+5)//6} | lead pending', font=font(32, True), fill='black')
        for j, ref in enumerate(refs):
            x = 30+j*595
            draw.text((x, 78), 'APPROVED '+ref['truth'], font=font(24, True), fill='black')
            draw.text((x, 113), ref['slot_id'], font=font(12), fill='black')
            paste_fit(canvas, ref['zoom'], (x, 145, x+570, 490))
        cells = []
        for j, d in enumerate(new[offset:offset+6]):
            s = slots[d['slot_id']]; x = 30+(j%2)*1190; y = 540+(j//2)*910
            assert m.sha(s['zoom']) == s['zoom_sha256'] and m.sha(s['line']) == s['line_sha256']
            draw.rectangle((x, y, x+1160, y+880), outline='#bbbbbb', width=2)
            draw.text((x+15, y+14), f"{offset+j+1:02d} {s['slot_id']}", font=font(19, True), fill='black')
            draw.text((x+15, y+48), ' | '.join(f"{r['context']}: {r['meaning']}" for r in d['reads']), font=font(18), fill='black')
            paste_fit(canvas, s['zoom'], (x+15, y+95, x+1145, y+690))
            paste_fit(canvas, s['line'], (x+15, y+720, x+1145, y+855))
            cells.append(dict(cell=offset+j+1, slot_id=s['slot_id'], zoom_sha256=s['zoom_sha256'], line_sha256=s['line_sha256'], box=[x,y,x+1160,y+880]))
        path = outdir/f'raised_{offset//6+1:02}.png'; canvas.save(path)
        with Image.open(path) as image:
            image.verify()
        sheets.append(dict(sheet=str(path), sha256=m.sha(path), cells=cells, references=prior['sheets'][0]['references']))
    m.dump(outdir/'index.json', dict(cell_count=len(new), sheets=sheets, decisions_sha256=m.sha(art/'decisions.jsonl'), reference_source=str(prior_path)))
    template = [dict(slot_id=d['slot_id'], zoom_sha256=slots[d['slot_id']]['zoom_sha256'], pixel_checked=False, printed=None, note='') for d in new]
    tp = outdir/'lead_template.jsonl'
    if tp.exists():
        assert m.rows(tp) == template, 'preserve completed lead work'
    else:
        m.jsonl(tp, template)
    (outdir/'index.md').write_text('# N1W1 F2 new raised agreements\n\n'+f'{len(new)} cells pending lead pixel rulings. Same four approved references as the original sheets.\n\n'+'\n'.join(f'- [Sheet {i+1}](raised_{i+1:02}.png)' for i in range(len(sheets)))+'\n')
    features = m.RUN/'features.jsonl'
    parent = {r['id']: r for r in m.rows(m.SOURCE)}
    raw = {}
    for line in features.open():
        row = json.loads(line)
        if row['id'] in parent:
            raw[row['id']] = row
    assert set(raw) == set(parent)
    byline = defaultdict(list)
    counts = Counter(category(d) for d in ds)
    for name in ('agreed_raised', 'hyphen_dash', 'baseline', 'other', 'disagreements', 'still_missing'):
        counts.setdefault(name, 0)
    for d in ds:
        byline[d['line_id']].append(d)
    output = []
    verification = []
    for lid, p in parent.items():
        text = raw[lid]['text']
        # Current candidate offsets are label-based; require exact raw equality.
        assert text.encode('utf-8') == p['label'].encode('utf-8')
        edits = []; holds = []; provenance = []
        for d in byline[lid]:
            s = slots[d['slot_id']]
            assert text[d['start']:d['end']] == d['old'] and d['end'] == d['start']+1
            if d['slot_id'] in confirmed:
                assert 'range' not in s['grammar_candidates'] and d['old'] in '-.'
                edits.append(dict(slot_id=d['slot_id'], start=d['start'], end=d['end'], original=d['old'], replacement='·', pixel_checked=True, ruling='docs/records/labelfix/secondary/N1W1_LEAD_RAISED.md'))
            elif category(d) not in ('baseline', 'hyphen_dash'):
                holds.append(dict(slot_id=d['slot_id'], start=d['start'], end=d['end'], status='hold', reason='pending_lead' if d['slot_id'] in raised else d['reason']))
            provenance.append(d)
        if not edits and not holds:
            continue
        chars = list(text)
        for e in edits:
            chars[e['start']] = e['replacement']
        result = ''.join(chars)
        actual = [(i, a, b) for i, (a, b) in enumerate(zip(text, result)) if a != b]
        expected = sorted((e['start'], e['original'], e['replacement']) for e in edits)
        assert len(result) == len(text) and actual == expected
        # Also verify unchanged UTF-8 segments, without normalization.
        cursor = 0
        for e in sorted(edits, key=lambda e: e['start']):
            assert result[cursor:e['start']].encode() == text[cursor:e['start']].encode()
            cursor = e['end']
        assert result[cursor:].encode() == text[cursor:].encode()
        output.append(dict(id=lid, text=result, parent_text=text, status='edit' if edits else 'hold', edits=edits, holds=holds, slot_provenance=provenance))
        verification.append(dict(id=lid, exact_diff=True, edits=len(edits), holds=len(holds)))
    path = m.ROOT/'artifacts/n1/n1_v1_w1.jsonl'
    m.jsonl(path, output)
    path.with_suffix('.sha256').write_text(m.sha(path)+'  '+path.name+'\n')
    m.dump(art/'f2_row_verification.json', verification)
    pending = path.with_name('n1_v1_w1_pending.json')
    if new:
        m.dump(pending, dict(status='pending_lead', slots=template, index=str(outdir/'index.json'), index_sha256=m.sha(outdir/'index.json')))
    registry = json.loads(m.REGISTRY.read_text())
    registry['versions']['google_raw_w1'] = dict(path=str(features), sha256=m.sha(features), parent=None, text_field='text', id_field='id', status='local', population=dict(rows=sum(1 for _ in features.open()), definition='exact W1 raw Google text'))
    registry['versions']['n1_v1_w1'] = dict(path=str(path), sha256=m.sha(path), parent='google_raw_w1', overlay=True, text_field='text', id_field='id', status='local', population=dict(overlay_rows=len(output), definition='confirmed separator edits and explicitly marked unresolved holds; otherwise inherit raw W1 text'))
    m.dump(m.REGISTRY, registry)
    from greekocr.labelfix import lqb
    truth = m.ROOT/'docs/records/labelfix/lqb/truth_v1_1.jsonl'
    score = lqb.run(truth, registry, ['google_raw_w1', 'n1_v1_w1'])
    m.dump(art/'f2_lqb_rescore.json', score)
    contexts = review['contexts']
    def status(e): return e.get('gate', {}).get('status', e.get('status'))
    physical = Counter(status(e) for v in contexts.values() for e in ([v['original'],v['replacement']] if 'replacement' in v else [v]))
    effective = Counter(status(v.get('replacement',v)) for v in contexts.values())
    manifest = dict(schema='N1W1F2-v1', version='n1_v1_w1', parent='google_raw_w1', output=dict(path=str(path), sha256=m.sha(path), rows=len(output)), edits=sum(len(r['edits']) for r in output), holds=sum(len(r['holds']) for r in output), hold_only_rows=sum(r['status']=='hold' for r in output), counts=dict(counts), contexts_physical=dict(physical), contexts_effective=dict(effective), new_raised=len(new), new_raised_sheets=len(sheets), confirmed_slots=list(confirmed), pending=str(pending) if new else None, exact_diff_verified_rows=len(verification), contexts=contexts, network=False, new_readers=0, probes=0, git_writes=False, browser_or_computer_use=False, inputs={str(p):m.sha(p) for p in [features,m.SOURCE,art/'decisions.jsonl',art/'review.json',prior_path,m.ROOT/'docs/records/labelfix/secondary/N1W1_LEAD_RAISED.md',Path(__file__),truth,truth.with_name('truth_v1_1_flags.jsonl')]}, evidence={str(p):m.sha(p) for p in [outdir/'index.json',tp,art/'f2_row_verification.json',art/'f2_lqb_rescore.json',m.REGISTRY]})
    truth_ids = {r['line_id'] for r in m.rows(truth)}
    manifest['lqb'] = dict(rescored=True, truth=str(truth), edited_rows_on_truth=len({r['id'] for r in output if r['edits']} & truth_ids), separator=score['versions']['n1_v1_w1']['n1_separator|A+B'], paired_separator=score['paired']['google_raw_w1→n1_v1_w1']['n1_separator|A+B'], note='N1 wildcard contamination keeps separator truth in_sample; no paired separator headline or improvement claim.')
    m.dump(path.with_name('n1_v1_w1_manifest.json'), manifest)
    receipt = art/'N1W1F2_RECEIPT.json'; m.dump(receipt, manifest)
    receipt.with_suffix('.sha256').write_text(m.sha(receipt)+'  '+receipt.name+'\n')
    return manifest


if __name__ == '__main__':
    result = build()
    print(json.dumps({k:v for k,v in result.items() if k not in ('contexts','inputs','evidence','confirmed_slots')}, indent=2))
