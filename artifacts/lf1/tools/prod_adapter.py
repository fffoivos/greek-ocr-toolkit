"""LF2 schema adapter and fetch inventory. No selection, reads, or crop checks."""
import argparse
import collections
import csv
from pathlib import Path
from lf1 import rows, jsonl, dump, sha

DRAW = Path.home()/'Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/bench02/census05/candidates_v3.jsonl'
CROPS = Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/lf1_prod/crops')
REMOTE = '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3'

DRAW_FIELDS = ('quota_scope', 'scope_rank', 'in_quota', 'overdraw_order')
DRAW_POLICY = 'explicit quota_scope/in_quota; reserves by overdraw_order; OK only'

def partition(candidates):
    """Validate explicit sourcing fields. Never infer membership from rank/quota/tags."""
    groups=collections.defaultdict(list)
    ids=set(); scope_ranks=collections.defaultdict(set); orders=collections.defaultdict(set)
    for original in candidates:
        r=dict(original); rid=r.get('line_id',r['row_id'])
        missing=[k for k in DRAW_FIELDS if k not in r]
        if missing: raise ValueError(f'{rid}: missing explicit draw fields {missing}')
        scope=r['quota_scope']; cl=r.get('draw_class',r['class'])
        parts=scope.split(':') if isinstance(scope,str) else []
        if (len(parts) not in (2,3) or not all(parts) or
                parts[:2]!=[r['split'],cl] or r['split'] not in ('test','dev')):
            raise ValueError(f'{rid}: invalid quota_scope {scope!r}')
        if type(r['in_quota']) is not bool or type(r['scope_rank']) is not int or r['scope_rank']<1:
            raise ValueError(f'{rid}: invalid explicit membership/scope_rank')
        order=r['overdraw_order']
        if (r['in_quota'] and order is not None) or (not r['in_quota'] and (type(order) is not int or order<1)):
            raise ValueError(f'{rid}: invalid overdraw_order')
        if rid in ids or r['scope_rank'] in scope_ranks[scope] or (order is not None and order in orders[scope]):
            raise ValueError(f'{rid}: duplicate line_id/scope_rank/overdraw_order')
        ids.add(rid);scope_ranks[scope].add(r['scope_rank'])
        if order is not None:orders[scope].add(order)
        r.update(line_id=rid,draw_class=cl,subgroup=parts[2] if len(parts)==3 else None)
        groups[scope].append(r)
    return dict(groups)

def draw_counts(candidates):
    return {scope:dict(in_quota=sum(r['in_quota'] for r in group),
                       reserve=sum(not r['in_quota'] for r in group))
            for scope,group in partition(candidates).items()}

def key(r):
    return r['parent_id'], r['row_id']

def line_ids(candidates):
    unique = len({r['row_id'] for r in candidates}) == len(candidates)
    return {key(r):r['row_id'] if unique else '/'.join(key(r)) for r in candidates}, 'row_id' if unique else 'parent_id/row_id'

def fetch_rows(candidates, crops=CROPS):
    result=[]
    for r in candidates:
        tranche=r['parent_id'].split('-')[2]
        remote=f"{REMOTE}/collection_{tranche.lower()}_originals/{r['source']}/{r['row_id']}.png"
        local=Path(crops)/Path(remote).relative_to(REMOTE)
        result.append(dict(row_id=r['row_id'],tranche=tranche,remote_path=remote,local_path=str(local)))
    return result

def write_fetch(path, candidates, crops=CROPS):
    with Path(path).open('w') as f:
        writer=csv.DictWriter(f,fieldnames=['row_id','tranche','remote_path','local_path'],delimiter='\t')
        writer.writeheader();writer.writerows(fetch_rows(candidates,crops))

def adapt(candidates, readout, crops=CROPS):
    counts=collections.Counter(key(r) for r in candidates)
    reads=collections.Counter(key(r) for r in readout)
    missing=set(counts)-set(reads); extra=set(reads)-set(counts)
    errors=dict(missing_readout=len(missing),extra_readout=len(extra),
                duplicate_candidates=sum(v-1 for v in counts.values()),
                duplicate_readout=sum(v-1 for v in reads.values()))
    if any(errors.values()): raise ValueError(str(errors))
    by_key={key(r):r for r in readout};ids,mode=line_ids(candidates)
    partition([dict(r,line_id=ids[key(r)]) for r in candidates])
    output=[]
    for r,f in zip(candidates,fetch_rows(candidates,crops)):
        read=by_key[key(r)]
        output.append(dict(r,line_id=ids[key(r)],draw_class=r['class'],
            **{'class':r['split']+'|'+r['class']},label=read['final_text'],
            source_crop=f['local_path'],source_sha256=read['crop_sha256']))
    return output,mode

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidates',type=Path,default=DRAW);p.add_argument('--readout',type=Path,required=True)
    p.add_argument('--draw-source',type=Path,default=DRAW,help='full v3 draw for subset provenance')
    p.add_argument('--crops',type=Path,default=CROPS);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    candidates=rows(a.candidates);source={key(r):r for r in rows(a.draw_source)}
    if any(source.get(key(r))!=r for r in candidates):
        raise ValueError('candidate subset differs from explicit draw source')
    result,mode=adapt(candidates,rows(a.readout),a.crops)
    jsonl(a.output,result)
    dump(str(a.output)+'.receipt.json',dict(rows=len(result),line_id=mode,
        class_encoding='<split>|<class>',draw_policy=DRAW_POLICY,draw_sha256=sha(a.draw_source),draw_source=str(a.draw_source),
        scopes=draw_counts(rows(a.candidates)),inputs={str(f):sha(f) for f in (a.candidates,a.readout,a.draw_source)},
        output_sha256=sha(a.output),missing_readout=0,extra_readout=0))

if __name__=='__main__':main()
