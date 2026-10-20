"""Option 1 (image only): read every mark-bearing cluster of every Google word on the three-way lines with the
existing detector + mark-shape classifier; record Google's class, the human class, the reading, abstentions."""
import json, sys, time
from PIL import Image
from greekocr.labelfix.candidates import pair_tokens
from greekocr.labelfix.ctc_align import transfer_alignment
from greekocr.labelfix.ink import analyse, mark_evidence
from greekocr.labelfix.markshape import features, load_model, mark_class
from greekocr.labelfix.sheet import load_alignments, crop_key
from greekocr.labelfix.spellink import locate
from greekocr.labelfix.text import MARK_BEARERS, clusters, nfd, strip_marks, tokenize
from greekocr.labelfix.validate import DEV_BOOKS, TOOLKIT, load_three_way

seed = 0
model = load_model(TOOLKIT / 'docs/labelfix/markshape_model.json')
reg = {json.loads(l)['line_id']: json.loads(l)['regime'] for l in open(TOOLKIT / f'docs/labelfix/validation_lines_s{seed}.jsonl')}
A = load_alignments(TOOLKIT / f'.cache/labelfix/align_s{seed}.jsonl')
out = open(sys.argv[1], 'w')
t0 = time.time()
for n, l in enumerate(load_three_way(seed)):
    if reg.get(l['line_id'], 'mono') == 'mono':
        continue
    al = A.get(crop_key(l['crop']))
    if al is None:
        continue
    if nfd(al.prediction) != l['model']:
        al = transfer_alignment(l['model'], al)
    ink = analyse(Image.open(l['crop']))
    gh = {g.index: h for g, h in pair_tokens(l['google'], l['human'])}
    gm = {g.index: m for g, m in pair_tokens(l['google'], l['model'])}
    for g in tokenize(l['google']):
        h = gh.get(g.index)
        if not g.core or h is None or strip_marks(nfd(g.core)) != strip_marks(nfd(h.core)):
            continue
        cg, ch = clusters(g.core), clusters(h.core)
        if len(cg) != len(ch):
            continue
        for i, (a, b) in enumerate(zip(cg, ch)):
            if a.base not in MARK_BEARERS:
                continue
            rec = dict(line_id=l['line_id'], doc=l['doc'], dev=l['doc'] in DEV_BOOKS, w=g.index, c=i,
                       word_err=g.core != h.core, g=mark_class(a.marks), h=mark_class(b.marks),
                       gword=g.core, hword=h.core, is_last=g.index == len(tokenize(l['google'])) - 1, trail=g.trail)
            loc = locate(g, gm.get(g.index), al, i)
            if loc is None:
                rec['abstain'] = 'unpaired'
            else:
                how, x0, x1, bx0, bx1 = loc
                ev = mark_evidence(ink, x0, x1, core_x0=bx0, core_x1=bx1)
                ab = None
                if ev.body_source != 'letter' or ev.n_letters_in_span != 1:
                    ab = 'localisation'
                elif ev.neighbour_marks:
                    ab = 'neighbour'
                elif any(b.faint for b in ev.above + ev.below):
                    ab = 'faint'
                elif ev.clipped_top or ev.clipped_bottom:
                    ab = 'clipped'
                pred, prob, dist = model.predict(features(ev))
                rec.update(abstain=ab, pred=pred, prob=round(prob, 5), p_g=round(dist.get(rec['g'] or '', 0.0), 5),
                           p_h=round(dist.get(rec['h'] or '', 0.0), 5), n_above=ev.n_above, n_below=len(ev.below), locator=how)
            out.write(json.dumps(rec, ensure_ascii=False) + '\n')
    if n % 200 == 0:
        print(n, round(time.time() - t0), flush=True)
out.close()
print('done', round(time.time() - t0))
