"""SS1 descriptive census analysis; no image, network or production-code access.

Run with the specified venv Python, -B. All writes stay in small_segments/q1.
"""
from pathlib import Path
import collections
import gzip
import hashlib
import json
import math
import re
import subprocess
import sys
import unicodedata
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
SMALL = BASE / 'small_segments'
OUT = SMALL / 'q1'
INPUTS = ['cells/population_cells.jsonl.gz', 'owner_marks_20261019.jsonl',
          'gate2/replay_calibration.jsonl', 'gate2/replay_segeval1.jsonl', 'scored/owner_rows.jsonl']
A_EDGES = [1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 15, 20, 30, 50, math.inf]
BOX = {'DROP_too_little', 'DROP_too_much', 'UNC_no_row'}
QUANTILES = [1, 5, 10, 25, 50, 75, 90, 95, 99]


def chars(row):
    """Use the saved visible census characters, never recomputed raw text length."""
    return row['characters']


def rotation(width_px, height_px):
    """Rotate h>w 90 degrees right before measurement: L=max, S=min, A=L/S; retain w/h."""
    L, S = max(width_px, height_px), min(width_px, height_px)
    return dict(rotated=height_px > width_px, L=L, S=S, A=L / S,
                unrotated_w_over_h=width_px / height_px)


def xheight(xh, L, S):
    """Carry xheight_px; divide L and S only by finite positive xh, otherwise unusable."""
    usable = xh is not None and math.isfinite(xh) and xh > 0
    return dict(xh=xh, xh_usable=usable, S_xh=S / xh if usable else None,
                L_xh=L / xh if usable else None)


def output_type(raw_text, is_numeric_output):
    """After strip, numeric flag wins; mixed needs a decimal digit and <=2 L* letters; else nonnumeric."""
    text = raw_text.strip()
    if is_numeric_output:
        return 'numeric'
    if any(c.isdecimal() for c in text) and sum(unicodedata.category(c).startswith('L') for c in text) <= 2:
        return 'mixed'
    return 'nonnumeric'


def wave_group(wave):
    """W1/W2 are collect_v3; every other literal wave is v2."""
    return 'collect_v3' if wave in {'W1', 'W2'} else 'v2'


def reason_category(verdict, reason):
    """Map literal 0.5 verdict/reason; preserve distinct unrecognised reasons with hashed short slugs."""
    r = reason.lower()
    if verdict == 'KEEP':
        return 'KEEP'
    if verdict == 'DROP' and 'too little ocr output' in r:
        return 'DROP_too_little'
    if verdict == 'DROP' and 'too much ocr output' in r:
        return 'DROP_too_much'
    if verdict == 'UNCERTAIN' and (('no row' in r and ('support' in r or 'detect' in r)) or
                                    'no supported row' in r or 'no detected row' in r):
        return 'UNC_no_row'
    known = {'a second complete printed line is visible.': 'second_line',
             'more than 2 complete neighbouring words are visible.': 'neighbour_words',
             'top and bottom padding together exceed 1.5 target-line heights.': 'padding',
             'no usable text box was measured.': 'no_usable_text_box',
             'the complete neighbouring-word count or line extent is unresolved.': 'neighbour_extent_unresolved',
             'the reading direction remains unresolved.': 'reading_direction_unresolved'}
    slug = known.get(r)
    if slug is None:
        slug = re.sub(r'[^a-z0-9]+', '_', r).strip('_')[:42] or 'empty'
        slug += '_' + hashlib.sha256(reason.encode()).hexdigest()[:8]
    return ('UNC' if verdict == 'UNCERTAIN' else verdict) + '_' + slug


def box_fail(category):
    """Box failure is exactly too-little, too-much or uncertain-no-row."""
    return category in BOX


def owner_class(decision):
    """Map KEEP/ACCEPT/GOOD-like tokens to good, DROP/REJECT/BAD-like to bad, else other."""
    tokens = set(re.findall(r'[A-Z]+', str(decision).upper()))
    good = bool(tokens & {'KEEP', 'ACCEPT', 'ACCEPTED', 'GOOD'})
    bad = bool(tokens & {'DROP', 'REJECT', 'REJECTED', 'BAD'})
    return 'good' if good and not bad else 'bad' if bad and not good else 'other'


def owner_bad_box(note):
    """Flag owner notes containing box, case-insensitively."""
    return 'box' in (note or '').lower()


def bucket(value, edges, aspect=False):
    """Right-closed buckets: an exact edge belongs to the lower bucket; missing -> unusable."""
    if value is None or not math.isfinite(value):
        return 'unusable'
    for i, edge in enumerate(edges):
        if value <= edge:
            if i == 0:
                return f'≤{edge:g}'
            return f'({edges[i-1]:g}, {edge:g}]' if math.isfinite(edge) else f'>{edges[i-1]:g}'
    raise ValueError(value)


def char_bucket(value, upper):
    """Integer char buckets; retain zero/negative in a separate printed bucket."""
    if value < 1:
        return '≤0'
    low = 1
    for hi in upper:
        if value <= hi:
            return str(low) if low == hi else f'{low}–{hi}'
        low = hi + 1
    return f'{low}+'


def candidate_definitions():
    """All 45 requested candidate definitions, applied to rotated dimensions; missing xh outside C4."""
    defs = []
    for k in [1,2,3,4,5,6,8,10,12,15]: defs.append((f'C1_chars_le_{k}', 'C1', k, None))
    for a in [1.5,2,3,4,5,6,8]: defs.append((f'C2_A_le_{a}', 'C2', None, a))
    for n in [50,100,150,200]: defs.append((f'C3_L_le_{n}', 'C3', n, None))
    for q in [3,5,8,10,15]: defs.append((f'C4_L_xh_le_{q}', 'C4', q, None))
    defs.append(('C5_S_le_40_L_le_200_chars_le_10', 'C5', None, None))
    for family, aspects in [('C6',[2,3,4]), ('C7',[3,4,6])]:
        for k in [3,5,8]:
            for a in aspects: defs.append((f'{family}_chars_le_{k}_A_le_{a}', family, k, a))
    return defs


def candidate_membership(data, definition):
    """C1 chars<=k; C2 A<=a; C3 L<=N; C4 usable L/xh<=q; C5 conjunction; C6 OR; C7 AND."""
    _, family, k, a = definition
    if family == 'C1': return data['chars'] <= k
    if family == 'C2': return data['A'] <= a
    if family == 'C3': return data['L'] <= k
    if family == 'C4': return data['xh_usable'] & (data['L_xh'] <= k)
    if family == 'C5': return (data['S'] <= 40) & (data['L'] <= 200) & (data['chars'] <= 10)
    if family == 'C6': return (data['chars'] <= k) | (data['A'] <= a)
    if family == 'C7': return (data['chars'] <= k) & (data['A'] <= a)
    raise ValueError(family)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()


def read_rows(path):
    with (gzip.open(path, 'rt') if str(path).endswith('.gz') else open(path)) as f:
        for line in f:
            yield json.loads(line)


def crop_hash(row):
    """Look only for explicitly crop-named hashes or binding.crop_sha256; never infer from text/page hashes."""
    if row.get('crop_sha256'): return row['crop_sha256']
    for name in ['binding', 'after', 'before', 'previous']:
        value = row.get(name)
        if isinstance(value, dict):
            found = crop_hash(value)
            if found: return found
    return None


def join_records(census, records):
    """Join each source record by line_id==row_id, else unique crop sha; report unmatched and ambiguous hashes."""
    ids = {v:i for i,v in enumerate(census['row_id'])}
    hashes = collections.defaultdict(list)
    for i, h in enumerate(census['crop_sha256']):
        if h: hashes[h].append(i)
    results, stats = [], {}
    for rec in records:
        s = stats.setdefault(rec['set'], dict(total=0, matched=0, unmatched=0, by_line_id=0,
                                              by_crop_sha256=0, unmatched_ids=[], ambiguous_sha_ids=[]))
        s['total'] += 1
        idx, method = ids.get(rec['line_id']), 'line_id'
        if idx is None:
            hits = hashes.get(rec.get('crop_sha256'), [])
            if len(hits) == 1: idx, method = hits[0], 'crop_sha256'
            elif len(hits) > 1: s['ambiguous_sha_ids'].append(rec['line_id'])
        if idx is None:
            s['unmatched'] += 1; s['unmatched_ids'].append(rec['line_id'])
        else:
            s['matched'] += 1; s['by_'+method] += 1
        results.append(dict(rec, census_index=idx, join_method=method if idx is not None else 'unmatched',
                            census_row_id=census.iloc[idx]['row_id'] if idx is not None else None))
    return results, stats


def pct(n, d): return 100 * int(n) / int(d) if d else None


def breaks(frame):
    n = len(frame)
    counts = frame['category'].value_counts()
    c = {name:int(counts.get(name, 0)) for name in ['KEEP','DROP_too_little','DROP_too_much','UNC_no_row']}
    c['other_non_KEEP'] = n - sum(c.values())
    c['box_fail'] = int(frame['box_fail'].sum())
    return dict(n=n, n_lt_30=n < 30, **{f'n_{k}':v for k,v in c.items()},
                **{f'pct_{k}':pct(v,n) for k,v in c.items()})


def clean(value):
    if isinstance(value, dict): return {str(k):clean(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)): return [clean(v) for v in value]
    if isinstance(value, np.generic): return clean(value.item())
    if isinstance(value, float) and not math.isfinite(value): return None
    return value


def write_json(path, data):
    path.write_text(json.dumps(clean(data), ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def md_table(rows):
    if not rows: return '_No rows._\n'
    keys = list(dict.fromkeys(k for row in rows for k in row))
    def fmt(v):
        if v is None: return '—'
        if isinstance(v, (dict,list)): v = json.dumps(clean(v),ensure_ascii=False)
        elif isinstance(v,float): v = f'{v:.6f}'.rstrip('0').rstrip('.')
        return str(v).replace('&','&amp;').replace('|','&#124;').replace('\r','\\r').replace('\n','\\n')
    return '\n'.join(['| '+' | '.join(keys)+' |','| '+' | '.join(['---']*len(keys))+' |']+
                     ['| '+' | '.join(fmt(row.get(k)) for k in keys)+' |' for row in rows])+'\n'


def main():
    OUT.mkdir(exist_ok=True)
    test = subprocess.run([sys.executable,'-B','-m','pytest','-c','/dev/null','-p','no:cacheprovider',
                           str(SMALL/'tests/test_ss1_q1.py'),'-q'],capture_output=True,text=True)
    (OUT/'tests.log').write_text(test.stdout+test.stderr)
    if test.returncode: raise SystemExit('SS1 FAILED: tests; see q1/tests.log')
    input_info = []
    for p in INPUTS:
        input_info.append(dict(path=str(BASE/p),sha256=sha(BASE/p)))
    print('Streaming census', flush=True)
    slim = []
    keep = ['row_id','crop_sha256','width_px','height_px','text_characters','raw_text','source','wave','verdict_05','reason_05']
    for r in read_rows(BASE/INPUTS[0]):
        v = {k:r[k] for k in keep}
        v['chars'] = chars(r)
        v.update(rotation(r['width_px'],r['height_px']))
        v.update(xheight(r.get('xheight_px'),v['L'],v['S']))
        v['output_type'] = output_type(r['raw_text'],r['is_numeric_output'])
        v['wave_group'] = wave_group(r['wave'])
        v['category'] = reason_category(r['verdict_05'],r['reason_05'])
        v['box_fail'] = box_fail(v['category'])
        slim.append(v)
    n = len(slim); input_info[0]['row_count'] = n
    if n != 592466:
        write_json(OUT/'SS1_RECEIPT.json',dict(status='FAILED',reason='census count mismatch',inputs=input_info,census_rows_read=n))
        raise SystemExit(f'SS1 FAILED: census row count {n} != 592466')
    df = pd.DataFrame(slim); del slim
    if not df.row_id.is_unique: raise SystemExit('SS1 FAILED: duplicate census row_id')
    print('Census loaded', n, flush=True)
    records, replay_records, decision_vocab, replay_counts = [], [], collections.Counter(), {}
    for j,p in enumerate(INPUTS[1:],1):
        count = 0
        for r in read_rows(BASE/p):
            count += 1
            common = dict(line_id=r['line_id'], crop_sha256=crop_hash(r), source_file=p)
            if j == 1:
                records.append(dict(common, set='O_marks', sheet=r.get('sheet'), decision=r['owner_mark'],
                                    owner_class=owner_class(r['owner_mark']),note=r.get('note',''),updated=r.get('updated')))
            if j in [2,3]:
                replay_records.append(dict(common,set='replay_calibration' if j==2 else 'replay_segeval1',
                                           **{f'verdict_0{v}':r.get(f'verdict_0{v}') for v in [5,6,7,8]},
                                           reason_08=r.get('after',{}).get('reason')))
                if j == 2 and r.get('owner_rating') is not None:
                    rating=r['owner_rating']; dec=rating.get('decision'); decision_vocab[dec]+=1
                    records.append(dict(common,set='O_ratings',sheet=None,decision=dec,owner_class=owner_class(dec),
                                        note=rating.get('note',''),updated=rating.get('updated')))
            if j == 4:
                records.append(dict(common,set='R_150',reader_state=r['reader_state'],pipeline_decision=r['decision']))
        input_info[j]['row_count']=count
    joined, joins = join_records(df,records)
    replays, replay_joins = join_records(df,replay_records)
    replay_by_idx = collections.defaultdict(list)
    for r in replays:
        if r['census_index'] is not None: replay_by_idx[r['census_index']].append(r)
    by_idx = collections.defaultdict(list)
    unmatched_owner=[]
    for r in joined:
        if r['census_index'] is not None: by_idx[r['census_index']].append(r)
        elif r['set'] != 'R_150': unmatched_owner.append(r)
    owners=[]
    conflicts=[]
    for idx, rr in by_idx.items():
        oo=[r for r in rr if r['set'] != 'R_150']
        if not oo: continue
        d=df.iloc[idx].to_dict(); d['line_id']=d.pop('row_id'); d['census_index']=idx
        d['sets']=sorted(set(r['set'] for r in oo)); d['owner_judgments']=oo
        d['owner_classes']=sorted(set(r['owner_class'] for r in oo))
        d['owner_good']=any(r['owner_class']=='good' for r in oo)
        d['owner_bad']=any(r['owner_class']=='bad' for r in oo)
        d['owner_conflict']=d['owner_good'] and d['owner_bad']
        if d['owner_conflict']: conflicts.append(d['line_id'])
        d['note']='; '.join(r['note'] for r in oo if r.get('note'))
        d['owner_bad_box']=owner_bad_box(d['note'])
        d['replay_evidence']=replay_by_idx[idx]
        for v in [6,7,8]:
            values=sorted(set(r[f'verdict_0{v}'] for r in replay_by_idx[idx] if r.get(f'verdict_0{v}') is not None))
            d[f'verdict_0{v}']=values[0] if len(values)==1 else None
            if len(values)>1: conflicts.append(dict(line_id=d['line_id'],field=f'verdict_0{v}',values=values))
        d['reason_08']='; '.join(sorted(set(r['reason_08'] for r in replay_by_idx[idx] if r.get('reason_08'))))
        d['category_08']=reason_category(d['verdict_08'],d['reason_08']) if d['verdict_08'] else None
        owners.append(d)
    # Unmatched owner records remain in the all-owner export, with null census measurements.
    for r in unmatched_owner:
        d={k:None for k in df.columns}; d.update(line_id=r['line_id'],sets=[r['set']],owner_judgments=[r],
            owner_classes=[r['owner_class']],owner_good=r['owner_class']=='good',owner_bad=r['owner_class']=='bad',
            owner_conflict=False,note=r.get('note',''),owner_bad_box=owner_bad_box(r.get('note')),
            census_index=None,verdict_06=None,verdict_07=None,verdict_08=None,category_08=None,reason_08=None)
        owners.append(d)
    owners.sort(key=lambda r:(r['chars'] is None,r['chars'] or 0,r['A'] or 0,r['line_id']))
    with open(OUT/'owner_joined.jsonl','w') as f:
        for d in owners: f.write(json.dumps(clean(d),ensure_ascii=False,allow_nan=False)+'\n')
    meta=dict(census_n=n, wave_vocabulary=df.wave.value_counts().to_dict(),output_type_counts=df.output_type.value_counts().to_dict(),
        empty_text_n=int(df.raw_text.str.strip().eq('').sum()),xh_unusable_n=int((~df.xh_usable).sum()),
        chars_le_zero_n=int(df.chars.le(0).sum()),rotation_n=int(df.rotated.sum()),
        owner_rating_vocabulary=dict(decision_vocab),owner_rating_mapping={k:owner_class(k) for k in decision_vocab},
        owner_joins=joins,replay_joins=replay_joins,owner_unique_input_line_ids=len({r['line_id'] for r in records if r['set']!='R_150'}),
        owner_unique_matched_census_lines=sum(r['chars'] is not None for r in owners),owner_conflicts=conflicts,
        per_set_unique_line_ids={s:len({r['line_id'] for r in records if r['set']==s}) for s in joins},
        all_sets_unique_line_ids=len({r['line_id'] for r in records}),
        replay_conflicts=[dict(census_row_id=df.iloc[i].row_id,field=f'verdict_0{v}',
            values=sorted({r[f'verdict_0{v}'] for r in rr if r.get(f'verdict_0{v}') is not None}))
            for i,rr in replay_by_idx.items() for v in [5,6,7,8]
            if len({r[f'verdict_0{v}'] for r in rr if r.get(f'verdict_0{v}') is not None})>1])
    t0=[dict(verdict_05=v,reason_05=r,category=c,n=int(k)) for (v,r,c),k in
        df.groupby(['verdict_05','reason_05','category'],dropna=False).size().items()]
    tables={'T0':t0,'T0_verdict_totals':[dict(verdict=k,n=int(v)) for k,v in df.verdict_05.value_counts().items()],
            'T0_category_totals':[dict(category=k,n=int(v)) for k,v in df.category.value_counts().items()]}
    t1=[]
    cohorts=[('overall',df)]+[(f'output_type={k}',df[df.output_type==k]) for k in ['numeric','mixed','nonnumeric']]
    cohorts += [('chars≤10',df[df.chars<=10]),('chars>10',df[df.chars>10])]
    cohorts += [(f'wave_group={k}',df[df.wave_group==k]) for k in ['collect_v3','v2']]
    for name,frame in cohorts:
        for field in ['width_px','height_px','L','S','A','chars','xh','S_xh','L_xh']:
            series=frame[field].dropna()
            qs=series.quantile([p/100 for p in QUANTILES],interpolation='linear')
            t1.append(dict(cohort=name,field=field,n=len(frame),n_measured=len(series),
                           **{f'p{p}':float(qs.loc[p/100]) for p in QUANTILES}))
    tables['T1']=t1
    def labels(upper): return ['≤0']+[char_bucket(v,upper) for v in [1]+[x+1 for x in upper]]
    def char_series(upper): return df.chars.map(lambda v:char_bucket(v,upper))
    b1=char_series([1,2,3,4,5,9,15]); t1b=[]
    for label in labels([1,2,3,4,5,9,15]):
        for typ in ['all','numeric','mixed','nonnumeric']:
            frame=df[(b1==label)&(True if typ=='all' else df.output_type==typ)]
            t1b.append(dict(chars_bucket=label,output_type=typ,n=len(frame),n_rotated=int(frame.rotated.sum()),
                           n_h_gt_1_25_w=int((frame.height_px>1.25*frame.width_px).sum()),
                           n_h_gt_2_w=int((frame.height_px>2*frame.width_px).sum())))
    tables['T1b']=t1b
    b2=char_series(list(range(1,31))+[40,60]); t2=[]
    for typ in ['all','numeric','nonnumeric+mixed']:
        for rot in ['all','yes','no']:
            mask=pd.Series(True,index=df.index)
            if typ=='numeric': mask &= df.output_type=='numeric'
            if typ=='nonnumeric+mixed': mask &= df.output_type!='numeric'
            if rot!='all': mask &= df.rotated.eq(rot=='yes')
            for label in labels(list(range(1,31))+[40,60]):
                t2.append(dict(output_type=typ,rotated=rot,chars_bucket=label,**breaks(df[mask & b2.eq(label)])))
    tables['T2']=t2
    dimensions={'A':A_EDGES,'S':[10,15,20,25,30,40,50,60,80,100,math.inf],
                'L':[25,50,75,100,150,200,300,500,1000,math.inf],
                'xh':[4,6,8,10,12,15,20,25,30,40,math.inf],
                'L_xh':[1,2,3,4,5,6,8,10,15,20,30,50,math.inf]}
    bs={}; t2b=[]
    for field,edges in dimensions.items():
        values=df[field].where(df.xh_usable) if field=='xh' else df[field]
        bs[field]=values.map(lambda v:bucket(v,edges))
        ll=list(dict.fromkeys([bucket(e,edges) for e in edges[:-1]]+[f'>{edges[-2]:g}']))
        if field in ['xh','L_xh']: ll+=['unusable']
        for label in ll: t2b.append(dict(dimension=field,bucket=label,**breaks(df[bs[field]==label])))
    tables['T2b']=t2b
    b3=char_series([1,2,3,4,5,7,9,12,15,20,30]); t3=[]
    for c in labels([1,2,3,4,5,7,9,12,15,20,30]):
        for a in list(dict.fromkeys([bucket(e,A_EDGES) for e in A_EDGES[:-1]]+['>50'])):
            f=df[b3.eq(c)&bs['A'].eq(a)]
            t3.append(dict(chars_bucket=c,A_bucket=a,n=len(f),n_box_fail=int(f.box_fail.sum()),pct_box_fail=pct(f.box_fail.sum(),len(f))))
    tables['T3']=t3
    print('Building candidate and owner tables',flush=True)
    t4=[]; matched_owners=[r for r in owners if r['census_index'] is not None]
    owner_groups={'O_marks':[r for r in joined if r['set']=='O_marks' and r['census_index'] is not None],
                  'O_ratings':[r for r in joined if r['set']=='O_ratings' and r['census_index'] is not None]}
    for sheet in sorted({r['sheet'] for r in owner_groups['O_marks']}):
        owner_groups['O_marks / '+sheet]=[r for r in owner_groups['O_marks'] if r['sheet']==sheet]
    for definition in candidate_definitions():
        membership=candidate_membership(df,definition); name=definition[0]
        for side,mask in [('inside',membership),('outside',~membership)]:
            f=df[mask]; base=dict(candidate=name,side=side)
            t4.append(dict(base,section='census',group='all',n=len(f),pct_census=pct(len(f),n),
                           pct_box_fail=pct(f.box_fail.sum(),len(f)),pct_KEEP=pct(f.verdict_05.eq('KEEP').sum(),len(f)),
                           n_chars_le_10=int(f.chars.le(10).sum()),
                           pct_box_fail_chars_le_10=pct(f[f.chars<=10].box_fail.sum(),f.chars.le(10).sum()),
                           xh_unusable_n=int((~f.xh_usable).sum())))
            for field in ['output_type','wave_group']:
                for value in sorted(df[field].unique()):
                    count=int(f[field].eq(value).sum())
                    t4.append(dict(base,section='capture_'+field,group=value,n=count,pct_census=pct(count,n),
                                   pct_of_group=pct(count,df[field].eq(value).sum()),pct_of_side=pct(count,len(f))))
            for group,rr in owner_groups.items():
                selected=[r for r in rr if mask.iloc[r['census_index']]]
                good={r['census_index'] for r in selected if r['owner_class']=='good'}
                t4.append(dict(base,section='owner',group=group,n=len(selected),
                    good=sum(r['owner_class']=='good' for r in selected),bad=sum(r['owner_class']=='bad' for r in selected),
                    other=sum(r['owner_class']=='other' for r in selected),
                    **false_reject_counts(good,df,replay_by_idx)))
            selected=[r for r in matched_owners if mask.iloc[r['census_index']]]
            good={r['census_index'] for r in selected if r['owner_good']}
            t4.append(dict(base,section='owner',group='unique',n=len(selected),good=sum(r['owner_good'] for r in selected),
                bad=sum(r['owner_bad'] for r in selected),other=sum(not r['owner_good'] and not r['owner_bad'] for r in selected),
                conflicts=sum(r['owner_conflict'] for r in selected),**false_reject_counts(good,df,replay_by_idx)))
            rr=[r for r in joined if r['set']=='R_150' and r['census_index'] is not None and mask.iloc[r['census_index']]]
            counts=collections.Counter(r['reader_state'] for r in rr)
            t4.append(dict(base,section='readers_only',group='R_150',n=len(rr),fine=counts.get('fine',0),
                           flagged=counts.get('flagged',0),unresolved=counts.get('unresolved',0),states=dict(counts)))
    tables['T4']=t4
    fields=['line_id','sets','owner_classes','owner_good','owner_bad','owner_conflict','note','owner_bad_box','raw_text','chars',
            'text_characters','width_px','height_px','rotated','L','S','A','unrotated_w_over_h','xh','L_xh','output_type',
            'source','wave','verdict_05','category','verdict_08']
    tables['T5']=[{k:r[k] for k in fields} for r in matched_owners if r['chars']<=20 or r['A']<=6]
    t6=[]; upper=[1,2,3,4,5,9,15,30]
    for version in ['05','08']:
        rejected=[r for r in matched_owners if r['owner_good'] and r['verdict_'+version] is not None and r['verdict_'+version]!='KEEP']
        cats=sorted({r['category' if version=='05' else 'category_08'] for r in rejected})
        for cat in cats:
            for label in labels(upper):
                rr=[r for r in rejected if r['category' if version=='05' else 'category_08']==cat and char_bucket(r['chars'],upper)==label]
                t6.append(dict(version=version,reason_category=cat,chars_bucket=label,n=len(rr),line_ids=[r['line_id'] for r in rr]))
    tables['T6']=t6
    meta['owner_good_reject_union_unique_n']=sum(r['owner_good'] and (r['verdict_05']!='KEEP' or
        (r['verdict_08'] is not None and r['verdict_08']!='KEEP')) for r in matched_owners)
    meta['owner_good_verdict08_available_n']=sum(r['owner_good'] and r['verdict_08'] is not None for r in matched_owners)
    methods={'quantiles':'pandas linear interpolation, excluding missing values; xh itself retains 0 if present; ratios require xh>0',
             'buckets':'Right closed: exact upper edges enter the lower bucket. ≤1 aspect bucket explicitly retained. Zero chars printed separately.',
             'percentages':'0–100, denominator is the printed n unless column names specify a chars≤10 or group subset; empty denominator=null.',
             'owner_unique':'Unique matched census lines; good=any good judgment, bad=any bad judgment; conflicts counted in both and listed explicitly.',
             'false_rejects':'Owner-good unique lines, verdict!=KEEP. Missing/conflicting replay verdicts excluded and availability printed. No owner label inferred from reader_state.',
             'T6':'Version-specific histograms on unique owner-good lines; 05 and 08 can overlap. 08 categories use literal after.reason, retained in owner_joined.',
             'T4':'Rows for inside and outside, census composition, each owner set/sheet plus unique, and readers. Unmatched source rows excluded from dimensional comparisons and listed in metadata.',
             'replay_resolution':'Both replay files retained. Identical versions collapse; conflicting version values become null and are listed.',
             'T2b':'All census rows pooled; same break-curve columns as T2, by each dimension bucket.',
             'scope':'Descriptive only; no judgments or recommendations. No images/network/Clariden accessed.'}
    validation = validate_tables(tables, meta)
    meta['table_validation'] = validation
    write_json(OUT/'q1.json',dict(metadata=meta,methods=methods,tables=tables))
    text=['# SS1 Q1 — census dimensions and candidate definitions\n',
          'Descriptive tables only. Percentages are on a 0–100 scale; — means undefined. Counts and full strings are also in q1.json.\n',
          '## Methods\n',md_table([dict(item=k,definition=v) for k,v in methods.items()]),
          '## Census and join metadata\n',md_table([dict(item=k,value=v) for k,v in meta.items()])]
    for name,rows in tables.items(): text += [f'## {name}\n',md_table(rows)]
    (OUT/'Q1_TABLES.md').write_text('\n'.join(text))
    # Verify input byte identity after the analysis, not merely at start.
    for info in input_info:
        info['sha256_after']=sha(info['path'])
        if info['sha256_after']!=info['sha256']: raise SystemExit('SS1 FAILED: input changed '+info['path'])
    output_paths=[OUT/'Q1_TABLES.md',OUT/'q1.json',OUT/'owner_joined.jsonl',OUT/'tests.log',SMALL/'tests/test_ss1_q1.py',Path(__file__).resolve()]
    receipt=dict(status='READY',inputs=input_info,outputs=[dict(path=str(p),sha256=sha(p)) for p in output_paths],
        script_sha256=sha(Path(__file__)),python=sys.version,python_executable=sys.executable,pandas=pd.__version__,numpy=np.__version__,
        census_rows_read=n,owner_join_counts=joins,replay_join_counts=replay_joins,test_result=dict(returncode=test.returncode,output=test.stdout+test.stderr),
        table_validation=validation, auxiliary_inputs=[dict(path=str(BASE/'cells/HANDOFF.md'),sha256=sha(BASE/'cells/HANDOFF.md'),row_count=None,format='Markdown schema/handoff')],
        input_hashes_unchanged=True,receipt_self_hash='Excluded to avoid circular self-hash',metadata=meta)
    write_json(OUT/'SS1_RECEIPT.json',receipt)
    print(json.dumps(clean(dict(census_n=n,categories=tables['T0_category_totals'],joins=joins,meta=meta)),ensure_ascii=False),flush=True)


def validate_tables(tables, meta):
    """Check independent table partitions and complementary candidate counts before publishing the receipt."""
    n = meta['census_n']
    checks = []
    def check(name, condition):
        if not condition: raise AssertionError(name)
        checks.append(name)
    for name in ['T0','T0_verdict_totals','T0_category_totals']:
        check(name+' total', sum(r['n'] for r in tables[name]) == n)
    for typ in ['all','numeric','mixed','nonnumeric']:
        expected = n if typ=='all' else meta['output_type_counts'][typ]
        check('T1b '+typ, sum(r['n'] for r in tables['T1b'] if r['output_type']==typ)==expected)
    for typ in ['all','numeric','nonnumeric+mixed']:
        expected = n if typ=='all' else meta['output_type_counts']['numeric'] if typ=='numeric' else n-meta['output_type_counts']['numeric']
        pooled = [r for r in tables['T2'] if r['output_type']==typ and r['rotated']=='all']
        split = [r for r in tables['T2'] if r['output_type']==typ and r['rotated']!='all']
        check('T2 '+typ+' all',sum(r['n'] for r in pooled)==expected)
        check('T2 '+typ+' rotations',sum(r['n'] for r in split)==expected)
        for row in pooled:
            parts=[r for r in split if r['chars_bucket']==row['chars_bucket']]
            for field in ['n','n_KEEP','n_DROP_too_little','n_DROP_too_much','n_UNC_no_row','n_other_non_KEEP','n_box_fail']:
                check('T2 cell '+typ+' '+row['chars_bucket']+' '+field,sum(r[field] for r in parts)==row[field])
    for dim in ['A','S','L','xh','L_xh']:
        check('T2b '+dim,sum(r['n'] for r in tables['T2b'] if r['dimension']==dim)==n)
    check('T3 census total',sum(r['n'] for r in tables['T3'])==n)
    check('T3 box_fail total',sum(r['n_box_fail'] for r in tables['T3'])==sum(r['n'] for r in tables['T0_category_totals'] if r['category'] in BOX))
    for candidate in {r['candidate'] for r in tables['T4']}:
        rr=[r for r in tables['T4'] if r['candidate']==candidate]
        check(candidate+' inside+outside',sum(r['n'] for r in rr if r['section']=='census')==n)
        for side in ['inside','outside']:
            subset=[r for r in rr if r['side']==side]
            total=next(r['n'] for r in subset if r['section']=='census')
            for field in ['output_type','wave_group']:
                check(candidate+' '+side+' '+field,sum(r['n'] for r in subset if r['section']=='capture_'+field)==total)
    check('45 candidates',len({r['candidate'] for r in tables['T4']})==45)
    check('T5 unique IDs',len({r['line_id'] for r in tables['T5']})==len(tables['T5']))
    check('T5 exact requested subset',all(r['chars']<=20 or r['A']<=6 for r in tables['T5']))
    return dict(status='PASS',checks_passed=len(checks),partitions='T0, T1b, T2 including rotated splits, T2b, T3, T4 inside/outside and composition, T5 uniqueness and subset')


def false_reject_counts(good, df, replay_by_idx):
    """Count unique owner-good non-KEEP lines and explicit replay availability, without treating missing as a reject."""
    avail=reject=conflict=0
    for i in good:
        vv={r['verdict_08'] for r in replay_by_idx[i] if r.get('verdict_08') is not None}
        if len(vv)==1:
            avail+=1; reject+=next(iter(vv))!='KEEP'
        elif len(vv)>1: conflict+=1
    return dict(owner_good_unique=len(good),good_verdict05_nonKEEP=sum(df.iloc[i].verdict_05!='KEEP' for i in good),
                good_verdict08_available=avail,good_verdict08_nonKEEP=reject,good_verdict08_conflict=conflict)


if __name__=='__main__': main()
