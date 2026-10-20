"""Offline frozen label-quality scoring. See docs/labelfix/lqb/SCORE_v1.md.

No recognition, adjudication, network access or writes to source worktrees.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import unicodedata as ud
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / 'docs/labelfix/lqb'
PROJECTS = Path.home() / 'Projects'
CLASSES = ('marks', 'letters', 'n1_separator', 'ru1_yer', 'ru2_yat', 'superscript', 'dash', 'lunate', 'lookalike', 'capitals', 'crop')
HEADS = ('breathing', 'accent', 'dialytika', 'subscript')
GROUPS = CLASSES + tuple('marks/'+h for h in HEADS)

def in_class(item, cls):
    return item['class'] == cls or (cls.startswith('marks/') and item['class']=='marks' and item['slot']['head']==cls.split('/')[1])


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()


def rows(path):
    import gzip
    with (gzip.open(path, 'rt') if str(path).endswith('.gz') else Path(path).open()) as f:
        for line in f:
            if line.strip(): yield json.loads(line)


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def clusters(text):
    result = []
    for c in ud.normalize('NFD', text):
        if ud.combining(c) and result: result[-1] += c
        else: result.append(c)
    return result


def letters(text): return [c for c in clusters(text) if c[0].isalpha()]


def factors(text):
    marks = ud.normalize('NFD', text)
    return [2 if '\u0314' in marks else 1 if '\u0313' in marks else 0,
            3 if '\u0342' in marks else 2 if '\u0300' in marks else 1 if '\u0301' in marks else 0,
            int('\u0308' in marks), int('\u0345' in marks)]


@lru_cache(None)
def union_scorer():
    # Imported source remains read-only, including __pycache__.
    sys.dont_write_bytecode = True
    peer = PROJECTS / 'greek-ocr-toolkit-spellcheck-r2prep'
    sys.path.append(str(peer)) if str(peer) not in sys.path else None
    spec = importlib.util.spec_from_file_location('_lqb_r2_score', peer / 'scripts/labelfix/r2_score.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache(100000)
def union_errors(printed, prediction):
    truth = letters(printed)
    source = [dict(line_id='toy', doc='toy', print_slots=[dict(id=str(i), base=c[0], targets=factors(c), unknown=[]) for i,c in enumerate(truth)])]
    pred = [dict(line_id='toy', start=i, base=c[0], factors=factors(c)) for i,c in enumerate(letters(prediction))]
    records = union_scorer().union_records(source, pred)
    return {int(r['id']): [int(a != b) for a,b in zip(r['truth'],r['prediction'])] for r in records if not r['inserted_prediction']}


@lru_cache(None)
def stat_module():
    sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location('_lqb_adjudicate_score',PROJECTS/'greek-ocr-toolkit-cleanup/greekocr/adjudicate/score.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def edit_distance(a, b):
    last = list(range(len(b)+1))
    for i, x in enumerate(a, 1):
        curr = [i]
        for j, y in enumerate(b, 1): curr.append(min(curr[-1]+1, last[j]+1, last[j-1]+(x!=y)))
        last = curr
    return last[-1]


def gap_class(glyph):
    if glyph and glyph.isspace():return 'space'
    glyph = glyph.strip()
    return {'.':'baseline dot', '·':'raised dot', '·':'raised dot', ',':'comma', '-':'hyphen', '‐':'hyphen', '–':'en dash', '—':'em dash', '':'nothing'}.get(glyph, 'other')


def sample_used(item, version, trained_on=()):
    return (version in item['used_by']
            or (version.lower().startswith('n1') and 'n1_*' in item['used_by'])
            or item.get('in_training') in trained_on)


def training_arms(name, registry):
    """Explicit training lineage, independent of label/admission version names."""
    arms=set();seen=set()
    while name:
        if name in seen:raise ValueError('cyclic version lineage: '+name)
        seen.add(name);v=registry['versions'][name]
        declared=v.get('trained_on', [])
        if not isinstance(declared,list) or any(not isinstance(x,str) or not x for x in declared):
            raise ValueError('trained_on must be a list of training arms: '+name)
        arms.update(declared);name=v.get('parent')
    return arms


def load_truth(truth, flags=None):
    """Apply line-level training flags in memory; never rewrite frozen truth."""
    truth=Path(truth);items=list(rows(truth))
    path=Path(flags) if flags is not None else truth.with_name(truth.stem+'_flags.jsonl')
    if flags is None and not path.exists() and truth.resolve() != (DEFAULT/'truth_v1.jsonl').resolve():
        return items,None
    known={r['line_id'] for r in items};byline={}
    for r in rows(path):
        if (set(r) != {'line_id','in_training'} or r['line_id'] not in known
                or not isinstance(r['in_training'],str) or not r['in_training']):
            raise ValueError('invalid truth flag: '+repr(r))
        if r['line_id'] in byline:raise ValueError('duplicate truth flag: '+r['line_id'])
        byline[r['line_id']]=r['in_training']
    for r in items:
        if r['line_id'] in byline:
            arm=byline[r['line_id']]
            if r.get('in_training',arm)!=arm:raise ValueError('conflicting truth flag: '+r['line_id'])
            r['in_training']=arm
    return items,sha256(path)


def error(item, text):
    """Return (errors, opportunities) or None for unavailable measurement."""
    c, s = item['class'], item.get('slot')
    if c == 'crop': return None  # Labels cannot measure physical crop correctness.
    if c == 'marks':
        if s.get('kind') == 'scoped_mark':
            pred = scoped_bases(item['context']['reference'], text, s['start'], s['end'])
            if pred is None:return None
            e = union_errors(item['context']['printed_word'], pred)
            return e[s['letter']][HEADS.index(s['head'])], 1
        if s.get('kind') == 'word_letter':
            words = text.split()
            if s['word'] >= len(words): pred = ''
            else: pred = words[s['word']]
            e = union_errors(item['context']['printed_word'], pred)
            return e[s['letter']][HEADS.index(s['head'])], 1
        ls = letters(text)
        pred = factors(ls[s['index']]) if s['index'] < len(ls) else [0]*4
        return int(pred[HEADS.index(s['head'])] != item['target']), 1
    if c == 'n1_separator':
        # The reference is the exact label on which these gap offsets were located.
        ref = item['context']['reference']
        a,b = item['context']['start'],item['context']['end']
        from difflib import SequenceMatcher
        # Anchor a gap to its two neighboring digit characters, so an
        # insertion into an originally empty gap is scored, not overlooked.
        opcodes=SequenceMatcher(None, ref, text, autojunk=False).get_opcodes()
        mapping={i:k+i-a for tag,a,b,k,l in opcodes if tag=='equal' for i in range(a,b)}
        if a and b<len(ref) and ref[a-1].isdigit() and ref[b].isdigit():
            left,right=mapping.get(a-1),mapping.get(b)
            if left is None or right is None:return 1,1
            x,y=left+1,right
        else:
            def boundary(pos):
                for tag,i,j,k,l in opcodes:
                    if tag=='equal' and i <= pos <= j:return k+pos-i
                    if i==pos:return k
                    if j==pos:return l
                return None
            x,y=boundary(a),boundary(b)
            if x is None or y is None:return 1,1
        predicted=gap_class(text[x:y]);target=item['printed']
        right=predicted in ('hyphen','en dash','em dash') if target=='any dash' else predicted==target
        return int(not right),1
    if s and s.get('kind') == 'offset':
        offset=s['offset']; pred=text[offset:offset+len(item['printed'])]
        return int(ud.normalize('NFC',pred)!=ud.normalize('NFC',item['printed'])),1
    if s and s.get('kind') == 'letter_index':
        ls=letters(text);pred=ls[s['index']] if s['index']<len(ls) else ''
        return int(ud.normalize('NFC',pred)!=ud.normalize('NFC',item['printed'])),1
    if c == 'letters':
        # Letter edit distance; mark differences belong to the four mark heads.
        if s and s.get('kind')=='base_span':
            ref=item['context']['reference'];hyp=''.join(x[0] for x in letters(text))
            from difflib import SequenceMatcher
            bounds={}
            for tag,a,b,c,d in SequenceMatcher(None,ref,hyp,autojunk=False).get_opcodes():
                if tag=='equal':
                    bounds.update({i:c+i-a for i in range(a,b+1)})
                else:bounds.setdefault(a,c);bounds[b]=d
            if s['start'] not in bounds or s['end'] not in bounds:return None
            text=hyp[bounds[s['start']]:bounds[s['end']]]
        if s and s.get('kind')=='word':
            ws=text.split();text=ws[s['word']] if s['word']<len(ws) else ''
        a=''.join(x[0] for x in letters(item['printed']))
        b=''.join(x[0] for x in letters(text))
        return edit_distance(a,b),max(len(a),len(b),1)
    return int(ud.normalize('NFC',text)!=ud.normalize('NFC',item['printed'])),1


@lru_cache(100000)
def scoped_bases(reference, text, start, end):
    """Map a certified partial word group through mark-blind line alignment.

    Reference offsets count letters, not recogniser words or Unicode codepoints.
    Return the original predicted clusters so their mark identities survive.
    """
    from difflib import SequenceMatcher
    ls=letters(text);hyp=''.join(x[0] for x in ls);bounds={}
    for tag,a,b,c,d in SequenceMatcher(None,reference,hyp,autojunk=False).get_opcodes():
        if tag=='equal':bounds.update({i:c+i-a for i in range(a,b+1)})
        else:bounds.setdefault(a,c);bounds[b]=d
    if start not in bounds or end not in bounds:return None
    return ''.join(ls[bounds[start]:bounds[end]])


def bootstrap_delta(pairs, seed=20261017, replicates=4000):
    """Paired error-rate difference B-A; resample whole documents, same pairs.

    Signed differences cannot use adjudicate.score.score's nonnegative
    numerator contract. Percentile interval, no unclustered fallback.
    """
    if not pairs: return dict(items=0, delta_per_100=None, ci95=None, documents=0, seed=seed, replicates=replicates)
    bydoc=defaultdict(lambda:np.zeros(4))
    for doc,ae,an,be,bn in pairs: bydoc[doc]+=np.array([ae,an,be,bn])
    m=np.array([bydoc[d] for d in sorted(bydoc)])
    total=m.sum(0); delta=100*(total[2]/total[3]-total[0]/total[1])
    rng=np.random.default_rng(seed)
    # Batched to avoid a huge replicates x documents matrix.
    estimates=[]
    for start in range(0,replicates,128):
        take=rng.integers(len(m),size=(min(128,replicates-start),len(m)))
        t=m[take].sum(1)
        estimates.extend(100*(t[:,2]/t[:,3]-t[:,0]/t[:,1]))
    return dict(items=len(pairs), delta_per_100=float(delta), ci95=np.quantile(estimates,[.025,.975]).tolist(), documents=len(m), seed=seed, replicates=replicates)


def load_version(name, registry, wanted=None, _cache=None):
    cache={} if _cache is None else _cache
    if name in cache:return cache[name]
    v=registry['versions'][name]
    if v.get('status')=='remote_unfetched':return {}
    p=Path(v['path']).expanduser()
    if sha256(p)!=v['sha256']:raise ValueError('version sha256 mismatch: '+name)
    if v.get('overlay') and 'parent_splits' in v:
        # A sparse held-out overlay inherits only its explicitly named RAW
        # splits. Existing train overlays keep their original parent population.
        splits=v['parent_splits'];parent=registry['versions'][v['parent']]
        if not isinstance(splits,list) or not splits or len(set(splits))!=len(splits):
            raise ValueError('invalid parent_splits: '+name)
        base={};seen=set()
        for split in splits:
            spec=parent['splits'][split];source=Path(spec['path']).expanduser()
            if sha256(source)!=spec['sha256']:raise ValueError('parent split sha256 mismatch: '+name)
            for r in rows(source):
                lid=r[spec['id_field']]
                if lid in seen:raise ValueError('duplicate parent split id: '+lid)
                seen.add(lid)
                if wanted is None or lid in wanted:base[lid]=r[spec['text_field']]
    else:
        base=dict(load_version(v['parent'],registry,wanted,cache)) if v.get('overlay') else {}
    for r in rows(p):
        lid=r[v.get('id_field','id')]
        if v.get('overlay') and 'parent_splits' in v and lid not in seen:
            raise ValueError('overlay id outside parent splits: '+lid)
        if wanted is None or lid in wanted:
            if v.get('inherit_label'):
                # Admissions restrict population; they do not widen the parent.
                if lid not in cache.setdefault('_parent_'+name,load_version(v['parent'],registry,wanted,cache)):continue
                base[lid]=cache['_parent_'+name][lid]
            else:base[lid]=r[v['text_field']]
    for extra in v.get('supplemental_sources', []):
        path=Path(extra['path'])
        if sha256(path)!=extra['sha256']:raise ValueError('supplemental sha256 mismatch: '+name)
        for r in rows(path):
            lid=r[extra['id_field']]
            if wanted is not None and lid not in wanted:continue
            value=r[extra['text_field']]
            if lid in base and base[lid]!=value:raise ValueError('conflicting source text: '+lid)
            base[lid]=value
    cache[name]=base
    return base


POPULATION_TYPES = {'uniform', 'locked_stratum'}


def sample_type(items):
    types={r['sample_type'] for r in items}
    return next(iter(types)) if len(types)==1 else 'mixed' if types else 'not measured'


def population_eligible(items):
    return bool(items) and all(r['sample_type'] in POPULATION_TYPES and r.get('population_eligible', True) for r in items)


def measurement_text(row):
    h=row['headline'];e=h['errors'];n=h['opportunities']
    if not n:return 'not measured'
    if row['sample_type']=='decision_audit':
        lo,hi=h['precision_wilson95']
        return f'decision precision: {n-e}/{n} correct (95% CI {lo:.3f}–{hi:.3f})'
    if h['errors_per_100'] is not None:return f"POPULATION: {h['errors_per_100']:.3f} errors per 100 opportunities"
    return f'{e} / {n} on this sample'


def intro_sentences(score):
    sentences=[]
    for cls in GROUPS:
        if '/' in cls:continue
        pair=score['paired'].get('google_raw→ru1_v1',{}).get(cls+'|A+B')
        ours='RU1 labels'
        if not pair or not pair['items']:
            pair=score['paired'].get('google_raw→w1_label',{}).get(cls+'|A+B')
            ours='W1 labels (RU1 comparison is in-sample)'
        if not pair or not pair['items']:continue
        desc=pair['sample_description'];ci=pair['delta_ci95']
        sentences.append(f"Google vs ours on {desc}: {pair['a_errors']} errors → {pair['b_errors']} errors (ours: {ours}; 95% interval for B−A on the sample: {ci[0]:.2f} to {ci[1]:.2f} errors per opportunity; {pair['items']} scoped items).")
    missing=[c for c in CLASSES if not any(v[c+'|A+B']['status']=='measured' for v in score['versions'].values())]
    sentences.append('Not measured: '+', '.join(missing)+'.')
    sentences.append('sf6 release (accents): not scored yet; its labels on the truth lines are being fetched')
    sentences.append('Network OFF: fetching is pending outside this task; no labels were fetched here.')
    return sentences


def summarize(items, predictions, version, split_samples=True, trained_on=()):
    result={}
    for cls in GROUPS:
        for tier in ('A','B','C','A+B'):
            subset=[r for r in items if in_class(r,cls) and r['tier'] in (('A','B') if tier=='A+B' else (tier,))]
            outside=[];inside=[];regression=[];buckets=defaultdict(list)
            for r in subset:
                if r['line_id'] not in predictions:continue
                value=error(r,predictions[r['line_id']])
                if value is None:continue
                bucket='in_sample' if sample_used(r,version,trained_on) else 'regression_only' if r.get('rate_eligible') is False else 'headline'
                (inside if bucket=='in_sample' else regression if bucket=='regression_only' else outside).append((r,value))
                buckets[r['sample_type']].append(r)
            def counts(values):
                e=sum(v[0] for r,v in values);n=sum(v[1] for r,v in values);eligible=population_eligible([r for r,v in values])
                return dict(items=len(values),errors=e,opportunities=n,errors_per_100=100*e/n if n and eligible else None,wilson95=stat_module().wilson(e/n,n) if n else None,precision_wilson95=stat_module().wilson((n-e)/n,n) if n else None)
            result[cls+'|'+tier]=dict(sample_type=sample_type([r for r,v in outside] or subset),sample_types=sorted(buckets),status='measured' if outside else 'not measured', truth_items=len(subset),headline=counts(outside),in_sample=counts(inside),regression_only=counts(regression),uncovered=len(subset)-len(outside)-len(inside)-len(regression))
    if split_samples:
        split={t:summarize([r for r in items if r['sample_type']==t],predictions,version,False,trained_on) for t in sorted({r['sample_type'] for r in items})}
        for key,row in result.items():
            row['by_sample_type']={t:values[key] for t,values in split.items() if values[key]['truth_items']}
    return result


def paired(items,a,b,aname,bname,a_trained_on=(),b_trained_on=()):
    result={}
    for cls in GROUPS:
        for tier in ('A','B','C','A+B'):
            pairs=[];selected=[]
            for r in items:
                if not in_class(r,cls) or r['tier'] not in (('A','B') if tier=='A+B' else (tier,)):continue
                if sample_used(r,aname,a_trained_on) or sample_used(r,bname,b_trained_on) or r.get('rate_eligible') is False:continue
                if r['line_id'] not in a or r['line_id'] not in b:continue
                aa=error(r,a[r['line_id']]);bb=error(r,b[r['line_id']])
                if aa is not None and bb is not None:
                    pairs.append((r['doc_id'],*aa,*bb));selected.append(r)
            out=bootstrap_delta(pairs);out['sample_type']=sample_type(selected)
            out['a_errors']=sum(x[1] for x in pairs);out['b_errors']=sum(x[3] for x in pairs)
            out['delta_per_opportunity']=out['delta_per_100']/100 if pairs else None
            out['delta_ci95']=[x/100 for x in out['ci95']] if pairs else None
            if not population_eligible(selected):out['delta_per_100']=None;out['ci95']=None
            out['sample_description']='; '.join(sorted({r.get('sample_description',r['provenance']['set']) for r in selected}))
            result[cls+'|'+tier]=out
    return result


def run(truth,registry,names,flags=None):
    items,flags_sha=load_truth(truth,flags);wanted={r['line_id'] for r in items};cache={}
    arms={n:training_arms(n,registry) for n in names}
    predictions={n:load_version(n,registry,wanted,cache) for n in names}
    pairs=list(zip(names,names[1:]))
    if 'google_raw' in names and 'ru1_v1' in names:pairs.append(('google_raw','ru1_v1'))
    for n in names:
        parent=registry['versions'][n].get('parent')
        if parent in names and (parent,n) not in pairs:pairs.append((parent,n))
    if 'ru1_v1' in names and 'sf6_release' in names and ('ru1_v1','sf6_release') not in pairs:pairs.append(('ru1_v1','sf6_release'))
    return dict(schema='lqb-score-v1.2',truth_sha256=sha256(truth),truth_flags_sha256=flags_sha,trained_on={n:sorted(arms[n]) for n in names},versions={n:summarize(items,predictions[n],n,trained_on=arms[n]) for n in names},paired={a+'→'+b:paired(items,predictions[a],predictions[b],a,b,arms[a],arms[b]) for a,b in pairs})


def main():
    parser=argparse.ArgumentParser(__doc__);sub=parser.add_subparsers(dest='command',required=True)
    for cmd in ('score','trend'):
        p=sub.add_parser(cmd);p.add_argument('--truth',type=Path,default=DEFAULT/'truth_v1.jsonl');p.add_argument('--registry',type=Path,default=DEFAULT/'versions.json');p.add_argument('--output',type=Path)
        p.add_argument('--flags',type=Path,help='training flags sidecar (default: <truth stem>_flags.jsonl beside truth)')
        if cmd=='score':p.add_argument('--version',action='append',required=True)
    args=parser.parse_args();registry=json.loads(args.registry.read_text());names=args.version if args.command=='score' else list(registry['versions'])
    result=run(args.truth,registry,names,args.flags)
    if args.output:dump(args.output,result)
    else:print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
