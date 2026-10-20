"""Build the two SHEET-1 demos from saved local evidence; no tool or network calls.

Run from the worktree root with the main checkout's Python. Gate geometry and
wording follow reference_scratch/build_gate_sheet.py; HTML uses only the package.
"""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input

import collections
import hashlib
import json
from pathlib import Path

from PIL import Image
from greekocr.adjudicate.owner_sheet import render

ROOT = Path(__file__).resolve().parents[2]
PROJECTS = Path.home() / 'Projects'
SEG = PROJECTS / 'greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1'
RU = PROJECTS / 'greek-ocr-toolkit-secondary/artifacts/ru1'
PARENT_ROOT = PROJECTS / 'greek-ocr-toolkit'
OUT = ROOT / 'docs/B_training_data/d_review/demo'


def records(path):
    with path.open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def sha(path):
    return hashlib.sha256(_data_input(path).read_bytes()).hexdigest()


# Saved measurement coordinates -> saved crop coordinates, exactly as reference.
def inv(frame):
    (a,b,c),(d,e,f),_=frame['source_to_measurement']; det=a*e-b*d
    return [[e/det,-b/det,(b*f-c*e)/det],[-d/det,a/det,(c*d-a*f)/det]]

def pt(M,x,y): return M[0][0]*x+M[0][1]*y+M[0][2], M[1][0]*x+M[1][1]*y+M[1][2]

def rect(M,b,cls):
    xs,ys=zip(pt(M,b[0],b[1]),pt(M,b[2],b[3])); x0,x1=min(xs),max(xs); y0,y1=min(ys),max(ys)
    return f'<rect class="{cls}" x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}"/>'

def poly(M,pts,cls,close=False):
    return f'<{"polygon" if close else "polyline"} class="{cls}" points="'+' '.join('%.1f,%.1f'%pt(M,x,y) for x,y in pts)+'"/>'

def overlay(a,w,h):
    e=a['evidence']; M=inv(a['frame']); out=[]; W,Hh=a['frame']['width'],a['frame']['height']
    for d in e.get('detected_rows',[]):
        if d['votes']<=0: continue
        c=d['curves']
        if d['side']=='main': out.append(poly(M,c['ascender'],'asc')); out.append(poly(M,c['base'],'base'))
        else: out.append(poly(M,c['base'],'nbase'))
    for L in e['lines']:
        if L['side']=='main': continue
        for g in L['word_groups']: out.append(rect(M,g['bbox'],'wwhole' if g['whole'] else 'wpart'))
    m=e['gate']['main_cut']
    for s in m['cut_spans']:
        y=0.5 if s['edge']=='top' else Hh-0.5
        out.append(poly(M,[[s['x0'],y],[s['x1'],y]],'cutspan' if s['min_visible']<.6 else 'cutspan2'))
    for c in m['crossings']:
        if 'leaves' in c.get('meaning',''):
            y=0.5 if c['edge']=='top' else Hh-0.5; x,yy=pt(M,c['x'],y)
            out.append(f'<circle class="cross" cx="{x:.1f}" cy="{yy:.1f}" r="5"/>')
    bx=e.get('box_evidence') or {}
    if bx.get('bbox'): out.append(rect(M,bx['bbox'],'tbox'))
    if bx.get('row_frame'): out.append(poly(M,bx['row_frame']['corners'],'rframe',close=True))
    return f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none">'+''.join(out)+'</svg>'

def inventory(e):
    bits=[]
    for L in e['lines']:
        tag='complete' if L['complete'] else f"{int(round(L['visible']*100))}% visible"
        if L['side']=='main': bits.append(f"MAIN: {L['bodies']} letters, {tag}, covers {int(round(L['coverage']*100))}%")
        else: bits.append(f"{L['side'].upper()}: {tag}, {L['bodies']} letter bodies, {L['whole_words']} whole / {L['cutoff_words']} cut-off words")
    return ' | '.join(bits) if bits else 'no rows detected'

def cutinfo(m):
    bits=['diagnostics only (no verdict): '+(f"skew {m['angle_deg']:+.1f}°" if m.get('angle_deg') is not None else 'no main row')]
    if m['baseline_exit']: bits.append('baseline LEAVES the crop at x='+', '.join(str(int(c['x'])) for c in m['crossings'] if 'leaves' in c.get('meaning','')))
    if m['low_visibility_span']: bits.append('letter bodies <60% visible over '+', '.join(f"{s['x0']}–{s['x1']} ({s['edge']}, {int(s['min_visible']*100)}%)" for s in m['cut_spans'] if s['min_visible']<.6))
    if m['cut_letters']: bits.append(f"{len(m['cut_letters'])} letters touch an edge")
    return ' | '.join(bits)

def decision_cards():
    owner = {r['line_id']: r for r in records(SEG / 'scored/owner_rows.jsonl')}
    replay = records(SEG / 'gate2/replay_segeval1.jsonl')
    cards = []
    for r in replay:
        a = r['after']; e = a['evidence']; g = e['gate']; lid = r['line_id']
        st = r['owner_standard_state']; v = r['verdict_08']
        # Preserve the reference sheet's saved owner-standard interpretation.
        maxvis = max([line['visible'] for line in e['lines'] if line['side'] != 'main'] or [0.0])
        faults = list(r['owner_faults']); nwnote = ''
        if 'neighbour_whole_word' in faults and maxvis < 0.9:
            faults.remove('neighbour_whole_word')
            nwnote = (f' (reader saw readable neighbour words, but the other rows are at most {int(maxvis*100)}% visible'
                      ' → cut-off words, not whole, under your 100% rule)')
            if not faults and st == 'faulty': st = 'fine'
        group = ('un' if st == 'unresolved' else 'unc' if v == 'UNCERTAIN' else
                 'fp' if v == 'DROP' and st == 'fine' else 'tp' if v == 'DROP' else 'fn' if st == 'faulty' else 'ok')
        crop = SEG / owner[lid]['crop']
        assert sha(crop) == a['binding']['crop_sha256'], lid
        with Image.open(crop) as image: w, h = image.size
        ans = owner[lid]['reader_answer']
        bx = e.get('box_evidence') or {}; rf = bx.get('row_frame') or {}; p = bx.get('prediction') or {}
        pad = (e.get('padding_evidence') or {}).get('total_padding_line_heights')
        length = ('not measured (gate failed)' if g['verdict'] != 'PASS' else
                  (f"OCR chars {e['characters']} vs expected {p['expected']:.1f} → ratio {(e['characters']+1)/(p['expected']+1):.2f} (0.5–1.5) | padding {pad:.2f} de-skewed heights (max 1.5) | de-skewed box {rf.get('length',0):.0f}×{rf.get('height',0):.1f} px, upright height {bx['bbox'][3]-bx['bbox'][1]}"
                   if p.get('expected') is not None else 'length unavailable'))
        rows = [dict(name='Google', text=owner[lid]['google_text']), dict(name='Lines found', text=inventory(e)),
                dict(name='Main line cut?', text=cutinfo(g['main_cut'])),
                dict(name='Gate', text=f"{g['verdict']}: {g['reason']} (whole neighbour words {g['whole_words']}, cut-off {g['cutoff_words']}, complete other rows {len(g['complete_rows'])})"),
                dict(name='Length', text=length),
                dict(name='Text vs crop', text='crop_ok ' + ans.get('crop_ok', '?') + ' | errors: ' +
                     (', '.join(ans.get('errors', [])) or 'none') + (' | ' + ans['detail'] if ans.get('detail') else '')),
                dict(name='Owner standard', text=('FAULT: ' + ', '.join(faults) if faults else 'unresolved' if st == 'unresolved' else 'fine') +
                     nwnote + (' — ' + ans['segmentation_detail'] if ans.get('segmentation_detail') else ''))]
        previous = r['previous']  # the saved 0.7 record, not 0.6 (r['before'])
        assert previous['tool_version'] == '0.7' and previous['verdict'] == r['verdict_07']
        cards.append(dict(line_id=lid, image=crop, group=group, rows=rows, tool_verdict=v,
                          versions=[dict(name='0.7', verdict=r['verdict_07'], text=previous['reason']),
                                    dict(name='0.8', verdict=v, text=a['reason'])],
                          overlay_svg=overlay(a, w, h), display={},
                          tags=[dict(text=lid.split('--')[0].split('-p0')[0]),
                                dict(text=v, **{'class': 'ok' if v == 'KEEP' else 'bad' if v == 'DROP' else 'warn'}),
                                dict(text=f'{w}×{h} px')],
                          data={'crop-sha256': sha(crop)}))
    order = [('fp', 'DROPPED but fine under your standard = false rejects'),
             ('fn', 'KEPT but faulty = misses'), ('unc', 'UNCERTAIN = pipeline HOLD'),
             ('tp', 'DROPPED and faulty = correct drops'), ('un', 'reader unresolved'), ('ok', 'KEPT and fine')]
    # First two available per reference group, then a further round if necessary.
    selected = []
    for index in range(len(cards)):
        for group, _ in order:
            bucket = [c for c in cards if c['group'] == group]
            if index < len(bucket) and len(selected) < 12: selected.append(bucket[index])
        if len(selected) == 12: break
    counts = collections.Counter(c['group'] for c in selected)
    groups = [dict(id=g, heading=f'{label} ({counts[g]} shown)') for g, label in order if counts[g]]
    return selected, dict(title='Segmentation 0.8 — gate2 replay, 12-line demo', variant='decision', sheet_prefix='gate', groups=groups,
        intro=('Local demo: 12 saved gate2 replay lines, sampled across the reference groups in their original order. '
               'The same crop, Google text, measurements, diagnostics, reader observations and owner-standard rows as the gate reference; '
               'the combined version row is split into saved 0.7 and 0.8 rows. This is a presentation replay, with no new tool evaluation.\n'
               'Standard: more than two whole neighbour words or a second complete line; de-skewed length vs Google (0.5–1.5); '
               'crop height at most upright box height + 1.5 de-skewed heights. Cut measurements are diagnostics only. '
               'Full 150-line reference scores: 0.8 false rejects 18, misses 14, HOLD 11; these are not scores of this demo.\n'
               'Overlay: blue upright box; magenta de-skewed box; green main row; orange dashed other rows; red whole neighbour word; '
               'grey dashed cut-off word; orange edge bars / red dots cut diagnostics.'))


def changed_segments(text, offsets):
    result = []; start = 0
    for offset in sorted(offsets):
        if offset > start: result.append(dict(text=text[start:offset]))
        result.append(dict(text=text[offset:offset+1], kind='changed'))
        start = offset + 1
    if start < len(text): result.append(dict(text=text[start:]))
    return result


def correction_cards():
    edits = [r for r in records(RU / 'ru1_v3_edits.jsonl') if r['edits']][:12]
    manifest = json.loads((RU / 'ru1_v3_edits_manifest.json').read_text())
    parent_path = Path(manifest['parent']['path'])
    assert sha(parent_path) == manifest['parent']['sha256']
    assert sha(RU / 'ru1_v3_edits.jsonl') == manifest['output']['sha256']
    wanted = {r['id'] for r in edits}; parents = {}
    with parent_path.open() as stream:
        for line in stream:
            row = json.loads(line)
            if row['id'] in wanted: parents[row['id']] = row
    cards = []
    for r in edits:
        parent = parents[r['id']]
        assert parent['label'] == r['label_parent']
        crop = PARENT_ROOT / parent['crop']
        # Use only the exact parent-referenced raster; no reconstructed crops.
        assert crop.is_file(), crop
        offsets = [edit['offset'] for edit in r['edits']]
        assert all(r['label_parent'][i] == 'ь' and r['label'][i] == 'ъ' for i in offsets)
        cards.append(dict(line_id=r['id'], image=crop, tool_verdict='UNCERTAIN' if r['holds'] else 'CHANGED',
                          rows=[dict(name='Google', text=r['label_parent']),
                                dict(name='Saved edits', text='; '.join(f"offset {e['offset']}: ь → ъ ({e['reason']})" for e in r['edits']))],
                          versions=[dict(name='Before', text=r['label_parent'], segments=changed_segments(r['label_parent'], offsets)),
                                    dict(name='After', verdict='UNCERTAIN' if r['holds'] else 'CHANGED', text=r['label'],
                                         segments=changed_segments(r['label'], offsets))],
                          printed='', tags=[dict(text='RU1 v3'), dict(text=parent['source']), dict(text=parent['split'])],
                          data={'crop-sha256': sha(crop)}))
    return cards, dict(title='RU1 v3 — 12 saved correction lines', variant='correction', sheet_prefix='sheet1-ru1',
        intro=('Local demo from greek-ocr-toolkit-secondary/artifacts/ru1/ru1_v3_edits.jsonl: the first 12 edited lines in file order. '
               'Native crops are local and resolved through the SHA-bound google_raw_v2_import parent and its crop paths; sf7 was not used. '
               'Google shows that exact parent label. Highlighted positions are saved ь → ъ changes, with no new readings or tool calls. '
               'Printed starts blank for the owner to supply the visible truth. No target geometry is recorded in this edit file, so no slot overlay is invented. '
               'The source manifest records 426 edited rows, 451 edits and 256 hold rows across 680 sparse records; these are source counts, not demo scores.'))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, build in [('decision_gate2.html', decision_cards), ('correction_ru1.html', correction_cards)]:
        cards, spec = build()
        assert len(cards) == 12
        target = OUT / name
        target.write_text(render(cards, spec))
        print(f'{target.relative_to(ROOT)}: {len(cards)} cards, {target.stat().st_size} bytes, SHA256 {sha(target)}')


if __name__ == '__main__':
    main()
