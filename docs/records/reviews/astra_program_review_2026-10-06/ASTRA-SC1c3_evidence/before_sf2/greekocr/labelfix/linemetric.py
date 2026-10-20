"""Whole-line letter-slot mark scoring against explicit PRINT truth.

Cached CTC spans locate input letters only. Unknown words/ambiguous slots are
excluded and counted, never filled from the recogniser or Google prefills.
"""
from collections import Counter
from .candidates import pair_tokens
from .ctc_align import transfer_alignment
from .spellink import locate
from .text import clusters, nfd, tokenize
from .markshape import mark_class

KINDS = ('accent', 'breathing', 'compound', 'subscript', 'dialytika', 'apostrophe')


def printed_words(line, adjudicated):
    gm = {g.index: m for g, m in pair_tokens(line['google'], line['model'])}
    gh = {g.index: h for g, h in pair_tokens(line['google'], line['human'])}
    out = {}
    for g in tokenize(line['google']):
        key = f"{line['line_id']}|{g.index}"
        if key in adjudicated:
            p = adjudicated[key]['printed']
            ts = tokenize(nfd(p)) if p is not None else []
            out[g.index] = ts[0].core if len(ts) == 1 else None
        else:
            h, m = gh.get(g.index), gm.get(g.index)
            out[g.index] = h.core if h and m and g.core == h.core == m.core else None
    return out


def printed_line(line, adjudicated):
    """Display known printed tokens including their punctuation; never Google prefill."""
    pw = printed_words(line, adjudicated)
    gh = {g.index:h for g,h in pair_tokens(line['google'],line['human'])}
    out = []
    for t in tokenize(line['google']):
        key = f"{line['line_id']}|{t.index}"
        if key in adjudicated:
            out.append(adjudicated[key]['printed'] or '[UNKNOWN]')
        elif pw.get(t.index) is not None and gh.get(t.index) is not None:
            out.append(gh[t.index].text)
        else:
            out.append('[UNKNOWN]')
    return ' '.join(out)


def mark_set(cls):
    """Compound is one semantic kind; its accent/breathing identities stay exact."""
    if not cls or cls == 'none':
        return set()
    parts = set(cls.split('+'))
    out = set()
    acc = parts & {'acute', 'grave', 'circumflex'}
    breath = parts & {'psili', 'dasia'}
    if acc and breath:
        out.add(('compound', '+'.join(sorted(acc | breath))))
    else:
        out.update(('accent', a) for a in acc)
        out.update(('breathing', b) for b in breath)
    out.update((p, p) for p in parts & {'subscript', 'dialytika', 'apostrophe'})
    return out


def slot_mapping(line, al, ink, adjudicated):
    """Map all letter components sorted by x to input characters through CTC.

    Competing character owners are unknown. Recognition differences do not gate
    candidates; locate uses proportional spans when the recogniser differs.
    """
    al = transfer_alignment(line['model'], al)
    letters = sorted((c for c in ink.components if c.role == 'letter'), key=lambda c:c.x0)
    gm = {g.index:m for g,m in pair_tokens(line['google'], line['model'])}
    pw = printed_words(line, adjudicated)
    owners = [[] for _ in letters]
    for g in tokenize(line['google']):
        gc = clusters(g.core)
        pc = clusters(pw[g.index]) if pw.get(g.index) is not None else []
        same = len(gc) == len(pc) and all(a.base == b.base for a,b in zip(gc,pc))
        for j, cl in enumerate(gc):
            if not cl.base.isalpha():
                continue
            loc = locate(g, gm.get(g.index), al, j)
            if loc is None or not letters:
                continue
            b0,b1 = loc[-2:]
            ovs = [max(0,min(c.x1,b1)-max(c.x0,b0)) for c in letters]
            k = max(range(len(letters)), key=lambda i:ovs[i])
            if ovs[k] <= 0:
                continue
            marks = mark_class(pc[j].marks) if same else None
            truth = mark_set(marks) if marks is not None else None
            # Apostrophe is printed punctuation after the consonant, not breathing.
            key = f"{line['line_id']}|{g.index}"
            if key in adjudicated:
                pt = tokenize(nfd(adjudicated[key]['printed'] or ''))
                trail = pt[0].trail if len(pt) == 1 else ''
            else:
                ht = {gg.index:hh for gg,hh in pair_tokens(line['google'],line['human'])}.get(g.index)
                trail = ht.trail if ht is not None else ''
            if truth is not None and j == len(gc)-1 and any(a in trail for a in "'’ʼ᾽"):
                truth.add(('apostrophe','apostrophe'))
            owners[k].append(dict(truth_reason='unsupported_printed_marks' if same and marks is None else None, base=cl.base, word=g.index, char=j, truth=truth,
                                  word_final=j == len(gc)-1, locator_span=[b0,b1]))
    result=[]
    for c, os in zip(letters,owners):
        d = os[0] if len(os)==1 else dict(base='',word=None,char=None,truth=None,word_final=False)
        result.append(dict(d, component=c))
    return result


def score_slots(slots):
    total=Counter(); by={k:Counter() for k in KINDS}
    for s in slots:
        truth=s['truth']
        if truth is None:
            total['unknown_slots']+=1
            continue
        total['known_slots']+=1
        unknown=set(s.get('unknown_kinds',()))
        for kind in unknown:
            total['unknown_'+kind+'_slots']+=1
        truth={tuple(x) for x in truth if x[0] not in unknown}; detected={tuple(x) for x in s['detected'] if x[0] not in unknown}
        for counter, t, d in [(total,truth,detected)]+[(by[k],{x for x in truth if x[0]==k},{x for x in detected if x[0]==k}) for k in KINDS]:
            counter['tp']+=len(t&d);counter['fp']+=len(d-t);counter['fn']+=len(t-d)
    return dict(total=summary(total), by_kind={k:summary(v) for k,v in by.items()})


def summary(c):
    c=dict(c);tp,fp,fn=(c.get(x,0) for x in ('tp','fp','fn'))
    p=tp/(tp+fp) if tp+fp else None;r=tp/(tp+fn) if tp+fn else None
    return dict(c,precision=p,recall=r,f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None)


def pooled(lines):
    total=Counter();by={k:Counter() for k in KINDS}
    for l in lines:
        for k,v in l['total'].items():
            if isinstance(v,int):total[k]+=v
        for kind,c in l['by_kind'].items():
            for k,v in c.items():
                if isinstance(v,int):by[kind][k]+=v
    return dict(total=summary(total),by_kind={k:summary(v) for k,v in by.items()})
