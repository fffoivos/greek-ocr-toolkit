"""Option 2 lower bound: a context-free diacritic restorer = for each word, strip the marks and take the most frequent
attested form in the regime lexicon. Scored on the HUMAN text of the three-way lines (proofread, held out of the lexicons)
and on the census errors / correct Google words. A context model can only improve on the ambiguous keys."""
import json
from collections import Counter
from greekocr.labelfix.candidates import pair_tokens
from greekocr.labelfix.lexicon import load_all
from greekocr.labelfix.text import lexicon_key, lower_word, nfd, strip_marks, tokenize, has_greek, is_all_caps
from greekocr.labelfix.validate import TOOLKIT, load_three_way
import sys
sys.path.insert(0, str(TOOLKIT))
from greekocr.labelfix.reach import final_grave_form

lex = load_all(TOOLKIT / 'docs/labelfix/lexicons')
reg = {json.loads(l)['line_id']: json.loads(l)['regime'] for l in open(TOOLKIT / 'docs/labelfix/validation_lines_s0.jsonl')}
def norm(w):  # positional grave is the grave stage's business: compare with final grave folded to acute
    w = lower_word(nfd(w))
    return w.replace('̀', '́')
def restore(word, L):
    v = L.variants(word)
    if not v:
        return None, 0, 0
    tot = sum(v.values())
    best = max(v, key=v.get)
    return best, v[best] / tot, len([f for f, n in v.items() if n >= 0.1 * v[best]])
stats = Counter()
per_class = Counter()
err_rows = {(json.loads(l)['line_id'], json.loads(l)['word_index']): json.loads(l) for l in open(TOOLKIT / 'docs/labelfix/spellcheck/reach_s0.jsonl')}
out = {}
for l in load_three_way(0):
    r = reg.get(l['line_id'], 'mono')
    if r == 'mono':
        continue
    L = lex[r]
    gh = {g.index: h for g, h in pair_tokens(l['google'], l['human'])}
    for g in tokenize(l['google']):
        h = gh.get(g.index)
        if not g.core or h is None or not has_greek(g.core) or is_all_caps(g.core):
            continue
        if strip_marks(nfd(g.core)).lower() != strip_marks(nfd(h.core)).lower():
            continue
        best, share, nalt = restore(h.core, L)
        right = best is not None and norm(best) == norm(h.core)
        stats['words'] += 1
        stats['covered'] += best is not None
        stats['right'] += right
        stats['ambiguous'] += nalt >= 2
        stats['ambiguous_right'] += right and nalt >= 2
        key = (l['line_id'], g.index)
        if g.core == h.core:
            stats['google_correct'] += 1
            if best is not None and norm(best) != norm(g.core):
                stats['would_change_correct'] += 1
        elif key in err_rows:
            e = err_rows[key]
            per_class[(e['stage'], 'n')] += 1
            per_class[(e['stage'], 'unigram_fixes')] += right
            per_class[(e['stage'], 'ambiguous')] += nalt >= 2
            out[f"{key[0]}|{key[1]}"] = best
print(json.dumps(stats))
for s in ('guard','constraint','grave','grave_line_end','lex_unique','lex_compete','lex_miss','real_word','human_unatt','human_error'):
    print(s, per_class[(s,'n')], 'unigram=human', per_class[(s,'unigram_fixes')], 'ambiguous key', per_class[(s,'ambiguous')])
json.dump(out, open(sys.argv[1], 'w'), ensure_ascii=False)
